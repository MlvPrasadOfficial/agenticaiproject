# 🤖 LangChain & Agent Workflow
## Enterprise Insights Copilot - AI Agent Implementation

### 🧠 Agent Architecture Overview

The AI system implements a **multi-agent orchestration pattern** using LangChain and LangGraph, where specialized agents collaborate to analyze data and generate insights.

```
AI Agent System
├── 🎯 Planning Agent          # Query analysis & routing
├── 📊 Data Analysis Agent     # Statistical analysis
├── 🔍 Query Agent            # Natural language processing
├── 💡 Insight Agent          # Business insights generation
└── 🔄 Workflow Coordinator   # Agent orchestration
```

---

## 🏗️ LangChain Configuration

### Core Setup
```python
# services/ai_service.py
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from langchain.memory import ConversationBufferWindowMemory
from langchain.agents import AgentType, initialize_agent
from langchain.tools import Tool
from typing import List, Dict, Any, Optional

class AIService:
    def __init__(self, config: AIConfig):
        self.config = config
        self.llm = self._setup_llm()
        self.embeddings = self._setup_embeddings()
        self.memory = self._setup_memory()
        self.vectorstore = self._setup_vectorstore()
        
    def _setup_llm(self) -> ChatOpenAI:
        """Initialize the primary language model."""
        return ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.1,
            max_tokens=2000,
            openai_api_key=self.config.openai_api_key,
            streaming=True,
        )
    
    def _setup_embeddings(self) -> OpenAIEmbeddings:
        """Initialize embeddings for vector search."""
        return OpenAIEmbeddings(
            model="text-embedding-3-large",
            openai_api_key=self.config.openai_api_key
        )
    
    def _setup_memory(self) -> ConversationBufferWindowMemory:
        """Initialize conversation memory."""
        return ConversationBufferWindowMemory(
            k=10,  # Remember last 10 interactions
            memory_key="chat_history",
            return_messages=True
        )
    
    def _setup_vectorstore(self) -> Pinecone:
        """Initialize vector database for RAG."""
        import pinecone
        
        pinecone.init(
            api_key=self.config.pinecone_api_key,
            environment=self.config.pinecone_environment
        )
        
        return Pinecone.from_existing_index(
            index_name="enterprise-insights",
            embedding=self.embeddings
        )
```

### Multi-LLM Router
```python
# services/llm_router.py
from typing import Dict, Any, Optional
from enum import Enum
from langchain.chat_models import ChatOpenAI, ChatAnthropic
from langchain.llms import GooglePalm

class LLMProvider(str, Enum):
    OPENAI_GPT4 = "openai_gpt4"
    CLAUDE_SONNET = "claude_sonnet"
    GEMINI_PRO = "gemini_pro"

class LLMRouter:
    def __init__(self, config: AIConfig):
        self.config = config
        self.models = self._initialize_models()
    
    def _initialize_models(self) -> Dict[LLMProvider, Any]:
        """Initialize all available language models."""
        models = {}
        
        # OpenAI GPT-4
        if self.config.openai_api_key:
            models[LLMProvider.OPENAI_GPT4] = ChatOpenAI(
                model="gpt-4-turbo-preview",
                temperature=0.1,
                openai_api_key=self.config.openai_api_key
            )
        
        # Anthropic Claude
        if self.config.anthropic_api_key:
            models[LLMProvider.CLAUDE_SONNET] = ChatAnthropic(
                model="claude-3-sonnet-20240229",
                temperature=0.1,
                anthropic_api_key=self.config.anthropic_api_key
            )
        
        # Google Gemini
        if self.config.google_api_key:
            models[LLMProvider.GEMINI_PRO] = GooglePalm(
                model="gemini-pro",
                temperature=0.1,
                google_api_key=self.config.google_api_key
            )
        
        return models
    
    def get_model(self, task_type: str, complexity: str = "medium") -> Any:
        """Route to appropriate model based on task requirements."""
        
        # Routing logic based on task type and complexity
        if task_type == "data_analysis" and complexity == "high":
            return self.models.get(LLMProvider.OPENAI_GPT4)
        elif task_type == "reasoning" and complexity == "high":
            return self.models.get(LLMProvider.CLAUDE_SONNET)
        elif task_type == "summarization":
            return self.models.get(LLMProvider.GEMINI_PRO)
        else:
            # Default to GPT-4
            return self.models.get(LLMProvider.OPENAI_GPT4)
    
    async def query_with_fallback(
        self,
        prompt: str,
        primary_model: LLMProvider,
        fallback_models: List[LLMProvider]
    ) -> str:
        """Query with automatic fallback on failure."""
        
        models_to_try = [primary_model] + fallback_models
        
        for model_type in models_to_try:
            try:
                model = self.models.get(model_type)
                if model:
                    response = await model.agenerate([prompt])
                    return response.generations[0][0].text
            except Exception as e:
                logger.warning(f"Model {model_type} failed: {e}")
                continue
        
        raise Exception("All models failed to respond")
```

