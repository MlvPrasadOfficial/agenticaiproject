# Developer Documentation: Enterprise Insights Copilot

## Architecture Overview

### System Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │  External       │
│   (Next.js 14) │◄──►│   (FastAPI)     │◄──►│  Services       │
│                 │    │                 │    │                 │
│ • React Query   │    │ • Multi-Agent   │    │ • Pinecone      │
│ • TypeScript    │    │ • RAG System    │    │ • Ollama        │
│ • Tailwind CSS  │    │ • LangChain     │    │ • PostgreSQL    │
│ • Glassmorphism │    │ • Vector DB     │    │ • Redis         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Technology Stack

#### Frontend Stack
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript 5.0+
- **Styling**: Tailwind CSS 3.3+ with custom glassmorphism theme
- **State Management**: React Query (TanStack Query) for server state
- **UI Components**: Custom component library with accessibility
- **Charts**: D3.js for advanced data visualization
- **Build Tool**: Webpack 5 with optimizations
- **Deployment**: Vercel with edge functions

#### Backend Stack
- **Framework**: FastAPI 0.104+ with async/await
- **Language**: Python 3.11+ with type hints
- **Database**: PostgreSQL 15+ with SQLAlchemy 2.0
- **Cache**: Redis 7+ for session and result caching
- **Vector Database**: Pinecone for RAG embeddings
- **AI/ML**: 
  - LangChain 0.1+ for agent orchestration
  - LangGraph for workflow management
  - Ollama for local LLM inference
  - sentence-transformers for embeddings
- **Authentication**: JWT with FastAPI Security
- **Deployment**: Render with Docker containers

#### DevOps & Infrastructure
- **Version Control**: Git with GitHub
- **CI/CD**: GitHub Actions with automated testing
- **Monitoring**: Custom logging with structured JSON
- **Documentation**: OpenAPI/Swagger auto-generated
- **Testing**: pytest (backend), Jest/RTL (frontend)

---

## Development Setup

### Prerequisites
```bash
# Required versions
Node.js >= 18.0.0
Python >= 3.11.0
Git >= 2.30.0
PostgreSQL >= 15.0
Redis >= 7.0
```

### Local Development Environment

#### 1. Clone Repository
```bash
git clone https://github.com/yourorg/enterprise-insights-copilot.git
cd enterprise-insights-copilot
```

#### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize database
alembic upgrade head

# Start development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your configuration

# Start development server
npm run dev
```

#### 4. External Services Setup

**Pinecone Configuration:**
```python
# Create index for RAG system
import pinecone

pinecone.init(api_key="your-key", environment="us-east-1")
pinecone.create_index(
    name="enterprise-insights",
    dimension=384,  # all-MiniLM-L6-v2 embedding dimension
    metric="cosine"
)
```

**Ollama Setup:**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull required models
ollama pull llama3.1:8b

# Start Ollama server
ollama serve
```

### Development Workflow

#### Git Workflow
```bash
# Feature development
git checkout -b feature/new-feature
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature

# Create pull request on GitHub
# After review and CI passes, merge to main
```

#### Code Quality
```bash
# Backend code quality
cd backend
black .                 # Code formatting
isort .                 # Import sorting
flake8 .               # Linting
mypy .                 # Type checking
pytest tests/ -v       # Run tests

# Frontend code quality
cd frontend
npm run lint           # ESLint
npm run type-check     # TypeScript
npm run test           # Jest tests
npm run build          # Production build test
```

---

## Code Architecture

### Backend Architecture

#### Project Structure
```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry
│   ├── core/
│   │   ├── config.py          # Configuration management
│   │   ├── logging.py         # Structured logging setup
│   │   └── pinecone_config.py # Vector DB configuration
│   ├── api/
│   │   └── v1/
│   │       ├── api.py         # Main API router
│   │       ├── health.py      # Health check endpoints
│   │       ├── upload.py      # File upload endpoints
│   │       ├── data.py        # Data processing endpoints
│   │       ├── agents.py      # AI agent endpoints
│   │       └── rag.py         # RAG system endpoints
│   ├── services/
│   │   ├── agent_service.py   # Multi-agent orchestration
│   │   ├── data_service.py    # Data processing logic
│   │   ├── upload_service.py  # File handling logic
│   │   └── rag_service.py     # RAG implementation
│   ├── models/
│   │   ├── agent_models.py    # Agent-related Pydantic models
│   │   ├── data_models.py     # Data processing models
│   │   └── rag_models.py      # RAG system models
│   ├── middleware/
│   │   ├── cors.py           # CORS configuration
│   │   ├── error_handler.py  # Global error handling
│   │   └── request_id.py     # Request tracking
│   └── utils/
│       ├── file_utils.py     # File processing utilities
│       └── validation.py     # Input validation helpers
├── tests/                    # Test suites
├── alembic/                 # Database migrations
├── requirements.txt         # Python dependencies
└── render.yaml             # Deployment configuration
```

