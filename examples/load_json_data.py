import argparse
import json
import os

# This script shows how to load NELA-GT-2019 JSON files


# Start here
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=str, help="Path to NELA JSON file")

    args = parser.parse_args()

    # Loading a single file
    print("- Loading file", args.path)
    with open(args.path) as fin:
        data = json.load(fin)

    # Display fields
    print("-> Loaded %d articles" % len(data))
    print("- Data fields:")
    for field in data[0]:
        print("    +", field)

    print("ALL DONE.")


if __name__ == "__main__":
    main()