#!/usr/bin/python3
"""Cronjob function to add tags from list and Google trends to the database"""
from Levenshtein import ratio
from models import storage
from models.tag import Tag
from models.article import Article
from pytrends.request import TrendReq


def populate_tags():
    """Add the tags from taglist.txt and current trends to the database"""
    tags_to_add = []
    db_keywords = storage.query(Tag.name).all()
    trending_keywords = get_trends()
    taglist_keywords = get_taglist_keywords()
    all_keywords = trending_keywords + taglist_keywords

    # Add the keyword if it's different enough from every existing tag
    for kw in all_keywords:
        for keyword in db_keywords:
            if (
                ratio(keyword[0], kw, score_cutoff=0.85) > 0
            ):
                break
        else:
            if kw not in tags_to_add:
                tags_to_add.append(kw)

    for tag_name in tags_to_add:
        new_tag = Tag(
            name=tag_name,
            type='keyword'
        )
        storage.new(new_tag)
    storage.save()

    if not tags_to_add:
        print('no new tags to add')
    else:
        print('added new tags:', tags_to_add)


def get_trends():
    """Fetch Google trends' trending keywords for the day in us and fr"""
    us_pytrends = TrendReq(hl='en-US', tz=360)
    fr_pytrends = TrendReq(hl='fr-FR', tz=60)

    trending_us_dataframe = us_pytrends.trending_searches(pn='united_states')
    trending_us = trending_us_dataframe.values.tolist()
    keywords_us = [keyword[0] for keyword in trending_us]

    trending_fr_dataframe = fr_pytrends.trending_searches(pn='france')
    trending_fr = trending_fr_dataframe.values.tolist()
    keywords_fr = [keyword[0] for keyword in trending_fr]

    trending_keywords = keywords_us + keywords_fr
    return trending_keywords


def get_taglist_keywords():
    """Get curated keywords from taglist.txt"""
    taglist_keywords = []
    with open('taglist.txt', 'r', encoding='utf-8') as f:
        for line in f:
            taglist_keywords.append(line.rstrip('\n'))
    return taglist_keywords
