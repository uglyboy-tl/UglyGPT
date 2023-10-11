#!/usr/bin/env python3
# -*-coding:utf-8-*-

import re
import requests
from bs4 import BeautifulSoup

def scrape_text_from_url(url:str):
    response = requests.get(url)
    if response.status_code != 200:
        return "Error: Could not retrieve content from URL."
    soup = BeautifulSoup(response.text, "html.parser")
    tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'p']
    paragraphs = soup.find_all(tags)
    text = " ".join([p.get_text() for p in paragraphs])
    text = text.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
    text = re.sub(r'\s+', ' ', text)
    return text