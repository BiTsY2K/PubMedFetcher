import argparse
import pandas as pd
import xml.etree.ElementTree as ET
from pubmedfetcher.pubmedEntrezQueries import EntrezQueries
from pubmedfetcher.pubmed_fetcher.pubmed_article_fetcher_modules import PubmedArticleFetcher 

def main():
  parser = argparse.ArgumentParser(
    description=f"""Fetch research papers from NCBI Entrez database based on a query specified and with at least one author 
    affiliated with a 'Pharaceutical' or 'BioTech' Company. 
    And store the result as a CSV file or print to the Console based on the based on provided file(-f or --file) parameter.
  """)
  parser.add_argument('-db', '--db', help="")
  parser.add_argument("-t", "--term", help="The search term to query the database with.")
  parser.add_argument("-f", "--file", default=None, help="Output File name to save the result. Default = None, Print the output to the console",)
  
  parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode. Print debug Infomation during execution")
  args = parser.parse_args()
  args_dict = vars(args)
  print(args)
  db = args.db if args.db is not None else 'pubmed'
  query = f'{args.term} AND ' if args.term is not None else ''
  query = query+'(pharmaceutical[AD] OR biotech[AD] OR "biosciences"[AD] OR "biotechnology"[AD] OR "pharma"[AD] OR "Inc"[AD] OR "Corp"[AD] OR "LLC"[AD])'

  keys_to_remove = ["db", "term"]
  args_dict = {key: value for key, value in args_dict.items() if key not in keys_to_remove}
  
  # Search Pubmed paper based on search Query 
  esearch = EntrezQueries().entrezSearch(db='pubmed', term=query, **args_dict)
  
  # Get the Ids of all pubmed papers for the search results
  search_tree_eSearchResult = ET.fromstring(esearch)
  ids = [id.text for id in search_tree_eSearchResult.findall(".//IdList/Id")]
  print("id: ", ids)

  # Fetch the papers from the pubmed database for given list of ids.
  efetch = EntrezQueries().entrezFetch(db='pubmed', id=ids, rettype='xml', retmode='text')

  # Get all the XML element with tag 'PubmedArticle'
  search_tree_PubmedArticleSet = ET.fromstring(efetch)
  pubmed_articles = [pubmed_article for pubmed_article in search_tree_PubmedArticleSet.findall(".//PubmedArticle")]

  # Empty list to store paper with at least one author affiliated with 
  # a pharmaceutical or biotech company 
  filtered_articles = []  
  for article in pubmed_articles:
     article_details = PubmedArticleFetcher()._fetch_article_details(article)
     # Author affiliated to non-academic institution
     if len(article_details["non_academic_authors"]) > 0: filtered_articles.append(article)

  for article in filtered_articles: 
    print("ARTICLES: ", article['pubmed_id'] )

  # Construct Dataframe table
  rows = []
  for article in filtered_articles:
    rows.append({
      "PubmedID": article["pubmed_id"],
      "Title": article["article_title"],
      "Publication Date": article["publication_date"],
      "Non-academic Author(s)": ", ".join(a["name"] for a in article["non_academic_authors"]),
      "Company Affiliation(s)": ", ".join(article["company_affiliations"]),
      "Corresponding Author Email": article["corresponding_author_email"] or ""
    })
  
  # Convert to Datafram using Pandas library
  df = pd.DataFrame(rows)

  # Output results: Save to CSV file 
  # default to console, if -f/--file flag with file path missing
  if (args.file):
    df.to_csv(args.file, index=False)
    print(f"Result saved to {args.file}")
  else: print(df.to_string)


if __name__ == "__main__":
    main()
