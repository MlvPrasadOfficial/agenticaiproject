# Enterprise Insights Copilot - API Documentation

## Overview
Comprehensive RESTful API for the Enterprise Insights Copilot platform featuring:
- File upload and processing
- Data analysis and visualization
- Multi-agent AI system
- RAG (Retrieval-Augmented Generation) capabilities
- Real-time conversation interface

**Base URL**: `https://enterprise-insights-backend.onrender.com/api/v1`  
**API Version**: 1.0.0  
**Documentation**: `https://enterprise-insights-backend.onrender.com/docs`

## Authentication
Currently using API key authentication. Include your API key in the header:
```
Authorization: Bearer your-api-key-here
```

## Core Endpoints

### Health & Status
Monitor system health and readiness.

#### `GET /health`
**Description**: Basic health check  
**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-06-28T10:00:00Z",
  "version": "1.0.0"
}
```

#### `GET /readiness` 
**Description**: Readiness check for all services  
**Response**:
```json
{
  "status": "ready",
  "services": {
    "database": "connected",
    "redis": "connected", 
    "pinecone": "connected",
    "ollama": "available"
  }
}
```

#### `GET /liveness`
**Description**: Liveness probe for Kubernetes  
**Response**: `200 OK` or `503 Service Unavailable`

---

## File Management

### File Upload
Secure file upload with validation and processing.

#### `POST /upload/files/upload`
**Description**: Upload files for processing  
**Content-Type**: `multipart/form-data`  
**Body**: Form data with file field  
**Response**:
```json
{
  "file_id": "uuid-string",
  "filename": "data.csv",
  "size": 1024000,
  "type": "text/csv",
  "status": "uploaded",
  "upload_time": "2024-06-28T10:00:00Z"
}
```

#### `GET /upload/files/status/{file_id}`
**Description**: Get upload status  
**Response**:
```json
{
  "file_id": "uuid-string",
  "status": "processed",
  "progress": 100,
  "message": "File processed successfully"
}
```

#### `DELETE /upload/files/{file_id}`
**Description**: Delete uploaded file  
**Response**: `204 No Content`

---

## Data Processing

### Data Preview
Quick data inspection and analysis.

#### `GET /data/preview/{file_id}`
**Description**: Get data preview with sample rows  
**Parameters**:
- `limit` (query): Number of rows (default: 10)
- `offset` (query): Row offset (default: 0)

**Response**:
```json
{
  "file_id": "uuid-string",
  "total_rows": 1000,
  "columns": ["name", "age", "salary"],
  "sample_data": [
    {"name": "John", "age": 30, "salary": 50000},
    {"name": "Jane", "age": 25, "salary": 60000}
  ],
  "data_types": {
    "name": "string",
    "age": "integer", 
    "salary": "integer"
  }
}
```

#### `GET /data/statistics/{file_id}`
**Description**: Get comprehensive data statistics  
**Response**:
```json
{
  "file_id": "uuid-string",
  "row_count": 1000,
  "column_count": 3,
  "memory_usage": "2.1 MB",
  "statistics": {
    "age": {
      "mean": 32.5,
      "median": 30,
      "std": 8.2,
      "min": 18,
      "max": 65
    }
  },
  "missing_values": {
    "age": 5,
    "salary": 0
  }
}
```

#### `GET /data/columns/analysis/{file_id}/{column_name}`
**Description**: Detailed analysis of specific column  
**Response**:
```json
{
  "column_name": "salary",
  "data_type": "integer",
  "unique_values": 150,
  "null_count": 0,
  "distribution": {
    "0-30000": 100,
    "30000-60000": 500,
    "60000-100000": 300
  },
  "outliers": [150000, 200000]
}
```

#### `GET /data/search/{file_id}`
**Description**: Search within data  
**Parameters**:
- `query` (query): Search term
- `columns` (query): Comma-separated column names

**Response**:
```json
{
  "results": [
    {"row_id": 1, "match_column": "name", "match_value": "John Smith"},
    {"row_id": 15, "match_column": "department", "match_value": "Engineering"}
  ],
  "total_matches": 2
}
```

#### `GET /data/export/{file_id}`
**Description**: Export processed data  
**Parameters**:
- `format` (query): csv, json, xlsx (default: csv)

**Response**: File download or JSON data

---

## Agent System

### Agent Execution
Multi-agent AI system for business insights.

#### `POST /agents/execute`
**Description**: Execute single agent  
**Body**:
```json
{
  "agent_type": "data_analysis",
  "query": "Analyze sales trends",
  "file_id": "uuid-string",
  "parameters": {
    "analysis_type": "trend",
    "time_period": "monthly"
  }
}
```

**Response**:
```json
{
  "execution_id": "uuid-string",
  "status": "running",
  "agent_type": "data_analysis",
  "started_at": "2024-06-28T10:00:00Z",
  "estimated_completion": "2024-06-28T10:05:00Z"
}
```

#### `GET /agents/execution/{execution_id}`
**Description**: Get execution status  
**Response**:
```json
{
  "execution_id": "uuid-string",
  "status": "completed",
  "progress": 100,
  "result": {
    "insights": ["Sales increased 15% in Q2", "Peak sales in June"],
    "charts": ["trend_chart.png"],
    "recommendations": ["Focus marketing in Q3"]
  },
  "execution_time": 45.2
}
```

#### `POST /agents/workflow/execute`
**Description**: Execute multi-agent workflow  
**Body**:
```json
{
  "workflow_type": "comprehensive_analysis",
  "query": "Complete business analysis",
  "file_id": "uuid-string",
  "agents": ["planning", "data_analysis", "query", "insight"]
}
```

### Agent Sessions
Persistent conversation sessions with agents.

#### `POST /agents/session`
**Description**: Create new session  
**Body**:
```json
{
  "session_name": "Q2 Analysis",
  "agent_types": ["data_analysis", "insight"],
  "context": {
    "business_unit": "sales",
    "time_period": "Q2-2024"
  }
}
```

#### `GET /agents/session/{session_id}`
**Description**: Get session details  
**Response**:
```json
{
  "session_id": "uuid-string",
  "session_name": "Q2 Analysis", 
  "status": "active",
  "created_at": "2024-06-28T10:00:00Z",
  "message_count": 5,
  "last_activity": "2024-06-28T10:30:00Z"
}
```

#### `POST /agents/conversation`
**Description**: Send message to session  
**Body**:
```json
{
  "session_id": "uuid-string",
  "message": "What are the key insights from the sales data?",
  "context": {
    "file_id": "uuid-string"
  }
}
```

#### `GET /agents/conversation/{session_id}/history`
**Description**: Get conversation history  
**Response**:
```json
{
  "session_id": "uuid-string",
  "messages": [
    {
      "id": "msg-1",
      "role": "user", 
      "content": "Analyze sales trends",
      "timestamp": "2024-06-28T10:00:00Z"
    },
    {
      "id": "msg-2",
      "role": "assistant",
      "content": "I've analyzed the sales data...",
      "timestamp": "2024-06-28T10:01:00Z",
      "agent_type": "data_analysis"
    }
  ]
}
```

---

## RAG System (Retrieval-Augmented Generation)

### Vector Embeddings
Generate and manage vector embeddings for semantic search.

#### `POST /rag/embeddings`
**Description**: Generate embeddings for texts  
**Body**:
```json
{
  "texts": ["Business report analysis", "Sales data insights"],
  "model_name": "all-MiniLM-L6-v2"
}
```

**Response**:
```json
{
  "embeddings": [
    [0.1, 0.2, -0.3, ...],
    [0.4, -0.1, 0.8, ...]
  ],
  "model_name": "all-MiniLM-L6-v2",
  "dimension": 384,
  "count": 2
}
```

### Document Processing
Chunk and store documents for retrieval.

#### `POST /rag/document/chunk`
**Description**: Chunk document for embedding  
**Content-Type**: `multipart/form-data`  
**Parameters**:
- `chunk_size`: Characters per chunk (default: 1000)
- `overlap`: Character overlap (default: 200)

**Response**:
```json
{
  "filename": "report.txt",
  "total_chunks": 25,
  "chunks": [
    {
      "id": "chunk_0",
      "text": "Executive Summary: Our Q2 results...",
      "start_pos": 0,
      "end_pos": 995,
      "metadata": {
        "chunk_index": 0,
        "character_count": 995,
        "word_count": 150
      }
    }
  ],
  "average_chunk_size": 980.5
}
```

#### `POST /rag/store`
**Description**: Store chunks as vectors  
**Body**:
```json
{
  "file_id": "uuid-string",
  "chunks": [
    {
      "id": "chunk_0",
      "text": "Content here...",
      "start_pos": 0,
      "end_pos": 1000,
      "metadata": {}
    }
  ],
  "metadata": {
    "document_type": "report",
    "author": "analyst"
  }
}
```

### Search Operations
Semantic and hybrid search capabilities.

#### `POST /rag/search`
**Description**: Semantic search using vectors  
**Body**:
```json
{
  "query": "sales performance analysis",
  "top_k": 10,
  "file_id": "uuid-string",
  "threshold": 0.7
}
```

**Response**:
```json
{
  "query": "sales performance analysis",
  "results": [
    {
      "id": "file_uuid_chunk_0",
      "score": 0.95,
      "text": "Sales performance in Q2 showed...",
      "file_id": "uuid-string",
      "chunk_id": "chunk_0",
      "start_pos": 0,
      "end_pos": 1000,
      "metadata": {}
    }
  ],
  "total_results": 8,
  "search_type": "semantic",
  "execution_time": 0.12,
  "success": true
}
```

#### `POST /rag/search/hybrid`
**Description**: Hybrid vector + keyword search  
**Body**:
```json
{
  "query": "sales performance",
  "top_k": 10,
  "alpha": 0.7,
  "keywords": ["revenue", "growth", "Q2"]
}
```

### Advanced RAG Features

#### `POST /rag/context/retrieve`
**Description**: Retrieve context with surrounding chunks  
**Body**:
```json
{
  "query": "revenue analysis",
  "top_k": 5,
  "context_window": 3,
  "file_id": "uuid-string"
}
```

#### `POST /rag/query/expand`
**Description**: Expand query for better retrieval  
**Body**:
```json
{
  "query": "sales trends",
  "method": "similarity",
  "num_expansions": 5
}
```

#### `POST /rag/rerank`
**Description**: Rerank results for relevance  
**Body**:
```json
{
  "query": "sales analysis",
  "results": [/* search results */],
  "top_k": 10
}
```

### RAG Management

#### `GET /rag/health`
**Description**: RAG system health check  
**Response**:
```json
{
  "status": "healthy",
  "embedding_model_ready": true,
  "vector_store_ready": true,
  "model_name": "all-MiniLM-L6-v2",
  "embedding_dimension": 384,
  "index_name": "enterprise-insights",
  "stats": {
    "total_vectors": 5000,
    "index_name": "enterprise-insights"
  }
}
```

#### `GET /rag/stats`
**Description**: RAG system statistics  
**Response**:
```json
{
  "status": "success",
  "stats": {
    "total_vectors": 5000,
    "total_files": 25,
    "index_name": "enterprise-insights",
    "embedding_model": "all-MiniLM-L6-v2",
    "embedding_dimension": 384,
    "health_status": "healthy",
    "namespaces": {}
  }
}
```

#### `DELETE /rag/vectors/{file_id}`
**Description**: Delete vectors for specific file  
**Response**:
```json
{
  "file_id": "uuid-string",
  "success": true,
  "message": "Successfully deleted vectors for file uuid-string",
  "deleted_at": "2024-06-28T10:00:00Z"
}
```

---

## Error Handling

### Standard Error Response
```json
{
  "detail": "Error description",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2024-06-28T10:00:00Z",
  "request_id": "uuid-string"
}
```

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `204` - No Content
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `413` - Payload Too Large
- `415` - Unsupported Media Type
- `422` - Validation Error
- `429` - Too Many Requests
- `500` - Internal Server Error
- `503` - Service Unavailable

---

## Rate Limiting
- **Global**: 1000 requests/hour per IP
- **Upload**: 10 files/minute per user
- **Agent Execution**: 5 concurrent executions per user
- **RAG Search**: 100 searches/minute per user

---

## Pagination
For endpoints returning lists:
```json
{
  "items": [...],
  "total": 1000,
  "page": 1,
  "page_size": 20,
  "has_next": true,
  "has_prev": false
}
```

---

## WebSocket Endpoints (Coming Soon)
Real-time updates for:
- Agent execution progress
- File processing status
- Live conversation streams

---

## SDK Examples

### Python
```python
import requests

