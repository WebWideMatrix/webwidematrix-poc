import logging
from collections import defaultdict

import nltk

from mies.celery import app


def extract_entity_names(t):
    entity_names = []

    if hasattr(t, 'label') and t.label:
        if t.label() == 'NE':
            entity_names.append(' '.join([child[0] for child in t]))
        else:
            for child in t:
                entity_names.extend(extract_entity_names(child))

    return entity_names


def extract_named_entities(text):
    sentences = nltk.sent_tokenize(text)
    tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
    tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
    chunked_sentences = nltk.ne_chunk_sents(tagged_sentences, binary=True)
    entity_names = []
    for tree in chunked_sentences:
        entity_names.extend(extract_entity_names(tree))
    return list(set(entity_names))


def filter_named_entities_by_appearance_in_metadata(named_entities, metadata):
    RANK_THRESHOLD = 2
    all_metadata = metadata.values()
    concept_rank = defaultdict(int)
    for concept in named_entities:
        score = 0
        for value in all_metadata:
            if concept in value:
                score += 1
        concept_rank[concept] = score
    return [concept for concept in named_entities if concept_rank[concept] > RANK_THRESHOLD]


@app.task(name='extract-article-concepts')
def extract_article_concepts_action(input_payload):
    """
    Algorithm:
    * Extract all named entity using POS tagging
    * Filter the list by just those named entities appearing in the article metadata
    :param input_payload:
    :return:
    """
    logging.info("Extracting article concepts")
    logging.info(input_payload)
    result_payloads = []
    raw = input_payload.get("raw")
    text = raw.get("text")
    summary = input_payload.get("summary")
    metadata = summary.get("metadata")
    named_entities = extract_named_entities(text)
    concepts = filter_named_entities_by_appearance_in_metadata(named_entities, metadata)

    for concept in concepts:
        result_payloads.append(
            {
                "content_type": "concept",
                "key": concept,
                "summary": {
                    "concept": concept,
                    "source": summary.get("display_url")
                },
                "payload": {
                    "concept": concept
                },
                "placement_hints": {
                    "new_bldg": True,
                    "same_flr": False,
                    "flr_above": True,
                    "location_by_index": False,
                }
            }
        )

    return result_payloads