---

## 🎯 Specialized Agents

### Planning Agent
```python
# agents/planning_agent.py
from langchain.agents import Agent
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from typing import Dict, Any, List

class PlanningAgent:
    def __init__(self, llm, vectorstore):
        self.llm = llm
        self.vectorstore = vectorstore
        self.tools = self._setup_tools()
        
    def _setup_tools(self) -> List[Tool]:
        """Setup tools for the planning agent."""
        return [
            Tool(
                name="query_analyzer",
                description="Analyze user query for intent and complexity",
                func=self._analyze_query
            ),
            Tool(
                name="capability_assessor",
                description="Assess required capabilities for the query",
                func=self._assess_capabilities
            ),
            Tool(
                name="workflow_planner",
                description="Plan workflow for complex queries",
                func=self._plan_workflow
            )
        ]
    
    async def plan_execution(self, user_query: str, data_context: Dict[str, Any]) -> Dict[str, Any]:
        """Plan how to execute the user's query."""
        
        planning_prompt = PromptTemplate(
            input_variables=["query", "data_context"],
            template="""
            As a Planning Agent, analyze this user query and data context to create an execution plan.
            
            User Query: {query}
            Data Context: {data_context}
            
            Please provide:
            1. Query classification (simple/complex, type: analysis/visualization/insight)
            2. Required agents (data_analysis, query, insight)
            3. Execution steps in order
            4. Expected output format
            5. Complexity score (1-10)
            
            Return as structured JSON.
            """
        )
        
        prompt = planning_prompt.format(query=user_query, data_context=data_context)
        response = await self.llm.agenerate([prompt])
        
        return self._parse_plan(response.generations[0][0].text)
    
    def _analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze query intent and complexity."""
        # Implementation for query analysis
        pass
    
    def _assess_capabilities(self, query: str) -> List[str]:
        """Assess what capabilities are needed."""
        # Implementation for capability assessment
        pass
    
    def _plan_workflow(self, query: str, capabilities: List[str]) -> Dict[str, Any]:
        """Plan the execution workflow."""
        # Implementation for workflow planning
        pass
```

