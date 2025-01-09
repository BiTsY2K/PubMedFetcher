import argparse
import logging
import pandas as pd
import xml.etree.ElementTree as ET
from pubmedfetcher.pubmed_fetcher import setup_logging
from pubmedfetcher.pubmed_fetcher.pubmed_article_fetcher_modules import EntrezQueries, PubmedArticleFetcher

def main():
  parser = argparse.ArgumentParser(
    description=f"""Fetch research papers from NCBI Entrez database based on a query specified and with at least one author 
    affiliated with a 'Pharaceutical' or 'BioTech' Company. 
    And store the result as a CSV file or print to the Console based on the based on provided file(-f or --file) parameter.
  """)
  
  parser.add_argument("-t", "--term", help="The search term to query the database with.")
  parser.add_argument("-f", "--file", default=None, help="Output File name to save the result. Default = None, Print the output to the console",)
  parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode. Print debug Infomation during execution")
  parser.add_argument('-max', '--retmax', type=int, default=20, help="Number of record to return with the matching search term. Default is 20.")
  parser.add_argument('-type', "--rettype", help="")
  parser.add_argument('-mode', "--retmode", help="")
  args = parser.parse_args()
  args_dict = vars(args)
  
  query = f'{args.term} AND ' if args.term is not None else ''
  query = query+'(pharmaceutical[AD] OR biotech[AD] OR "biosciences"[AD] OR "biotechnology"[AD] OR "pharma"[AD] OR "Inc"[AD] OR "Corp"[AD] OR "LLC"[AD])'

  keys_to_remove = ["term", "debug", "file"]
  args_dict = {key: value for key, value in args_dict.items() if key not in keys_to_remove}

  setup_logging(args.debug)
  logger = logging.getLogger(__name__)

  try:
    logger.debug(f"\nSearching PubMed with Query: {query}\nAnd with parameters,\n{'\n\t$'.join([f"{key}={value}" for key, value in args_dict.items()])}")
    # Search Pubmed paper based on search Query 
    esearch = EntrezQueries().entrezSearch(db='pubmed', term=query, **args_dict)
    if 'eSearchResult' not in esearch:
      raise ValueError("Invalid Search Response.")
    
    # Get the Ids of all pubmed papers for the search results
    search_tree_eSearchResult = ET.fromstring(esearch)
    ids = [id.text for id in search_tree_eSearchResult.findall(".//IdList/Id")]

    logger.debug(f"\nFetching the papers from the pubmed database.")
    # Fetch the papers from the pubmed database for given list of ids.
    efetch = EntrezQueries().entrezFetch(db='pubmed', id=ids, rettype='xml', retmode='text')
    if "PubmedArticle" not in efetch:
      raise ValueError("Invalid Fetch Response.")
    
    # Get all the XML element with tag 'PubmedArticle'
    search_tree_PubmedArticleSet = ET.fromstring(efetch)
    pubmed_articles = [pubmed_article for pubmed_article in search_tree_PubmedArticleSet.findall(".//PubmedArticle")]
  except Exception as e:
    logger.error(f"Error: {e}")
    raise exit(1)
  
  logger.debug(f'\nArticle(s) fetched.')
  
  # Empty list to store paper with at least one author affiliated with 
  # a pharmaceutical or biotech company 
  filtered_articles = []  
  for article in pubmed_articles:
    article_details = PubmedArticleFetcher()._fetch_article_details(article)
    # Author affiliated to non-academic institution
    if article_details and len(article_details["non_academic_authors"]) > 0: 
      filtered_articles.append(article_details)

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
    try:
      logger.debug(f"Saving to {args.file}.csv")
      df.to_csv(f"{args.file}.csv", index=False)
      print(f"Result saved to {args.file}.csv")
    except:
      logger.error(f"Error: {e}")
  else: print(df)


if __name__ == "__main__":
    main()
