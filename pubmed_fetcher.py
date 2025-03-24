import requests
import pandas as pd
import argparse
from typing import List, Dict, Tuple

def fetch_pubmed_papers(query: str, max_results: int = 10) -> List[str]:
    """Fetches PubMed paper IDs based on the query."""
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    search_url = f"{base_url}esearch.fcgi?db=pubmed&term={query}&retmax={max_results}&retmode=json"
    
    response = requests.get(search_url)
    response.raise_for_status()
    paper_ids = response.json().get("esearchresult", {}).get("idlist", [])
    
    return paper_ids

def fetch_paper_details(paper_id: str) -> Dict:
    """Fetch details for a given PubMed paper ID."""
    fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={paper_id}&retmode=json"
    response = requests.get(fetch_url)
    response.raise_for_status()
    
    return response.json()  # Needs further processing

def identify_non_academic_authors(authors: List[Dict]) -> Tuple[List[str], List[str]]:
    """Identifies authors affiliated with biotech/pharma companies."""
    non_academic_authors = []
    company_affiliations = []

    for author in authors:
        affil = author.get("affiliation", "").lower()
        if any(keyword in affil for keyword in ["biotech", "pharma", "inc.", "corp"]):
            non_academic_authors.append(author["name"])
            company_affiliations.append(affil)

    return non_academic_authors, company_affiliations

def save_results_to_csv(results: List[Dict], filename: str = "papers.csv") -> None:
    df = pd.DataFrame(results)
    df.to_csv(filename, index=False)

def main(query: str = None, file: str = None):
    if query is None:
        query = input("Enter PubMed search query: ")
    
    papers = fetch_pubmed_papers(query)
    results = [fetch_paper_details(p) for p in papers]
    
    if file:
        save_results_to_csv(results, file)
        print(f"Results saved to {file}")
    else:
        print(results)

if __name__ == "__main__":
    try:
        import sys
        if len(sys.argv) > 1:
            parser = argparse.ArgumentParser(description="Fetch research papers from PubMed.")
            parser.add_argument("query", type=str, help="PubMed search query")
            parser.add_argument("-f", "--file", type=str, help="Output file name")
            args = parser.parse_args()
            main(args.query, args.file)
        else:
            main()
    except Exception as e:
        print(f"Error: {e}")
