# News-Alert-System
Description: This project implements a News Alert System that continuously scrapes news articles related to specific keywords and locations from predefined URLs, summarizes the articles, and sends email alerts with the summarized news.


Imports: The script imports necessary libraries including time, requests, BeautifulSoup for web scraping, re for regular expressions, smtplib for email functionality, MIMEText for email content, torch and transformers for NLP, and pipeline for summarization.

Model Initialization: It initializes the summarization model and tokenizer using the Hugging Face Transformers library.

Tense Identification: A function identify_tenses is defined to identify the tense of a given paragraph using a pre-trained NLP model.

Email Function: A function send_email is defined to send email notifications with the given subject, body, sender, recipients, and password.

Keyword and URL Setup: Keywords related to disasters and locations, as well as URLs of news sources, are defined.

News Collection: The get_news function collects news articles from the specified URLs, extracts relevant information using NLP and regular expressions, summarizes the articles, and organizes them based on location.

Sending Notifications: If an email and password are provided, the script sends email notifications with the summarized news articles.

Continuous Execution: The get_news function is called in a continuous loop, running every 300 seconds (5 minutes), ensuring that news is continuously collected and notifications are sent periodically.


Instructions:

Update the disaster_keywords, location_keywords, urls, email, and password variables with appropriate values.
Run the script (news_alert_system.py) to start collecting and summarizing news articles.
Ensure that the email and password are correctly configured to receive email notifications.


Dependencies:

Python 3.x
Requests
BeautifulSoup
Transformers
Torch
