import requests
from urllib.parse import urlencode

email = None
api_key = None

def _contruct_params(params, join_ids=True):
    """
    Construct/format parameter dict for the request

    Args:
      params (dict or None): User-supplied parameters
      join_ids (bool): If True and the "id" key of ``params`` is a list
        containing multiple UIDs, join them into a single comma-delimited string.
    Return:
      dict: Parameters with defaults added and keys with None values removed.
    """
    if (params is None):
      params = {}
    
    params.setdefault('email', email)
    params.setdefault('api_key', api_key)

    # Remove None values from the parameters
    params = {key: value for key, value in params.items() if value is not None}
    
    # Format "id" parameter
    if join_ids and 'id' in params:
       params['id'] = _format_ids(params['id'])
       
    return params


def _format_ids(ids):
    """
    Convert one or more UIDs to a single comma-delimited string.

    Input may be a single ID as an integer or string, an iterable of strings/ints,
    or a string of IDs already separated by commas.
    """
    # Single integer, just convert to str
    if isinstance(ids, int):
        return str(ids)

    # String which represents one or more IDs joined by commas
    # Remove any whitespace around commas if they are present
    if isinstance(ids, str):
        return ",".join(id.strip() for id in ids.split(","))

    # Not a string or integer, assume iterable
    return ",".join(map(str, ids))


def _has_api_key(request):
    """
    Check if a Request has the api_key parameter set, to set the rate limit.

    Works with GET or POST requests.
    """

    if request.method == "POST":
      # checks whether the string "api_key=" is present as a byte string in the data payload.
      return b"api_key=" in request.data
    
    # checks whether the string "api_key=" is present in the URL. 
    # Parameters are typically passed as part of the URL query string.
    return "api_key=" in request.full_url

def _request(url, payloads=None, post=None, join_ids=True):
  """
  Build an HTTP request object for accessing an E-utility service based on the size of the URL-encoded parameters or the `post` flag.

  Args:
    url (str)       : The base URL for the E-utility CGI script or endpoint.
    payloads (dict) : A dictionary of query parameters to include in the request.
    post (bool)     : 
          Determines whether to use the HTTP POST method instead of GET. 
          If `None` (default), the decision is based on the length of the URL-encoded parameters:
            - If the encoded parameters exceed 1000 characters, POST is used.
            - Otherwise, GET is used. 
          Explicitly setting this to `True` or `False` overrides the length-based decision.
    joins_ids (bool): Join certain IDs within the `payloads` before URL encoding. This flag is passed to a 
          helper function like `_construct_params`, which processes the parameters accordingly.  

  Returns:
    A `requests.Response` object resulting from the HTTP request. 
  """
  params = _contruct_params(payloads, join_ids)

  # Convert parameters in the form of a URL-encoded string.
  params_str = urlencode(params, doseq=True)

  # By default, post is None. Set to a boolean to over-ride length choice:
  post = True if post is None and len(params_str) >= 1000 else None

  # NCBI prefers an HTTP POST instead of an HTTP GET if there are more than about 200 IDs
  print("len: ", len(params['id']))
  print(params['id'])
  post = True if post is None and 'id' in params and (params['id'].count(',') + 1) >= 200 else None

  return (
    requests.get(f'{url}?{params_str}') if post is None else requests.post(url, data=params_str.encode('utf8'))
  )