import requests
from bs4 import BeautifulSoup
import re
import smtplib
from email.mime.text import MIMEText
import time


def identify_past_tense(sentence):
    irregular_past_tense_verbs = ["was", "were", "had", "did", "hit", "saw", "said", "went", "made", "took", "got",
                                  "gave", "knew", "thought", "came", "saw"]
    past_time_indicators = ["yesterday", "last", "ago", "in", "on", "recently", "earlier", "previously", "before",
                            "ended", "walked", "talked", "played", "jumped"]

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
    present_time_indicators = ["today", "now", "currently", "at the moment", "right now", "these days",
                               "usually", "every day", "at this moment", "ongoing", "always", "never", "often",
                               "sometimes", "rarely"]

    words = sentence.lower().split()

    for i, word in enumerate(words):
        if word in present_continuous_aux and i + 1 < len(words) and words[i + 1].endswith("ing"):
            return "Present Continuous Tense"

    for i, word in enumerate(words):
        if word in present_perfect_aux and i + 1 < len(words):
            next_word = words[i + 1]
            if next_word.endswith("ed") or next_word.endswith("en") or next_word in ["gone", "done", "seen",
                                                                                     "been"]:
                return "Present Perfect Tense"

    for i, word in enumerate(words):
        if word in present_perfect_aux and i + 1 < len(words) and words[i + 1] == "been" and i + 2 < len(
                words) and words[i + 2].endswith("ing"):
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
    future_time_indicators = ["tomorrow", "next", "soon", "will", "shall", "might", "could", "may",
                              "I will", "I am going to", "We plan to", "We will soon", "We are intending to"]

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
    tenses = " ".join([identify_past_tense(paragraph), identify_present_tense(paragraph), identify_future_tense(paragraph)])
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

def get_news():
    urls = [
        "https://www.ndtv.com/topic/tsunami-warning",
        # "https://www.ndtv.com/topic/disaster-recovery"
    ]

    disaster_keywords = ["Tsunami"]
    location_keywords = ["japan"]
    Matched_news = []

    for url in urls:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        s = soup.find_all('ul', class_="src_lst-ul")

        if s:
            for item in s:
                for news in item.find_all("li"):
                    news_text = news.get_text()
                    for keyword in disaster_keywords:
                        if re.search(keyword, news_text, re.IGNORECASE):
                            if news_text not in Matched_news:
                                Matched_news.append(news_text)
                                break

    Matches_loc = []
    for news in Matched_news:
        for location in location_keywords:
            if re.search(location, news, re.IGNORECASE):
                Matches_loc.append(news)
                break

    news_by_location = {}

    for news in Matches_loc:
        content = news.split('\n')[1]
        headline = news.split('\n')[0]
        tenses = identify_tenses(headline)
        if "Past Tense" not in tenses:
            print('\n', f'{tenses} - {headline}')
            print('\n', f' CONTENT :  {content.strip()}')

        for keyword in location_keywords:
            if keyword.lower() in content.lower():
                if keyword not in news_by_location:
                    news_by_location[keyword] = []
                news_by_location[keyword].append((headline, content, tenses))
                break

    for location, news_list in news_by_location.items():
        if news_list:
            subject = f"{location} News"
            body = "\n".join([f"{i + 1}. {headline}" for i, (headline, _, _) in enumerate(news_list)])
            sender = "hareshanmuhan@gmail.com"
            recipients = ["hareshanmuhan@gmail.com"]
            password = "ekcq mnix imoc tgiz"

            send_email(subject, body, sender, recipients, password)


while True:
    get_news()
    time.sleep(300)