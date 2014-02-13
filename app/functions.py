import quepy
import urllib
from datetime import datetime
from SPARQLWrapper import SPARQLWrapper, JSON
from models import Query


def removeDuplicates(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x)]


def print_define(results, target, metadata=None):
	for result in results["results"]["bindings"]:
		if result[target]["xml:lang"] == "en":
			return result[target]["value"]


def quepyProcess(question=None):
	success = True
	nlq_answer = ""
	query = ""
	results = ""

	sparql = SPARQLWrapper("http://115.146.84.150/annex/openimpact/sparql/query")
	dbpedia = quepy.install("dbpedia")
	# quepy.set_loglevel("DEBUG")

	target, query, metadata = dbpedia.get_query(urllib.unquote(question))       # Quepy does its thing.
	try:
		if target.startswith("?"):
			target = target[1:]
		if query:
			sparql.setQuery(query)
			sparql.setReturnFormat(JSON)
			results = sparql.query().convert()
			nlq_answer = print_define(results, target, metadata)
			success=True
	except:
		if query is None:
			query= ""
			nlq_answer="I have no clue"
			alert="I'm sorry, Dave. I'm afraid I can't do that. "
			success=False
		pass

	timestamp = datetime.utcnow()
	sparql_id = urllib.quote_plus(str(query))

	return [ Query(
		sparql_id = sparql_id,
		sparql_code = query,
		question = question,
		votes = None, 
		tags = [],
		timestamp = timestamp,
		asks = 1,
		success = success), nlq_answer]
