import requests
from bs4 import BeautifulSoup
import re

class CitationScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def scrape_metadata(self, url):
        """Extracts title, authors, and date from a given URL."""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # 1. Title
            title = soup.title.string.strip() if soup.title else "Sans titre"
            # Try OpenGraph or Meta tags for better titles
            og_title = soup.find("meta", property="og:title")
            if og_title:
                title = og_title["content"].strip()

            # 2. Authors (Generic search in meta tags)
            authors = "Auteur inconnu"
            author_meta = soup.find("meta", attrs={"name": re.compile(r"author", re.I)})
            if author_meta:
                authors = author_meta["content"].strip()
            elif soup.find("meta", property="article:author"):
                authors = soup.find("meta", property="article:author")["content"].strip()

            # 3. Publication Date
            pub_date = "Date inconnue"
            date_meta = soup.find("meta", attrs={"name": re.compile(r"date|pub|time", re.I)})
            if date_meta:
                pub_date = date_meta["content"].strip()
            elif soup.find("meta", property="article:published_time"):
                pub_date = soup.find("meta", property="article:published_time")["content"].strip()
            
            return {
                "url": url,
                "title": title,
                "authors": authors,
                "pub_date": pub_date
            }

        except Exception as e:
            return {"error": str(e)}
