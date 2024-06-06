import gradio as gr
import requests
from bs4 import BeautifulSoup
import re
import smtplib
from email.mime.text import MIMEText
import time


def identify_past_tense(sentence):
    irregular_past_tense_verbs = ["was", "were", "had", "did", "hit", "saw", "said", "went", "made", "took", "got",
                                  "gave", "knew", "thought", "came", "saw"]
    past_time_indicators = ["yesterday", "last", "ago", "in", "on", "recently", "earlier", "previously", "before"]

    words = sentence.lower().split()
    for word in words:
        if word in irregular_past_tense_verbs:
            return "Past Tense"
        if word.endswith("ed"):
            return "Past Tense"
    for past in past_time_indicators:
        if past in words:
            return "Past Tense"
        break
    return ""


def identify_present_tense(sentence):
    present_tense_aux = ["am", "is", "are", "has", "have"]
    present_continuous_aux = ["am", "is", "are"]
    present_perfect_aux = ["has", "have"]
    present_time_indicators = ["today", "now", "currently", "at the moment", "right now", "these days"]

    words = sentence.lower().split()

    for i, word in enumerate(words):
        if word in present_continuous_aux and i + 1 < len(words) and words[i + 1].endswith("ing"):
            return "Present Continuous Tense"

    for i, word in enumerate(words):
        if word in present_perfect_aux and i + 1 < len(words):
            next_word = words[i + 1]
            if next_word.endswith("ed") or next_word.endswith("en") or next_word in ["gone", "done", "seen", "been"]:
                return "Present Perfect Tense"

    for i, word in enumerate(words):
        if word in present_perfect_aux and i + 1 < len(words) and words[i + 1] == "been" and i + 2 < len(words) and \
                words[i + 2].endswith("ing"):
            return "Present Perfect Continuous Tense"
    for word in words:
        if word in present_tense_aux:
            return "Present Tense"
        if word.endswith("s") and word not in present_tense_aux and word not in ["is", "was", "has", "does"]:
            return "Present Tense"
    for present in present_time_indicators:
        if present in words:
            return "Present Tense"
        break
    return ""


def identify_future_tense(sentence):
    future_tense_auxiliaries = ["will", "shall"]
    future_time_indicators = ["tomorrow", "next", "soon"]
    words = sentence.lower().split()
    for word in words:
        if word in future_tense_auxiliaries:
            return "Future Tense"
    for i, word in enumerate(words):
        if i + 1 < len(words) and words[i + 1] == "to" and i + 2 < len(words) and words[i + 2].endswith("ing"):
            return "Future Tense"
    for future in future_time_indicators:
        if future in words:
            return "Future Tense"
        break
    return ""


def identify_tenses(paragraph):
    tenses = " ".join(
        [identify_past_tense(paragraph), identify_present_tense(paragraph), identify_future_tense(paragraph)])
    tenses = [t for t in tenses.split() if t]
    return " ".join(tenses)



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
def get_news(disaster_keywords, location_keywords,url):

    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    s = soup.find_all('ul', class_="src_lst-ul")

    Matched_news = []

    if s:
        for item in s:
            for news in item.find_all("li"):
                news_text = news.get_text()
                for keyword in disaster_keywords.split(","):
                    if re.search(keyword.strip(), news_text, re.IGNORECASE):
                        if news_text not in Matched_news:
                            Matched_news.append(news_text)
                            break

    Matches_loc = []
    for news in Matched_news:
        for location in location_keywords.split(","):
            if re.search(location.strip(), news, re.IGNORECASE):
                Matches_loc.append(news)
                break

    news_by_location = {}

    for news in Matches_loc:
        content = news.split('\n')[1]
        headline = news.split('\n')[0]
        tenses = identify_tenses(content)

        for keyword in location_keywords.split(","):
            if keyword.lower() in content.lower():
                if keyword not in news_by_location:
                    news_by_location[keyword] = []
                news_by_location[keyword].append((headline, content, tenses))
                break

    results = []
    for location, news_list in news_by_location.items():
        if news_list:
            subject = f"{location} News"
            body = "\n".join([f"{i + 1}. {headline}" for i, (headline, _, _) in enumerate(news_list)])
            results.append(body)
            if email and password:
                send_email(subject, body, email, [email], password)

    return "\n\n".join(results)


    while True:
        get_news()
        time.sleep(300)

css = """
body {background-color: yellow;}
"""
iface = gr.Interface(fn=get_news, inputs=[gr.Textbox(placeholder="Disaster Name"),
                                          gr.Textbox(placeholder="Location Name"),
                                          gr.Textbox(placeholder="Enter your URL")],
                     theme=gr.themes.Default(primary_hue=gr.themes.colors.red, secondary_hue=gr.themes.colors.pink),
                     css=css,
                     outputs="text",
                     title="NEWS FINDER",
                     description="Enter the disaster name and name of the location to get the latest news headlines.")

iface.launch(share=True)
