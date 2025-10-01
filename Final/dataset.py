import requests
import pandas as pd

from typing import List
from bs4 import (BeautifulSoup, Tag)


BASE_URL = 'https://habr.com'
USER_AGENT_MS_EDGE = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'

DS_COL_ID = 'id'
DS_COL_TITLE = 'title'
DS_COL_AUTHOR = 'author'
DS_COL_DATE = 'date'
DS_COL_COMPLEXITY = 'complexity'
DS_COL_READING_TIME = 'reading_time'
DS_COL_TAGS = 'tags'
DS_COL_HUBS = 'hubs'
DS_COL_SCORE = 'score'
DS_COL_BOOKMARKS = 'bookmarks'
DS_COL_COMMENTS = 'comments'
DS_COL_TEXT = 'text'

DATASET_COLUMNS = [
    DS_COL_ID, DS_COL_TITLE, DS_COL_AUTHOR, DS_COL_DATE, DS_COL_COMPLEXITY, DS_COL_READING_TIME,
    DS_COL_TAGS, DS_COL_HUBS, DS_COL_SCORE, DS_COL_BOOKMARKS, DS_COL_COMMENTS, DS_COL_TEXT
]


def make_soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, 'html.parser')


def extract_text(tag: Tag) -> str:
    return tag.text.strip() if tag else None


def extract_sub_spans_text(tag: Tag, sub_span_class: str) -> list:
    a_tags = tag.find_all('a', class_=sub_span_class) if tag else []
    return [extract_text(a.find('span')) for a in a_tags]


def extract_content(tag: Tag) -> str:
    return tag.get('content') if tag else None


def parse_article(article_response: requests.Response) -> dict:
    soup = make_soup(article_response.text)

    article_id = extract_content(soup.find('meta', {'property': 'aiturec:item_id'}))
    article_title = extract_content(soup.find('meta', {'name': 'aiturec:title'}))
    article_author = extract_text(soup.find('a', class_='tm-user-info__username'))
    article_date = extract_content(soup.find('meta', {'property': 'aiturec:datetime'}))
    article_complexity = extract_text(soup.find('span', class_='tm-article-complexity__label'))
    article_reading_time = extract_text(soup.find('span', class_='tm-article-reading-time__label'))

    article_tags_div = soup.find('div', class_='tm-separated-list tag-list tm-article-presenter__meta-list')
    article_tags = extract_sub_spans_text(article_tags_div, 'tm-tags-list__link')

    article_hubs_div = soup.find('div', class_='tm-separated-list tm-article-presenter__meta-list')
    article_hubs = extract_sub_spans_text(article_hubs_div, 'tm-hubs-list__link')

    article_rating_div = soup.find('div', class_='article-rating')
    acticle_score_counter = extract_text(article_rating_div.find('span', class_='tm-votes-lever__score-counter'))
    if acticle_score_counter is None or str(acticle_score_counter) == '':
        acticle_score_counter = extract_text(article_rating_div.find('span', class_='tm-votes-meter__value'))

    article_bookmarks_counter = extract_text(soup.find('span', class_='bookmarks-button__counter'))

    acticle_comments_counter_a = soup.find('a', class_='article-comments-counter-link')
    acticle_comments_counter = extract_text(acticle_comments_counter_a.find('span', class_='value'))

    article_text_tag = soup.find('div', class_='article-formatted-body')
    acticle_text = article_text_tag.getText(separator=' ', strip=True) if article_text_tag else ''

    return {
        DS_COL_ID: article_id,
        DS_COL_TITLE: article_title,
        DS_COL_AUTHOR: article_author,
        'date': article_date,
        'complexity': article_complexity,
        'reading_time': article_reading_time,
        'tags': article_tags,
        'hubs': article_hubs,
        'score': acticle_score_counter,
        'bookmarks': article_bookmarks_counter,
        'comments': acticle_comments_counter,
        'text': acticle_text
    }


def fetch_page(url: str) -> requests.Response:
    headers = {'User-Agent': USER_AGENT_MS_EDGE}
    return requests.get(url, headers=headers)


def fetch_max_page_number(root_page_url: str) -> int:
    root_page_response = fetch_page(root_page_url)
    soup = make_soup(root_page_response.text)
    pagination_div = soup.find('div', class_='tm-pagination__pages')
    pagination_pages_a = pagination_div.find_all('a', class_='tm-pagination__page')
    page_numbers = [int(page_a.text) if page_a else 0 for page_a in pagination_pages_a]
    return max(page_numbers)


def fetch_article_links(base_url: str, url_path: str) -> List[str]:
    article_links: List[str] = []

    max_page_number = fetch_max_page_number(f"{base_url}{url_path}/")

    for page in range(0, max_page_number):
        print(f"Collecting links from {url_path} page {page + 1} of {max_page_number}...")

        page_response = fetch_page(f"{base_url}{url_path}/page{page+1}/")

        soup = make_soup(page_response.text)
        article_links_a_tags = soup.find_all('a', class_='tm-article-snippet__readmore')

        for link_href in [link.get('href') for link in article_links_a_tags]:
            if link_href:
                article_links.append(BASE_URL + link_href)

    return article_links


def log_article(article: dict):
    print(f"Article ID: {article[DS_COL_ID]}")
    print(f"Title: {article[DS_COL_TITLE]}")
    print(f"Author: {article[DS_COL_AUTHOR]}")
    print(f"Date: {article['date']}")
    print(f"Complexity: {article['complexity']}")
    print(f"Reading Time: {article['reading_time']}")
    print(f"Tags: {article['tags']}")
    print(f"Hubs: {article['hubs']}")
    print(f"Score: {article['score']}")
    print(f"Bookmarks: {article['bookmarks']}")
    print(f"Comments: {article['comments']}")
    print(f"Text: {article['text'][:100]}...")
    print("-" * 110)


def save_dataframe(df: pd.DataFrame, name: str, file_name: str):
    print(f"Saving `{name}` to {file_name}")
    df.to_excel(file_name, sheet_name=name, index=False, header=True)


def fetch_dataset(name: str, file_name: str, url_path: str):
    print(f"Fetching {name} from {BASE_URL}{url_path}...")
    article_links = fetch_article_links(BASE_URL, url_path)
    print(f"Got {len(article_links)} articles.\n")

    ds = pd.DataFrame(columns=DATASET_COLUMNS)
    for link in article_links:
        article_response = fetch_page(link)
        article = parse_article(article_response)
        ds = pd.concat([ds, pd.DataFrame([article])], ignore_index=True)
        log_article(article)

    save_dataframe(ds, name, file_name)


fetch_dataset('HABR train-test dataset', 'habr_articles_train_test.xlsx', '/ru/companies/otus/articles')
fetch_dataset('HABR validation dataset', 'habr_articles_validation.xlsx', '/ru/articles')
