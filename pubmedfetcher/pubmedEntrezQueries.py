import requests
import xml.etree.ElementTree as ET
from __init__ import _request

class PubMedEntrezQueries:
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
      Note: If no database parameter is supplied, infoEntrezQuery will return a list of all valid Entrez databases.
    """
    endpoint = 'einfo'
    payload = {}
    payload.update(kwargs)
    url = f'{self.baseURL}/{endpoint}.{self.endpoint_suffix}'
    response = requests.get(url, params=payload)

    return response
  

  def entrezSearch(self, db, term, **kwargs):
    """
    Searches and retrieves primary IDs (for use in FetchEntrezQuery, LinkEntrezQuery and SummaryEntrezQuery) and term translations, 
    and optionally retains results for future use in the user's environment.

    Args:

    Returns:
      A list of primary IDs from the search matching a text query
    """
    if 'retmax' in kwargs and kwargs['retmax'] > 10_000:
      kwargs['retmax'] = 10_000
      print('Fetching more than 10,000 results is currently not supported.')
      print('Refining query for 10_000 results.')

    endpoint = 'esearch'
    payload = {
      'db': db,
      'term': term 
    }
    payload.update(kwargs)
    url = f'{self.baseURL}/{endpoint}.{self.endpoint_suffix}'
    response = _request(url, payload)
    response.raise_for_status()
    search_tree = ET.fromstring(response.text)
    ids = [id_elem.text for id_elem in search_tree.findall("./IdList/Id")]
    return ids


  def entrezSummary(self, db, id, **kwargs):
    """
    EntrezSummary retrieves document summaries(DocSums) for a list of primary IDs or 
    for a set of UIds stored on the Entrez History Server

    See the online documentation for an explanation of the parameters:
    http://www.ncbi.nlm.nih.gov/books/NBK25499/#chapter4.ESummary

    Args:
      db (str: required)  : Database from which to retrieve DocSums. The value must be a valid Entrez database name.
      id (list: required) : UID list. Either a single UID or a comma-delimited list of UIDs may be provided. All of the UIDs must be from the database specified by db

    Returns:
      Handle to the results, in XML format (XML DocSums)
    """
    endpoint = 'esummary'
    payload = {
      'db': db,
      'id': id
    }
    payload.update(kwargs)
    url = f'{self.baseURL}/{endpoint}.{self.endpoint_suffix}'
    response = _request(url, payload)
    response.raise_for_status()
    return response.text


  def fetchEntrezQuery(self, database, ids):
    endpoint = 'efetch'
    params  = {
      'db': 'pubmed',
      'id': _format_ids(ids),
      'rettype': 'xml',
      'retmode': 'xml',
    }

    url = f'{self.baseURL}/{endpoint}.{self.endpoint_suffix}'
    response = requests.get(url, params)
    return response.content
