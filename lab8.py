import pandas as pd
import rdflib
import spotlight

from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, XSD, FOAF
from spotlight import SpotlightException

# Spotlight
SERVER = "https://api.dbpedia-spotlight.org/en/annotate"
CONFIDENCE = 0.5

ex = Namespace("http://example.org/")
dbr = Namespace("http://dbpedia.org/resource/")
dul = Namespace("http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#")
schema = Namespace("http://schema.org/")
sem = Namespace("http://semanticweb.cs.vu.nl/2009/11/sem/")
tl = Namespace("http://purl.org/NET/c4dm/timeline.owl#")
wd = Namespace("http://www.wikidata.org/entity/")


class RussiaInvestigationGraph(Graph):
	""" Class handler for the Russia Investigation Dataset """
	def __init__(self):
		super().__init__()

	@staticmethod
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
		return annotations[0]

	def add_metadata(self, annotation):
		""" Adds the types of an annotation to the graph """
		types = annotation["types"].split(",")
		entity = URIRef(annotation["URI"])
		for _type in types:
			if "dbpedia" in _type.lower():
				self.add((entity, RDF.type, URIRef(dbr + _type.split(":")[1])))
			elif "wikidata" in _type.lower():
				self.add((entity, RDF.type, URIRef(wd + _type.split(":")[1])))
			elif "schema" in _type:
				self.add((entity, RDF.type, URIRef(schema + _type.split(":")[1])))
			elif "FOAF" in _type:
				self.add((entity, RDF.type, URIRef(FOAF + _type.split("/0.1/")[1])))
			elif "DUL" in _type:
				self.add((entity, RDF.type, URIRef(dul + _type.split(":")[1])))
	
	def add_row(self, row, g):
		""" Method for adding all information in a row to the graph """
		name = row["investigation"]
		inves_start = row["investigation-start"]
		inves_end = row["investigation-end"]
		inves_days = row["investigation-days"]
		investigatee_annotation = self.annotate_entity(row["name"])
		indict_days = row["indictment-days"]
		result = row["type"]
		cp_date = row["cp-date"]
		cp_days = row["cp-days"]
		overtnd = row["overturned"]
		pardoned = row["pardoned"]
		american = row["american"]
		pres_annotation = self.annotate_entity(row["president"])

		# Main event (investigation) URI
		investigation = URIRef(ex + name)

		# Investigatee information
		investigatee = URIRef(investigatee_annotation["URI"])
		self.add((investigatee, RDF.type, sem.Actor))
		self.add((investigatee, sem.hasActorType, dbr.Suspect))
		if american:
			self.add((investigatee, sem.hasActorType, ex.American))
		self.add((investigatee, ex.actorIn, investigation))
		self.add_metadata(investigatee_annotation)

		# President information
		pres = URIRef(pres_annotation["URI"])
		self.add((pres, RDF.type, sem.Actor))
		self.add((pres, sem.hasActorType, dbr.President))
		self.add_metadata(pres_annotation)

		# Main event
		self.add((investigation, RDF.type, dbr.Criminal_Investigation))
		self.add((investigation, RDF.type, sem.Event))
		self.add((investigation, RDFS.label, Literal(name, datatype=XSD.str)))
		self.add((investigation, sem.hasBeginTimeStamp, Literal(inves_start, datatype=XSD.date)))
		self.add((investigation, sem.hasEndTimeStamp, Literal(inves_end, datatype=XSD.date)))
		self.add((investigation, tl.durationInt, Literal(inves_days, datatype=XSD.int)))
		self.add((investigation, sem.hasActor, investigatee))
		self.add((investigation, sem.hasActor, pres))
				
		# Sub event for conviction/guilty-plea
		if result != "nan" and result != "indictment":
			# I use blank nodes for the representation of the convictions
			conviction = BNode()
			# Alternatively a named node can be used, but keep in mind that the URIs should be unique for each conviction-type-event in order to separate them.
			self.add((investigation, sem.hasSubEvent, conviction))
			self.add((conviction, RDF.type, sem.Event))
			self.add((conviction, sem.eventType, URIRef(ex + result)))
			self.add((conviction, ex.indictmentDays, Literal(indict_days, datatype=XSD.int)))
			if overtnd:
				self.add((conviction, sem.eventType, ex.Overturned))
			if pardoned:
				self.add((conviction, sem.eventType, ex.Pardoned))
			self.add((conviction, sem.hasTime, Literal(cp_date, datatype=XSD.date)))
			self.add((conviction, tl.durationInt, Literal(cp_days, datatype=XSD.int)))
			self.add((conviction, sem.hasActor, investigatee))


g = RussiaInvestigationGraph()
g.bind("rdf", RDF)
g.bind("ex", ex)
g.bind("dbr", dbr)
g.bind("dul", dul)
g.bind("schema", schema)
g.bind("sem", sem)
g.bind("tl", tl)
g.bind("wd", wd)

df = pd.read_csv("lab8/data/investigations.csv")
df["name"] = df["name"].astype("str")
df["type"] = df["type"].astype("str")
# Apply takes an execuatable as an arugment and executes this on every row (with axis=1 parameter)
df.apply(g.add_row, axis=1)

# This will be equivalent to df.apply, but apply is slightly faster
# for row in df.iterrows():
# 	row = row[1]
# 	name = row["investigation"]

	# investigation = URIRef(ex + name)
	# g.add((investigation, RDF.type, sem.Event))
		

g.serialize("lab8/output.ttl", format="ttl")
