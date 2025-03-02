"""
Web Scraper for Sustainability Data

Scrapes and extracts sustainability information from various websites, reports, and articles.
"""
import logging
import httpx
import re
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse, urljoin
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class WebScraper:
    """
    Scrapes sustainability-related content from websites, reports, and articles.
    """
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.sustainability_keywords = [
            "sustainability", "sustainable", "ESG", "environmental", "social", "governance",
            "climate change", "carbon emissions", "greenhouse gas", "GHG", "net zero",
            "renewable energy", "social impact", "corporate responsibility", "CSR",
            "biodiversity", "circular economy", "water conservation", "waste management",
            "supply chain sustainability", "carbon footprint", "green initiatives"
        ]
        # Define patterns to identify sustainability reports
        self.report_patterns = [
            r"sustainability[-_\s]report",
            r"esg[-_\s]report",
            r"integrated[-_\s]report",
            r"annual[-_\s]sustainability", 
            r"environmental[-_\s]report",
            r"impact[-_\s]report"
        ]
    
    async def scrape_sustainability_data(self, 
                                        query: str, 
                                        max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape sustainability data based on a query.
        
        Args:
            query: The search query to use
            max_results: Maximum number of results to return
            
        Returns:
            List of dictionaries containing scraped data
        """
        logger.info(f"Starting web scraping for query: '{query}'")
        
        # Step 1: Perform search and collect URLs
        search_urls = await self._search_for_sustainability_content(query, max_results)
        
        # Step 2: Scrape content from each URL
        scraped_data = []
        for url in search_urls:
            try:
                data = await self._scrape_url(url, query)
                if data:
                    scraped_data.append(data)
                    
                    # Break if we've reached the maximum number of results
                    if len(scraped_data) >= max_results:
                        break
            except Exception as e:
                logger.error(f"Error scraping URL {url}: {str(e)}")
        
        logger.info(f"Completed web scraping for query: '{query}'. Found {len(scraped_data)} results.")
        return scraped_data
    
    async def _search_for_sustainability_content(self, 
                                               query: str, 
                                               max_results: int = 10) -> List[str]:
        """
        Use DuckDuckGo search to find sustainability content.
        """
        # For now, we'll implement a basic DuckDuckGo search using their API
        sustainability_query = f"{query} sustainability ESG"
        
        try:
            # Use the DuckDuckGo API for searching
            search_url = f"https://api.duckduckgo.com/?q={sustainability_query}&format=json"
            response = await self.client.get(search_url)
            search_data = response.json()
            
            urls = []
            
            # Extract URLs from the results
            if "Results" in search_data:
                for result in search_data["Results"]:
                    if "FirstURL" in result:
                        urls.append(result["FirstURL"])
            
            # Add urls from related topics
            if "RelatedTopics" in search_data:
                for topic in search_data["RelatedTopics"]:
                    if "FirstURL" in topic:
                        urls.append(topic["FirstURL"])
            
            # As a fallback, if the API didn't return results in the expected format,
            # extract URLs from the response using regex
            if not urls:
                url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\.-]*(?:\?\S*)?'
                urls = re.findall(url_pattern, str(search_data))
            
            # Deduplicate and limit
            unique_urls = list(dict.fromkeys(urls))
            return unique_urls[:max_results]
            
        except Exception as e:
            logger.error(f"Error searching for content: {str(e)}")
            return []
    
    async def _scrape_url(self, url: str, query: str) -> Optional[Dict[str, Any]]:
        """
        Scrape content from a specific URL.
        """
        try:
            # Check if URL seems valid
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                logger.warning(f"Invalid URL format: {url}")
                return None
            
            # Request the URL
            response = await self.client.get(url)
            if response.status_code != 200:
                logger.warning(f"Failed to fetch URL {url}: Status {response.status_code}")
                return None
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract basic metadata
            title = self._extract_title(soup)
            
            # If we can't extract a title, this is probably not a valid page
            if not title:
                logger.warning(f"Could not extract title from {url}")
                return None
            
            # Extract other elements
            description = self._extract_description(soup)
            content = self._extract_main_content(soup)
            date = self._extract_date(soup)
            
            # Extract sustainability-specific information
            sustainability_metrics = self._extract_sustainability_metrics(content)
            is_sustainability_report = self._is_sustainability_report(title, content)
            sustainability_categories = self._categorize_sustainability_content(content)
            
            # Determine content relevance
            relevance_score = self._calculate_relevance_score(title, content, query)
            
            # Return structured data
            return {
                "url": url,
                "title": title,
                "description": description,
                "content": content[:5000],  # Limit content length
                "date": date,
                "is_sustainability_report": is_sustainability_report,
                "sustainability_categories": sustainability_categories,
                "sustainability_metrics": sustainability_metrics,
                "relevance_score": relevance_score,
                "scraped_at": datetime.now().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Error scraping URL {url}: {str(e)}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract the title from the HTML."""
        if soup.title:
            return soup.title.string.strip()
        
        # Try h1 if title tag is missing
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
            
        return ""
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract the description from the HTML."""
        # Try meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and 'content' in meta_desc.attrs:
            return meta_desc['content'].strip()
        
        # Try first paragraph
        first_p = soup.find('p')
        if first_p:
            return first_p.get_text().strip()
            
        return ""
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract the main content from the HTML."""
        # Remove script and style elements
        for script_or_style in soup(['script', 'style', 'nav', 'header', 'footer']):
            script_or_style.decompose()
        
        # Try to find main content containers
        content_candidates = soup.find_all(['article', 'main', 'div.content', 'div.main', '.post-content'])
        
        if content_candidates:
            # Use the largest content block
            largest = max(content_candidates, key=lambda x: len(x.get_text()))
            return largest.get_text(separator=' ', strip=True)
        
        # Fallback to body content
        return soup.get_text(separator=' ', strip=True)
    
    def _extract_date(self, soup: BeautifulSoup) -> str:
        """Extract the publication date from the HTML."""
        # Try common date elements and meta tags
        date_meta = soup.find('meta', attrs={'property': 'article:published_time'})
        if date_meta and 'content' in date_meta.attrs:
            return date_meta['content']
        
        # Look for time elements
        time_element = soup.find('time')
        if time_element and 'datetime' in time_element.attrs:
            return time_element['datetime']
        
        # Try to find date patterns in the text
        content = soup.get_text()
        date_patterns = [
            r'\d{1,2}\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s\d{4}',
            r'\d{4}-\d{2}-\d{2}'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(0)
        
        return ""
    
    def _extract_sustainability_metrics(self, content: str) -> Dict[str, Any]:
        """Extract sustainability metrics from the content."""
        metrics = {}
        
        # Look for common sustainability metrics
        carbon_pattern = r'carbon\s+(?:footprint|emissions|intensity).*?(\d+[\d,.]*)\s*(?:tons|t\s*CO2|kg)'
        carbon_match = re.search(carbon_pattern, content, re.IGNORECASE)
        if carbon_match:
            metrics['carbon_emissions'] = carbon_match.group(1)
        
        # Energy consumption
        energy_pattern = r'energy\s+(?:consumption|usage|intensity).*?(\d+[\d,.]*)\s*(?:MWh|kWh|GJ)'
        energy_match = re.search(energy_pattern, content, re.IGNORECASE)
        if energy_match:
            metrics['energy_consumption'] = energy_match.group(1)
        
        # Water usage
        water_pattern = r'water\s+(?:consumption|usage|intensity).*?(\d+[\d,.]*)\s*(?:m3|cubic\s+meters|liters|gallons)'
        water_match = re.search(water_pattern, content, re.IGNORECASE)
        if water_match:
            metrics['water_usage'] = water_match.group(1)
        
        return metrics
    
    def _is_sustainability_report(self, title: str, content: str) -> bool:
        """Determine if the content is a sustainability report."""
        # Check title
        title_lower = title.lower()
        for pattern in self.report_patterns:
            if re.search(pattern, title_lower):
                return True
        
        # Check content for typical sustainability report sections
        report_sections = [
            'executive summary', 'key performance indicators', 'environmental performance',
            'social impact', 'governance structure', 'materiality assessment',
            'stakeholder engagement', 'sustainable development goals', 'sdgs',
            'gri index', 'sasb disclosure', 'tcfd disclosure'
        ]
        
        content_lower = content.lower()
        section_count = sum(1 for section in report_sections if section in content_lower)
        
        # If at least 3 typical sections are found
        return section_count >= 3
    
    def _categorize_sustainability_content(self, content: str) -> List[str]:
        """Categorize sustainability content into different ESG categories."""
        categories = []
        content_lower = content.lower()
        
        # Environmental categories
        if any(kw in content_lower for kw in ['carbon emissions', 'greenhouse gas', 'ghg', 'carbon footprint', 'climate change']):
            categories.append('emissions')
        
        if any(kw in content_lower for kw in ['energy efficiency', 'renewable energy', 'energy consumption']):
            categories.append('energy')
            
        if any(kw in content_lower for kw in ['water usage', 'water conservation', 'water footprint']):
            categories.append('water')
            
        if any(kw in content_lower for kw in ['waste management', 'waste reduction', 'circular economy']):
            categories.append('waste')
        
        # Social categories
        if any(kw in content_lower for kw in ['diversity', 'inclusion', 'human rights', 'labor practices', 'community engagement']):
            categories.append('social')
            
        # Governance categories
        if any(kw in content_lower for kw in ['board structure', 'executive compensation', 'business ethics', 'transparency']):
            categories.append('governance')
        
        return categories
    
    def _calculate_relevance_score(self, title: str, content: str, query: str) -> float:
        """Calculate relevance score based on the query and sustainability focus."""
        score = 0.0
        
        # Check if query terms appear in title (higher weight)
        query_terms = query.lower().split()
        title_lower = title.lower()
        
        for term in query_terms:
            if term in title_lower:
                score += 10.0
        
        # Check if query terms appear in content
        content_lower = content.lower()
        for term in query_terms:
            score += content_lower.count(term) * 1.0
        
        # Adjust score based on sustainability keyword presence
        for keyword in self.sustainability_keywords:
            if keyword in title_lower:
                score += 5.0
            score += content_lower.count(keyword) * 0.5
        
        # Normalize score to 0-100 range
        return min(100.0, score)