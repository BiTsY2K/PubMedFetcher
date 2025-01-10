# PubMed Paper Fetcher

A Python command-line tool to fetch research papers from PubMed and identify papers with authors affiliated with pharmaceutical or biotech companies.

## Features

- Search PubMed using their full query syntax
- Identify authors with non-academic affiliations
- Export results to CSV with detailed paper information
- Command-line interface with multiple options
- Type-hinted Python code for better maintainability

## Installation

### Prerequisites

- Python 3.13 or higher
- Poetry for dependency management

### Setup

1. Clone the repository:

```bash
git clone https://github.com/BiTsY2K/PubMedFetcher.git
cd pubmedfetcher
```

2. Install dependencies using Poetry:

```bash
poetry install
```

This will install all required dependencies:

- requests (>=2.32.3)
- pandas (>=2.2.3)
- logging (>=0.4.9.6)

## Usage

The tool can be used via the command line using the `get-papers-list` command installed by Poetry.

### Basic Usage

```bash
poetry run get-papers-list "<your-search-query>"
```

### Command Line Options

- `-h, --help`: Display usage instructions
- `-d, --debug`: Print debug information during execution
- `-f, --file FILENAME`: Specify output file path (CSV format)
  - If not provided, results will be printed to console

### Examples

1. Basic search with output to console:

```bash
poetry run get-papers-list "cancer immunotherapy"
```

2. Search with file output:

```bash
poetry run get-papers-list "CRISPR" -f results.csv
```

3. Search with debug information:

```bash
poetry run get-papers-list "antibody development" -d -f results.csv
```

## Output Format

The tool generates a CSV file with the following columns:

- PubmedID: Unique identifier for the paper
- Title: Title of the paper
- Publication Date: Date the paper was published
- Non-academic Author(s): Names of authors affiliated with non-academic institutions
- Company Affiliation(s): Names of pharmaceutical/biotech companies
- Corresponding Author Email: Email address of the corresponding author

## Project Structure

```
pubmedfetcher/
├── pubmedfetcher/
│   ├── pubmed_fetcher/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── modules.py
│   ├── __init__.py
│   ├── types.py
│   └── tests/
│       ├── __init__.py
│       └── test_fetcher.py
├── LICENSE.md
├── README.md
├── poetry.lock
├── pyproject.toml
└── test_data.xml
```

## Tools and Resources Used

1. Development Tools:

   - Poetry for dependency management
   - GitHub for version control
   - Python's type hints for static typing

2. Key Libraries:
   - requests: For API communication
   - pandas: For data manipulation and CSV export
   - logging: For debug information and error tracking

## Useful Links

### Official Documentation

- [PubMed E-utilities Documentation](https://www.ncbi.nlm.nih.gov/books/NBK25501/)
- [PubMed API Reference](https://www.ncbi.nlm.nih.gov/books/NBK25500/)
- [NCBI Help Manual](https://www.ncbi.nlm.nih.gov/books/NBK3831/)

### Development Tools

- [Poetry Documentation](https://python-poetry.org/docs/)
- [Python Type Hints Guide](https://docs.python.org/3/library/typing.html)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Requests Library Documentation](https://requests.readthedocs.io/)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

ROHIT RAI (rohitrai2948@gmail.com)
