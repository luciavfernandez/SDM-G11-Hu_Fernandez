from rdflib import Graph, URIRef, Literal, Namespace, BNode
from rdflib.namespace import RDF, RDFS, XSD, OWL
from SPARQLWrapper import SPARQLWrapper, BASIC, POST, JSON

graphdb_server = "http://localhost:7200"
repository = "KnowledgeGraphAssignment2"
username = "admin"
password = "root"

pap = Namespace("http://www.example.edu/papers/")

def get_sparql_connection():
    sparql = SPARQLWrapper(f"{graphdb_server}/repositories/{repository}/statements")
    sparql.setHTTPAuth(BASIC)
    sparql.setCredentials(username, password)
    sparql.setMethod(POST)
    sparql.setReturnFormat(JSON)
    return sparql

def create_schema():
    g = Graph()
    
    g.bind("pap", pap)
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.bind("xsd", XSD)
    g.bind("owl", OWL)
    
    # Define all classes
    classes = [
        pap.paper,
        pap.publication,
        pap.event,
        pap.person,
        pap.keyword,
        pap.journal,
        pap.written_by,
        pap.reviewed_by
    ]
    
    for cls in classes:
        g.add((cls, RDF.type, OWL.Class))
    
    # Define subclasses
    subclasses = [
        (pap.workshop, pap.event),
        (pap.conference, pap.event),
        (pap.volume, pap.publication),
        (pap.edition, pap.publication),
        (pap.author, pap.person),
        (pap.reviewer, pap.person)
    ]
    
    for sub, parent in subclasses:
        g.add((sub, RDF.type, OWL.Class))
        g.add((sub, RDFS.subClassOf, parent))
    
    # Define object properties
    obj_properties = [
        (pap.cites, pap.paper, pap.paper),
        (pap.has_keyword, pap.paper, pap.keyword),
        (pap.published_in, pap.paper, pap.publication),
        (pap.belongs_to, pap.edition, pap.event),
        (pap.is_in, pap.volume, pap.journal),
        (pap.reviewed_by_paper, pap.reviewed_by, pap.paper),
        (pap.reviewed_by_person, pap.reviewed_by, pap.reviewer),
        (pap.written_by_paper, pap.written_by, pap.paper),
        (pap.written_by_person, pap.written_by, pap.author)
    ]
    
    for prop, domain, range_ in obj_properties:
        g.add((prop, RDF.type, OWL.ObjectProperty))
        g.add((prop, RDFS.domain, domain))
        g.add((prop, RDFS.range, range_))
    
    # Define subproperties
    subproperties = [
        (pap.belongs_to_conference, pap.belongs_to, pap.edition, pap.conference),
        (pap.belongs_to_workshop, pap.belongs_to, pap.edition, pap.workshop),
        (pap.published_in_volume, pap.published_in, pap.paper, pap.volume),
        (pap.published_in_edition, pap.published_in, pap.paper, pap.edition)
    ]
    
    for prop, parent, domain, range_ in subproperties:
        g.add((prop, RDF.type, OWL.ObjectProperty))
        g.add((prop, RDFS.subPropertyOf, parent))
        g.add((prop, RDFS.domain, domain))
        g.add((prop, RDFS.range, range_))
    
    # Define data properties
    data_properties = [
        # Paper attributes
        (pap.p_paperid, pap.paper, XSD.string),
        (pap.p_title, pap.paper, XSD.string),
        (pap.p_doi, pap.paper, XSD.string),
        (pap.p_url, pap.paper, XSD.string),
        (pap.p_year, pap.paper, XSD.int),
        
        # Person attributes
        (pap.per_name, pap.person, XSD.string),
        
        # Keyword attributes
        (pap.k_name, pap.keyword, XSD.string),
        
        # Complex attributes
        (pap.w_position, pap.written_by, XSD.int),
        (pap.r_position, pap.reviewed_by, XSD.int),
        (pap.r_score, pap.reviewed_by, XSD.int),
        (pap.r_main_feedback, pap.reviewed_by, XSD.string),
        (pap.r_decision, pap.reviewed_by, XSD.string),
        
        # Volume attributes
        (pap.v_name, pap.volume, XSD.string),
        (pap.v_year, pap.volume, XSD.int),
        
        # Edition attributes
        (pap.ed_venue, pap.edition, XSD.string),
        (pap.ed_year, pap.edition, XSD.int),
        (pap.ed_name, pap.edition, XSD.string),
        
        # Journal attributes
        (pap.j_name, pap.journal, XSD.string),
        
        # Event attributes
        (pap.e_name, pap.event, XSD.string),
        (pap.e_type, pap.event, XSD.string)
    ]
    
    for prop, domain, range_ in data_properties:
        g.add((prop, RDF.type, OWL.DatatypeProperty))
        g.add((prop, RDFS.domain, domain))
        g.add((prop, RDFS.range, range_))
    
    return g

def main():
    try:
  
        schema_graph = create_schema()
        sparql = get_sparql_connection()
        
        # Handle serialization properly
        nt_data = schema_graph.serialize(format='nt')
        if isinstance(nt_data, bytes):
            nt_data = nt_data.decode('utf-8')
        
        query = f"INSERT DATA {{ {nt_data} }}"
        sparql.setQuery(query)
        results = sparql.query()
        print("Schema created in GraphDB!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()