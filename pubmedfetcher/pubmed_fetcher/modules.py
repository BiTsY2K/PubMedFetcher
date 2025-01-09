import logging
from typing import List, Tuple
import xml.etree.ElementTree
from pubmedfetcher.pubmed_fetcher.__init__ import _is_academic_affiliation, _extract_email, _request

from pubmedfetcher.types import Article, Author

class PubmedArticleFetcher:
  def __init__(self):
    self.logger = logging.getLogger(__name__)
  
  def _fetch_publicationDate(self, article_date: xml.etree.ElementTree) -> str:
    """
    Extract and format publication date from a PubMed article XML element.
    
    Handles date formats in PubMed XML, including incomplete dates like year-only or year-month.
    
    Args:
      article_date (xml.etree.ElementTree.Element): XML element containing date information
      Expected structure:
        <PubDate>
            <Year>YYYY</Year>
            <Month>MonthName</Month>
            <Day>DD</Day>
        </PubDate>
    
    Returns:
      str: Formatted date string in "DD Month YYYY" format.
        Returns partial dates if only year/month are available:
        - "Month YYYY" if no day
        - "YYYY" if only year
        Returns empty string if no valid date components are found.
    """
    # Safe extraction of data with empty string as default values for text if tag is missing
    year_text = article_date.find("./Year").text if article_date.find("./Year") is not None else ""
    month_text = article_date.find("./Month").text if article_date.find("./Month") else ""
    day_text = article_date.find("./Day").text if article_date.find("./Day") is not None else ""
    
    # Build date string based on available components
    if year_text and month_text and day_text:
        return f"{day_text} {month_text} {year_text}"
    elif year_text and month_text:
        return f"{month_text} {year_text}"
    elif year_text:
        return year_text
    else:
        return ""

  def _fetch_author_details(self, author: xml.etree.ElementTree) -> Tuple[Author, str, str]:
    """
    Extract and process author details from a PubMed XML author element.
    
    Parses author information including name, affiliation, and email address.
    It also classifies whether the affiliation is academic or non-academic. Email addresses
    are extracted from affiliation text if present.
    
    Args:
      author (xml.etree.ElementTree.Element): XML element containing author data
      Expected structure:
        <Author>
            <ForeName>...</ForeName>
            <LastName>...</LastName>
            <AffiliationInfo>
                <Affiliation>...</Affiliation>
            </AffiliationInfo>
        </Author>

    Returns:
      tuple: A tuple containing three elements:
        1. dict: Author information with the following keys:
            - name (str): Full name (forename + lastname)
            - affiliation (str): Complete affiliation text
            - email (str): Author's email if found in affiliation
            - is_academic_affiliation (bool): True if affiliated with academia
        2. str: Company affiliation text if non-academic, empty string otherwise
        3. str: Author's email if non-academic, empty string otherwise

    Note:
      - Empty strings are used as default values for missing XML elements
      - Email is extracted from affiliation text using _extract_email helper
      - Academic status is determined by _is_academic_affiliation helper
    """
    # Extract author affiliation components from XML
    affiliation = author.find("./AffiliationInfo/Affiliation")

    # Use empty string as default values for text if tag is missing
    affiliation_text = affiliation.text if affiliation is not None else ""

    # Determine academic status and set the corresponding value
    # Store company affiliation if it's non-academic and email for non-academic authors 
    is_academic_affiliation = _is_academic_affiliation(affiliation_text)

    if is_academic_affiliation:
      return {}, '', ''

    # Extract author name components from XML
    author_forename = author.find("./ForeName")
    author_lastname = author.find("./LastName")

    # Use empty string as default values for text if tag is missing
    author_forename_text = author_forename.text if author_forename is not None else ""
    author_lastname_text = author_lastname.text if author_lastname is not None else ""
    
    # Extract email from affiliation text if present
    author_email = _extract_email(affiliation_text) if affiliation_text else ""

    company_affiliation = affiliation_text if affiliation_text and not is_academic_affiliation else ""
    corresponding_email = author_email if author_email and not is_academic_affiliation else ""

    return {
      "name": f"{author_forename_text} {author_lastname_text}".strip(),
      "affiliation": affiliation_text,
      "email": author_email,
      "is_academic_affiliation": is_academic_affiliation
    }, company_affiliation, corresponding_email

  def _fetch_article_details(self, article: xml.etree.ElementTree) -> Article:
    """
    Extract key details from a PubMed article XML element.
        
    Args:
      article (xml.etree.ElementTree.Element): XML element containing article data
    
    Returns:
      dict: Dictionary containing the following article metadata:
        - pubmed_id (str): PubMed identifier
        - article_title (str): Title of the article
        - publication_date (str): Formatted publication date
        - non_academic_authors (list): List of authors with non-academic affiliations
            Each author is a dict containing author details
        - company_affiliations (list): Unique list of company/organization affiliations
        - corresponding_author_email (str): Email of the corresponding author, if available
    """

    # Extract basic article metadata with fallback to empty string if elements are missing
    pub_date = self._fetch_publicationDate(article.find(".//PubDate"))
    pubmed_id = article.find(".//PMID").text if article.find(".//PMID") is not None else ""
    article_title = article.find(".//ArticleTitle").text if article.find(".//ArticleTitle") is not None else ""
    
    # Get all authors listed in the articles
    authors_list = article.findall("./MedlineCitation/Article/AuthorList/Author")
    
    # Process each author's information
    authors: List[Author] = []          # List to store all processed author information
    company_affiliation: List[str] = [] # List to store all company affiliations
    corresponding_email = None          # Store first found email (assumed to be corresponding author)
    
    # Extract details for each author
    for author in authors_list:
      author, affiliation, email = self._fetch_author_details(author)
      if not author:
        continue
      authors.append(author)
      #print("author: ",author)
      if affiliation: company_affiliation.append(affiliation)
      # Store the first email found as the corresponding author's email
      if not corresponding_email and email: corresponding_email = email

    return {
      'pubmed_id': pubmed_id, 
      'article_title': article_title,
      'publication_date': pub_date, 
      'non_academic_authors': [a for a in authors if not a['is_academic_affiliation']],
      'company_affiliations': list(set(company_affiliation)),
      'corresponding_author_email': corresponding_email
    }

