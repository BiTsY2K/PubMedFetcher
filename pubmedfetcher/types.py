from typing import TypedDict, List, Optional, Dict, Any
from datetime import date

class Author(TypedDict):
  name: str
  affiliation: Optional[str]
  email: Optional[str]
  is_academic: bool

class Article(TypedDict):
  pubmed_id: str
  title: str
  publication_date: date
  non_academic_authors: List[Author]
  company_affiliations: List[str]
  corresponding_author_email: Optional[str]