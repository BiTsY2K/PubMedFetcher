import re

def _is_academic_affiliation(affiliation):
  academic_keywords = {'university', 'college', 'school of', 'institute of', 'academic', 'academia', 'faculty of'}
  return False if not affiliation else (keyword in affiliation.lower() for keyword in academic_keywords)

def _extract_email(text):
  email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
  match = re.search(email_pattern, text)
  return match.group(0) if match else None

__all__ = [_is_academic_affiliation, _extract_email]