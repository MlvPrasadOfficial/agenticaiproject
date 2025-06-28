"""
Unit tests for backend API health endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_health_endpoint(self, test_client: TestClient):
        """Test basic health endpoint."""
        response = test_client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
    
    def test_readiness_endpoint(self, test_client: TestClient):
        """Test readiness endpoint."""
        response = test_client.get("/api/v1/readiness")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "checks" in data
        assert isinstance(data["checks"], dict)
    
    def test_liveness_endpoint(self, test_client: TestClient):
        """Test liveness endpoint."""
        response = test_client.get("/api/v1/liveness")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "alive"


class TestDataProcessingUtils:
    """Test data processing utility functions."""
    
    def test_detect_file_type_csv(self):
        """Test CSV file type detection."""
        from app.services.data_processor import detect_file_type
        
        content = "name,age,city\nJohn,30,NYC\nJane,25,LA"
        file_type = detect_file_type("test.csv", content.encode())
        assert file_type == "csv"
    
    def test_detect_file_type_json(self):
        """Test JSON file type detection."""
        from app.services.data_processor import detect_file_type
        
        content = '{"users": [{"name": "John", "age": 30}]}'
        file_type = detect_file_type("test.json", content.encode())
        assert file_type == "json"
    
    def test_validate_csv_structure(self):
        """Test CSV structure validation."""
        from app.services.data_processor import validate_csv_structure
        
        content = "name,age,city\nJohn,30,NYC\nJane,25,LA"
        is_valid, errors = validate_csv_structure(content)
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_csv_structure_invalid(self):
        """Test CSV structure validation with invalid data."""
        from app.services.data_processor import validate_csv_structure
        
        content = "name,age,city\nJohn,thirty,NYC\nJane,25"  # Missing column
        is_valid, errors = validate_csv_structure(content)
        assert not is_valid
        assert len(errors) > 0


class TestAgentManager:
    """Test agent manager functionality."""
    
    @pytest.fixture
    def agent_manager(self):
        """Create agent manager instance."""
        from app.services.agent_manager import AgentManager
        return AgentManager()
    
    def test_create_execution(self, agent_manager, mock_session_id):
        """Test agent execution creation."""
        execution = agent_manager.create_execution(
            agent_type="planning",
            query="Test query",
            session_id=mock_session_id
        )
        
        assert execution["execution_id"]
        assert execution["agent_type"] == "planning"
        assert execution["query"] == "Test query"
        assert execution["session_id"] == mock_session_id
        assert execution["status"] == "pending"
    
    def test_get_execution_status(self, agent_manager, mock_execution_id):
        """Test getting execution status."""
        # First create an execution
        execution = agent_manager.create_execution(
            agent_type="analysis", 
            query="Test", 
            session_id="test-session"
        )
        
        # Then get its status
        status = agent_manager.get_execution_status(execution["execution_id"])
        assert status["execution_id"] == execution["execution_id"]
        assert "status" in status
        assert "created_at" in status


class TestSessionManager:
    """Test session manager functionality."""
    
    @pytest.fixture
    def session_manager(self):
        """Create session manager instance."""
        from app.services.session_manager import SessionManager
        return SessionManager()
    
    def test_create_session(self, session_manager):
        """Test session creation."""
        session = session_manager.create_session(
            user_id="test-user",
            session_name="Test Session"
        )
        
        assert session["session_id"]
        assert session["user_id"] == "test-user"
        assert session["session_name"] == "Test Session"
        assert "created_at" in session
    
    def test_get_session(self, session_manager):
        """Test getting session by ID."""
        # Create a session first
        created_session = session_manager.create_session(
            user_id="test-user",
            session_name="Test Session"
        )
        
        # Then retrieve it
        session = session_manager.get_session(created_session["session_id"])
        assert session is not None
        assert session["session_id"] == created_session["session_id"]
    
    def test_list_sessions(self, session_manager):
        """Test listing sessions."""
        # Create a few sessions
        session_manager.create_session("user1", "Session 1")
        session_manager.create_session("user1", "Session 2")
        
        sessions = session_manager.list_sessions(user_id="user1")
        assert len(sessions) >= 2
        assert all("session_id" in s for s in sessions)


class TestConversationManager:
    """Test conversation manager functionality."""
    
    @pytest.fixture
    def conversation_manager(self):
        """Create conversation manager instance."""
        from app.services.conversation_manager import ConversationManager
        return ConversationManager()
    
    def test_add_message(self, conversation_manager, mock_session_id):
        """Test adding message to conversation."""
        message = conversation_manager.add_message(
            session_id=mock_session_id,
            message_type="user",
            content="Hello, AI!"
        )
        
        assert message["message_id"]
        assert message["session_id"] == mock_session_id
        assert message["message_type"] == "user"
        assert message["content"] == "Hello, AI!"
        assert "timestamp" in message
    
    def test_get_conversation_history(self, conversation_manager, mock_session_id):
        """Test getting conversation history."""
        # Add a few messages
        conversation_manager.add_message(mock_session_id, "user", "Hello")
        conversation_manager.add_message(mock_session_id, "assistant", "Hi there!")
        
        history = conversation_manager.get_conversation_history(mock_session_id)
        assert len(history) >= 2
        assert all("message_id" in msg for msg in history)
        assert all("timestamp" in msg for msg in history)