### Data Analysis Agent
```python
# agents/data_analysis_agent.py
import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Any, List, Optional
from langchain.tools import Tool

class DataAnalysisAgent:
    def __init__(self, llm):
        self.llm = llm
        self.tools = self._setup_tools()
    
    def _setup_tools(self) -> List[Tool]:
        """Setup data analysis tools."""
        return [
            Tool(
                name="descriptive_statistics",
                description="Calculate descriptive statistics for datasets",
                func=self._calculate_descriptive_stats
            ),
            Tool(
                name="correlation_analysis",
                description="Perform correlation analysis between variables",
                func=self._perform_correlation_analysis
            ),
            Tool(
                name="trend_analysis",
                description="Analyze trends in time series data",
                func=self._analyze_trends
            ),
            Tool(
                name="outlier_detection",
                description="Detect outliers in datasets",
                func=self._detect_outliers
            ),
            Tool(
                name="statistical_tests",
                description="Perform statistical significance tests",
                func=self._perform_statistical_tests
            )
        ]
    
    async def analyze_data(
        self,
        data: pd.DataFrame,
        analysis_type: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform comprehensive data analysis."""
        
        analysis_prompt = PromptTemplate(
            input_variables=["data_summary", "analysis_type", "parameters"],
            template="""
            As a Data Analysis Agent, perform {analysis_type} analysis on this dataset.
            
            Data Summary:
            - Shape: {data_summary[shape]}
            - Columns: {data_summary[columns]}
            - Data Types: {data_summary[dtypes]}
            
            Analysis Parameters: {parameters}
            
            Please provide:
            1. Statistical findings
            2. Key insights
            3. Recommendations
            4. Visualization suggestions
            5. Confidence levels
            
            Focus on actionable business insights.
            """
        )
        
        data_summary = {
            "shape": data.shape,
            "columns": data.columns.tolist(),
            "dtypes": data.dtypes.to_dict()
        }
        
        # Perform actual analysis
        analysis_results = await self._execute_analysis(data, analysis_type, parameters)
        
        # Generate insights using LLM
        prompt = analysis_prompt.format(
            data_summary=data_summary,
            analysis_type=analysis_type,
            parameters=parameters
        )
        
        llm_response = await self.llm.agenerate([prompt])
        insights = self._parse_insights(llm_response.generations[0][0].text)
        
        return {
            "statistical_results": analysis_results,
            "insights": insights,
            "recommendations": self._generate_recommendations(analysis_results)
        }
    
    def _calculate_descriptive_stats(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate comprehensive descriptive statistics."""
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        stats_dict = {}
        for col in numeric_cols:
            stats_dict[col] = {
                "mean": data[col].mean(),
                "median": data[col].median(),
                "std": data[col].std(),
                "min": data[col].min(),
                "max": data[col].max(),
                "skewness": stats.skew(data[col].dropna()),
                "kurtosis": stats.kurtosis(data[col].dropna()),
                "q25": data[col].quantile(0.25),
                "q75": data[col].quantile(0.75),
                "null_count": data[col].isnull().sum(),
                "unique_count": data[col].nunique()
            }
        
        return stats_dict
    
    def _perform_correlation_analysis(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Perform correlation analysis."""
        numeric_data = data.select_dtypes(include=[np.number])
        
        # Pearson correlation
        pearson_corr = numeric_data.corr(method='pearson')
        
        # Spearman correlation
        spearman_corr = numeric_data.corr(method='spearman')
        
        # Find strong correlations
        strong_correlations = []
        for i in range(len(pearson_corr.columns)):
            for j in range(i+1, len(pearson_corr.columns)):
                corr_value = pearson_corr.iloc[i, j]
                if abs(corr_value) > 0.7:  # Strong correlation threshold
                    strong_correlations.append({
                        "variable1": pearson_corr.columns[i],
                        "variable2": pearson_corr.columns[j],
                        "correlation": corr_value,
                        "strength": "strong" if abs(corr_value) > 0.8 else "moderate"
                    })
        
        return {
            "pearson_matrix": pearson_corr.to_dict(),
            "spearman_matrix": spearman_corr.to_dict(),
            "strong_correlations": strong_correlations
        }
```

### Query Agent
```python
# agents/query_agent.py
from langchain.agents import Agent
from langchain.tools import Tool
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from typing import Dict, Any, List

class QueryAgent:
    def __init__(self, llm, vectorstore):
        self.llm = llm
        self.vectorstore = vectorstore
        self.retriever = self._setup_retriever()
        self.tools = self._setup_tools()
    
    def _setup_retriever(self):
        """Setup RAG retriever with compression."""
        base_retriever = self.vectorstore.as_retriever(
            search_type="mmr",  # Maximum Marginal Relevance
            search_kwargs={"k": 10, "fetch_k": 20}
        )
        
        compressor = LLMChainExtractor.from_llm(self.llm)
        
        return ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=base_retriever
        )
    
    async def process_natural_language_query(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process natural language queries about data."""
        
        # Retrieve relevant context
        relevant_docs = await self.retriever.aretrieve_documents(query)
        
        # Build enhanced prompt with context
        enhanced_prompt = f"""
        Query: {query}
        
        Data Context: {context}
        
        Relevant Information:
        {self._format_retrieved_docs(relevant_docs)}
        
        Please provide:
        1. Direct answer to the query
        2. Supporting evidence from the data
        3. Confidence level
        4. Additional insights
        5. Follow-up questions
        """
        
        response = await self.llm.agenerate([enhanced_prompt])
        
        return {
            "answer": response.generations[0][0].text,
            "sources": [doc.metadata for doc in relevant_docs],
            "confidence": self._calculate_confidence(relevant_docs),
            "follow_up_questions": self._generate_follow_ups(query, context)
        }
    
    def _format_retrieved_docs(self, docs: List) -> str:
        """Format retrieved documents for prompt."""
        formatted = []
        for i, doc in enumerate(docs[:5]):  # Limit to top 5
            formatted.append(f"Source {i+1}: {doc.page_content[:500]}...")
        return "\n\n".join(formatted)
```

