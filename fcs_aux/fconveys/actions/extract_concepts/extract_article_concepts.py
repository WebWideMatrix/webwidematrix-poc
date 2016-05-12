import logging
from collections import defaultdict

import nltk
from SPARQLWrapper import SPARQLWrapper, JSON

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


def get_entries_in_wikipedia(name):
    entries = []
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    name = name.replace(" ", "_")
    query = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?label
        WHERE { <http://dbpedia.org/resource/%s> rdfs:label ?label }
    """ % name
    sparql.setReturnFormat(JSON)
    sparql.setQuery(query)
    results = sparql.query().convert()
    for result in results["results"]["bindings"]:
        entries.append(result["label"]["value"])
    return entries


# TODO template function for filtering

def filter_named_entities_by_appearance_in_metadata(named_entities, metadata):
    RANK_THRESHOLD = 2
    all_metadata = metadata.values()
    concept_rank = defaultdict(int)
    for concept in named_entities:
        score = 0
        for value in all_metadata:
            if value is not None and concept in value:
                score += 1
        concept_rank[concept] = score
    results = [concept for concept in named_entities if concept_rank[concept] > RANK_THRESHOLD]
    logging.info("Metadata ditched" + ":"*80)
    logging.info([c for c in named_entities if c not in results])
    return results


def filter_by_appearance_in_wikipedia(named_entities):
    RANK_THRESHOLD = 1
    concept_rank = defaultdict(int)
    for concept in named_entities:
        score = len(get_entries_in_wikipedia(concept))
        concept_rank[concept] = score
    results = [concept for concept in named_entities if concept_rank[concept] > RANK_THRESHOLD]
    logging.info("Wikipedia ditched" + ":"*80)
    logging.info([c for c in named_entities if c not in results])
    return results


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
    filter_by_metadata = True
    filter_by_wikipedia = True
    result_payloads = []
    text = input_payload.get("text")
    metadata = input_payload.get("metadata", {})
    logging.info("Mm"*300)
    logging.info(metadata)
    concepts = extract_named_entities(text)
    nconcepts = len(concepts)
    # TODO consolidate ranking & tagging (rank by all criteria)
    if filter_by_metadata and metadata.values() and any(metadata.values()):
        concepts = filter_named_entities_by_appearance_in_metadata(concepts, metadata)
        logging.info("Metadata"*300)
        logging.info("Metadata based filtering returned {} out of {} named entities".format(
            len(concepts), nconcepts
        ))
        nconcepts = len(concepts)
    if filter_by_wikipedia:
        logging.info("Wikipedia"*300)
        concepts = filter_by_appearance_in_wikipedia(concepts)
        logging.info("Wikipedia based filtering returned {} out of {} named entities".format(
            len(concepts), nconcepts
        ))
        famous = True

    for concept in concepts:
        result_payloads.append(
            {
                "contentType": "concept",
                "key": concept,
                "summary": {
                    "concept": concept,
                    "famous": famous,
                    "source": input_payload.get("display_url")
                },
                "payload": {
                    "concept": concept,
                    "famous": famous
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