#### Key Design Patterns

**Dependency Injection:**
```python
from fastapi import Depends
from app.services.rag_service import get_rag_service, RAGService

@router.post("/search")
async def search(
    request: SearchRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    return await rag_service.semantic_search(request.query)
```

**Service Layer Pattern:**
```python
class RAGService:
    def __init__(self):
        self.embedding_model = None
        self.vector_store = None
    
    async def initialize(self):
        """Initialize service dependencies"""
        
    async def semantic_search(self, query: str) -> SearchResponse:
        """Business logic for semantic search"""
```

**Pydantic Models for Type Safety:**
```python
class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    top_k: int = Field(default=10, ge=1, le=100)
    file_id: Optional[str] = None

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total_results: int
    success: bool
```

### Frontend Architecture

#### Project Structure
```
frontend/
├── src/
│   ├── app/                    # Next.js 14 App Router
│   │   ├── layout.tsx         # Root layout component
│   │   ├── page.tsx           # Home page
│   │   ├── globals.css        # Global styles
│   │   └── (dashboard)/       # Dashboard route group
│   ├── components/
│   │   ├── ui/                # Reusable UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   └── Modal.tsx
│   │   ├── charts/            # Data visualization components
│   │   ├── upload/            # File upload components
│   │   └── agents/            # Agent-specific components
│   ├── hooks/                 # Custom React hooks
│   │   ├── useUpload.ts
│   │   ├── useAgents.ts
│   │   └── useRAG.ts
│   ├── lib/
│   │   ├── api.ts            # API client configuration
│   │   ├── utils.ts          # Utility functions
│   │   └── constants.ts      # Application constants
│   ├── types/                # TypeScript type definitions
│   │   ├── api.ts
│   │   ├── agents.ts
│   │   └── rag.ts
│   └── styles/               # Additional styling
├── public/                   # Static assets
├── package.json
├── next.config.ts
├── tailwind.config.ts
└── vercel.json              # Deployment configuration
```

#### Component Architecture

**Glassmorphism UI Components:**
```tsx
// components/ui/Card.tsx
interface CardProps {
  children: React.ReactNode;
  className?: string;
  glassmorphism?: boolean;
}

export function Card({ children, className, glassmorphism = true }: CardProps) {
  return (
    <div className={cn(
      "rounded-lg border",
      glassmorphism && "backdrop-blur-sm bg-white/10 border-white/20",
      className
    )}>
      {children}
    </div>
  );
}
```

**React Query Integration:**
```tsx
// hooks/useAgents.ts
export function useExecuteAgent() {
  return useMutation({
    mutationFn: (params: AgentExecutionParams) => 
      api.agents.execute(params),
    onSuccess: (data) => {
      queryClient.invalidateQueries(['agents', 'executions']);
    }
  });
}

// Component usage
function AgentInterface() {
  const executeAgent = useExecuteAgent();
  
  const handleExecute = (query: string) => {
    executeAgent.mutate({
      agent_type: 'data_analysis',
      query,
      file_id: selectedFileId
    });
  };
  
  return (
    <div>
      {executeAgent.isLoading && <Spinner />}
      {executeAgent.error && <ErrorMessage />}
      {executeAgent.data && <Results data={executeAgent.data} />}
    </div>
  );
}
```

**D3.js Chart Components:**
```tsx
// components/charts/TrendChart.tsx
export function TrendChart({ data }: { data: TrendData[] }) {
  const svgRef = useRef<SVGSVGElement>(null);
  
  useEffect(() => {
    if (!svgRef.current || !data.length) return;
    
    const svg = d3.select(svgRef.current);
    // D3.js visualization logic
  }, [data]);
  
  return <svg ref={svgRef} className="w-full h-96" />;
}
```

---

## API Development

### Adding New Endpoints