### Insight Agent
```python
# agents/insight_agent.py
from typing import Dict, Any, List
from langchain.prompts import PromptTemplate

class InsightAgent:
    def __init__(self, llm):
        self.llm = llm
    
    async def generate_business_insights(
        self,
        analysis_results: Dict[str, Any],
        business_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate actionable business insights."""
        
        insight_prompt = PromptTemplate(
            input_variables=["analysis_results", "business_context"],
            template="""
            As a Business Insight Agent, analyze these data findings and generate actionable insights.
            
            Analysis Results: {analysis_results}
            Business Context: {business_context}
            
            Please provide:
            1. Key Business Insights (3-5 main findings)
            2. Action Recommendations (specific, measurable)
            3. Risk Assessments
            4. Opportunity Identification
            5. Success Metrics
            6. Implementation Timeline
            
            Focus on practical, implementable recommendations that drive business value.
            Format as structured output with priorities.
            """
        )
        
        prompt = insight_prompt.format(
            analysis_results=analysis_results,
            business_context=business_context
        )
        
        response = await self.llm.agenerate([prompt])
        insights = self._parse_structured_insights(response.generations[0][0].text)
        
        return {
            "insights": insights,
            "priority_actions": self._prioritize_actions(insights),
            "impact_assessment": self._assess_impact(insights),
            "implementation_roadmap": self._create_roadmap(insights)
        }
    
    def _prioritize_actions(self, insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prioritize recommended actions by impact and feasibility."""
        # Implementation for action prioritization
        pass
    
    def _assess_impact(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """Assess potential business impact of insights."""
        # Implementation for impact assessment
        pass
```

---

## 🔄 LangGraph Workflow Orchestration

### Workflow State Management
```python
# workflows/data_analysis_workflow.py
from langgraph import StateGraph, END
from typing import Dict, Any, List
import asyncio

class DataAnalysisWorkflow:
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the workflow graph."""
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("planning", self._planning_node)
        workflow.add_node("data_analysis", self._data_analysis_node)
        workflow.add_node("query_processing", self._query_processing_node)
        workflow.add_node("insight_generation", self._insight_generation_node)
        workflow.add_node("result_synthesis", self._result_synthesis_node)
        
        # Add edges
        workflow.add_edge("planning", "data_analysis")
        workflow.add_edge("data_analysis", "query_processing")
        workflow.add_edge("query_processing", "insight_generation")
        workflow.add_edge("insight_generation", "result_synthesis")
        workflow.add_edge("result_synthesis", END)
        
        # Set entry point
        workflow.set_entry_point("planning")
        
        return workflow.compile()
    
    async def execute(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the complete workflow."""
        
        state = WorkflowState(**initial_state)
        
        # Execute workflow
        result = await self.graph.ainvoke(state)
        
        return {
            "final_result": result,
            "execution_trace": state.execution_trace,
            "performance_metrics": state.performance_metrics
        }
    
    async def _planning_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Planning node execution."""
        planning_agent = self.ai_service.get_agent("planning")
        
        plan = await planning_agent.plan_execution(
            state.user_query,
            state.data_context
        )
        
        state.execution_plan = plan
        state.execution_trace.append({
            "node": "planning",
            "timestamp": datetime.utcnow(),
            "result": "Plan created successfully"
        })
        
        return {"execution_plan": plan}
    
    async def _data_analysis_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Data analysis node execution."""
        data_agent = self.ai_service.get_agent("data_analysis")
        
        analysis_results = await data_agent.analyze_data(
            state.dataset,
            state.execution_plan["analysis_type"],
            state.execution_plan["parameters"]
        )
        
        state.analysis_results = analysis_results
        state.execution_trace.append({
            "node": "data_analysis",
            "timestamp": datetime.utcnow(),
            "result": "Data analysis completed"
        })
        
        return {"analysis_results": analysis_results}
    
    async def _query_processing_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Query processing node execution."""
        query_agent = self.ai_service.get_agent("query")
        
        query_results = await query_agent.process_natural_language_query(
            state.user_query,
            state.analysis_results
        )
        
        state.query_results = query_results
        state.execution_trace.append({
            "node": "query_processing",
            "timestamp": datetime.utcnow(),
            "result": "Query processed successfully"
        })
        
        return {"query_results": query_results}
    
    async def _insight_generation_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Insight generation node execution."""
        insight_agent = self.ai_service.get_agent("insight")
        
        insights = await insight_agent.generate_business_insights(
            state.analysis_results,
            state.business_context
        )
        
        state.insights = insights
        state.execution_trace.append({
            "node": "insight_generation",
            "timestamp": datetime.utcnow(),
            "result": "Insights generated successfully"
        })
        
        return {"insights": insights}
    
    async def _result_synthesis_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Final result synthesis."""
        
        final_result = {
            "answer": state.query_results["answer"],
            "insights": state.insights,
            "supporting_data": state.analysis_results,
            "confidence": state.query_results["confidence"],
            "recommendations": state.insights["priority_actions"],
            "execution_summary": {
                "total_time": self._calculate_total_time(state.execution_trace),
                "nodes_executed": len(state.execution_trace),
                "success": True
            }
        }
        
        state.final_result = final_result
        
        return {"final_result": final_result}

class WorkflowState:
    def __init__(self, **kwargs):
        self.user_query: str = kwargs.get("user_query", "")
        self.dataset: pd.DataFrame = kwargs.get("dataset")
        self.data_context: Dict[str, Any] = kwargs.get("data_context", {})
        self.business_context: Dict[str, Any] = kwargs.get("business_context", {})
        
        # Workflow state
        self.execution_plan: Dict[str, Any] = {}
        self.analysis_results: Dict[str, Any] = {}
        self.query_results: Dict[str, Any] = {}
        self.insights: Dict[str, Any] = {}
        self.final_result: Dict[str, Any] = {}
        
        # Execution tracking
        self.execution_trace: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, Any] = {}
```

