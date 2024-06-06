import time
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
    print(f'\nSending the news to your email...')
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, msg.as_string())
    print(f"Message sent!\n")

disaster_keywords = ["tsunami", "earthquake"]
location_keywords = ["japan", "taiwan"]
urls = ["https://www.ndtv.com/topic/tsunami-warning","https://www.ndtv.com/topic/disaster-recovery"]
email = "hareshanmuhan@gmail.com"
password = "ekcq mnix imoc tgiz"

def get_news():
    print("COLLECTING THE NEWS FROM THE URLS.....")
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
            location_heading = f"{location.capitalize()} - NEWS\n"
            news_body = "\n\n".join([f"{i + 1}. {summary}" for i, (headline, summary) in enumerate(news_list)])
            results.append(f"{location_heading}\n{news_body}")
            print(location_heading)
            print(news_body)

            if email and password:
                send_email(f"{location.capitalize()} - ALERT!!", news_body, email, [email], password)

    if not results:
        print("No relevant news articles found")
        return "No relevant news articles found"

    return "\n\n".join(results)

while True:
    get_news()
    time.sleep(300)
