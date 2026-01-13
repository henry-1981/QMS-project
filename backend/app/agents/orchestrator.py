from langgraph.graph import StateGraph, END
from app.agents.base_agent import AgentState
from app.agents.design_engineer_agent import design_engineer_agent
from app.agents.ra_agent import ra_agent
from app.agents.qa_agent import qa_agent
from app.agents.pm_agent import pm_agent
from app.agents.risk_manager_agent import risk_manager_agent
from app.agents.verification_agent import verification_agent


class QMSOrchestrator:
    def __init__(self):
        self.graph = self._build_graph()
    
    def _build_graph(self):
        workflow = StateGraph(AgentState)
        
        workflow.add_node("design_engineer", design_engineer_agent.execute)
        workflow.add_node("project_manager", pm_agent.execute)
        workflow.add_node("risk_manager", risk_manager_agent.execute)
        workflow.add_node("regulatory_affairs", ra_agent.execute)
        workflow.add_node("verification", verification_agent.execute)
        workflow.add_node("quality_assurance", qa_agent.execute)
        
        workflow.set_entry_point("design_engineer")
        
        workflow.add_edge("design_engineer", "project_manager")
        workflow.add_edge("project_manager", "risk_manager")
        workflow.add_edge("risk_manager", "regulatory_affairs")
        workflow.add_edge("regulatory_affairs", "verification")
        workflow.add_edge("verification", "quality_assurance")
        workflow.add_edge("quality_assurance", END)
        
        return workflow.compile()
    
    async def run(self, initial_state: AgentState) -> AgentState:
        result = await self.graph.ainvoke(initial_state)
        return result
    
    async def run_single_agent(self, agent_type: str, initial_state: AgentState) -> AgentState:
        agents = {
            "design_engineer": design_engineer_agent,
            "project_manager": pm_agent,
            "risk_manager": risk_manager_agent,
            "regulatory_affairs": ra_agent,
            "verification": verification_agent,
            "quality_assurance": qa_agent
        }
        
        agent = agents.get(agent_type)
        if not agent:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        result = await agent.execute(initial_state)
        return result


orchestrator = QMSOrchestrator()
