# BrainUs AI Python Examples

Complete Python examples for integrating BrainUs AI API with popular frameworks and patterns.

## Table of Contents

- [Framework Examples](#framework-examples)
  - [Django REST Framework](#django-rest-framework)
  - [Flask](#flask)
  - [FastAPI](#fastapi)
- [Pattern Examples](#pattern-examples)
  - [Async/Await Patterns](#asyncawait-patterns)
  - [Batch Processing](#batch-processing)
  - [Error Handling](#error-handling)
- [Basic Usage](#basic-usage)
- [Setup](#setup)
- [Running Examples](#running-examples)

## Framework Examples

### Django REST Framework

**File:** [django_example.py](django_example.py)

Demonstrates integration with Django REST Framework with async views and caching support.

**Features:**

- Async API views (Django 3.1+)
- Query caching with Django cache framework
- Clean error handling
- RESTful response formatting

**Requirements:**

```bash
pip install djangorestframework brainus-ai
```

**Usage:**
Add to your Django project's views and configure in `settings.py`:

```python
BRAINUS_API_KEY = os.getenv('BRAINUS_API_KEY')
```

---

### Flask

**File:** [flask_example.py](flask_example.py)

Flask 2.0+ application with async route support and retry logic.

**Features:**

- Async routes (Flask 2.0+)
- Rate limit retry mechanism
- Health check endpoint
- JSON response handling

**Requirements:**

```bash
pip install flask brainus-ai
```

**Usage:**

```bash
export BRAINUS_API_KEY=your_api_key
python flask_example.py
```

Test the API:

```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is photosynthesis?"}'
```

---

### FastAPI

**File:** [fastapi_example.py](fastapi_example.py)

Modern FastAPI application built for async operations.

**Features:**

- Native async support
- Pydantic models for validation
- CORS middleware
- Background tasks for logging
- OpenAPI documentation
- Health check endpoint

**Requirements:**

```bash
pip install fastapi uvicorn brainus-ai
```

**Usage:**

```bash
export BRAINUS_API_KEY=your_api_key
python fastapi_example.py
```

Or with uvicorn:

```bash
uvicorn fastapi_example:app --reload
```

Access the API documentation at: http://localhost:8000/docs

---

## Pattern Examples

### Async/Await Patterns

**File:** [async_patterns.py](async_patterns.py)

Demonstrates various async patterns for efficient query processing.

**Features:**

- Single query execution
- Parallel multiple queries
- Query with timeout
- Fallback store patterns
- Error handling in async context

**Usage:**

```bash
export BRAINUS_API_KEY=your_api_key
python async_patterns.py
```

**Key Patterns:**

```python
# Parallel queries
results = await query_multiple(queries)

# With timeout
result = await query_with_timeout(query, timeout=10.0)

# With fallback stores
result = await query_with_fallback(query, ["primary", "secondary", "default"])
```

---

### Batch Processing

**File:** [batch_processing.py](batch_processing.py)

Process large batches of queries with rate limiting and progress tracking.

**Features:**

- Batch processing with configurable size
- Rate limiting between batches
- Progress tracking
- CSV file input/output
- Error handling per query
- Comprehensive statistics

**Requirements:**

```bash
pip install brainus-ai pandas
```

**Usage:**

```bash
export BRAINUS_API_KEY=your_api_key
python batch_processing.py
```

**CSV Processing:**

```python
await process_csv_file(
    input_file='queries.csv',
    output_file='results.csv',
    query_column='query',
    batch_size=10
)
```

---

### Error Handling

**File:** [error_handling.py](error_handling.py)

Comprehensive error handling patterns for production use.

**Features:**

- All error types handling
- Retry logic with exponential backoff
- Fallback mechanisms
- Input validation
- Rate limit handling
- Batch error handling

**Usage:**

```bash
export BRAINUS_API_KEY=your_api_key
python error_handling.py
```

**Error Types Handled:**

- `AuthenticationError` - Invalid API key
- `RateLimitError` - Rate limit exceeded (with retry)
- `QuotaExceededError` - Usage quota exceeded
- `APIError` - General API errors
- `BrainusError` - Base exception class

---

## Basic Usage

**File:** [basic_usage.py](basic_usage.py)

Simple example to get started quickly.

**Usage:**

```bash
export BRAINUS_API_KEY=your_api_key
python basic_usage.py
```

---

## Setup

### 1. Install the SDK

```bash
pip install brainus-ai
```

### 2. Set Your API Key

**Option A: Environment Variable (Recommended)**

```bash
export BRAINUS_API_KEY=your_api_key_here
```

**Option B: In Code (Not Recommended for Production)**

```python
client = BrainusAI(api_key="your_api_key_here")
```

### 3. Install Framework Dependencies

Choose based on your needs:

```bash
# For Django examples
pip install djangorestframework

# For Flask examples
pip install flask

# For FastAPI examples
pip install fastapi uvicorn

# For batch processing
pip install pandas
```

---

## Running Examples

### Quick Start

```bash
# Set your API key
export BRAINUS_API_KEY=your_api_key

# Run any example
python examples/basic_usage.py
python examples/async_patterns.py
python examples/error_handling.py
```

### Web Frameworks

**Flask:**

```bash
python examples/flask_example.py
# API available at http://localhost:5000
```

**FastAPI:**

```bash
python examples/fastapi_example.py
# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

---

## Common Patterns

### Context Manager (Recommended)

```python
async with BrainusAI(api_key=os.getenv("BRAINUS_API_KEY")) as client:
    result = await client.query(query="What is AI?", store_id="default")
```

### Manual Management

```python
client = BrainusAI(api_key=os.getenv("BRAINUS_API_KEY"))
try:
    result = await client.query(query="What is AI?", store_id="default")
finally:
    await client.close()
```

### Error Handling

```python
from brainus_ai import BrainusAI, BrainusError, RateLimitError

try:
    async with BrainusAI(api_key=api_key) as client:
        result = await client.query(query="What is AI?")
except RateLimitError as e:
    await asyncio.sleep(e.retry_after)
except BrainusError as e:
    print(f"Error: {e}")
```

---

## Example Output

```python
result = await client.query(query="What is photosynthesis?")

print(result.answer)
# "Photosynthesis is the process by which..."

print(result.has_citations)
# True

if result.citations:
    for citation in result.citations:
        print(f"Source: {citation.source}")
```

---

## Next Steps

- **[Python SDK Documentation](../src/brainus_ai/)** - Complete SDK reference
- **[GitHub Repository](https://github.com/brainuslk/brainus-ai-python)** - Source code and issues
- **[API Documentation](https://brainus.ai/docs)** - Full API documentation

---

## Support

If you encounter any issues or have questions:

- 📧 Email: developers@brainus.lk
- 🐛 Issues: [GitHub Issues](https://github.com/brainuslk/brainus-ai-python/issues)
- 📖 Docs: [brainus.ai/docs](https://developers.brainus.lk/docs)

---

## License

These examples are provided under the same license as the BrainUs AI Python SDK.