#### 1. Define Pydantic Models
```python
# app/models/new_feature_models.py
class NewFeatureRequest(BaseModel):
    parameter: str = Field(..., description="Required parameter")
    optional_param: Optional[int] = Field(default=None)

class NewFeatureResponse(BaseModel):
    result: str
    success: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

#### 2. Create Service Layer
```python
# app/services/new_feature_service.py
class NewFeatureService:
    async def process_request(self, request: NewFeatureRequest) -> NewFeatureResponse:
        # Business logic here
        result = await self._process_logic(request.parameter)
        return NewFeatureResponse(
            result=result,
            success=True
        )
```

#### 3. Add API Endpoints
```python
# app/api/v1/new_feature.py
router = APIRouter(prefix="/new-feature", tags=["New Feature"])

@router.post("/process", response_model=NewFeatureResponse)
async def process_new_feature(
    request: NewFeatureRequest,
    service: NewFeatureService = Depends(get_new_feature_service)
) -> NewFeatureResponse:
    """Process new feature request"""
    try:
        return await service.process_request(request)
    except Exception as e:
        logger.error(f"New feature processing failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Processing failed: {str(e)}"
        )
```

#### 4. Include in Main Router
```python
# app/api/v1/api.py
from app.api.v1 import new_feature

api_router.include_router(
    new_feature.router,
    tags=["New Feature"]
)
```

### Testing API Endpoints

#### Unit Tests
```python
# tests/test_new_feature.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_new_feature_success():
    response = client.post(
        "/api/v1/new-feature/process",
        json={"parameter": "test_value"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "result" in data

def test_new_feature_validation_error():
    response = client.post(
        "/api/v1/new-feature/process",
        json={}  # Missing required parameter
    )
    assert response.status_code == 422
```

#### Integration Tests
```python
# tests/test_integration.py
@pytest.mark.asyncio
async def test_full_workflow():
    # Test complete workflow from file upload to insights
    file_response = await upload_test_file()
    agent_response = await execute_agent(file_response["file_id"])
    assert agent_response["status"] == "completed"
```

---

## RAG System Development

### Adding New Embedding Models

#### 1. Update RAG Service
```python
# app/services/rag_service.py
class RAGService:
    SUPPORTED_MODELS = {
        "all-MiniLM-L6-v2": 384,
        "all-mpnet-base-v2": 768,
        "text-embedding-ada-002": 1536  # OpenAI
    }
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.embedding_dimension = self.SUPPORTED_MODELS[model_name]
```

#### 2. Add Model Configuration
```python
# app/core/config.py
class Settings(BaseSettings):
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    OPENAI_API_KEY: Optional[str] = None
    
    @validator("EMBEDDING_MODEL")
    def validate_model(cls, v):
        supported = ["all-MiniLM-L6-v2", "all-mpnet-base-v2", "text-embedding-ada-002"]
        if v not in supported:
            raise ValueError(f"Unsupported model: {v}")
        return v
```

### Custom Search Algorithms

#### Implementing Hybrid Search
```python
async def hybrid_search(
    self, 
    query: str, 
    alpha: float = 0.7,  # Vector weight
    top_k: int = 10
) -> SearchResponse:
    """Combine vector and keyword search"""
    
    # Vector search
    vector_results = await self.semantic_search(query, top_k * 2)
    
    # Keyword search
    keyword_results = await self._keyword_search(query, top_k * 2)
    
    # Combine with weighted scoring
    combined_results = self._combine_results(
        vector_results.results,
        keyword_results,
        alpha
    )
    
    return SearchResponse(
        query=query,
        results=combined_results[:top_k],
        search_type="hybrid"
    )
```

---

## Agent System Development

### Creating Custom Agents

#### 1. Define Agent Interface
```python
# app/agents/base_agent.py
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(self, query: str, context: Dict[str, Any]) -> AgentResponse:
        """Execute agent with given query and context"""
        pass
    
    @abstractmethod
    async def validate_input(self, query: str) -> bool:
        """Validate if agent can handle the query"""
        pass
```

#### 2. Implement Custom Agent
```python
# app/agents/custom_agent.py
class CustomAnalysisAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Custom Analysis",
            description="Performs custom business analysis"
        )
    
    async def execute(self, query: str, context: Dict[str, Any]) -> AgentResponse:
        # Custom analysis logic
        results = await self._perform_analysis(query, context)
        
        return AgentResponse(
            agent_name=self.name,
            result=results,
            confidence=0.95,
            execution_time=2.3
        )
    
    async def validate_input(self, query: str) -> bool:
        # Check if query matches agent capabilities
        keywords = ["custom", "analysis", "business"]
        return any(keyword in query.lower() for keyword in keywords)
```

#### 3. Register Agent
```python
# app/services/agent_service.py
class AgentRegistry:
    def __init__(self):
        self.agents = {
            "planning": PlanningAgent(),
            "data_analysis": DataAnalysisAgent(),
            "query": QueryAgent(),
            "insight": InsightAgent(),
            "custom": CustomAnalysisAgent()  # New agent
        }
```

### LangGraph Workflow Integration

#### Define Workflow
```python
# app/workflows/analysis_workflow.py
from langgraph import StateGraph, END

def create_analysis_workflow():
    workflow = StateGraph(AnalysisState)
    
    # Add nodes
    workflow.add_node("planning", planning_agent)
    workflow.add_node("data_analysis", data_analysis_agent)
    workflow.add_node("custom_analysis", custom_analysis_agent)
    workflow.add_node("insight", insight_agent)
    
    # Define edges
    workflow.add_edge("planning", "data_analysis")
    workflow.add_conditional_edges(
        "data_analysis",
        decide_next_agent,
        {
            "custom": "custom_analysis",
            "insight": "insight"
        }
    )
    workflow.add_edge("custom_analysis", "insight")
    workflow.add_edge("insight", END)
    
    return workflow.compile()
```

---

## Frontend Development

### Creating New Components

#### Component Development Pattern
```tsx
// components/NewFeature/NewFeature.tsx
interface NewFeatureProps {
  data: NewFeatureData;
  onAction: (action: string) => void;
  className?: string;
}

export function NewFeature({ data, onAction, className }: NewFeatureProps) {
  const [state, setState] = useState<NewFeatureState>({});
  
  // Custom hook for API integration
  const { mutate: performAction, isLoading } = useNewFeatureAction();
  
  const handleAction = useCallback((action: string) => {
    performAction({ action, data: state });
    onAction(action);
  }, [state, performAction, onAction]);
  
  return (
    <Card className={cn("p-6", className)}>
      <div className="space-y-4">
        {/* Component content */}
      </div>
    </Card>
  );
}

// Export with memo for performance
export default memo(NewFeature);
```

#### Custom Hooks Pattern
```tsx
// hooks/useNewFeature.ts
export function useNewFeature(featureId?: string) {
  // Query for fetching data
  const query = useQuery({
    queryKey: ['newFeature', featureId],
    queryFn: () => api.newFeature.get(featureId),
    enabled: !!featureId
  });
  
  // Mutation for actions
  const mutation = useMutation({
    mutationFn: api.newFeature.update,
    onSuccess: () => {
      queryClient.invalidateQueries(['newFeature']);
    }
  });
  
  return {
    data: query.data,
    isLoading: query.isLoading,
    error: query.error,
    update: mutation.mutate,
    isUpdating: mutation.isLoading
  };
}
```

### State Management

#### React Query Configuration
```tsx
// lib/react-query.ts
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      retry: (failureCount, error) => {
        if (error.status === 404) return false;
        return failureCount < 3;
      }
    },
    mutations: {
      retry: 1
    }
  }
});
```

#### Global State (when needed)
```tsx
// context/AppContext.tsx
interface AppState {
  currentFile: FileData | null;
  activeSession: SessionData | null;
  preferences: UserPreferences;
}

