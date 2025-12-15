"""
Flask Application Example

This example shows how to integrate BrainUs API with Flask.
Flask 2.0+ supports async routes.

Requirements:
    pip install flask brainus-ai

Usage:
    export BRAINUS_API_KEY=your_api_key
    python flask_example.py
"""

from flask import Flask, request, jsonify
from brainus_ai import BrainusAI, RateLimitError
import os
import asyncio

app = Flask(__name__)


async def query_with_retry(query, store_id="default", max_retries=3):
    """
    Helper to retry on rate limit errors
    
    Args:
        query: The query string
        store_id: The store ID to query
        max_retries: Maximum number of retry attempts
        
    Returns:
        QueryResult object
        
    Raises:
        RateLimitError: If max retries exceeded
    """
    async with BrainusAI(api_key=os.getenv("BRAINUS_API_KEY")) as client:
        for attempt in range(max_retries):
            try:
                return await client.query(query=query, store_id=store_id)
            except RateLimitError as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(e.retry_after)


@app.route('/api/query', methods=['POST'])
async def query():
    """
    Query endpoint
    
    POST /api/query
    {
        "query": "What is photosynthesis?",
        "store_id": "default"
    }
    """
    data = request.json

    if not data or 'query' not in data:
        return jsonify({'error': 'Query is required'}), 400

    try:
        result = await query_with_retry(
            query=data['query'],
            store_id=data.get('store_id', 'default')
        )

        return jsonify({
            'answer': result.answer,
            # Serialize citations using model_dump() if Pydantic, or dict comprehension
            'citations': [
                c.model_dump() if hasattr(c, 'model_dump') else c.__dict__ 
                for c in result.citations
            ] if result.citations else [],
            'has_citations': result.has_citations
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
