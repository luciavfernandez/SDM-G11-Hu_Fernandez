import requests
import json
import random
import uuid
import re
import ftfy
import unicodedata
from synthetic_data import *

def normalize(text):
    if not isinstance(text, str):
        return text
    text = ftfy.fix_text(text)
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r'[\u0000-\u001F\u007F\u0080-\u009F\u200b-\u200f\u202a-\u202e\u2060-\u206f]', '', text)
    return text

query = "Computer Science" 
hits = 5
response_format = "json" 

url = f"https://dblp.org/search/publ/api?q={query.replace(' ', '+')}&h={hits}&format={response_format}"

# Send a GET request to DBLP API
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    papers = data["result"]["hits"].get("hit", [])
    
    all_authors = set()
    author_dict = {}  

    for paper in papers:
        authors = paper["info"].get("authors", {}).get("author", [])
        if isinstance(authors, dict):
            authors = [authors]

        for author in authors:
            author_id = author.get("@pid", "unknown_id")
            author_text = author.get("text", "")
            author_text = normalize(author_text)
            all_authors.add((author_id, author_text))
            author_dict[author_text] = {"@pid": author_id, "text": author_text}

    author_list = list(all_authors)
    paper_ids = [str(uuid.uuid4()) for _ in papers]
    
    for i, paper in enumerate(papers):
        info = paper["info"]
        paper_id = paper_ids[i]
        
        keywords = random.sample(keyword_list, 3)
        review = random.sample(paper_reviews, 1)
        affiliation = random.sample(affiliations, 1)
        
        authors = info.get("authors", {}).get("author", [])
        if isinstance(authors, dict):
            authors = [authors]
        
        normalized_authors = []
        for author in authors:
            if isinstance(author, dict):
                author_text = author.get("text", "")
                author_text = normalize(author_text)
                author["text"] = author_text
                normalized_authors.append(author)
        authors = normalized_authors
        
        current_authors = {author["text"] for author in authors}

        possible_reviewers = [author_dict[name] for name in author_dict if name not in current_authors]
        selected_reviewers = random.sample(possible_reviewers, 3) if len(possible_reviewers) >= 3 else possible_reviewers
        normalized_reviewers = []
        for reviewer in selected_reviewers:
            if isinstance(reviewer, dict):
                reviewer_text = reviewer.get("text", "")
                reviewer_text = normalize(reviewer_text)
                reviewer["text"] = reviewer_text
                normalized_reviewers.append(reviewer)
        reviewers = normalized_reviewers if len(normalized_reviewers) > 1 else normalized_reviewers[0] if normalized_reviewers else {}
        
        cited_papers = []
        available_papers = [p for j, p in enumerate(papers) if paper_ids[j] != paper_id]
        
        random.shuffle(available_papers)
        for p in available_papers:
            cited_authors = p["info"].get("authors", {}).get("author", [])
            if isinstance(cited_authors, dict):
                cited_authors = [cited_authors]
            cited_author_names = {a["text"] for a in cited_authors}
            
            if not current_authors.intersection(cited_author_names):
                cited_papers.append(paper_ids[papers.index(p)])
                if len(cited_papers) >= min(random.randint(1, 5), len(available_papers)):
                    break

        new_info = {}
        for key, value in info.items():
            new_info[key] = value
            if key == "authors":  
                new_info["paperid"] = paper_id
        
        new_info["keywords"] = keywords
        new_info["reviewers"] = {"author": reviewers}
        new_info["review"] = review
        new_info["affiliation"] = affiliation
        new_info["cited"] = cited_papers
        if new_info["type"] == 'Books and Theses':
            new_info["type"] = 'Journal'
        new_info = update_type(new_info)
        new_info = assign_event_attributes(new_info)
        
        paper["info"] = new_info
    with open("dblp.json", "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)

    for i, paper in enumerate(papers, 1):
        print(f"\n--- Paper {i} ---")
        for key, value in paper["info"].items():
            print(f"{key}: {value}")

    print("\nUpdated data saved as dblp.json")

else:
    print("Failed to retrieve data from DBLP API")