"""
Agent Capability Assessment System
Task 106: Create agent capability assessment system
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Set, Callable
from datetime import datetime, timezone, timedelta
from enum import Enum
from dataclasses import dataclass, field
from uuid import uuid4
import json
import statistics
from collections import defaultdict

logger = logging.getLogger(__name__)


class CapabilityType(str, Enum):
    """Types of agent capabilities"""
    DATA_ANALYSIS = "data_analysis"
    DATA_VISUALIZATION = "data_visualization"
    FILE_PROCESSING = "file_processing"
    NATURAL_LANGUAGE = "natural_language"
    MATHEMATICAL_COMPUTATION = "mathematical_computation"
    STATISTICAL_ANALYSIS = "statistical_analysis"
    MACHINE_LEARNING = "machine_learning"
    DATABASE_OPERATIONS = "database_operations"
    REPORT_GENERATION = "report_generation"
    CODE_GENERATION = "code_generation"
    PROBLEM_SOLVING = "problem_solving"
    REASONING = "reasoning"
    PLANNING = "planning"
    COLLABORATION = "collaboration"
    ERROR_RECOVERY = "error_recovery"
    ADAPTATION = "adaptation"


class CapabilityLevel(str, Enum):
    """Capability proficiency levels"""
    NOVICE = "novice"          # 0-20%
    BEGINNER = "beginner"      # 20-40%
    INTERMEDIATE = "intermediate"  # 40-60%
    ADVANCED = "advanced"      # 60-80%
    EXPERT = "expert"          # 80-100%


class AssessmentMethod(str, Enum):
    """Methods for capability assessment"""
    SELF_ASSESSMENT = "self_assessment"
    PERFORMANCE_BASED = "performance_based"
    USER_FEEDBACK = "user_feedback"
    PEER_EVALUATION = "peer_evaluation"
    BENCHMARK_TEST = "benchmark_test"
    TASK_COMPLETION = "task_completion"
    ERROR_ANALYSIS = "error_analysis"


@dataclass
class CapabilityMetric:
    """Individual capability metric"""
    name: str
    description: str
    weight: float = 1.0  # Importance weight
    min_value: float = 0.0
    max_value: float = 1.0
    current_value: float = 0.0
    historical_values: List[float] = field(default_factory=list)
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def update_value(self, value: float):
        """Update metric value"""
        self.current_value = max(self.min_value, min(self.max_value, value))
        self.historical_values.append(self.current_value)
        self.last_updated = datetime.now(timezone.utc)
        
        # Keep last 100 values
        if len(self.historical_values) > 100:
            self.historical_values = self.historical_values[-100:]
    
    def get_trend(self) -> str:
        """Get trend direction"""
        if len(self.historical_values) < 2:
            return "stable"
        
        recent = self.historical_values[-5:]  # Last 5 values
        if len(recent) < 2:
            return "stable"
        
        avg_recent = statistics.mean(recent)
        avg_older = statistics.mean(self.historical_values[:-5]) if len(self.historical_values) > 5 else avg_recent
        
        if avg_recent > avg_older * 1.1:
            return "improving"
        elif avg_recent < avg_older * 0.9:
            return "declining"
        else:
            return "stable"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "weight": self.weight,
            "current_value": self.current_value,
            "trend": self.get_trend(),
            "last_updated": self.last_updated.isoformat(),
            "historical_count": len(self.historical_values)
        }


@dataclass
class Capability:
    """Agent capability definition"""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    type: CapabilityType = CapabilityType.DATA_ANALYSIS
    description: str = ""
    
    # Capability assessment
    current_level: CapabilityLevel = CapabilityLevel.NOVICE
    confidence_score: float = 0.0  # 0.0 to 1.0
    
    # Metrics
    metrics: Dict[str, CapabilityMetric] = field(default_factory=dict)
    
    # Requirements and dependencies
    prerequisites: List[str] = field(default_factory=list)  # Other capability IDs
    dependent_capabilities: List[str] = field(default_factory=list)
    
    # Assessment history
    assessment_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_assessed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def calculate_overall_score(self) -> float:
        """Calculate overall capability score from metrics"""
        if not self.metrics:
            return 0.0
        
        total_weight = sum(metric.weight for metric in self.metrics.values())
        if total_weight == 0:
            return 0.0
        
        weighted_sum = sum(
            metric.current_value * metric.weight 
            for metric in self.metrics.values()
        )
        
        return weighted_sum / total_weight
    
    def update_level_from_score(self):
        """Update capability level based on overall score"""
        score = self.calculate_overall_score()
        
        if score >= 0.8:
            self.current_level = CapabilityLevel.EXPERT
        elif score >= 0.6:
            self.current_level = CapabilityLevel.ADVANCED
        elif score >= 0.4:
            self.current_level = CapabilityLevel.INTERMEDIATE
        elif score >= 0.2:
            self.current_level = CapabilityLevel.BEGINNER
        else:
            self.current_level = CapabilityLevel.NOVICE
    
    def add_metric(self, metric: CapabilityMetric):
        """Add a metric to this capability"""
        self.metrics[metric.name] = metric
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "description": self.description,
            "current_level": self.current_level.value,
            "confidence_score": self.confidence_score,
            "overall_score": self.calculate_overall_score(),
            "metrics": {name: metric.to_dict() for name, metric in self.metrics.items()},
            "prerequisites": self.prerequisites,
            "dependent_capabilities": self.dependent_capabilities,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "last_assessed": self.last_assessed.isoformat()
        }


@dataclass
class CapabilityAssessment:
    """Assessment result for a capability"""
    capability_id: str
    agent_id: str
    assessment_id: str = field(default_factory=lambda: str(uuid4()))
    
    # Assessment details
    method: AssessmentMethod = AssessmentMethod.PERFORMANCE_BASED
    assessor: str = "system"  # Who performed the assessment
    
    # Results
    score: float = 0.0  # 0.0 to 1.0
    level: CapabilityLevel = CapabilityLevel.NOVICE
    confidence: float = 0.0
    
    # Evidence
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    metrics_evaluated: Dict[str, float] = field(default_factory=dict)
    
    # Context
    assessment_context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Recommendations
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "agent_id": self.agent_id,
            "assessment_id": self.assessment_id,
            "method": self.method.value,
            "assessor": self.assessor,
            "score": self.score,
            "level": self.level.value,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "metrics_evaluated": self.metrics_evaluated,
            "assessment_context": self.assessment_context,
            "timestamp": self.timestamp.isoformat(),
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "improvement_suggestions": self.improvement_suggestions
        }


class CapabilityAssessor:
    """Base class for capability assessors"""
    
    def __init__(self, name: str, method: AssessmentMethod):
        self.name = name
        self.method = method
    
    async def assess_capability(
        self, 
        agent_id: str, 
        capability: Capability, 
        context: Dict[str, Any]
    ) -> CapabilityAssessment:
        """Assess a capability - to be implemented by subclasses"""
        raise NotImplementedError


class PerformanceBasedAssessor(CapabilityAssessor):
    """Assess capabilities based on performance metrics"""
    
    def __init__(self):
        super().__init__("Performance Assessor", AssessmentMethod.PERFORMANCE_BASED)
    
    async def assess_capability(
        self, 
        agent_id: str, 
        capability: Capability, 
        context: Dict[str, Any]
    ) -> CapabilityAssessment:
        """Assess capability based on performance data"""
        assessment = CapabilityAssessment(
            capability_id=capability.id,
            agent_id=agent_id,
            method=self.method,
            assessor=self.name,
            assessment_context=context
        )
        
        # Evaluate each metric
        total_score = 0.0
        total_weight = 0.0
        evidence = []
        
        for metric_name, metric in capability.metrics.items():
            score = metric.current_value
            weight = metric.weight
            
            total_score += score * weight
            total_weight += weight
            
            assessment.metrics_evaluated[metric_name] = score
            
            # Add evidence
            evidence.append({
                "metric": metric_name,
                "value": score,
                "trend": metric.get_trend(),
                "description": metric.description
            })
        
        # Calculate overall score
        if total_weight > 0:
            assessment.score = total_score / total_weight
        
        # Determine level
        assessment.level = self._score_to_level(assessment.score)
        
        # Set confidence based on data availability
        assessment.confidence = min(1.0, len(capability.metrics) * 0.2)
        
        assessment.evidence = evidence
        
        # Generate recommendations
        self._generate_recommendations(assessment, capability)
        
        return assessment
    
    def _score_to_level(self, score: float) -> CapabilityLevel:
        """Convert score to capability level"""
        if score >= 0.8:
            return CapabilityLevel.EXPERT
        elif score >= 0.6:
            return CapabilityLevel.ADVANCED
        elif score >= 0.4:
            return CapabilityLevel.INTERMEDIATE
        elif score >= 0.2:
            return CapabilityLevel.BEGINNER
        else:
            return CapabilityLevel.NOVICE
    
    def _generate_recommendations(self, assessment: CapabilityAssessment, capability: Capability):
        """Generate improvement recommendations"""
        score = assessment.score
        
        # Identify strengths and weaknesses
        for metric_name, metric_score in assessment.metrics_evaluated.items():
            if metric_score >= 0.7:
                assessment.strengths.append(f"Strong performance in {metric_name}")
            elif metric_score <= 0.3:
                assessment.weaknesses.append(f"Needs improvement in {metric_name}")
        
        # General recommendations based on level
        if assessment.level == CapabilityLevel.NOVICE:
            assessment.improvement_suggestions.extend([
                "Focus on building foundational skills",
                "Practice with simpler tasks",
                "Seek guidance and training"
            ])
        elif assessment.level == CapabilityLevel.BEGINNER:
            assessment.improvement_suggestions.extend([
                "Gradually increase task complexity",
                "Build consistency in performance",
                "Learn from mistakes and feedback"
            ])
        elif assessment.level == CapabilityLevel.INTERMEDIATE:
            assessment.improvement_suggestions.extend([
                "Tackle more challenging problems",
                "Develop specialized techniques",
                "Share knowledge with others"
            ])


class TaskCompletionAssessor(CapabilityAssessor):
    """Assess capabilities based on task completion success"""
    
    def __init__(self):
        super().__init__("Task Completion Assessor", AssessmentMethod.TASK_COMPLETION)
    
    async def assess_capability(
        self, 
        agent_id: str, 
        capability: Capability, 
        context: Dict[str, Any]
    ) -> CapabilityAssessment:
        """Assess capability based on task completion data"""
        assessment = CapabilityAssessment(
            capability_id=capability.id,
            agent_id=agent_id,
            method=self.method,
            assessor=self.name,
            assessment_context=context
        )
        
        # Extract task completion data from context
        completed_tasks = context.get("completed_tasks", [])
        failed_tasks = context.get("failed_tasks", [])
        
        if not completed_tasks and not failed_tasks:
            assessment.confidence = 0.0
            return assessment
        
        total_tasks = len(completed_tasks) + len(failed_tasks)
        success_rate = len(completed_tasks) / total_tasks if total_tasks > 0 else 0.0
        
        # Calculate average completion time and quality
        avg_completion_time = 0.0
        avg_quality_score = 0.0
        
        if completed_tasks:
            completion_times = [task.get("completion_time", 0) for task in completed_tasks]
            quality_scores = [task.get("quality_score", 0.5) for task in completed_tasks]
            
            avg_completion_time = statistics.mean(completion_times)
            avg_quality_score = statistics.mean(quality_scores)
        
        # Calculate overall score
        assessment.score = (success_rate * 0.5) + (avg_quality_score * 0.3) + (
            max(0, 1 - avg_completion_time / 3600) * 0.2  # Penalty for long completion times
        )
        
        assessment.level = self._score_to_level(assessment.score)
        assessment.confidence = min(1.0, total_tasks * 0.1)  # Higher confidence with more data
        
        # Add evidence
        assessment.evidence = [
            {"type": "success_rate", "value": success_rate, "description": f"Completed {len(completed_tasks)}/{total_tasks} tasks"},
            {"type": "avg_quality", "value": avg_quality_score, "description": f"Average quality score: {avg_quality_score:.2f}"},
            {"type": "avg_time", "value": avg_completion_time, "description": f"Average completion time: {avg_completion_time:.1f}s"}
        ]
        
        return assessment
    
    def _score_to_level(self, score: float) -> CapabilityLevel:
        """Convert score to capability level"""
        if score >= 0.8:
            return CapabilityLevel.EXPERT
        elif score >= 0.6:
            return CapabilityLevel.ADVANCED
        elif score >= 0.4:
            return CapabilityLevel.INTERMEDIATE
        elif score >= 0.2:
            return CapabilityLevel.BEGINNER
        else:
            return CapabilityLevel.NOVICE


class CapabilityManager:
    """Main capability management system"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.capabilities: Dict[str, Capability] = {}
        self.assessors: Dict[AssessmentMethod, CapabilityAssessor] = {}
        self.assessment_history: List[CapabilityAssessment] = []
        
        # Initialize default assessors
        self.assessors[AssessmentMethod.PERFORMANCE_BASED] = PerformanceBasedAssessor()
        self.assessors[AssessmentMethod.TASK_COMPLETION] = TaskCompletionAssessor()
        
        # Initialize default capabilities
        self._initialize_default_capabilities()
    
    def _initialize_default_capabilities(self):
        """Initialize default capabilities for Enterprise Insights"""
        default_capabilities = [
            {
                "name": "Data Analysis",
                "type": CapabilityType.DATA_ANALYSIS,
                "description": "Ability to analyze and interpret data",
                "metrics": {
                    "accuracy": CapabilityMetric("accuracy", "Accuracy of analysis results", 1.0),
                    "speed": CapabilityMetric("speed", "Speed of analysis completion", 0.8),
                    "complexity": CapabilityMetric("complexity", "Ability to handle complex datasets", 1.2)
                }
            },
            {
                "name": "Data Visualization",
                "type": CapabilityType.DATA_VISUALIZATION,
                "description": "Ability to create effective visualizations",
                "metrics": {
                    "chart_quality": CapabilityMetric("chart_quality", "Quality of generated charts", 1.0),
                    "appropriateness": CapabilityMetric("appropriateness", "Appropriate chart type selection", 1.1),
                    "aesthetics": CapabilityMetric("aesthetics", "Visual appeal and clarity", 0.8)
                }
            },
            {
                "name": "Natural Language Processing",
                "type": CapabilityType.NATURAL_LANGUAGE,
                "description": "Ability to understand and generate natural language",
                "metrics": {
                    "comprehension": CapabilityMetric("comprehension", "Understanding of user queries", 1.2),
                    "response_quality": CapabilityMetric("response_quality", "Quality of generated responses", 1.0),
                    "context_awareness": CapabilityMetric("context_awareness", "Awareness of conversation context", 1.1)
                }
            },
            {
                "name": "Statistical Analysis",
                "type": CapabilityType.STATISTICAL_ANALYSIS,
                "description": "Ability to perform statistical analysis",
                "metrics": {
                    "test_selection": CapabilityMetric("test_selection", "Appropriate statistical test selection", 1.0),
                    "interpretation": CapabilityMetric("interpretation", "Correct interpretation of results", 1.2),
                    "significance": CapabilityMetric("significance", "Understanding of statistical significance", 1.0)
                }
            },
            {
                "name": "Problem Solving",
                "type": CapabilityType.PROBLEM_SOLVING,
                "description": "Ability to solve complex problems",
                "metrics": {
                    "decomposition": CapabilityMetric("decomposition", "Breaking down complex problems", 1.0),
                    "solution_quality": CapabilityMetric("solution_quality", "Quality of proposed solutions", 1.2),
                    "creativity": CapabilityMetric("creativity", "Creative problem-solving approaches", 0.9)
                }
            }
        ]
        
        for cap_def in default_capabilities:
            capability = Capability(
                name=cap_def["name"],
                type=cap_def["type"],
                description=cap_def["description"]
            )
            
            for metric_name, metric in cap_def["metrics"].items():
                capability.add_metric(metric)
            
            self.capabilities[capability.id] = capability
    
    def get_capability(self, capability_id: str) -> Optional[Capability]:
        """Get capability by ID"""
        return self.capabilities.get(capability_id)
    
    def get_capability_by_name(self, name: str) -> Optional[Capability]:
        """Get capability by name"""
        for capability in self.capabilities.values():
            if capability.name.lower() == name.lower():
                return capability
        return None
    
    def get_capabilities_by_type(self, capability_type: CapabilityType) -> List[Capability]:
        """Get capabilities by type"""
        return [cap for cap in self.capabilities.values() if cap.type == capability_type]
    
    def add_capability(self, capability: Capability) -> str:
        """Add new capability"""
        self.capabilities[capability.id] = capability
        return capability.id
    
    def update_metric(
        self, 
        capability_id: str, 
        metric_name: str, 
        value: float
    ) -> bool:
        """Update capability metric"""
        capability = self.capabilities.get(capability_id)
        if not capability:
            return False
        
        metric = capability.metrics.get(metric_name)
        if not metric:
            return False
        
        metric.update_value(value)
        capability.update_level_from_score()
        capability.last_assessed = datetime.now(timezone.utc)
        
        return True
    
    async def assess_capability(
        self, 
        capability_id: str, 
        method: AssessmentMethod = AssessmentMethod.PERFORMANCE_BASED,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[CapabilityAssessment]:
        """Assess a specific capability"""
        capability = self.capabilities.get(capability_id)
        if not capability:
            logger.error(f"Capability {capability_id} not found")
            return None
        
        assessor = self.assessors.get(method)
        if not assessor:
            logger.error(f"No assessor found for method {method}")
            return None
        
        assessment = await assessor.assess_capability(
            self.agent_id, 
            capability, 
            context or {}
        )
        
        # Update capability with assessment results
        capability.confidence_score = assessment.confidence
        capability.last_assessed = assessment.timestamp
        capability.assessment_history.append(assessment.to_dict())
        
        # Keep last 50 assessments
        if len(capability.assessment_history) > 50:
            capability.assessment_history = capability.assessment_history[-50:]
        
        # Store assessment
        self.assessment_history.append(assessment)
        
        logger.info(f"Assessed capability {capability.name}: {assessment.level.value} (score: {assessment.score:.2f})")
        
        return assessment
    
    async def assess_all_capabilities(
        self, 
        method: AssessmentMethod = AssessmentMethod.PERFORMANCE_BASED,
        context: Optional[Dict[str, Any]] = None
    ) -> List[CapabilityAssessment]:
        """Assess all capabilities"""
        assessments = []
        
        for capability_id in self.capabilities.keys():
            assessment = await self.assess_capability(capability_id, method, context)
            if assessment:
                assessments.append(assessment)
        
        return assessments
    
    def get_capability_summary(self) -> Dict[str, Any]:
        """Get summary of all capabilities"""
        summary = {
            "agent_id": self.agent_id,
            "total_capabilities": len(self.capabilities),
            "capability_breakdown": defaultdict(int),
            "level_distribution": defaultdict(int),
            "average_scores": {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        total_score = 0.0
        total_confidence = 0.0
        
        for capability in self.capabilities.values():
            # Count by type
            summary["capability_breakdown"][capability.type.value] += 1
            
            # Count by level
            summary["level_distribution"][capability.current_level.value] += 1
            
            # Calculate averages
            score = capability.calculate_overall_score()
            total_score += score
            total_confidence += capability.confidence_score
            
            summary["average_scores"][capability.name] = {
                "score": score,
                "level": capability.current_level.value,
                "confidence": capability.confidence_score
            }
        
        if self.capabilities:
            summary["overall_average_score"] = total_score / len(self.capabilities)
            summary["overall_average_confidence"] = total_confidence / len(self.capabilities)
        
        return summary
    
    def get_strengths_and_weaknesses(self) -> Dict[str, List[str]]:
        """Identify agent's strengths and weaknesses"""
        strengths = []
        weaknesses = []
        
        for capability in self.capabilities.values():
            score = capability.calculate_overall_score()
            
            if score >= 0.7 and capability.current_level in [CapabilityLevel.ADVANCED, CapabilityLevel.EXPERT]:
                strengths.append(capability.name)
            elif score <= 0.3 or capability.current_level == CapabilityLevel.NOVICE:
                weaknesses.append(capability.name)
        
        return {
            "strengths": strengths,
            "weaknesses": weaknesses
        }
    
    def get_improvement_plan(self) -> List[Dict[str, Any]]:
        """Generate improvement plan based on assessments"""
        plan = []
        
        # Identify capabilities that need improvement
        for capability in self.capabilities.values():
            score = capability.calculate_overall_score()
            
            if score < 0.6:  # Below advanced level
                # Find specific metrics that need improvement
                weak_metrics = [
                    metric_name for metric_name, metric in capability.metrics.items()
                    if metric.current_value < 0.5
                ]
                
                plan.append({
                    "capability": capability.name,
                    "current_level": capability.current_level.value,
                    "current_score": score,
                    "target_level": "advanced",
                    "weak_metrics": weak_metrics,
                    "priority": "high" if score < 0.3 else "medium",
                    "estimated_effort": "high" if len(weak_metrics) > 2 else "medium"
                })
        
        # Sort by priority and score
        plan.sort(key=lambda x: (x["priority"] == "high", -x["current_score"]))
        
        return plan


# Global capability managers
_capability_managers: Dict[str, CapabilityManager] = {}


def get_capability_manager(agent_id: str) -> CapabilityManager:
    """Get or create capability manager for an agent"""
    if agent_id not in _capability_managers:
        _capability_managers[agent_id] = CapabilityManager(agent_id)
    return _capability_managers[agent_id]


async def assess_agent_capabilities(
    agent_id: str, 
    method: AssessmentMethod = AssessmentMethod.PERFORMANCE_BASED,
    context: Optional[Dict[str, Any]] = None
) -> List[CapabilityAssessment]:
    """Assess all capabilities for an agent"""
    manager = get_capability_manager(agent_id)
    return await manager.assess_all_capabilities(method, context)


def get_agent_capability_summary(agent_id: str) -> Dict[str, Any]:
    """Get capability summary for an agent"""
    manager = get_capability_manager(agent_id)
    return manager.get_capability_summary()


def update_agent_capability_metric(
    agent_id: str, 
    capability_name: str, 
    metric_name: str, 
    value: float
) -> bool:
    """Update a capability metric for an agent"""
    manager = get_capability_manager(agent_id)
    capability = manager.get_capability_by_name(capability_name)
    
    if not capability:
        logger.warning(f"Capability {capability_name} not found for agent {agent_id}")
        return False
    
    return manager.update_metric(capability.id, metric_name, value)
