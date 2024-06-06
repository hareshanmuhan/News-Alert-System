import gradio as gr
import requests
from bs4 import BeautifulSoup
import re
import smtplib
from email.mime.text import MIMEText
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

model_path = r".\model"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)

label_mapping = {
    'present': 0,
    'future': 1,
    'past': 2,
    'present perfect continuous': 3,
    'future perfect': 4,
    'past perfect': 5,
    'future continuous': 6,
    'past perfect continuous': 7,
    'present continuous': 8,
    'past continuous': 9,
    'future perfect continuous': 10,
    'present perfect': 11,
}
inv_label_mapping = {v: k for k, v in label_mapping.items()}


def identify_tenses(paragraph):
    inputs = tokenizer(paragraph, return_tensors="pt")
    with torch.no_grad():
        logits = model(**inputs).logits
    predicted_class_id = logits.argmax().item()
    predicted_label = inv_label_mapping[predicted_class_id]
    return predicted_label


def send_email(subject, body, sender, recipients, password):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, msg.as_string())
    print("Message sent!")


email = "hareshanmuhan@gmail.com"
password = "ekcq mnix imoc tgiz"


def get_news(disaster_name, location_name, url):
    disaster_keywords = disaster_name.split(",") if disaster_name else []
    location_keywords = location_name.split(",") if location_name else []
    urls = url.split(",") if url else []

    news_by_location = {}
    unique_news = set()

    for url in urls:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        s = soup.find_all('ul', class_="src_lst-ul")

        if s:
            for item in s:
                for news in item.find_all("li"):
                    news_text = news.get_text()
                    for keyword in disaster_keywords:
                        if re.search(keyword.strip(), news_text, re.IGNORECASE):
                            headline = news_text.split('\n')[0]
                            content = " ".join(news_text.split('\n')[1:])
                            tenses = identify_tenses(content)

                            if tenses != 'past':
                                if news_text not in unique_news:
                                    unique_news.add(news_text)

                                    summary = summarizer(content, max_length=150, min_length=20, do_sample=False)[0][
                                        'summary_text']

                                    for keyword_loc in location_keywords:
                                        if keyword_loc.lower() in content.lower():
                                            if keyword_loc not in news_by_location:
                                                news_by_location[keyword_loc] = []
                                            news_by_location[keyword_loc].append((headline, summary))
                                            break

    results = []
    for location, news_list in news_by_location.items():
        if news_list:
            subject = f"{location.capitalize()} News "
            body = "\n\n".join([f"{i + 1}. {summary}" for i, (headline, summary) in enumerate(news_list)])
            results.append(f"{subject}\n{body}")
            if email and password:
                send_email(subject, body, email, [email], password)

    if not results:
        return "No relevant news articles found"

    return "\n\n".join(results)


css = """
body {background-color: yellow;}
"""
iface = gr.Interface(fn=get_news, inputs=[
    gr.Textbox(placeholder="Disaster Name (comma-separated)"),
    gr.Textbox(placeholder="Location Name (comma-separated)"),
    gr.Textbox(placeholder="Enter your URLs (comma-separated)")
],
                     outputs="text",
                     title="NEWS FINDER",
                     description="Enter the disaster name, location name, and URLs to get the latest news headlines.",
                     theme=gr.themes.Default(primary_hue=gr.themes.colors.red, secondary_hue=gr.themes.colors.pink),
                     css=css)

iface.launch(share=True)
