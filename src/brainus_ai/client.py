"""Main client for the Brainus AI SDK."""

from __future__ import annotations

import httpx
from typing import Any

from .exceptions import (
    AuthenticationError,
    RateLimitError,
    QuotaExceededError,
    APIError,
)
from .models import QueryRequest, QueryResponse, UsageStats, Plan, QueryFilters


class BrainusAI:
    """
    Brainus AI Python Client.

    Example:
        >>> from brainus_ai import BrainusAI
        >>> client = BrainusAI(api_key="brainus_...")
        >>> response = await client.query(
        ...     query="What is Python?",
        ...     store_id="abc123"  # Optional - uses default if not provided
        ... )
        >>> print(response.answer)
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.brainus.lk",
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        """
        Initialize the Brainus AI client.

        Args:
            api_key: Your Brainus AI API key (brainus_...)
            base_url: Base URL for the API (default: production gateway)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts for failed requests
        """
        if not api_key or not api_key.startswith("brainus_"):
            raise AuthenticationError("Invalid API key format. Expected format: brainus_...")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "X-API-Key": self.api_key,
                "Content-Type": "application/json",
                "User-Agent": "brainus-ai-python/0.1.0",
            },
            timeout=httpx.Timeout(timeout),
            transport=httpx.AsyncHTTPTransport(retries=max_retries),
        )

    async def query(
        self,
        query: str,
        store_id: str | None = None,
        filters: QueryFilters | dict[str, str] | None = None,
        model: str | None = None,
    ) -> QueryResponse:
        """
        Query the Brainus AI system.

        Args:
            query: The question or query text
            store_id: File search store ID (optional - uses default if not provided)
            filters: Optional metadata filters (e.g., QueryFilters or {"subject": "ICT", "grade": "12"})
            model: Gemini model to use (must be in your plan's allowed_models)

        Returns:
            QueryResponse with answer and citations

        Raises:
            AuthenticationError: If API key is invalid
            RateLimitError: If rate limit is exceeded
            QuotaExceededError: If monthly quota is exceeded
            APIError: For other API errors

        Example:
            >>> response = await client.query(
            ...     query="What is Object-Oriented Programming?",
            ...     store_id="abc123",
            ...     filters=QueryFilters(subject="ICT", grade="12"),
            ...     model="brainusai-thinking"
            ... )
            >>> print(response.answer)
            >>> for citation in response.citations:
            ...     print(f"Source: {citation.document_name}, Pages: {citation.pages}")
        """
        # Convert dict filters to QueryFilters if needed
        if filters is not None and isinstance(filters, dict) and not isinstance(filters, QueryFilters):
            filters = QueryFilters(**filters)
        
        request_data = QueryRequest(query=query, store_id=store_id, filters=filters, model=model)

        response = await self._make_request(
            method="POST",
            endpoint="/api/v1/dev/query",
            json=request_data.model_dump(exclude_none=True),
        )

        return QueryResponse(**response)

    async def get_usage(self) -> UsageStats:
        """
        Get current usage statistics for your API key.

        Returns:
            UsageStats with request counts, quotas, and costs

        Raises:
            AuthenticationError: If API key is invalid
            APIError: For other API errors

        Example:
            >>> stats = await client.get_usage()
            >>> print(f"Total requests: {stats.total_requests}")
            >>> print(f"Quota remaining: {stats.quota_remaining}")
        """
        response = await self._make_request(
            method="GET",
            endpoint="/api/v1/dev/usage",
        )

        return UsageStats(**response)

    async def get_plans(self) -> list[Plan]:
        """
        Get available API plans.

        Returns:
            List of available plans with details

        Raises:
            AuthenticationError: If API key is invalid
            APIError: For other API errors

        Example:
            >>> plans = await client.get_plans()
            >>> for plan in plans:
            ...     print(f"{plan.name}: {plan.rate_limit_per_minute} req/min")
        """
        response = await self._make_request(
            method="GET",
            endpoint="/api/v1/dev/plans",
        )

        return [Plan(**plan) for plan in response.get("plans", [])]

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Make an HTTP request to the API with error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments to pass to httpx

        Returns:
            Response JSON as dictionary

        Raises:
            AuthenticationError: If API key is invalid (401)
            RateLimitError: If rate limit exceeded (429)
            QuotaExceededError: If quota exceeded (403)
            APIError: For other errors
        """
        try:
            response = await self._client.request(method, endpoint, **kwargs)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            try:
                error_data = e.response.json()
                error_message = error_data.get("detail", str(e))
            except Exception:
                error_message = str(e)

            if status_code == 401:
                raise AuthenticationError(error_message)
            elif status_code == 429:
                retry_after = e.response.headers.get("Retry-After")
                raise RateLimitError(
                    error_message,
                    retry_after=int(retry_after) if retry_after else None,
                )
            elif status_code == 400:
                if "No store_id provided and no default store configured" in error_message:
                    raise APIError(
                        "No store_id provided and no default store configured. "
                        "Please provide a store_id in your request.",
                        status_code=400
                    )
                raise APIError(error_message, status_code=status_code)
            elif status_code == 403 and "quota" in error_message.lower():
                raise QuotaExceededError(error_message)
            else:
                raise APIError(error_message, status_code=status_code)

        except httpx.RequestError as e:
            raise APIError(f"Request failed: {str(e)}")

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> BrainusAI:
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self.close()















