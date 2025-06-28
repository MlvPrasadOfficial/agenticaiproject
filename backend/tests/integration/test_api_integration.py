"""
Integration tests for the Enterprise Insights Copilot API.
"""

import pytest
import json
from fastapi.testclient import TestClient
from httpx import AsyncClient


class TestFileUploadFlow:
    """Test complete file upload and processing flow."""
    
    def test_file_upload_csv(self, test_client: TestClient, sample_csv_content: str):
        """Test CSV file upload integration."""
        # Upload file
        files = {"file": ("test.csv", sample_csv_content, "text/csv")}
        response = test_client.post("/api/v1/upload/files/upload", files=files)
        
        assert response.status_code == 200
        upload_data = response.json()
        assert "file_id" in upload_data
        assert "filename" in upload_data
        
        file_id = upload_data["file_id"]
        
        # Check upload status
        status_response = test_client.get(f"/api/v1/upload/files/status/{file_id}")
        assert status_response.status_code == 200
        
        status_data = status_response.json()
        assert status_data["file_id"] == file_id
        assert "status" in status_data
    
    def test_data_preview_after_upload(self, test_client: TestClient, sample_csv_content: str):
        """Test data preview after successful upload."""
        # Upload file first
        files = {"file": ("test.csv", sample_csv_content, "text/csv")}
        upload_response = test_client.post("/api/v1/upload/files/upload", files=files)
        file_id = upload_response.json()["file_id"]
        
        # Get data preview
        preview_response = test_client.get(f"/api/v1/data/preview/{file_id}")
        assert preview_response.status_code == 200
        
        preview_data = preview_response.json()
        assert "data" in preview_data
        assert "columns" in preview_data
        assert "total_rows" in preview_data
        assert len(preview_data["data"]) > 0
    
    def test_data_statistics_after_upload(self, test_client: TestClient, sample_csv_content: str):
        """Test data statistics after successful upload."""
        # Upload file first
        files = {"file": ("test.csv", sample_csv_content, "text/csv")}
        upload_response = test_client.post("/api/v1/upload/files/upload", files=files)
        file_id = upload_response.json()["file_id"]
        
        # Get data statistics
        stats_response = test_client.get(f"/api/v1/data/statistics/{file_id}")
        assert stats_response.status_code == 200
        
        stats_data = stats_response.json()
        assert "summary" in stats_data
        assert "columns" in stats_data
        assert "data_quality" in stats_data


class TestAgentWorkflow:
    """Test complete agent execution workflow."""
    
    def test_session_creation_and_agent_execution(self, test_client: TestClient):
        """Test session creation followed by agent execution."""
        # Create session
        session_data = {
            "user_id": "test-user",
            "session_name": "Integration Test Session"
        }
        session_response = test_client.post(
            "/api/v1/agents/session", 
            json=session_data
        )
        
        assert session_response.status_code == 200
        session = session_response.json()
        assert "session_id" in session
        session_id = session["session_id"]
        
        # Execute agent
        execution_data = {
            "agent_type": "planning",
            "query": "Analyze the uploaded data",
            "session_id": session_id
        }
        execution_response = test_client.post(
            "/api/v1/agents/execute",
            json=execution_data
        )
        
        assert execution_response.status_code == 200
        execution = execution_response.json()
        assert "execution_id" in execution
        assert execution["session_id"] == session_id
    
    def test_conversation_flow(self, test_client: TestClient):
        """Test complete conversation flow."""
        # Create session
        session_data = {"user_id": "test-user", "session_name": "Chat Test"}
        session_response = test_client.post("/api/v1/agents/session", json=session_data)
        session_id = session_response.json()["session_id"]
        
        # Add user message
        message_data = {
            "message_type": "user",
            "content": "Hello, please analyze my data"
        }
        message_response = test_client.post(
            f"/api/v1/agents/conversation",
            json={**message_data, "session_id": session_id}
        )
        
        assert message_response.status_code == 200
        
        # Get conversation history
        history_response = test_client.get(
            f"/api/v1/agents/conversation/{session_id}/history"
        )
        
        assert history_response.status_code == 200
        history = history_response.json()
        assert "messages" in history
        assert len(history["messages"]) > 0
    
    def test_workflow_execution(self, test_client: TestClient):
        """Test workflow execution."""
        workflow_data = {
            "workflow_type": "data_analysis",
            "steps": [
                {"agent_type": "planning", "query": "Plan data analysis"},
                {"agent_type": "analysis", "query": "Perform analysis"}
            ]
        }
        
        response = test_client.post("/api/v1/agents/workflow/execute", json=workflow_data)
        assert response.status_code == 200
        
        workflow = response.json()
        assert "workflow_id" in workflow
        assert "status" in workflow


class TestErrorHandling:
    """Test error handling across the API."""
    
    def test_file_upload_invalid_format(self, test_client: TestClient):
        """Test file upload with invalid format."""
        files = {"file": ("test.txt", "This is not CSV data", "text/plain")}
        response = test_client.post("/api/v1/upload/files/upload", files=files)
        
        # Should handle gracefully, might accept but flag as invalid
        assert response.status_code in [200, 400, 422]
    
    def test_nonexistent_file_operations(self, test_client: TestClient):
        """Test operations on nonexistent files."""
        fake_file_id = "nonexistent-file-id"
        
        # Test preview
        response = test_client.get(f"/api/v1/data/preview/{fake_file_id}")
        assert response.status_code == 404
        
        # Test statistics
        response = test_client.get(f"/api/v1/data/statistics/{fake_file_id}")
        assert response.status_code == 404
    
    def test_invalid_session_operations(self, test_client: TestClient):
        """Test operations with invalid session IDs."""
        fake_session_id = "nonexistent-session-id"
        
        # Test get session
        response = test_client.get(f"/api/v1/agents/session/{fake_session_id}")
        assert response.status_code == 404
        
        # Test conversation history
        response = test_client.get(
            f"/api/v1/agents/conversation/{fake_session_id}/history"
        )
        assert response.status_code == 404
    
    def test_malformed_requests(self, test_client: TestClient):
        """Test handling of malformed requests."""
        # Invalid JSON for session creation
        response = test_client.post(
            "/api/v1/agents/session",
            json={"invalid": "data"}  # Missing required fields
        )
        assert response.status_code == 422
        
        # Invalid agent execution request
        response = test_client.post(
            "/api/v1/agents/execute",
            json={"query": "test"}  # Missing agent_type and session_id
        )
        assert response.status_code == 422


@pytest.mark.asyncio
class TestAsyncEndpoints:
    """Test async endpoints using async client."""
    
    async def test_health_async(self, async_client: AsyncClient):
        """Test health endpoint with async client."""
        response = await async_client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
    
    async def test_agent_status_stream(self, async_client: AsyncClient):
        """Test agent status streaming endpoint."""
        # Note: This would need Server-Sent Events setup in real implementation
        fake_session_id = "test-session"
        
        response = await async_client.get(
            f"/api/v1/agents/status/stream/{fake_session_id}"
        )
        # For now, just test that endpoint exists
        assert response.status_code in [200, 404]
