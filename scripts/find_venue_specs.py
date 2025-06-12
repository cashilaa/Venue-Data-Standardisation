"""
Script to help find venue technical specifications online.

This script provides guidance on finding technical specifications for venues.
"""

import os
import sys
import webbrowser
from pathlib import Path

def suggest_search_queries(venue_name):
    """Generate search queries for finding venue technical specifications."""
    queries = [
        f"{venue_name} technical specifications",
        f"{venue_name} tech specs",
        f"{venue_name} lighting equipment",
        f"{venue_name} sound equipment",
        f"{venue_name} venue pack",
        f"{venue_name} production guide",
    ]
    return queries

def open_search_engine(query):
    """Open a web browser with the search query."""
    # URL encode the query
    import urllib.parse
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.google.com/search?q={encoded_query}"
    
    # Open in default web browser
    webbrowser.open(url)
    
    return url

def main():
    """Main function to help find venue technical specifications."""
    if len(sys.argv) < 2:
        print("Usage: python find_venue_specs.py <venue_name>")
        print("Example: python find_venue_specs.py 'Royal Albert Hall'")
        sys.exit(1)
    
    venue_name = sys.argv[1]
    print(f"Helping you find technical specifications for: {venue_name}")
    
    # Generate search queries
    queries = suggest_search_queries(venue_name)
    
    print("\nSuggested search queries:")
    for i, query in enumerate(queries, 1):
        print(f"{i}. {query}")
    
    # Ask which query to use
    print("\nEnter the number of the query to search, or 0 to exit:")
    try:
        choice = int(input("> "))
        if choice == 0:
            sys.exit(0)
        elif 1 <= choice <= len(queries):
            query = queries[choice-1]
            url = open_search_engine(query)
            print(f"Opened search in browser: {url}")
        else:
            print("Invalid choice.")
    except ValueError:
        print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    main()