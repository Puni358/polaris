#!/usr/bin/env python3
import urllib.request
import json
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def search_sites():
    url = "https://meta.fieldsites.se/sparql"
    # SPARQL query for SITES_MET_ANS_NMS datasets
    query = """
    PREFIX cpmeta: <http://meta.icos-cp.eu/ontologies/cpmeta/>
    SELECT ?dobj ?fileName ?spec ?submissionTime ?timeStart ?timeEnd
    WHERE {
        ?dobj cpmeta:hasObjectSpec ?spec .
        ?dobj cpmeta:hasName ?fileName .
        FILTER (regex(?fileName, "SITES_MET_ANS_NMS", "i"))
        OPTIONAL { ?dobj cpmeta:wasSubmittedBy/cpmeta:hasSubmissionTime ?submissionTime }
        OPTIONAL { ?dobj cpmeta:hasTemporalInterval/cpmeta:hasStartRange ?timeStart }
        OPTIONAL { ?dobj cpmeta:hasTemporalInterval/cpmeta:hasEndRange ?timeEnd }
    }
    ORDER BY ?fileName
    """
    req = urllib.request.Request(url, data=query.encode("utf-8"), headers={
        "Content-Type": "application/sparql-query",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0"
    })
    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            bindings = data["results"]["bindings"]
            print(f"Found {len(bindings)} SITES_MET_ANS_NMS datasets via SPARQL:")
            for b in bindings:
                dobj = b["dobj"]["value"]
                obj_id = dobj.split("/")[-1]
                name = b["fileName"]["value"]
                t_start = b.get("timeStart", {}).get("value", "")
                t_end = b.get("timeEnd", {}).get("value", "")
                print(f"  ID: {obj_id} | Name: {name} | Range: {t_start} to {t_end}")
    except Exception as e:
        print("SPARQL query failed:", e)

search_sites()
