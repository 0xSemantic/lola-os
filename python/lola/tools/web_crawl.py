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
        # Use model_dump (Pydantic v2) defensively if config is Pydantic
        config = load_config()
        try:
            config_data = config.model_dump()
        except Exception:
            # fallback if load_config returns a plain dict-like object
            config_data = getattr(config, "__dict__", {}) or {}

        # Crawler instance (Crawl4AI)
        self.crawler = AsyncWebCrawler()
        self.timeout = config_data.get("crawl_timeout", 30)
        self.max_retries = config_data.get("crawl_retries", 3)
        logger.info("WebCrawlTool init", extra={"timeout": self.timeout, "retries": self.max_retries})

    async def execute(self, url: str, css_selector: Optional[str] = None, xpath: Optional[str] = None, output_format: str = "json") -> Dict[str, Any]:
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
        # Basic format checks (fast-fail)
        if not isinstance(url, str) or not url.strip():
            raise ValueError("Invalid params for web crawl: url required.")
        if not url.startswith("http://") and not url.startswith("https://"):
            raise ValueError("Invalid params for web crawl: url must start with http:// or https://")
        if output_format not in ("json", "markdown"):
            raise ValueError("Invalid params for web crawl: output_format must be 'json' or 'markdown'")

        # Allow BaseTool.validate to perform richer validation if present
        validated = self.validate(url=url, css_selector=css_selector, xpath=xpath, output_format=output_format)
        if not validated or not validated.get("valid", False):
            # If validate explicitly returns invalid, propagate as ValueError
            raise ValueError("Invalid params for web crawl.")

        return await self._async_crawl(url, css_selector, xpath, output_format)

    def execute_sync(self, url: str, css_selector: Optional[str] = None, xpath: Optional[str] = None, output_format: str = "json") -> Dict[str, Any]:
        """
        Synchronous wrapper for callers that want sync call semantics.
        Internally runs the async execute() in a fresh event loop.
        """
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(self.execute(url, css_selector, xpath, output_format))
        finally:
            try:
                loop.close()
            finally:
                asyncio.set_event_loop(None)

    async def _async_crawl(self, url: str, css_selector: Optional[str] = None, xpath: Optional[str] = None, output_format: str = "json") -> Dict[str, Any]:
        """Internal async crawl with retries."""
        last_exc = None
        for attempt in range(self.max_retries):
            try:
                # Use asyncio.wait_for for older Python compatibility instead of asyncio.timeout
                crawl_result = await asyncio.wait_for(
                    self.crawler.arun(url=url, css_selector=css_selector, xpath=xpath),
                    timeout=self.timeout
                )
                content = crawl_result.json if output_format == "json" else crawl_result.markdown
                metadata = {"title": crawl_result.page_title, "links": crawl_result.links}
                return {"content": content, "metadata": metadata}
            except Exception as e:
                last_exc = e
                logger.warning("Crawl retry", extra={"attempt": attempt + 1, "error": str(e)})
                # last attempt -> raise detailed ValueError
                if attempt == self.max_retries - 1:
                    raise ValueError(f"Crawl failed after {self.max_retries} retries: {e}")
                # otherwise continue and retry
                await asyncio.sleep(0.1 * (attempt + 1))
        # Should not reach here
        raise ValueError(f"Crawl failed: {last_exc}")

__all__ = ["WebCrawlTool"]
