import pandas as pd
import rdflib
import spotlight
from pprint import pprint
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, XSD, FOAF
from spotlight import SpotlightException

# Spotlight
SERVER = "https://api.dbpedia-spotlight.org/en/annotate"
CONFIDENCE = 0.5

ex = Namespace("http://example.com/")

def annotate_entity(entity, filters={"types":"DBpedia:Person"}):
	""" Uses DBpedia Spotlight to annotate a string with a corresponding DBpedia resource and its types. Returns only the first DBpedia-resource and metadata from the response """
	annotations = [{
		"URI": ex + entity.replace(" ", "_"),
		"types": "DBpedia:Person"
	}]
	if entity and entity != "nan":	
		try:
			annotations = spotlight.annotate(SERVER, entity, confidence=CONFIDENCE, filters=filters)
		except SpotlightException as e:
			print(e)
	return annotations


pprint(annotate_entity("Donald Trump"))

# Output:
# [{'URI': 'http://dbpedia.org/resource/Donald_Trump',
#   'offset': 0,
#   'percentageOfSecondRank': 0.00012963329126449333,
#   'similarityScore': 0.999840592270902,
#   'support': 22045,
#   'surfaceForm': 'Donald Trump',
#   'types': 'Http://xmlns.com/foaf/0.1/Person,Wikidata:Q82955, Wikidata:Q5,Wikidata:Q24229398,Wikidata:Q215627,DUL:NaturalPerson,DUL:Agent,Schema:Person,DBpedia:Person,DBpedia:Agent,DBpedia:Politician'}
# ]