import json
import urllib.parse
from rdflib import Graph, URIRef, Literal, Namespace, BNode
from rdflib.namespace import RDF, RDFS, XSD, OWL
from SPARQLWrapper import SPARQLWrapper, BASIC, POST, JSON
from collections import defaultdict

# GraphDB connection details
GRAPHDB_SERVER = "http://localhost:7200"
REPOSITORY = "KnowledgeGraphAssignment2"
USERNAME = "admin"
PASSWORD = "root"
PAP = Namespace("http://www.example.edu/papers/")

def get_sparql_connection():
    sparql = SPARQLWrapper(f"{GRAPHDB_SERVER}/repositories/{REPOSITORY}/statements")
    sparql.setHTTPAuth(BASIC)
    sparql.setCredentials(USERNAME, PASSWORD)
    sparql.setMethod(POST)
    sparql.setReturnFormat(JSON)
    return sparql

def insert_data(graph):
    sparql = get_sparql_connection()
    nt_data = graph.serialize(format='nt').decode('utf-8') if isinstance(graph.serialize(format='nt'), bytes) else graph.serialize(format='nt')
    query = f"INSERT DATA {{ {nt_data} }}"
    sparql.setQuery(query)
    try:
        results = sparql.query()
        print("Data inserted successfully!")
        return True
    except Exception as e:
        print("An error happened: ", e)
        return False

