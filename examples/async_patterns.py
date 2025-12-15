"""
Async/Await Patterns Example

This example demonstrates various async patterns with BrainUs AI.

Requirements:
    pip install brainus-ai

Usage:
    export BRAINUS_API_KEY=your_api_key
    python async_patterns.py
"""

import asyncio
from brainus_ai import BrainusAI
import os
from typing import List, Dict


async def query_single(query: str, store_id: str = "default") -> Dict:
    """
    Query a single question
    
    Args:
        query: The question to ask
        store_id: The store ID to query
        
    Returns:
        Dict with query and result
    """
    async with BrainusAI(api_key=os.getenv("BRAINUS_API_KEY")) as client:
        result = await client.query(query=query, store_id=store_id)
        return {
            'query': query,
            'answer': result.answer,
            'citations_count': len(result.citations) if result.citations else 0
        }


async def query_multiple(queries: List[str], store_id: str = "default") -> List[Dict]:
    """
    Query multiple questions in parallel
    
    This is much faster than querying sequentially because all
    requests are made concurrently.
    
    Args:
        queries: List of questions to ask
        store_id: The store ID to query
        
    Returns:
        List of results
    """
    async with BrainusAI(api_key=os.getenv("BRAINUS_API_KEY")) as client:
        tasks = [
            client.query(query=q, store_id=store_id)
            for q in queries
        ]
        results = await asyncio.gather(*tasks)
    
    return [
        {
            'query': q,
            'answer': r.answer,
            'citations_count': len(r.citations) if r.citations else 0
        }
        for q, r in zip(queries, results)
    ]


async def query_with_timeout(query: str, timeout: float = 10.0) -> Dict:
    """
    Query with a timeout
    
    Args:
        query: The question to ask
        timeout: Maximum seconds to wait
        
    Returns:
        Dict with result or error
    """
    try:
        result = await asyncio.wait_for(
            query_single(query),
            timeout=timeout
        )
        return result
    except asyncio.TimeoutError:
        return {
            'query': query,
            'error': f'Query timed out after {timeout}s'
        }


async def query_with_fallback(query: str, fallback_stores: List[str]) -> Dict:
    """
    Query with fallback to alternative stores
    
    Args:
        query: The question to ask
        fallback_stores: List of store IDs to try in order
        
    Returns:
        Result from first successful store
    """
    async with BrainusAI(api_key=os.getenv("BRAINUS_API_KEY")) as client:
        for store_id in fallback_stores:
            try:
                result = await client.query(query=query, store_id=store_id)
                return {
                    'query': query,
                    'answer': result.answer,
                    'store_used': store_id,
                    'success': True
                }
            except Exception as e:
                print(f"Failed with {store_id}: {e}")
                continue
        
        return {
            'query': query,
            'error': 'All stores failed',
            'success': False
        }


async def main():
    """Main example demonstrating different async patterns"""
    
    print("=" * 60)
    print("ASYNC PATTERNS DEMONSTRATION")
    print("=" * 60)
    
    # Example 1: Single query
    print("\n1. Single Query:")
    result = await query_single("What is photosynthesis?")
    print(f"   Q: {result['query']}")
    print(f"   A: {result['answer'][:100]}...")
    
    # Example 2: Multiple queries in parallel
    print("\n2. Multiple Parallel Queries:")
    queries = [
        "What is photosynthesis?",
        "Explain the water cycle",
        "What causes earthquakes?"
    ]
    results = await query_multiple(queries)
    for r in results:
        print(f"   Q: {r['query']}")
        print(f"   A: {r['answer'][:80]}...")
        print()
    
    # Example 3: Query with timeout
    print("\n3. Query with Timeout:")
    result = await query_with_timeout("What is machine learning?", timeout=10.0)
    if 'error' in result:
        print(f"   Error: {result['error']}")
    else:
        print(f"   Q: {result['query']}")
        print(f"   A: {result['answer'][:100]}...")
    
    # Example 4: Query with fallback stores
    print("\n4. Query with Fallback Stores:")
    result = await query_with_fallback(
        "What is quantum computing?",
        fallback_stores=["primary", "secondary", "default"]
    )
    if result['success']:
        print(f"   Q: {result['query']}")
        print(f"   Store: {result['store_used']}")
        print(f"   A: {result['answer'][:100]}...")
    else:
        print(f"   Error: {result['error']}")


if __name__ == "__main__":
    asyncio.run(main())
