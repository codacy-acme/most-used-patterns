# Repository Analysis Tool

This Python script provides a comprehensive analysis of repository tools, languages, and patterns within a PostgreSQL database environment. It connects to two databases, `accounts` for project settings and `analysis` for algorithm-related data. The script performs several key functions, including listing enabled tools per repository, fetching languages per repository, determining default tools based on languages, and accumulating active pattern counts for tools and repositories. The results are sorted by the count of patterns in descending order.

## Prerequisites

Before you run this script, ensure you have the following installed:

- Python 3.x
- `psycopg2` for PostgreSQL database connection
- `python-dotenv` for environment variable management
- `inquirer` for interactive command line user interfaces

Make sure you also have a `.env` file in the same directory as the script with the necessary database connection variables:

```env
DB_HOST=your_database_host
DB_USERNAME=your_database_username
DB_PASSWORD=your_database_password
DB_PORT=your_database_port
DB_ANALYSIS_NAME=your_analysis_database_name
DB_ACCOUNTS_NAME=your_accounts_database_name
```

# Installation

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Place the script and your .env file in the same directory.

## Usage
Run the script with the following command:

```bash
python main.py
```