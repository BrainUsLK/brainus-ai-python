"""
Batch Processing Example

This example demonstrates processing large batches of queries with
rate limiting, error handling, and progress tracking.

Requirements:
    pip install brainus-ai pandas

Usage:
    export BRAINUS_API_KEY=your_api_key
    python batch_processing.py
"""

from brainus_ai import BrainusAI
import pandas as pd
from typing import List, Dict
import asyncio
import os
from datetime import datetime


async def process_batch(
    queries: List[str], 
    batch_size: int = 10,
    store_id: str = "default",
    rate_limit_delay: float = 1.0
) -> List[Dict]:
    """
    Process queries in batches with rate limiting
    
    Args:
        queries: List of query strings
        batch_size: Number of queries to process at once
        store_id: Store ID to query
        rate_limit_delay: Seconds to wait between batches
        
    Returns:
        List of result dictionaries
    """
    results = []
    total_batches = (len(queries) + batch_size - 1) // batch_size

    async with BrainusAI(api_key=os.getenv("BRAINUS_API_KEY")) as client:
        for batch_num, i in enumerate(range(0, len(queries), batch_size), 1):
            batch = queries[i:i + batch_size]
            
            print(f"Processing batch {batch_num}/{total_batches} ({len(batch)} queries)...")

            # Create tasks for the batch
            tasks = [
                client.query(query=q, store_id=store_id)
                for q in batch
            ]

            # Execute batch with error handling
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for query, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    results.append({
                        'query': query,
                        'answer': None,
                        'error': str(result),
                        'citations_count': 0,
                        'success': False
                    })
                else:
                    results.append({
                        'query': query,
                        'answer': result.answer,
                        'error': None,
                        'citations_count': len(result.citations) if result.citations else 0,
                        'success': True
                    })

            # Rate limiting: wait between batches
            if i + batch_size < len(queries):
                await asyncio.sleep(rate_limit_delay)

    return results


async def process_csv_file(
    input_file: str,
    output_file: str,
    query_column: str = 'query',
    batch_size: int = 10
):
    """
    Process queries from a CSV file
    
    Args:
        input_file: Path to input CSV with queries
        output_file: Path to save results CSV
        query_column: Name of column containing queries
        batch_size: Batch size for processing
    """
    print(f"\nReading queries from {input_file}...")
    df = pd.read_csv(input_file)
    
    if query_column not in df.columns:
        raise ValueError(f"Column '{query_column}' not found in CSV")
    
    queries = df[query_column].tolist()
    print(f"Found {len(queries)} queries")
    
    print(f"\nProcessing in batches of {batch_size}...")
    start_time = datetime.now()
    
    results = await process_batch(queries, batch_size=batch_size)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Create results DataFrame
    results_df = pd.DataFrame(results)
    
    # Add original data
    for col in df.columns:
        if col != query_column:
            results_df[col] = df[col]
    
    # Save results
    results_df.to_csv(output_file, index=False)
    
    # Print statistics
    success_count = results_df['success'].sum()
    print(f"\n{'='*60}")
    print(f"BATCH PROCESSING COMPLETE")
    print(f"{'='*60}")
    print(f"Total queries: {len(queries)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {len(queries) - success_count}")
    print(f"Duration: {duration:.2f}s")
    print(f"Average time per query: {duration/len(queries):.2f}s")
    print(f"Results saved to: {output_file}")


async def process_with_progress(queries: List[str]) -> List[Dict]:
    """
    Process queries with detailed progress tracking
    
    Args:
        queries: List of query strings
        
    Returns:
        List of results
    """
    results = []
    
    async with BrainusAI(api_key=os.getenv("BRAINUS_API_KEY")) as client:
        for i, query in enumerate(queries, 1):
            try:
                print(f"[{i}/{len(queries)}] Processing: {query[:50]}...")
                result = await client.query(query=query, store_id="default")
                
                results.append({
                    'query': query,
                    'answer': result.answer,
                    'citations_count': len(result.citations) if result.citations else 0,
                    'success': True
                })
                print(f"  ✓ Success ({len(result.answer)} chars)")
                
            except Exception as e:
                results.append({
                    'query': query,
                    'error': str(e),
                    'success': False
                })
                print(f"  ✗ Error: {e}")
            
            # Small delay between requests
            if i < len(queries):
                await asyncio.sleep(0.5)
    
    return results


async def main():
    """Main example demonstrating batch processing"""
    
    print("=" * 60)
    print("BATCH PROCESSING DEMONSTRATION")
    print("=" * 60)
    
    # Example queries
    sample_queries = [
        "What is photosynthesis?",
        "Explain the water cycle",
        "What causes earthquakes?",
        "How do vaccines work?",
        "What is climate change?",
        "Explain DNA structure",
        "What is the theory of evolution?",
        "How does the internet work?",
    ]
    
    # Process with progress tracking
    print("\nProcessing queries with progress tracking:")
    results = await process_with_progress(sample_queries[:3])
    
    print(f"\nResults:")
    for r in results:
        if r['success']:
            print(f"  ✓ {r['query'][:40]}... -> {r['answer'][:60]}...")
        else:
            print(f"  ✗ {r['query'][:40]}... -> Error: {r['error']}")
    
    # Process in batches
    print("\n" + "=" * 60)
    print("Processing in batches:")
    batch_results = await process_batch(sample_queries, batch_size=3)
    
    success_count = sum(1 for r in batch_results if r['success'])
    print(f"\nBatch Summary:")
    print(f"  Total: {len(batch_results)}")
    print(f"  Success: {success_count}")
    print(f"  Failed: {len(batch_results) - success_count}")
    
    # Save to CSV (optional)
    df = pd.DataFrame(batch_results)
    output_file = "batch_results.csv"
    df.to_csv(output_file, index=False)
    print(f"\n  Results saved to: {output_file}")


# Example usage with CSV file
# Uncomment to use:
"""
async def example_csv():
    # Create sample input CSV
    sample_df = pd.DataFrame({
        'id': range(1, 11),
        'query': [
            "What is photosynthesis?",
            "Explain the water cycle",
            "What causes earthquakes?",
            "How do vaccines work?",
            "What is climate change?",
            "Explain DNA structure",
            "What is the theory of evolution?",
            "How does the internet work?",
            "What is machine learning?",
            "Explain quantum computing"
        ]
    })
    sample_df.to_csv('queries.csv', index=False)
    
    # Process the CSV
    await process_csv_file(
        input_file='queries.csv',
        output_file='results.csv',
        query_column='query',
        batch_size=3
    )

# asyncio.run(example_csv())
"""


if __name__ == "__main__":
    asyncio.run(main())
