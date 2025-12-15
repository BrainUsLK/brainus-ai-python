"""
Error Handling Example

This example demonstrates comprehensive error handling patterns for BrainUs AI.

Requirements:
    pip install brainus-ai

Usage:
    export BRAINUS_API_KEY=your_api_key
    python error_handling.py
"""

from brainus_ai import (
    BrainusAI,
    BrainusError,
    AuthenticationError,
    RateLimitError,
    QuotaExceededError,
    APIError
)
import asyncio
import os
from typing import Optional


async def basic_error_handling(query: str) -> Optional[dict]:
    """
    Basic error handling with try-except
    
    Args:
        query: The question to ask
        
    Returns:
        Result dict or None on error
    """
    try:
        async with BrainusAI(api_key=os.getenv("BRAINUS_API_KEY")) as client:
            result = await client.query(query=query, store_id="default")
            return {
                'answer': result.answer,
                'success': True
            }
    except BrainusError as e:
        print(f"Error: {e}")
        return None


async def robust_query(query: str, max_retries: int = 3) -> Optional[dict]:
    """
    Query with comprehensive error handling and retry logic
    
    Args:
        query: The question to ask
        max_retries: Maximum retry attempts for recoverable errors
        
    Returns:
        Result dict or None on permanent failure
    """
    async with BrainusAI(api_key=os.getenv("BRAINUS_API_KEY")) as client:
        for attempt in range(max_retries):
            try:
                result = await client.query(query=query, store_id="default")
                return {
                    'answer': result.answer,
                    'citations': result.citations,
                    'has_citations': result.has_citations,
                    'success': True,
                    'attempts': attempt + 1
                }

            except AuthenticationError as e:
                # Permanent error - no retry
                print(f"❌ Authentication failed: {e}")
                print("Check your API key!")
                return {
                    'error': 'authentication_failed',
                    'message': str(e),
                    'success': False
                }

            except RateLimitError as e:
                # Recoverable - wait and retry
                print(f"⏳ Rate limited. Waiting {e.retry_after}s...")
                await asyncio.sleep(e.retry_after)
                continue

            except QuotaExceededError as e:
                # Permanent error - no retry
                print(f"❌ Quota exceeded: {e}")
                print("Consider upgrading your plan!")
                return {
                    'error': 'quota_exceeded',
                    'message': str(e),
                    'success': False
                }

            except APIError as e:
                # Potentially recoverable - retry with backoff
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"⚠️  API error. Retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    print(f"❌ API error after {max_retries} attempts: {e}")
                    return {
                        'error': 'api_error',
                        'message': str(e),
                        'success': False
                    }

            except BrainusError as e:
                # Generic error
                print(f"❌ Unexpected error: {e}")
                return {
                    'error': 'unexpected_error',
                    'message': str(e),
                    'success': False
                }

    return {
        'error': 'max_retries_exceeded',
        'message': f'Failed after {max_retries} attempts',
        'success': False
    }


async def query_with_fallback(query: str, fallback_answer: str = "Unable to process query") -> dict:
    """
    Query with a fallback answer on error
    
    Args:
        query: The question to ask
        fallback_answer: Default answer if query fails
        
    Returns:
        Result dict with answer (from API or fallback)
    """
    try:
        async with BrainusAI(api_key=os.getenv("BRAINUS_API_KEY")) as client:
            result = await client.query(query=query, store_id="default")
            return {
                'answer': result.answer,
                'source': 'api',
                'success': True
            }
    except Exception as e:
        print(f"⚠️  Query failed, using fallback: {e}")
        return {
            'answer': fallback_answer,
            'source': 'fallback',
            'success': False,
            'error': str(e)
        }


