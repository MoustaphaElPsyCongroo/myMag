#!/usr/bin/python3
from datetime import datetime
from google.cloud import language_v1
from models import storage
from models.tag import Tag
from random import randint
from time import mktime
import article_parser
import json
import re
import yake
from Levenshtein import ratio


def get_random_header(header_list):
    random_index = randint(0, len(header_list) - 1)
    return header_list[random_index]


def extract_article_content(url):
    """Extract article content from url"""
    try:
        with open('headers.json', 'r', encoding='utf8') as f:
            headers = json.load(f)
    except Exception as e:
        print('error: ', e)
        return ''

    title, content = article_parser.parse(
        url=url,
        output="markdown",
        timeout=5,
        headers=get_random_header(headers))

    if len(content) <= 1000:
        return ''

    # Remove all text between parenthesis (links)
    content = re.sub(r"\([^)]*\)", "", content)

    return content[:1970]


def extract_tags(content, lang):
    """Extract tags from a string

    Returns:
        A list of tuples of (tag, confidence)
    """
    tags = []
    invalid_tags = ['', 'Other', 'span', 'span class', 'p', 'div', 'div class']
    all_tags_raw = []

    client = language_v1.LanguageServiceClient()
    type_ = language_v1.Document.Type.PLAIN_TEXT
    document = {"content": content, "type_": type_}

    content_categories_version = (
        language_v1
        .ClassificationModelOptions.V2Model.ContentCategoriesVersion.V2
    )
    response = client.classify_text(
        request={
            "document": document,
            "classification_model_options": {
                "v2_model":
                    {"content_categories_version": content_categories_version}
            },
        }
    )

    for category in response.categories:
        name_path = category.name
        confidence = category.confidence
        names = name_path.split('/')

        for tag in names:
            if tag not in invalid_tags and tag not in all_tags_raw:
                tags.append((tag, confidence))
            all_tags_raw.append(tag)

    custom_kw_extractor = yake.KeywordExtractor(
        lan=lang,
        n=2,
        dedupLim=0.9,
        dedupFunc='seqm',
        windowsSize=1,
        top=15,
        features=None)
    tag_keywords = []
    keywords = custom_kw_extractor.extract_keywords(content)

    print('keywords before:', keywords)

    # Check the Levenshtein ratio of Yake's keywords against all keywords (not
    # tags) already in database. If this ratio is > 0 with this score cutoff,
    # we consider the two words the same keyword. Ex: révolutionner/révolution.
    known_keywords = storage.query(Tag.name).filter(
        Tag.type == 'keyword').all()

    print('known_keywords: ', known_keywords)

    # Keyword in known_keywords is a one char tuple, so keyword[0]
    keywords = [kw[0] for kw in keywords]
    for keyword in known_keywords:
        for kw in keywords:
            if ratio(keyword[0].lower(),
                     kw.lower(),
                     score_cutoff=0.65) > 0 and keyword[0] not in tag_keywords:
                tag_keywords.append(keyword[0])

    if len(tag_keywords) == 0:
        tag_keywords = keywords[:2]

    tag_keywords = [(tag, None) for tag in tag_keywords]
    print('tag_keywords: ', tag_keywords)

    for false_couples in tag_keywords:
        tags.append(false_couples)

    print('all tags final: ', tags)
    return tags


def get_new_entries_for_feed(feed_obj, last_update):
    """Get new feed entries if they are younger
    than the last time the feed was polled"""
    lst = last_update
    entries = []

    for entry in feed_obj.entries:
        if 'published_parsed' in entry:
            published_parsed = entry.published_parsed
        else:
            published_parsed = entry.updated_parsed

        if datetime.fromtimestamp(mktime(published_parsed)) > lst:
            entries.append(entry)

    return entries


def serialize_articles(articles):
    """Convert article objects of a list into a list of dicts,
      displaying tags"""
    article_dicts = []
    for article in articles:
        article_dict = article.to_dict()
        article_dict['tags'] = []
        for assoc in article.article_tag_associations:
            tag_name = assoc.tag.name
            tag_confidence = assoc.confidence
            article_dict['tags'].append([tag_name, tag_confidence])
        article_dicts.append(article_dict)
    return article_dicts
