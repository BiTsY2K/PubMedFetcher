import argparse
from pubmedEntrezQueries import PubMedEntrezQueries 

def main():
  parser = argparse.ArgumentParser(description="Fetch PubMed papers")
  parser.add_argument('-u', '--utility', required=True, help='')
  parser.add_argument('-t', '--term', help="The search term to query the database with.")
  parser.add_argument('-id', '--id', nargs='+', type=str, help="")
  parser.add_argument('-db', '--db', help=
    f'''The NCBI database to query.
      DATABASES: [
      "pubmed", "protein", "nuccore", "ipg", "nucleotide", "structure", "genome", "annotinfo", "assembly", "bioproject", 
      "biosample", "blastdbinfo", "books", "cdd", "clinvar", "gap", "gapplus", "grasp", "dbvar", "gene", "gds", "geoprofiles", 
      "medgen", "mesh", "nlmcatalog", "omim", "orgtrack", "pmc", "popset", "proteinclusters", "pcassay", "protfam", "pccompound", 
      "pcsubstance", "seqannot", "snp", "sra", "taxonomy", "biocollections", "gtr"
      ]
    ''')
  parser.add_argument('-max', '--retmax', type=int, default=20, help="Number of record to return with the matching search term. Default is 20.")
  args = parser.parse_args()

  args_dict = vars(args)
  print(args_dict)

  pubmedentrez_query = PubMedEntrezQueries()

  match args.utility:
    case 'einfo': 
      einfo = pubmedentrez_query.entrezInfo(**args_dict)
    case 'esearch':
      keys_to_remove = ["db", "term"]
      args_dict = {key: value for key, value in args_dict.items() if key not in keys_to_remove}
      esearch_idlist = pubmedentrez_query.entrezSearch(args.db, args.term, **args_dict)
      print("Entrez Search (ids): ", esearch_idlist)
    case 'esummary':
      keys_to_remove = ["db", "id"]
      args_dict = {key: value for key, value in args_dict.items() if key not in keys_to_remove}
      esummary = pubmedentrez_query.entrezSummary(args.db, args.id, **args_dict)
      print("Entrez Summary: ", esummary)

if __name__ == '__main__':
  main()