export const AppContext = createContext<AppState | null>(null);

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AppState>(initialState);
  
  return (
    <AppContext.Provider value={state}>
      {children}
    </AppContext.Provider>
  );
}
```

---

## Testing Strategy

### Backend Testing

#### Test Configuration
```python
# tests/conftest.py
@pytest.fixture
async def test_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def test_db():
    # Create test database
    engine = create_engine("sqlite:///test.db")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    
    yield TestingSessionLocal()
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)
```

#### Service Testing
```python
# tests/test_rag_service.py
@pytest.mark.asyncio
async def test_rag_service_embedding_generation():
    service = RAGService()
    await service.initialize()
    
    texts = ["test document", "another test"]
    embeddings = await service.generate_embeddings(texts)
    
    assert len(embeddings) == 2
    assert len(embeddings[0]) == 384  # Embedding dimension
```

### Frontend Testing

#### Component Testing
```tsx
// components/__tests__/NewFeature.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { NewFeature } from '../NewFeature';

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } }
  });
  
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('NewFeature', () => {
  it('renders correctly', () => {
    render(
      <NewFeature data={mockData} onAction={jest.fn()} />,
      { wrapper: createWrapper() }
    );
    
    expect(screen.getByText('New Feature')).toBeInTheDocument();
  });
  
  it('handles user interactions', async () => {
    const onAction = jest.fn();
    render(
      <NewFeature data={mockData} onAction={onAction} />,
      { wrapper: createWrapper() }
    );
    
    fireEvent.click(screen.getByRole('button', { name: 'Action' }));
    await waitFor(() => expect(onAction).toHaveBeenCalled());
  });
});
```

#### E2E Testing
```tsx
// e2e/upload-and-analyze.spec.ts
import { test, expect } from '@playwright/test';

