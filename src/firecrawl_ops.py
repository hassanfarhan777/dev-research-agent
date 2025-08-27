"""
firecrawl_ops.py

This module provides an abstraction layer over the Firecrawl API for searching and scraping web content
related to developer tools and companies. It encapsulates Firecrawl operations for use in a structured
research workflow.

Main Features:
- Search for companies or tools based on a query
- Scrape website content for further analysis
- Handles API key loading securely via environment variables
"""

import os
from firecrawl import FirecrawlApp
from dotenv import load_dotenv

# Load environment variables from a .env file into os.environ
load_dotenv()


class FirecrawlService:
    """
    A service class that wraps FirecrawlApp to perform search and scrape operations.

    It abstracts and simplifies the use of Firecrawl's functionality by:
    - Loading the API key from environment variables
    - Providing error-handled methods to search and scrape content
    """

    def __init__(self):
        """
        Initializes the FirecrawlService with an API key from the environment.

        Raises:
            ValueError: If the FIRECRAWL_API_KEY environment variable is not set.
        """
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            raise ValueError("FIRECRAWL_API_KEY environment variable not set")
        self.app = FirecrawlApp(api_key=api_key)

    def search_companies(self, query: str):
        """
        Performs a Firecrawl search for articles or websites related to a given query.

        Args:
            query (str): The search query, usually describing a developer tool or category.

        Returns:
            FirecrawlSearchResult | None: The resulting object with metadata and URLs, or None on failure.
        """
        try:
            # Firecrawl's search method does not support num_results or filters
            result = self.app.search(
                query=f"{query} company pricing"
            )
            return result
        except Exception as e:
            print(f"Error during search: {e}")
            return None

    def scrape_company_pages(self, url: str):
        """
        Scrapes the content of a website at the given URL using Firecrawl.

        Args:
            url (str): The full URL of the page to scrape.

        Returns:
            FirecrawlScrapeResult | None: The scraped content, usually in markdown format, or None on failure.
        """
        try:
            result = self.app.scrape_url(
                url,
                formats=['markdown']  # Can be ['text'], ['html'], etc., but markdown is easiest to parse
            )
            return result
        except Exception as e:
            print(f"Error during scraping: {e}")
            return None