def load_dblp_data(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_valid_uri(base, identifier):
    safe_id = urllib.parse.quote(identifier.replace(' ', '_').replace('/', '_'), safe='')
    return URIRef(PAP + f"{base}_{safe_id}")

def create_paper_uri(paper_id):
    return create_valid_uri("paper", paper_id)

def create_person_uri(person_id):
    return create_valid_uri("person", person_id)

def create_keyword_uri(keyword):
    return create_valid_uri("keyword", keyword)

def create_publication_uri(pub_type, pub_name):
    pub_type = pub_type.lower().replace(' ', '_')
    return create_valid_uri(pub_type, pub_name)

def create_volume_uri(volume_info):
    return create_valid_uri("volume", volume_info)

def create_edition_uri(edition_info):
    return create_valid_uri("edition", edition_info)

def create_review_uri(review_info):
    return create_valid_uri("review", str(review_info))

def generate_statistics(graph):
    """Generate statistics about the knowledge graph."""
    stats = {
        'classes': defaultdict(int),
        'properties': defaultdict(int),
        'instances': defaultdict(int),
        'triples_by_property': defaultdict(int)
    }
    
    # Count class instances
    for s, p, o in graph.triples((None, RDF.type, None)):
        if isinstance(o, URIRef):
            class_name = str(o).split('/')[-1]
            stats['classes'][class_name] += 1
    
    # Count property usage
    for s, p, o in graph:
        if p != RDF.type:
            prop_name = str(p).split('/')[-1]
            stats['properties'][prop_name] += 1
            stats['triples_by_property'][prop_name] += 1
    
    # Count instances per main class
    main_classes = ['paper', 'author', 'reviewer', 'workshop', 'journal', 'edition', 'volume']
    for cls in main_classes:
        cls_uri = getattr(PAP, cls)
        stats['instances'][cls] = len(list(graph.subjects(RDF.type, cls_uri)))
    
    return stats

def print_statistics(stats):
    """Print statistics in a readable format."""
    print("\nKnowledge Graph Statistics:")
    print("="*50)
    
    print("\nClasses and subclasses and Instance Counts:")
    for cls, count in stats['classes'].items():
        print(f"{cls}: {count}")
    
    print("\nMain Class Instances:")
    for cls, count in stats['instances'].items():
        print(f"{cls}: {count}")
    
    print("\nTotal Triples:", sum(stats['triples_by_property'].values()))
    print("="*50)

def process_dblp_data(json_data):
    g = Graph()
    g.bind("pap", PAP)
    
    hits = json_data.get('result', {}).get('hits', {}).get('hit', [])
    if not hits:
        raise ValueError("Invalid JSON structure'")

    for hit in hits:
        info = hit['info']
        paper_id = info['paperid']
        paper_uri = create_paper_uri(paper_id)
        
        # Paper instance
        g.add((paper_uri, RDF.type, PAP.paper))
        g.add((paper_uri, PAP.p_paperid, Literal(paper_id, datatype=XSD.string)))
        g.add((paper_uri, PAP.p_title, Literal(info['title'], datatype=XSD.string)))
        
        if 'doi' in info:
            g.add((paper_uri, PAP.p_doi, Literal(info['doi'], datatype=XSD.string)))
        if 'url' in info:
            g.add((paper_uri, PAP.p_url, Literal(info['url'], datatype=XSD.string)))
        if 'year' in info:
            g.add((paper_uri, PAP.p_year, Literal(int(info['year']), datatype=XSD.int)))
        
        # Authors
        authors = info['authors']['author']
        if not isinstance(authors, list):
            authors = [authors]
            
        for i, author in enumerate(authors):
            author_uri = create_person_uri(author['@pid'])
            g.add((author_uri, RDF.type, PAP.author)) 
            g.add((author_uri, PAP.per_name, Literal(author['text'], datatype=XSD.string)))
            
            written_by_uri = create_valid_uri("written_by", f"{paper_id}_{i}")
            g.add((written_by_uri, RDF.type, PAP.written_by))
            g.add((written_by_uri, PAP.written_by_paper, paper_uri))
            g.add((written_by_uri, PAP.written_by_person, author_uri))
            g.add((written_by_uri, PAP.w_position, Literal(i+1, datatype=XSD.int)))
        
        # Keywords
        if 'keywords' in info:
            for keyword in info['keywords']:
                keyword_uri = create_keyword_uri(keyword)
                g.add((keyword_uri, RDF.type, PAP.keyword))
                g.add((keyword_uri, PAP.k_name, Literal(keyword, datatype=XSD.string)))
                g.add((paper_uri, PAP.has_keyword, keyword_uri))
        
       
        pub_type = info.get('type', 'Workshop').lower()
        pub_name = info['event_name'] if 'event_name' in info else (
            info['venue'][0] if 'venue' in info and isinstance(info['venue'], list) else info.get('venue', 'Unknown')
        )
        
        if pub_type == "conference":
            event_uri = create_publication_uri("conference", pub_name)
            g.add((event_uri, RDF.type, PAP.conference))
            g.add((event_uri, PAP.e_name, Literal(pub_name, datatype=XSD.string)))
            g.add((event_uri, PAP.e_type, Literal(pub_type, datatype=XSD.string)))
            
            if 'event_name' in info:
                edition_uri = create_edition_uri(f"{info['event_name']}_{info.get('city', 'unknown')}")
                g.add((edition_uri, RDF.type, PAP.edition))
                g.add((edition_uri, PAP.ed_name, Literal(info['event_name'], datatype=XSD.string)))
                if 'city' in info:
                    g.add((edition_uri, PAP.ed_venue, Literal(info['city'], datatype=XSD.string)))
                if 'year' in info:
                    g.add((edition_uri, PAP.ed_year, Literal(int(info['year']), datatype=XSD.int)))
                
                # Use specific subproperty for conference
                g.add((edition_uri, PAP.belongs_to_conference, event_uri))
                g.add((paper_uri, PAP.published_in_edition, edition_uri))
                
        elif pub_type == "workshop":
            event_uri = create_publication_uri("workshop", pub_name)
            g.add((event_uri, RDF.type, PAP.workshop))
            g.add((event_uri, PAP.e_name, Literal(pub_name, datatype=XSD.string)))
            g.add((event_uri, PAP.e_type, Literal(pub_type, datatype=XSD.string)))
            
            if 'event_name' in info:
                edition_uri = create_edition_uri(f"{info['event_name']}_{info.get('city', 'unknown')}")
                g.add((edition_uri, RDF.type, PAP.edition))
                g.add((edition_uri, PAP.ed_name, Literal(info['event_name'], datatype=XSD.string)))
                if 'city' in info:
                    g.add((edition_uri, PAP.ed_venue, Literal(info['city'], datatype=XSD.string)))
                if 'year' in info:
                    g.add((edition_uri, PAP.ed_year, Literal(int(info['year']), datatype=XSD.int)))
                if 'edition' in info:
                    g.add((edition_uri, PAP.ed_number, Literal(int(info['edition']), datatype=XSD.int)))
                
             
                g.add((edition_uri, PAP.belongs_to_workshop, event_uri))
                g.add((paper_uri, PAP.published_in_edition, edition_uri))
                
        elif pub_type == "journal":
            journal_uri = create_publication_uri("journal", pub_name)
            g.add((journal_uri, RDF.type, PAP.journal))
            g.add((journal_uri, PAP.j_name, Literal(pub_name, datatype=XSD.string)))
            
            if 'volume' in info:
                volume_uri = create_volume_uri(f"{pub_name}_{info['volume']}")
                g.add((volume_uri, RDF.type, PAP.volume))
                g.add((volume_uri, PAP.v_name, Literal(info['volume'], datatype=XSD.string)))
                if 'year' in info:
                    g.add((volume_uri, PAP.v_year, Literal(int(info['year']), datatype=XSD.int)))
                g.add((volume_uri, PAP.is_in, journal_uri))
                g.add((paper_uri, PAP.published_in_volume, volume_uri))

        # Reviews
        if 'review' in info:
          
            reviews = info['review'] if isinstance(info['review'], list) else [info['review']]
            review = reviews[0]  
    
            # We only have three reviewers always
            reviewers = []
            if 'reviewers' in info and 'author' in info['reviewers']:
                reviewers = info['reviewers']['author']
                if not isinstance(reviewers, list):
                    reviewers = [reviewers]
                reviewers = reviewers[:3]  
    
          
            for position, reviewer in enumerate(reviewers, start=1):
                # Create reviewer instance
                reviewer_uri = create_person_uri(reviewer['@pid'])
                g.add((reviewer_uri, RDF.type, PAP.reviewer))
                g.add((reviewer_uri, PAP.per_name, Literal(reviewer['text'], datatype=XSD.string)))

                review_uri = create_review_uri(f"{paper_id}_review_{position}")
                g.add((review_uri, RDF.type, PAP.reviewed_by))
                g.add((review_uri, PAP.r_score, Literal(review['score'], datatype=XSD.int)))
                g.add((review_uri, PAP.r_main_feedback, Literal(review['main_feedback'], datatype=XSD.string)))
                g.add((review_uri, PAP.r_decision, Literal(review['decision'], datatype=XSD.string)))
                g.add((review_uri, PAP.reviewed_by_paper, paper_uri))
                g.add((review_uri, PAP.reviewed_by_person, reviewer_uri))
                g.add((review_uri, PAP.r_position, Literal(position, datatype=XSD.int)))
        
        if 'cited' in info:
            for cited_id in info['cited']:
                cited_uri = create_paper_uri(cited_id)
                g.add((paper_uri, PAP.cites, cited_uri))
    
    return g

def main():
    try:
        dblp_data = load_dblp_data('dblp_5.json')
        dblp_graph = process_dblp_data(dblp_data)
        
        if insert_data(dblp_graph):
            stats = generate_statistics(dblp_graph)
            print_statistics(stats)

        dblp_graph.serialize(destination='G11-B2_2_ABOX-Hu-Fernandez .ttl', format='turtle')
        print("\nDone!")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()