class EntrezQueries:
  def __init__(self):
    self.baseURL='https://eutils.ncbi.nlm.nih.gov/entrez/eutils'
    self.endpoint_suffix='fcgi'

  def entrezInfo(self, **kwargs):
    """
    Provides field names, index term counts, last update, and available links for each Entrez database.
    Provides a list Entrez databases, if no database parameter is supplied.
  
    Args: 
      database (str): Name of the Entrez database.
    
    Returns:
      XML containing database statistics
      Note: If no database parameter is supplied, entrezInfo will return a list of all valid Entrez databases.
    """
    endpoint = 'einfo'
    payload = {}
    payload.update(kwargs)
    url = f'{self.baseURL}/{endpoint}.{self.endpoint_suffix}'
    response = _request(url, payload)
    response.raise_for_status()
    return response.text

  def entrezSearch(self, db='pubmed', term=None, **kwargs):
    """
    Searches and retrieves primary IDs (for use in FetchEntrezQuery, LinkEntrezQuery and SummaryEntrezQuery) and term translations, 
    and optionally retains results for future use in the user's environment.

    Args:

    Returns:
      A list of primary IDs from the search matching a text query
    """
    endpoint = 'esearch'
    payload = {
      'db': db,
      'term': term 
    }
    payload.update(kwargs)
    url = f'{self.baseURL}/{endpoint}.{self.endpoint_suffix}'
    response = _request(url, payload)
    response.raise_for_status()
    return response.text

  def entrezSummary(self, db='pubmed', id=None, **kwargs):
    """
    EntrezSummary retrieves document summaries(DocSums) for a list of primary IDs or 
    for a set of UIds stored on the Entrez History Server

    See the online documentation for an explanation of the parameters:
    http://www.ncbi.nlm.nih.gov/books/NBK25499/#chapter4.ESummary

    Args:
      db (type: str) (default = pubmed)  : Database from which to retrieve DocSums. The value must be a valid Entrez database name.
      id (type: list) : UID list. Either a single UID or a comma-delimited list of UIDs may be provided. All of the UIDs must be from the database specified by db\n
        Required Parameter – Used only when input is from a UID list

    Returns:
      Handle to the results, in XML format (XML DocSums)
    """
    endpoint = 'esummary'
    payload = {
      'db': db,
    }

    if id is not None:
        payload.update({'id': id})

    payload.update(kwargs)
    url = f'{self.baseURL}/{endpoint}.{self.endpoint_suffix}'
    response = _request(url, payload)
    response.raise_for_status()
    return response.text

  def entrezFetch(self, db='pubmed', id=None, **kwargs):
    """
    EntrezFetch retrieve formatted data records in the requested format for a list of input UIDs 
    or for a set of UIDs stored on the Entrez History server.
    
    See the online documentation for an explanation of the parameters:
    http://www.ncbi.nlm.nih.gov/books/NBK25499/#chapter4.EFetch

    Args:
      db (type: str) (default = pubmed)  : Database from which to retrieve DocSums. The value must be a valid Entrez database name.
      id (type: list) : UID list. Either a single UID or a comma-delimited list of UIDs may be provided. All of the UIDs must be from the database specified by db\n
        Required Parameter - Used only when input is from a UID list

    Returns:
      Formatted data records as specified
    """
    endpoint = 'efetch'
    payload = {
      'db': db,
    }
    
    if id is not None:
        payload.update({'id': id})

    payload.update(kwargs)
    url = f'{self.baseURL}/{endpoint}.{self.endpoint_suffix}'
    response = _request(url, payload)
    response.raise_for_status()
    return response.text
