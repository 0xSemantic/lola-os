# Standard imports
import asyncio
from typing import Optional, Dict, Any

# Third-party imports
from crawl4ai import AsyncWebCrawler

# Local imports
from lola.utils.config import load_config
from lola.utils.logging import setup_logger
from .base import BaseTool

"""
File: Web crawl tool for LOLA using Crawl4AI for dynamic/JS sites.

Purpose: Enables agents to crawl web for structured JSON/Markdown output with selectors for RAG-like ingestion in V1.
How: Extends BaseTool with async crawl, CSS/XPath selectors, retries, config for timeout, logs extract.
Why: Bridges off-chain data to on-chain agents in V1, no lock-in (config selectors/timeout).
Full Path: lola-os/python/lola/tools/web_crawl.py
"""

logger = setup_logger("lola.tools.web_crawl")

class WebCrawlTool(BaseTool):
    """WebCrawlTool: Crawl4AI-based tool for web research. Does NOT handle non-URLs—string URL only."""

    def __init__(self):
        """
        Init WebCrawlTool with crawl4ai crawler and config timeout/retries.

        Does Not: Load config in init—via parent BaseTool.
        """
        super().__init__(
            name="web_crawl",
            description="Crawls web URL for structured JSON/Markdown with optional CSS/XPath selectors for extraction."
        )
        config = load_config()
        self.crawler = AsyncWebCrawler()
        self.timeout = config.get("crawl_timeout", 30)
        self.max_retries = config.get("crawl_retries", 3)
        logger.info("WebCrawlTool init", extra={"timeout": self.timeout, "retries": self.max_retries})

    def execute(self, url: str, css_selector: Optional[str] = None, xpath: Optional[str] = None, output_format: str = "json") -> Dict[str, Any]:
        """
        Async crawls URL with selectors, returns structured content/metadata.

        Args:
            url: Target URL (str).
            css_selector: CSS for extraction (e.g., ".content"; optional).
            xpath: XPath for extraction (e.g., "//div[@id='main']"; optional).
            output_format: "json" or "markdown" (default: "json").

        Returns:
            Dict {"content": str, "metadata": {"title": str, "links": list}}.

        Does Not: Cache—stateless per call.
        """
        if not self.validate(url=url, css_selector=css_selector, xpath=xpath, output_format=output_format)["valid"]:
            raise ValueError("Invalid params for web crawl.")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self._async_crawl(url, css_selector, xpath, output_format))
        finally:
            loop.close()
        logger.info("Web crawl executed", extra={"url": url, "format": output_format, "content_len": len(result["content"])})
        return result

    async def _async_crawl(self, url: str, css_selector: Optional[str], xpath: Optional[str], output_format: str) -> Dict[str, Any]:
        """Internal async crawl with retries."""
        for attempt in range(self.max_retries):
            try:
                async with asyncio.timeout(self.timeout):
                    crawl_result = await self.crawler.arun(url=url, css_selector=css_selector, xpath=xpath)
                content = crawl_result.json if output_format == "json" else crawl_result.markdown
                metadata = {"title": crawl_result.page_title, "links": crawl_result.links}
                return {"content": content, "metadata": metadata}
            except Exception as e:
                logger.warning("Crawl retry", extra={"attempt": attempt + 1, "error": str(e)})
                if attempt == self.max_retries - 1:
                    raise ValueError(f"Crawl failed after {self.max_retries} retries: {e}")
        return {"content": "", "metadata": {}}

__all__ = ["WebCrawlTool"]