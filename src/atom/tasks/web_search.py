"""Web search integration for Atom using DuckDuckGo.

Provides privacy-focused web search capabilities without requiring API keys.
Results are extracted, summarized, and spoken to the user.

Features:
- DuckDuckGo search (no API key required, privacy-focused)
- Result parsing and summarization
- Rate limiting and error handling
- Source citation
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import time
from atom.utils.logger import setup_logger

logger = setup_logger(__name__, 'atom.log')


@dataclass
class SearchResult:
    """Represents a single search result.
    
    Attributes:
        title: Result title
        snippet: Result text snippet
        link: URL to the result
        source: Source domain
    """
    title: str
    snippet: str
    link: str
    source: str


class WebSearch:
    """Web search integration using DuckDuckGo.
    
    Provides privacy-friendly web search without API keys.
    
    Attributes:
        last_search_time (float): Timestamp of last search for rate limiting
        min_interval (float): Minimum seconds between searches
    """
    
    def __init__(self, min_interval: float = 1.0):
        """Initialize web search.
        
        Args:
            min_interval: Minimum seconds between searches (rate limiting)
        """
        self.last_search_time = 0.0
        self.min_interval = min_interval
        logger.info("WebSearch initialized")
    
    def _rate_limit(self):
        """Apply rate limiting to avoid overwhelming search service."""
        current_time = time.time()
        elapsed = current_time - self.last_search_time
        
        if elapsed < self.min_interval:
            sleep_time = self.min_interval - elapsed
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self.last_search_time = time.time()
    
    def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """Perform web search using DuckDuckGo.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of SearchResult objects
        """
        try:
            # Apply rate limiting
            self._rate_limit()
            
            # Try using duckduckgo_search library if available
            try:
                from duckduckgo_search import DDGS
                
                logger.info(f"Performing DuckDuckGo search: {query}")
                
                results = []
                with DDGS() as ddgs:
                    search_results = ddgs.text(query, max_results=max_results)
                    
                    for result in search_results:
                        # Extract source domain from URL
                        try:
                            from urllib.parse import urlparse
                            parsed = urlparse(result.get('href', ''))
                            source = parsed.netloc
                        except:
                            source = "Unknown"
                        
                        results.append(SearchResult(
                            title=result.get('title', 'No title'),
                            snippet=result.get('body', 'No description'),
                            link=result.get('href', ''),
                            source=source
                        ))
                
                logger.info(f"Found {len(results)} search results")
                return results
                
            except ImportError:
                logger.warning("duckduckgo_search not installed, using fallback search")
                return self._fallback_search(query, max_results)
                
        except Exception as e:
            logger.error(f"Error performing web search: {e}", exc_info=True)
            return []
    
    def _fallback_search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """Fallback search using requests and BeautifulSoup.
        
        Args:
            query: Search query string
            max_results: Maximum number of results
            
        Returns:
            List of SearchResult objects
        """
        try:
            import requests
            from bs4 import BeautifulSoup
            from urllib.parse import quote_plus, urlparse
            
            # Use DuckDuckGo HTML (no JavaScript required)
            search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Find result divs
            result_divs = soup.find_all('div', class_='result', limit=max_results)
            
            for div in result_divs:
                try:
                    # Extract title
                    title_tag = div.find('a', class_='result__a')
                    title = title_tag.get_text(strip=True) if title_tag else 'No title'
                    link = title_tag.get('href', '') if title_tag else ''
                    
                    # Extract snippet
                    snippet_tag = div.find('a', class_='result__snippet')
                    snippet = snippet_tag.get_text(strip=True) if snippet_tag else 'No description'
                    
                    # Extract source
                    source = urlparse(link).netloc if link else 'Unknown'
                    
                    results.append(SearchResult(
                        title=title,
                        snippet=snippet,
                        link=link,
                        source=source
                    ))
                    
                except Exception as e:
                    logger.debug(f"Error parsing search result: {e}")
                    continue
            
            logger.info(f"Fallback search found {len(results)} results")
            return results
            
        except ImportError as e:
            logger.error(f"Required libraries not installed: {e}")
            logger.error("Please install: pip install requests beautifulsoup4")
            return []
        except Exception as e:
            logger.error(f"Fallback search error: {e}", exc_info=True)
            return []
    
    def get_summary(self, results: List[SearchResult], max_results: int = 3) -> str:
        """Generate a summary of search results for speaking.
        
        Args:
            results: List of SearchResult objects
            max_results: Maximum results to include in summary
            
        Returns:
            String summary of results
        """
        if not results:
            return "I couldn't find any results for that search."
        
        summary = f"I found {len(results)} results. "
        
        for i, result in enumerate(results[:max_results], 1):
            # Truncate long snippets
            snippet = result.snippet
            if len(snippet) > 150:
                snippet = snippet[:147] + "..."
            
            summary += f"{i}. {result.title}. {snippet}. "
        
        if len(results) > max_results:
            summary += f"And {len(results) - max_results} more results."
        
        return summary
    
    def get_first_result_summary(self, results: List[SearchResult]) -> Optional[str]:
        """Get just the first result summary for quick answers.
        
        Args:
            results: List of SearchResult objects
            
        Returns:
            Summary of first result or None
        """
        if not results:
            return None
        
        first = results[0]
        return f"According to {first.source}, {first.snippet}"


# Example usage
if __name__ == "__main__":
    print("Web Search Demo")
    print("=" * 50)
    
    search = WebSearch()
    
    # Test search
    query = "Python programming language"
    print(f"\nSearching for: {query}")
    results = search.search(query, max_results=3)
    
    if results:
        print(f"\nFound {len(results)} results:\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.title}")
            print(f"   {result.snippet[:100]}...")
            print(f"   Source: {result.source}")
            print(f"   Link: {result.link}")
            print()
        
        print("=" * 50)
        print("Summary for speaking:")
        print(search.get_summary(results, max_results=2))
        
        print("\n" + "=" * 50)
        print("First result summary:")
        print(search.get_first_result_summary(results))
    else:
        print("No results found")
    
    print("\n" + "=" * 50)
    print("Demo complete!")
