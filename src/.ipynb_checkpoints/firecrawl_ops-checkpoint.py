# import os
# from firecrawl import FirecrawlApp, ScrapeOptions
# from dotenv import load_dotenv

# load_dotenv()

# class FirecrawlService:
#     def __init__(self):
#         api_key = os.getenv("FIRECRAWL_API_KEY")
#         if not api_key:
#             raise ValueError("FIRECRAWL_API_KEY environment variable not set")
#         self.app = FirecrawlApp(api_key=api_key)

#     def search_companies(self, query: str, num_results: int = 5):
#         try:
#             result = self.app.search(
#                 query=f"{query} company pricing",
#                 num_results=num_results,
#                 scrape_options=ScrapeOptions(
#                     format=["markdown"]
#                 )
#             )
#             return result
#         except Exception as e:
#             print(f"Error during search: {e}")
#             return None

#     def scrape_company_pages(self, url: str):
#         try:
#             result = self.app.scrape_url(
#                 url,
#                 format=["markdown"]
#             )
#             return result
#         except Exception as e:
#             print(f"Error during scraping: {e}")
#             return None





import os
from firecrawl import FirecrawlApp
from dotenv import load_dotenv

load_dotenv()

class FirecrawlService:
    def __init__(self):
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            raise ValueError("FIRECRAWL_API_KEY environment variable not set")
        self.app = FirecrawlApp(api_key=api_key)

    def search_companies(self, query: str):
        try:
            # Removed num_results and scrape_options, as they are not supported by the search method.
            result = self.app.search(
                query=f"{query} company pricing"
            )
            return result
        except Exception as e:
            print(f"Error during search: {e}")
            return None

    def scrape_company_pages(self, url: str):
        try:
            result = self.app.scrape_url(
                url,
                params={"format": "markdown"}
            )
            return result
        except Exception as e:
            print(f"Error during scraping: {e}")
            return None