test('complete upload and analysis workflow', async ({ page }) => {
  // Navigate to app
  await page.goto('/');
  
  // Upload file
  await page.setInputFiles('[data-testid="file-upload"]', 'test-data.csv');
  await expect(page.getByText('Upload successful')).toBeVisible();
  
  // Start analysis
  await page.fill('[data-testid="query-input"]', 'Analyze sales trends');
  await page.click('[data-testid="analyze-button"]');
  
  // Wait for results
  await expect(page.getByText('Analysis complete')).toBeVisible({ timeout: 30000 });
  
  // Verify results
  await expect(page.getByTestId('analysis-results')).toBeVisible();
});
```

---

## Performance Optimization

### Backend Optimization

#### Database Query Optimization
```python
# Use SQLAlchemy relationships efficiently
class FileData(Base):
    __tablename__ = "files"
    
    id = Column(String, primary_key=True)
    # ... other columns
    
    # Lazy loading for large datasets
    analysis_results = relationship(
        "AnalysisResult", 
        back_populates="file",
        lazy="select"  # or "dynamic" for very large datasets
    )

# Optimize queries
def get_file_with_results(db: Session, file_id: str):
    return db.query(FileData)\
        .options(joinedload(FileData.analysis_results))\
        .filter(FileData.id == file_id)\
        .first()
```

#### Caching Strategy
```python
# Redis caching for expensive operations
from functools import wraps
import pickle