# File upload
with open('data.csv', 'rb') as f:
    response = requests.post(
        'https://api.enterprise-insights.com/api/v1/upload/files/upload',
        files={'file': f},
        headers={'Authorization': 'Bearer your-api-key'}
    )

# Agent execution
response = requests.post(
    'https://api.enterprise-insights.com/api/v1/agents/execute',
    json={
        'agent_type': 'data_analysis',
        'query': 'Analyze sales trends',
        'file_id': file_id
    }
)
```

### JavaScript
```javascript
// Upload file
const formData = new FormData();
formData.append('file', file);

const response = await fetch('/api/v1/upload/files/upload', {
  method: 'POST',
  body: formData,
  headers: {
    'Authorization': 'Bearer your-api-key'
  }
});

// RAG search
const searchResponse = await fetch('/api/v1/rag/search', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer your-api-key'
  },
  body: JSON.stringify({
    query: 'sales performance',
    top_k: 10
  })
});
```

---

## Development & Testing

### Local Development
```bash
# Start backend
cd backend
uvicorn main:app --reload

# API docs available at: http://localhost:8000/docs
```

### Testing
```bash
# Run API tests
pytest tests/test_api.py -v

# Load testing
ab -n 1000 -c 10 http://localhost:8000/health
```

---

## Support & Resources

- **Interactive Docs**: `/docs` (Swagger UI)
- **Alternative Docs**: `/redoc` (ReDoc)
- **GitHub**: [enterprise-insights-copilot](https://github.com/yourorg/enterprise-insights-copilot)
- **Support**: support@enterprise-insights.com
- **Status Page**: https://status.enterprise-insights.com

---

*Last Updated: June 28, 2024*  
*API Version: 1.0.0*
