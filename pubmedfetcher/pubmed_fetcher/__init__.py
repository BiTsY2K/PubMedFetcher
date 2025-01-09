import re
import logging
import requests
from urllib.parse import urlencode

def setup_logging(debug: bool) -> None:
  """Configure logging based on debug flag."""
  level = logging.DEBUG if debug else logging.INFO
  logging.basicConfig(
    level = level,
    format = "%(message)s",
  )

def _is_academic_affiliation(affiliation):
  """
  Check if a given affiliation string indicates an academic institution.

  Args:
    affiliation (str): The affiliation string to check. Can be None or empty.

  Returns:
    bool: True if the affiliation appears to be academic, False otherwise.
  """
  # Return False if affiliation is empty/None
  if not affiliation:
    return False
  
  academic_keywords = {'university', 'lab', '.edu.' 'college', 'school of', 'institute of', 'academic', 'academia', 'faculty of'}
  
  for keyword in academic_keywords:
    # Check if affiliation contains any academic-related keywords 
    if keyword in affiliation.lower():
      return True
  return False

def _extract_email(text):
  email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
  match = re.search(email_pattern, text)
  return match.group(0) if match else None

def _contruct_params(params, join_ids=True):
  """
  Construct/format parameter dict for the request

  Args:
    params (dict or None): User-supplied parameters
    join_ids (bool): If True and the "id" key of `params` is a list containing multiple UIDs, 
      join them into a single comma-delimited string. Default: True

  Return:
    dict: Parameters with defaults added and keys with None values removed.
  """
  if (params is None):
    params = {}

  # Remove None values from the parameters
  params = {key: value for key, value in params.items() if value is not None}
  
  # Format "id" parameter
  if join_ids and 'id' in params:
    params['id'] = _format_ids(params['id'])
      
  return params

def _format_ids(ids):
  """
  Convert one or more UIDs to a single comma-delimited string.
  
  Handles multiple input formats to create a consistent comma-separated string
  of IDs for API requests.
  Input may be a single ID as an integer or string, an iterable of strings/ints,
  or a string of IDs already separated by commas.
  
  Args:
    ids: Input IDs in any of these formats:
      - Single integer (e.g., 123)
      - Single string (e.g., "123" or "123,456")
      - Iterable of integers or strings (e.g., [123, 456] or ["123", "456"])

  Returns:
    str: Comma-separated string of IDs with no whitespace around commas
  """
  # Single integer, just convert to str
  if isinstance(ids, int):
      return str(ids)

  # String which represents one or more IDs joined by commas
  # Remove any whitespace around commas if they are present
  if isinstance(ids, str):
      return ",".join(id.strip() for id in ids.split(","))

  # Convert iterable to comma-separated string
  return ",".join(map(str, ids))

def _request(url, payloads=None, post=None, ecitmatch=False, join_ids=True):
  """
  Build an HTTP request object for accessing an E-utility service based on 
  the size of the URL-encoded parameters or the `post` flag.

  Args:
    url (str): Base URL for the E-utility endpoint.
    payloads (dict, optional): A dictionary of query parameters to include in the request.
    post (bool, optional): 
        Determines whether to use the HTTP POST method instead of GET. 
        If `None` (default), the decision is based on the length of the URL-encoded parameters:
          - If the encoded parameters exceed 1000 characters, POST is used.
          - Otherwise, GET is used. 
        Explicitly setting this to `True` or `False` overrides the length-based decision.
    ecitmatch (bool): If True, preserves pipe characters in URL encoding for the ecitmatch tool. Default: False
    joins_ids (bool): Join certain IDs within the `payloads` before URL encoding. This flag is passed to a 
        helper function like `_construct_params`, which processes the parameters accordingly. Default: True

  Returns:
    requests.Response: A `requests.Response` object resulting from the HTTP request. 
  """
  # Process and Convert parameters in the form of a URL-encoded string
  params = _contruct_params(payloads, join_ids)
  params_str = urlencode(params, doseq=True)

  # Preserve URL-encoding for pipe ("|") characters, required by the ecitmatch tool.
  if ecitmatch: params_str = params_str.replace("%7C", "|")

  # Determine request method based on size and ID count
  if post is None:
    if len(params_str) >= 1000: post = True # Switch to POST if parameters are too long
    elif 'id' in params and (params['id'].count(',') + 1) >= 200: post = True # Switch to POST if too many IDs

  return (
    requests.get(f'{url}?{params_str}') if post is None else requests.post(url, data=params_str.encode('utf8'))
  )

__all__ = [
  _is_academic_affiliation, _extract_email, _contruct_params, _format_ids, _request
]