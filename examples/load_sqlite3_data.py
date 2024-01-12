import argparse
import sqlite3
import pandas as pd
# This script shows an example of how to use NELA-GT-2019 with sqlite3
# For more info, see: https://github.com/mgruppi/nela-gt


# Execute a given SQL query on the database and return values
def execute_query(path, query):
    conn = sqlite3.connect(path)
    # execute query on database and retrieve them with fetchall
    results = conn.cursor().execute(query).fetchall()
    return results


# Execute query and load results into pandas dataframe
def execute_query_pandas(path, query):
    conn = sqlite3.connect(path)
    df = pd.read_sql_query(query, conn)
    return df


# Start here
def main():
    # Make input command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=str, help="Path to NELA database file.")
    args = parser.parse_args()

    # Query 1: select the title, source and url from 10 articles
    query = "SELECT title, source, url FROM newsdata LIMIT 10"

    data = execute_query(args.path, query)

    for result in data:
        print(result)

    # Alternatively, one can fetch queries into a pandas dataframe:
    df = execute_query_pandas(args.path, query)

    print("-- Same results but in a Pandas dataframe.")
    print(df)

    print("- ALL DONE.")


if __name__ == "__main__":
    main()