import requests
from bs4 import BeautifulSoup

class BlogFetcher:
    BLOG_PAGE_URL = 'https://www.amsterdamstandard.com/blog/'
    AI_PAGES = BLOG_PAGE_URL + 'tag/ai'

    def get_page_content(self, url: str) -> str:
        response = requests.get(url)
        response.raise_for_status()
        return response.text

    def get_blog_urls(self, urls: list[str]) -> list[str]:
        return [url for url in urls if self.BLOG_PAGE_URL in url]

    def find_ai_urls(self, html_content: str) -> list[str]:
        soup = BeautifulSoup(html_content, 'html.parser')
        urls = [a['href'] for a in soup.find_all('a', href=True)]
        return self.get_blog_urls(urls)

    def fetch_ai_blog_urls(self) -> list[str]:
        html = self.get_page_content(self.AI_PAGES)
        return self.find_ai_urls(html)

    def fetch_blog_post_details(self, url: str) -> dict:
        """
        Fetch and parse a blog post, extracting title, body, authors, tags, and date.
        Returns a dict with keys: title, body, authors, tags, date.
        """
        html = self.get_page_content(url)
        soup = BeautifulSoup(html, 'html.parser')

        # Title
        title_tag = soup.find('div', attrs={'data-hs-cos-field': 'title'})
        title = title_tag.get_text(strip=True) if title_tag else ''

        # Authors and Date
        author_date_div = soup.select_one('div.container.py-10.flex.flex-wrap > div.w-full')
        author, date = '', ''
        if author_date_div:
            text = author_date_div.get_text(strip=True)
            # Example: "Written by: Miki, on February 14, 2025"
            if text.startswith("Written by:"):
                try:
                    author_part, date_part = text.replace("Written by:", "").split(", on ")
                    author = author_part.strip()
                    date = date_part.strip()
                except Exception:
                    pass
        authors = [author] if author else []

        # Tags
        tags = []
        tag_divs = soup.select('div.w-full.flex.flex-wrap.pt-4.gap-2 > div.relative')
        for tag_div in tag_divs:
            tag_text = tag_div.get_text(strip=True)
            if tag_text and not tag_text.startswith("Tags:"):
                tags.append(tag_text)

        # Main Body: get all text from the main content area, preserving headings and paragraphs
        body_span = soup.find('span', id='hs_cos_wrapper_post_body')
        body = ''
        if body_span:
            parts = []
            for tag in body_span.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li']):
                text = tag.get_text(strip=True)
                if text:
                    parts.append(text)
            body = '\n'.join(parts)

        # Compose a full text for embedding (title, author, date, tags, body)
        full_text = f"Title: {title}\nAuthor(s): {', '.join(authors)}\nDate: {date}\nTags: {', '.join(tags)}\n\n{body}"

        return {
            'title': title,
            'body': full_text,
            'authors': authors,
            'tags': tags,
            'date': date
        }
