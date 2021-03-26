# Semantic Lifting - CSV
This task was given av part of my TA work in the INFO216 course at UiB and involves converting non-semantic data from a CSV format into a semantic graph.
The lab8.py file is a proposed solution.

## Topic
Today's topic involves lifting data in CSV format into RDF. The goal is for you to learn how we can convert non-semantic data into RDF as well as getting familiar with some common vocabularies.

Fortunately, CSV is already structured in a way that makes the creation of triples relatively easy.

We will also use Pandas Dataframes which will contain our CSV data in python code, and we'll do some basic data manipulation to improve our output data.

## Relevant Libraries - Classes, Functions and Methods and Vocabularies
### Libraries
* RDFlib concepts from earlier (Graph, Namespace, URIRef, Literal, BNode)
* Pandas: DataFrame, apply, iterrows, astype
* DBpedia Spotlight

### Semantic Vocabularies
You do not have to use the same one, but these should be well suited.
* RDF:
	* rdf:type
* RDFS:
	* rdfs:label
* Simple Event Ontology (sem):
	* sem:Event, sem:eventType, sem:Actor, sem:hasActor, sem:hasActorType, sem:hasBeginTimeStamp, sem:EndTimeStamp, sem:hasTime, sem:hasSubEvent
* TimeLine Ontology (tl): 
	* tl:durationInt
* An example-namespace to represent terms not found elsewhere (ex):
	* ex:IndictmentDays, ex:Overturned, ex:Pardoned
* DBpedia

## Tasks
Today we will be working with FiveThirtyEight's russia-investigation dataset. It contains special investigations conducted by the United States since the Watergate-investigation with information about them to May 2017. If you found the last weeks exercice doable, I recommend trying to write this with object-oriented programming (OOP) structure, as this tends to make for cleaner code.

It contains the following columns:
* investigation
* investigation-start
* investigation-end
* investigation-days
* name
* indictment-days
* type
* cp-date
* cp-days
* overturned
* pardoned
* american
* president

More information about the columns and the dataset here: https://github.com/fivethirtyeight/data/tree/master/russia-investigation

Our goal is to convert this non-semantic dataset into a semantic one. To do this we will go row-by-row through the dataset and extract the content of each column.
An investigation may have multiple rows in the dataset if it investigates multiple people, you can choose to represent these as one or multiple entities in the graph. Each investigation may also have a sub-event representing the result of the investigation, this could for instance be indictment or guilty-plea.

For a row we will start by creating a resource representing the investigation. In this example we handle all investigations with the same name as the samme entity, and will therefore use the name of the investigation ("investigation"-column) to create the URI:

```py
name = row["investigation"]

investigation = URIRef(ex + name)
g.add((investigation, RDF.type, sem.Event))
```

Further we will create a relation between the investigation and all its associated columns. For when the investigation started we'll use the "investigation-start"-column and we can use the property sem:hasBeginTimeStamp:

```py
investigation_start = row["investigation-start"]

g.add((investigation, sem.hasBeginTimeStamp, Literal(investigation_start, datatype=XSD.datetime)))
```

To represent the result of the investigation, if it has one, We can create another entity and connect it to the investigation using the sem:hasSubEvent. If so the following columns can be attributed to the sub-event:
* type
* indictment-days
* overturned
* pardon
* cp_date
* cp_days
* name (the name of the investigatee, not the name of the investigation)

## Code to get you started
```py

import pandas as pd
import rdflib

from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, XSD

ex = Namespace("http://example.org/")
dbr = Namespace("http://dbpedia.org/resource/")
sem = Namespace("http://semanticweb.cs.vu.nl/2009/11/sem/")
tl = Namespace("http://purl.org/NET/c4dm/timeline.owl#")

g = Graph()
g.bind("ex", ex)
g.bind("dbr", dbr)
g.bind("sem", sem)
g.bind("tl", tl)

df = pd.read_csv("data/investigations.csv")
# We need to correct the type of the columns in the DataFrame, as Pandas assigns an incorrect type when it reads the file (for me at least). We use .astype("str") to convert the content of the columns to a string.
df["name"] = df["name"].astype("str")
df["type"] = df["type"].astype("str")

# iterrows creates an iterable object (list of rows)
for row in df.iterrows():
	# Do something here to add the content of the row to the graph 
	pass

g.serialize("output.ttl", format="ttl")
```

## If you have more time
If you have not already you should include some checks to assure that you don't add any empty columns to your graph.

If you have more time you can implement DBpedia Spotlight to link the people mentioned in the dataset to DBpedia resources. You can use the same code example as in the last lab, but you will need some error-handling for when DBpedia is unable to find a match. For instance:

```py
# Parameter given to spotlight to filter out results with confidence lower than this value
CONFIDENCE = 0.5

def annotate_entity(entity, filters={"types":"DBpedia:Person"}):
	try:
		annotations = spotlight.annotate(SERVER, entity, confidence=CONFIDENCE, filters=filters)
        return annotations
    # This catches errors thrown from Spotlight, including when no resource is found in DBpedia
	except SpotlightException as e:
		print(e)
		# Implement some error handling here
```

Here we use the types-filter with DBpedia:Person, as we only want it to match with people. You can choose to only implement the URIs in the response, or the types as well. An issue here is that 


## Useful readings
* [Information about the dataset](https://github.com/fivethirtyeight/data/tree/master/russia-investigation)
* [Article about working with pandas.DataFrames and CSV](https://towardsdatascience.com/pandas-dataframe-playing-with-csv-files-944225d19ff)
* [Pandas DataFrame documentation](https://pandas.pydata.org/pandas-docs/stable/reference/frame.html)
* [Simple Event Ontology Descripiton](https://semanticweb.cs.vu.nl/2009/11/sem/#sem:eventType)
* [The TimeLine Ontology Description](http://motools.sourceforge.net/timeline/timeline.html)
* [Spotlight Documentation](https://www.dbpedia-spotlight.org/api)