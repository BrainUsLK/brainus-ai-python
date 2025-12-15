"""
Django REST Framework Example

This example shows how to integrate BrainUs API with Django REST Framework.
Django 3.1+ supports async views.

Requirements:
    pip install djangorestframework brainus-ai

Setup:
    Add to settings.py:
    BRAINUS_API_KEY = os.getenv('BRAINUS_API_KEY')
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from brainus_ai import BrainusAI, BrainusError
from django.conf import settings
from django.core.cache import cache
import hashlib


class QueryView(APIView):
    """
    API endpoint for querying BrainUs with caching support.
    
    POST /api/query
    {
        "query": "What is photosynthesis?",
        "store_id": "default"
    }
    """
    
    async def post(self, request):
        query = request.data.get('query')
        store_id = request.data.get('store_id', 'default')

        if not query:
            return Response(
                {'error': 'Query is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Cache key based on query
        cache_key = f"brainus_{hashlib.md5(query.encode()).hexdigest()}"

        # Check cache first
        cached_result = await cache.aget(cache_key)
        if cached_result:
            return Response({
                'answer': cached_result,
                'cached': True
            })

        try:
            # Make API request
            async with BrainusAI(api_key=settings.BRAINUS_API_KEY) as client:
                result = await client.query(query=query, store_id=store_id)

            # Cache for 1 hour
            await cache.aset(cache_key, result.answer, 3600)

            return Response({
                'answer': result.answer,
                'citations': result.citations,
                'has_citations': result.has_citations,
                'cached': False
            })

        except BrainusError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# URL Configuration (urls.py)
"""
from django.urls import path
from .views import QueryView

urlpatterns = [
    path('api/query', QueryView.as_view(), name='query'),
]
"""
