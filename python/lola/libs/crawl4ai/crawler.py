# Standard imports
import asyncio
from typing import Optional, Dict, Any

# Third-party imports
from crawl4ai import AsyncWebCrawler

# Local imports
from lola.utils.logging import setup_logger

"""
File: Wrapper for Crawl4AI with LOLA async crawling and structured extraction.

Purpose: Enables agents to crawl JS-heavy sites with selectors for JSON/Markdown output.
How: Wraps AsyncWebCrawler with retries, CSS/XPath selectors, and error logging.
Why: Bridges web data to on-chain agents in V1, no lock-in (config selectors).
Full Path: lola-os/python/lola/libs/crawl4ai/crawler.py
"""

logger = setup_logger("lola.crawl4ai")

class LOLAWebCrawler:
    """LOLAWebCrawler: Crawl4AI adapter for LOLA. Does NOT handle non-URL inputs—use URLs only."""

    def __init__(self, max_retries: int = 3, timeout: int = 30):
        """
        Initialize LOLAWebCrawler with retries and timeout.

        Args:
            max_retries: Retry count on fail (default: 3).
            timeout: Crawl timeout seconds (default: 30).

        Does Not: Load config—use utils/config for custom selectors.
        """
        self.crawler = AsyncWebCrawler()
        self.max_retries = max_retries
        self.timeout = timeout
        logger.info("LOLAWebCrawler init", extra={"retries": max_retries, "timeout": timeout})

    async def crawl(self, url: str, css_selector: Optional[str] = None, xpath: Optional[str] = None, output_format: str = "json") -> Dict[str, Any]:
        """
        Async crawls URL with optional selectors, returns structured data.

        Args:
            url: Target URL.
            css_selector: CSS for extraction (e.g., ".content").
            xpath: XPath for extraction (e.g., "//div[@id='main']").
            output_format: "json" or "markdown" (default: "json").

        Returns:
            Dict with "content", "metadata" (title, links, etc.).

        Does Not: Cache results—stateless per call.
        """
        for attempt in range(self.max_retries):
            try:
                async with asyncio.timeout(self.timeout):
                    result = await self.crawler.arun(url=url, css_selector=css_selector, xpath=xpath)
                content = result.markdown if output_format == "markdown" else result.json
                content_len = len(str(content)) if content is not None else 0  # Inline: Handle None/Mock for tests
                logger.info("Crawl success", extra={"url": url, "format": output_format, "len": content_len})
                return {"content": content, "metadata": {"title": result.page_title, "links": result.links}}
            except Exception as e:
                logger.warning("Crawl fail, retrying", extra={"url": url, "attempt": attempt+1, "error": str(e)})
                if attempt == self.max_retries - 1:
                    raise
        # Unreachable, but for type
        return {}

__all__ = ["LOLAWebCrawler"]