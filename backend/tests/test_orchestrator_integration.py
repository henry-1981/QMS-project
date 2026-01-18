import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import json
from app.agents.orchestrator import orchestrator
from app.agents.base_agent import AgentState, BaseAgent
from app.db.models import DesignProject, DesignChange, User, RiskItem
from app.services.vector_db_service import vector_db_service
from app.services.gdrive_service import gdrive_service
from app.agents.design_engineer_agent import design_engineer_agent
from app.agents.pm_agent import pm_agent
from app.agents.risk_manager_agent import risk_manager_agent
from app.agents.ra_agent import ra_agent
from app.agents.verification_agent import verification_agent
from app.agents.qa_agent import qa_agent

# Mock Response class for LLM
class MockLLMResponse:
    def __init__(self, content):
        self.content = content

@pytest_asyncio.fixture
async def setup_test_data(db_session, test_user_data, test_project_data, test_change_data):
    # Create User
    user_data = test_user_data.copy()
    if "password" in user_data:
        user_data["password_hash"] = user_data.pop("password")
        
    user = User(**user_data)
    db_session.add(user)
    db_session.commit() # Commit to get ID
    db_session.refresh(user)

    # Create Project
    project_data = test_project_data.copy()
    project_data["created_by"] = user.id
    project = DesignProject(**project_data)
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    # Create Change
    change_data = test_change_data.copy()
    change_data["project_id"] = project.id
    change_data["created_by"] = user.id
    change_data["change_number"] = "CN-2024-001"
    change = DesignChange(**change_data)
    db_session.add(change)
    db_session.commit()
    db_session.refresh(change)
    
    # Create Risk Item (so RiskManager has something to do)
    risk = RiskItem(
        risk_number="R001",
        project_id=project.id,
        hazard="Electric Shock",
        severity=5,
        probability=2,
        risk_level="Medium"
    )
    db_session.add(risk)
    db_session.commit()
    
    return change

@pytest.mark.asyncio
async def test_full_orchestrator_workflow(db_session, setup_test_data):
    change = setup_test_data
    
    # Generic Mock LLM response that satisfies most agents (returning JSON)
    # We construct a superset of keys expected by different agents
    mock_json_response = json.dumps({
        # Common
        "status": "ok", 
        "recommendations": ["Recommendation 1", "Recommendation 2"],
        "findings": {"key": "value"},
        
        # Design Engineer
        "impact_analysis": {"affected_docs": []},
        
        # PM
        "schedule_impact": {},
        "resource_allocation": {},
        "dependencies": {},
        "risk_factors": {},
        "priority_assessment": "medium",
        "comments": "Proceed",
        
        # Risk
        "reassessed_risks": [],
        "new_risks": [],
        "risk_categories": {},
        "priority_risks": [],
        
        # RA
        "regulatory_impact": "low",
        "submission_required": False,
        
        # Verification
        "test_plan": [],
        "required_tests": [],
        
        # QA
        "approval_status": "approved",
        "review_comments": "Looks good"
    })
    
    mock_llm = AsyncMock()
    mock_llm.ainvoke.return_value = MockLLMResponse(mock_json_response)

    mock_llm = AsyncMock()
    mock_llm.ainvoke.return_value = MockLLMResponse(mock_json_response)
    
    # Mock dependencies
    # We mock the specific methods on the actual service instances and agent llms
    with patch.object(design_engineer_agent, "llm", mock_llm), \
         patch.object(pm_agent, "llm", mock_llm), \
         patch.object(risk_manager_agent, "llm", mock_llm), \
         patch.object(ra_agent, "llm", mock_llm), \
         patch.object(verification_agent, "llm", mock_llm), \
         patch.object(qa_agent, "llm", mock_llm), \
         patch.object(BaseAgent, "_get_db_session") as mock_get_db, \
         patch.object(vector_db_service, "search") as mock_vdb_search, \
         patch.object(gdrive_service, "read_excel_file") as mock_gdrive_read:
        
        # Configure DB Mock to return the test session
        # IMPORTANT: We must prevent agents from closing the test session
        mock_session = MagicMock(wraps=db_session)
        mock_session.close = MagicMock() 
        mock_get_db.return_value = mock_session
        
        # Vector DB Mock
        mock_vdb_search.return_value = {"documents": [["Doc A", "Doc B"]]}
        
        # GDrive Mock
        mock_df = MagicMock()
        mock_df.empty = False
        mock_df.to_string.return_value = "Risk Data: ..."
        mock_gdrive_read.return_value = mock_df
        
        # Initial State
        initial_state: AgentState = {
            "messages": [],
            "change_id": change.id,
            "user_role": "design_engineer",
            "current_step": "start",
            "analysis_results": {},
            "next_agent": "design_engineer"
        }
        
        # Run Orchestrator
        final_state = await orchestrator.run(initial_state)
        
        # Debug output
        print("\nFinal Analysis Results Keys:", final_state["analysis_results"].keys())
        for agent, result in final_state["analysis_results"].items():
            print(f"{agent} status: {result.get('status')}")
            if result.get('status') == 'error':
                print(f"Error detail: {result.get('error')}")

        # Assertions
        # Check overall flow - ensure all agents in the chain executed
        expected_agents = [
            "design_engineer", 
            "project_manager", 
            "risk_manager", 
            "regulatory_affairs", 
            "verification_validation", 
            "quality_assurance"
        ]
        
        for agent in expected_agents:
            assert agent in final_state["analysis_results"], f"Agent {agent} did not run"
            assert final_state["analysis_results"][agent]["status"] == "completed", f"Agent {agent} failed or did not complete"