def cache_result(expiration: int = 3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached = await redis_client.get(cache_key)
            if cached:
                return pickle.loads(cached)
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await redis_client.setex(
                cache_key, 
                expiration, 
                pickle.dumps(result)
            )
            return result
        return wrapper
    return decorator

# Usage
@cache_result(expiration=1800)  # 30 minutes
async def expensive_analysis(data: pd.DataFrame) -> AnalysisResult:
    # Expensive computation here
    pass
```

#### Async Processing
```python
# Background task processing
from celery import Celery

celery_app = Celery('enterprise_insights')

@celery_app.task
def process_large_file(file_id: str):
    # Long-running file processing
    pass

# In API endpoint
@router.post("/upload/process-async")
async def process_file_async(file_id: str):
    task = process_large_file.delay(file_id)
    return {"task_id": task.id, "status": "processing"}
```

### Frontend Optimization

#### Component Optimization
```tsx
// Memo for expensive components
const ExpensiveChart = memo(({ data }: { data: ChartData[] }) => {
  const chartData = useMemo(() => {
    // Expensive data transformation
    return processChartData(data);
  }, [data]);
  
  return <D3Chart data={chartData} />;
});

// Virtual scrolling for large lists
import { FixedSizeList as List } from 'react-window';

function VirtualizedTable({ items }: { items: TableItem[] }) {
  const Row = ({ index, style }: { index: number; style: CSSProperties }) => (
    <div style={style}>
      <TableRow item={items[index]} />
    </div>
  );
  
  return (
    <List
      height={600}
      itemCount={items.length}
      itemSize={50}
      width="100%"
    >
      {Row}
    </List>
  );
}
```

#### Bundle Optimization
```typescript
// next.config.ts
const nextConfig: NextConfig = {
  // Enable SWC minification
  swcMinify: true,
  
  // Optimize images
  images: {
    domains: ['your-cdn.com'],
    formats: ['image/webp', 'image/avif']
  },
  
  // Code splitting
  experimental: {
    optimizePackageImports: ['d3', '@tanstack/react-query']
  },
  
  // Bundle analyzer
  webpack: (config, { dev, isServer }) => {
    if (!dev && !isServer) {
      config.plugins.push(
        new (require('webpack-bundle-analyzer').BundleAnalyzerPlugin)({
          analyzerMode: 'static',
          openAnalyzer: false
        })
      );
    }
    return config;
  }
};
```

---

## Deployment & DevOps

### CI/CD Pipeline

#### GitHub Actions Workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          cd backend
          pytest tests/ -v --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Run tests
        run: |
          cd frontend
          npm run test:ci
          npm run build

  deploy-backend:
    needs: [test-backend, test-frontend]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Render
        run: |
          # Render auto-deploys from main branch
          echo "Backend deployment triggered automatically"

  deploy-frontend:
    needs: [test-backend, test-frontend]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
          vercel-args: '--prod'
          working-directory: frontend
```

### Monitoring & Logging

#### Structured Logging
```python
# app/core/logging.py
import structlog
from pythonjsonlogger import jsonlogger

def setup_logging():
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
```

#### Health Checks
```python
# app/api/v1/health.py
@router.get("/readiness")
async def readiness_check():
    """Kubernetes readiness probe"""
    checks = {
        "database": await check_database(),
        "redis": await check_redis(),
        "pinecone": await check_pinecone(),
        "ollama": await check_ollama()
    }
    
    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if all_healthy else "not_ready",
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

---

## Contributing Guidelines

### Code Style

#### Python (Backend)
```python
# Follow PEP 8 with these additions:
# - Line length: 88 characters (Black default)
# - Type hints required for all public functions
# - Docstrings for all classes and public methods

class ExampleService:
    """Service for handling example operations."""
    
    async def process_data(
        self, 
        data: pd.DataFrame, 
        options: ProcessingOptions
    ) -> ProcessingResult:
        """
        Process data with given options.
        
        Args:
            data: Input DataFrame to process
            options: Processing configuration
            
        Returns:
            ProcessingResult with status and results
            
        Raises:
            ProcessingError: If processing fails
        """
        pass
```

#### TypeScript (Frontend)
```typescript
// Use strict TypeScript configuration
// Prefer interfaces over types for object shapes
// Use const assertions for immutable data

interface ComponentProps {
  readonly data: ReadonlyArray<DataItem>;
  readonly onAction: (action: ActionType) => void;
  readonly className?: string;
}

// Use explicit return types for complex functions
function processData(input: InputData): ProcessedData {
  // Implementation
}

// Prefer named exports
export { ComponentName, useCustomHook, processData };
```

### Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Write Tests First** (TDD approach)
   ```python
   # Write failing test
   def test_new_feature():
       assert new_feature() == expected_result
   
   # Implement feature to make test pass
   ```

3. **Commit with Conventional Commits**
   ```bash
   git commit -m "feat: add new RAG search algorithm"
   git commit -m "fix: resolve memory leak in chart rendering"
   git commit -m "docs: update API documentation for new endpoints"
   ```

4. **Ensure All Checks Pass**
   - Tests pass locally
   - Code formatted and linted
   - Type checking passes
   - Documentation updated

5. **Create Pull Request**
   - Use descriptive title
   - Reference related issues
   - Include screenshots for UI changes
   - Request appropriate reviewers

### Documentation Standards

- **API Changes**: Update OpenAPI schemas
- **New Features**: Add to user guide
- **Architecture Changes**: Update developer docs
- **Configuration**: Update environment setup guide

---

## Troubleshooting

### Common Development Issues

#### Backend Issues
```bash
# Module import errors
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"

# Database connection issues
alembic current  # Check migration status
alembic upgrade head  # Apply migrations

# Pinecone connection issues
python -c "import pinecone; pinecone.init(api_key='your-key')"
```

#### Frontend Issues
```bash
# Clear Next.js cache
rm -rf .next
npm run build

# TypeScript errors
npm run type-check
npx tsc --noEmit

# Package conflicts
rm -rf node_modules package-lock.json
npm install
```

### Performance Debugging

#### Backend Profiling
```python
import cProfile
import pstats

def profile_function():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Your code here
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions
```

#### Frontend Performance
```tsx
// React DevTools Profiler
import { Profiler } from 'react';

function onRenderCallback(id, phase, actualDuration) {
  console.log('Component:', id, 'Phase:', phase, 'Duration:', actualDuration);
}

<Profiler id="MyComponent" onRender={onRenderCallback}>
  <MyComponent />
</Profiler>
```

---

## Additional Resources

### External Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [LangChain Documentation](https://python.langchain.com/)
- [Pinecone Documentation](https://docs.pinecone.io/)

### Tools & Libraries
- **Development**: VS Code, PyCharm, Cursor
- **API Testing**: Postman, Insomnia, httpie
- **Database**: DBeaver, pgAdmin
- **Monitoring**: Datadog, New Relic, Sentry

### Community
- **GitHub Discussions**: For feature requests and questions
- **Discord Server**: Real-time developer chat
- **Documentation Wiki**: Community-contributed guides

---

*This documentation is continuously updated. For the latest version, check the [docs repository](https://github.com/yourorg/enterprise-insights-docs).*
