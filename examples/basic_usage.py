"""Basic usage example for the Brainus AI Python SDK."""

import asyncio
import os
from brainus_ai import BrainusAI


async def main():
    # Get API key from environment variable
    api_key = os.getenv("BRAINUS_API_KEY")
    if not api_key:
        print("Error: BRAINUS_API_KEY environment variable not set")
        return

    # Initialize the client
    async with BrainusAI(api_key=api_key) as client:
        # Example 1: Query with no filters
        print("Example 1: Simple query")
        print("-" * 50)
        response = await client.query(
            query="What is Object-Oriented Programming?",
            # store_id is optional - uses default if not provided
        )
        print(f"Answer: {response.answer}\n")

        if response.has_citations:
            print("Citations:")
            for citation in response.citations:
                print(f"  - {citation.document_name} (Pages: {citation.pages})")
        print()

        # Example 2: Query with filters
        print("Example 2: Query with filters")
        print("-" * 50)
        from brainus_ai import QueryFilters
        
        response = await client.query(
            query="Explain inheritance in programming",
            store_id="your_store_id",  # Optional
            model="brainusai-thinking",  # Optional
            filters=QueryFilters(subject="ICT", grade="12"),
        )
        print(f"Answer: {response.answer[:200]}...\n")

        # Example 3: Get usage statistics
        print("Example 3: Usage statistics")
        print("-" * 50)
        stats = await client.get_usage()
        print(f"Total requests: {stats.total_requests}")
        print(f"Quota used: {stats.quota_percentage}%")
        if stats.quota_remaining:
            print(f"Quota remaining: {stats.quota_remaining}")
        print()

        # Example 4: Get available plans
        print("Example 4: Available plans")
        print("-" * 50)
        plans = await client.get_plans()
        for plan in plans:
            print(f"{plan.name}:")
            print(f"  Rate limit: {plan.rate_limit_per_minute} req/min")
            print(f"  Monthly quota: {plan.monthly_quota or 'Unlimited'}")
            print(f"  Price: LKR {plan.price_lkr or 0}/month")
            print(f"  Allowed models: {', '.join(plan.allowed_models)}")
        print()


if __name__ == "__main__":
    asyncio.run(main())