---

## 🔧 Advanced Features

### Parallel Agent Execution
```python
# workflows/parallel_execution.py
import asyncio
from typing import List, Dict, Any

class ParallelExecutor:
    def __init__(self, agents: Dict[str, Any]):
        self.agents = agents
    
    async def execute_parallel_analysis(
        self,
        query: str,
        data: pd.DataFrame,
        analysis_types: List[str]
    ) -> Dict[str, Any]:
        """Execute multiple analysis types in parallel."""
        
        tasks = []
        for analysis_type in analysis_types:
            task = asyncio.create_task(
                self._execute_single_analysis(query, data, analysis_type)
            )
            tasks.append((analysis_type, task))
        
        results = {}
        for analysis_type, task in tasks:
            try:
                result = await task
                results[analysis_type] = result
            except Exception as e:
                results[analysis_type] = {"error": str(e)}
        
        return results
```

### Agent Performance Monitoring
```python
# monitoring/agent_monitor.py
from typing import Dict, Any
import time
from dataclasses import dataclass

@dataclass
class AgentMetrics:
    agent_name: str
    execution_time: float
    success_rate: float
    error_count: int
    total_executions: int

class AgentMonitor:
    def __init__(self):
        self.metrics: Dict[str, AgentMetrics] = {}
    
    async def track_execution(self, agent_name: str, func, *args, **kwargs):
        """Track agent execution with metrics."""
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            self._update_metrics(agent_name, execution_time, True)
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._update_metrics(agent_name, execution_time, False)
            raise e
    
    def _update_metrics(self, agent_name: str, execution_time: float, success: bool):
        """Update agent performance metrics."""
        if agent_name not in self.metrics:
            self.metrics[agent_name] = AgentMetrics(
                agent_name=agent_name,
                execution_time=0,
                success_rate=0,
                error_count=0,
                total_executions=0
            )
        
        metrics = self.metrics[agent_name]
        metrics.total_executions += 1
        
        if success:
            # Update success rate
            metrics.success_rate = (
                metrics.success_rate * (metrics.total_executions - 1) + 1
            ) / metrics.total_executions
        else:
            metrics.error_count += 1
            metrics.success_rate = (
                metrics.success_rate * (metrics.total_executions - 1)
            ) / metrics.total_executions
        
        # Update average execution time
        metrics.execution_time = (
            metrics.execution_time * (metrics.total_executions - 1) + execution_time
        ) / metrics.total_executions
```

---

This LangChain and agent workflow implementation provides a robust, scalable AI system capable of complex data analysis and insight generation through coordinated multi-agent orchestration.
