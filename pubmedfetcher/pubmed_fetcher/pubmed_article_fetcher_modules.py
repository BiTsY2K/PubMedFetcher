from __init__ import _is_academic_affiliation, _extract_email

class PubmedArticleFetcher:
  def __init__(self):
    pass
  
  def _fetch_publicationDate(self, article_date):
    # Safe extraction of data with empty string as default values for text if tag is missing
    year_text = article_date.find("./Year").text if article_date.find("./Year") is not None else ""
    month_text = article_date.find("./Month").text if article_date.find("./Month") else ""
    day_text = article_date.find("./Day").text if article_date.find("./Day") is not None else ""
    return f'{day_text} {month_text} {year_text}'.strip()

  def _fetch_author_details(self, author):
    """
    Extract and process author details from a PubMed XML author element.
    
    Args:
      author (xml.etree.ElementTree.Element): XML element containing author data

    Returns:
    """

    # Extract 'Authors' child elements tag
    author_forename = author.find("./ForeName")
    author_lastname = author.find("./LastName")
    affiliation = author.find("./AffiliationInfo/Affiliation")

    # Use empty string as default values for text if tag is missing
    author_forename_text = author_forename.text if author_forename is not None else ""
    author_lastname_text = author_lastname.text if author_lastname is not None else ""
    affiliation_text = affiliation.text if affiliation is not None else ""
    author_email = _extract_email(affiliation_text) if not affiliation_text else ""

    is_academic_affiliation = _is_academic_affiliation(affiliation_text)
    company_affiliation = affiliation_text if affiliation_text and not is_academic_affiliation else ""
    corresponding_email = author_email if author_email and not is_academic_affiliation else ""

    return {
      "name": f"{author_forename_text} {author_lastname_text}".strip(),
      "affiliation": affiliation_text,
      "email": author_email,
      "is_academic_affiliation": is_academic_affiliation
    }, company_affiliation, corresponding_email


  def _fetch_article_details(self, article):
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
    authors = []                  # List to store all processed author information
    company_affiliation = []      # List to store all company affiliations
    corresponding_email = None    # Store first found email (assumed to be corresponding author)
    
    # Extract details for each author
    for author in authors_list:
      author, affiliation, email = self._fetch_author_details(author)
      authors.append(author)
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