async def validate_and_query(query: str) -> Optional[dict]:
    """
    Validate input before querying
    
    Args:
        query: The question to ask
        
    Returns:
        Result dict or None if validation fails
    """
    # Input validation
    if not query or not query.strip():
        print("❌ Error: Query cannot be empty")
        return {
            'error': 'validation_error',
            'message': 'Query cannot be empty',
            'success': False
        }
    
    if len(query) > 5000:
        print("❌ Error: Query too long (max 5000 characters)")
        return {
            'error': 'validation_error',
            'message': 'Query exceeds maximum length',
            'success': False
        }
    
    # Query with error handling
    try:
        async with BrainusAI(api_key=os.getenv("BRAINUS_API_KEY")) as client:
            result = await client.query(query=query, store_id="default")
            return {
                'answer': result.answer,
                'success': True
            }
    except BrainusError as e:
        return {
            'error': 'api_error',
            'message': str(e),
            'success': False
        }


async def batch_with_error_handling(queries: list[str]) -> list[dict]:
    """
    Process multiple queries with individual error handling
    
    Args:
        queries: List of questions
        
    Returns:
        List of results (successes and failures)
    """
    results = []
    
    async with BrainusAI(api_key=os.getenv("BRAINUS_API_KEY")) as client:
        for i, query in enumerate(queries, 1):
            print(f"\n[{i}/{len(queries)}] Processing: {query[:50]}...")
            
            try:
                result = await client.query(query=query, store_id="default")
                results.append({
                    'query': query,
                    'answer': result.answer,
                    'success': True
                })
                print(f"  ✓ Success")
                
            except RateLimitError as e:
                print(f"  ⏳ Rate limited, waiting {e.retry_after}s...")
                await asyncio.sleep(e.retry_after)
                # Retry once
                try:
                    result = await client.query(query=query, store_id="default")
                    results.append({
                        'query': query,
                        'answer': result.answer,
                        'success': True
                    })
                    print(f"  ✓ Success (after retry)")
                except Exception as retry_error:
                    results.append({
                        'query': query,
                        'error': str(retry_error),
                        'success': False
                    })
                    print(f"  ✗ Failed after retry: {retry_error}")
                    
            except Exception as e:
                results.append({
                    'query': query,
                    'error': str(e),
                    'success': False
                })
                print(f"  ✗ Error: {e}")
            
            # Small delay between queries
            if i < len(queries):
                await asyncio.sleep(0.5)
    
    return results


async def main():
    """Main example demonstrating error handling patterns"""
    
    print("=" * 60)
    print("ERROR HANDLING DEMONSTRATION")
    print("=" * 60)
    
    # Example 1: Basic error handling
    print("\n1. Basic Error Handling:")
    result = await basic_error_handling("What is photosynthesis?")
    if result:
        print(f"   ✓ Success: {result['answer'][:80]}...")
    
    # Example 2: Robust query with retries
    print("\n2. Robust Query with Retry Logic:")
    result = await robust_query("Explain the water cycle")
    if result and result['success']:
        print(f"   ✓ Success (attempts: {result['attempts']})")
        print(f"   Answer: {result['answer'][:80]}...")
    else:
        print(f"   ✗ Failed: {result['error']}")
    
    # Example 3: Query with fallback
    print("\n3. Query with Fallback:")
    result = await query_with_fallback(
        "What is quantum computing?",
        fallback_answer="Quantum computing is a complex topic."
    )
    print(f"   Source: {result['source']}")
    print(f"   Answer: {result['answer'][:80]}...")
    
    # Example 4: Validation before query
    print("\n4. Validation Before Query:")
    
    # Valid query
    result = await validate_and_query("What causes earthquakes?")
    if result and result['success']:
        print(f"   ✓ Valid query succeeded")
    
    # Invalid query (empty)
    result = await validate_and_query("")
    if result and not result['success']:
        print(f"   ✗ Validation failed: {result['message']}")
    
    # Example 5: Batch with error handling
    print("\n5. Batch Processing with Error Handling:")
    queries = [
        "What is photosynthesis?",
        "Explain DNA structure",
        "What is machine learning?"
    ]
    results = await batch_with_error_handling(queries)
    
    success_count = sum(1 for r in results if r['success'])
    print(f"\n   Summary:")
    print(f"   Total: {len(results)}")
    print(f"   Success: {success_count}")
    print(f"   Failed: {len(results) - success_count}")


if __name__ == "__main__":
    asyncio.run(main())
