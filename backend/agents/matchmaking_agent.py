from .base_agent import BaseAgent
from typing import Dict, Any, List, Optional
import json

# Gemini import
try:
    import google.generativeai as genai
except ImportError:
    genai = None


class MatchmakingAgent(BaseAgent):
    """
    AI-powered CA matchmaking agent.
    Intelligently connects clients to appropriate CA experts based on query analysis,
    expertise matching, and service requirements.
    
    Actions:
    - find_expert: Match client query to appropriate CA expert
    - analyze_query: Understand client needs and requirements
    - recommend_services: Suggest relevant CA services
    - assess_complexity: Evaluate query complexity and resource needs
    """
    def __init__(self, gemini_api_key: Optional[str] = None):
        super().__init__("MatchmakingAgent")
        self.gemini_api_key = gemini_api_key
        self.gemini_client = None
        
        if self.gemini_api_key and genai:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_client = genai.GenerativeModel("gemini-2.0-flash")
            except Exception as e:
                print(f"⚠️ Failed to initialize Gemini for MatchmakingAgent: {e}")

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        action = task.get("action")
        params = task.get("params", {})

        if action == "find_expert":
            return self._find_expert(params)
        elif action == "analyze_query":
            return self._analyze_query(params)
        elif action == "recommend_services":
            return self._recommend_services(params)
        elif action == "assess_complexity":
            return self._assess_complexity(params)
        else:
            return {"status": "error", "message": f"Unknown action '{action}' for MatchmakingAgent"}

    def _find_expert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Match client to appropriate CA expert using AI
        """
        topic = params.get("topic", "general")
        query = params.get("query", "")
        client_profile = params.get("client_profile", {})
        available_experts = params.get("available_experts", [])
        
        if not self.gemini_client:
            return {
                "status": "success",
                "topic": topic,
                "assigned": "CA_Team_General",
                "note": "Basic assignment - AI matching not available"
            }
        
        try:
            prompt = f"""As a CA firm coordinator, match this client query to the best expert:

Client Query: {query}
Topic: {topic}
Client Profile: {json.dumps(client_profile, indent=2)}
Available Experts: {json.dumps(available_experts, indent=2)}

Analyze and provide:
1. Query Classification:
   - Domain: (Tax/Audit/GST/Advisory/Corporate Law/etc.)
   - Complexity: (Simple/Moderate/Complex/Highly Complex)
   - Urgency: (Low/Medium/High/Critical)
2. Required Expertise:
   - Technical skills needed
   - Industry knowledge required
   - Experience level needed
3. Best Match Recommendation:
   - Expert name/team
   - Match score (0-100)
   - Rationale for match
4. Alternative experts (if applicable)
5. Estimated engagement:
   - Time required
   - Resource allocation
   - Billing considerations
6. Pre-engagement checklist for the CA
7. Success metrics for this engagement

Format as professional client-expert matching report."""

            response = self.gemini_client.generate_content(prompt)
            
            return {
                "status": "success",
                "topic": topic,
                "matching_analysis": response.text.strip(),
                "query": query,
                "matched_at": self._get_timestamp()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Expert matching failed: {str(e)}"
            }

    def _analyze_query(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep analysis of client query to understand needs
        """
        query = params.get("query", "")
        context = params.get("context", "")
        
        if not self.gemini_client:
            return {
                "status": "error",
                "message": "Gemini AI required for query analysis"
            }
        
        try:
            prompt = f"""As a senior CA analyzing a client query:

Client Query: {query}
Context: {context}

Provide detailed analysis:
1. Query Intent:
   - Primary objective
   - Underlying concerns
   - Implicit needs
2. Service Classification:
   - Assurance services
   - Tax services
   - Advisory services
   - Compliance services
   - Multiple services required
3. Complexity Assessment:
   - Technical difficulty
   - Time sensitivity
   - Regulatory complexity
   - Stakeholder involvement
4. Information Gaps:
   - Missing details needed
   - Questions to ask client
   - Documents required
5. Preliminary Scope Definition
6. Risk Factors:
   - Client risks
   - Engagement risks
   - Reputation risks
7. Value Proposition:
   - What client values most
   - Success criteria
8. Recommended Approach:
   - Engagement structure
   - Team composition
   - Timeline estimate

Format as professional query analysis brief."""

            response = self.gemini_client.generate_content(prompt)
            
            return {
                "status": "success",
                "query": query,
                "analysis": response.text.strip(),
                "analyzed_at": self._get_timestamp()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Query analysis failed: {str(e)}"
            }

    def _recommend_services(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recommend relevant CA services based on client situation
        """
        client_info = params.get("client_info", {})
        business_stage = params.get("business_stage", "")  # startup/growth/mature
        
        if not self.gemini_client:
            return {
                "status": "error",
                "message": "Gemini AI required for service recommendations"
            }
        
        try:
            prompt = f"""As a CA business advisor, recommend services:

Client Information: {json.dumps(client_info, indent=2)}
Business Stage: {business_stage}

Recommend appropriate CA services:
1. Essential Services (must-have):
   - Service name
   - Why essential
   - Typical cost range
   - Timeline
2. High-Value Services (recommended):
   - Service name
   - Business benefit
   - ROI potential
   - Priority level
3. Optional Services (nice-to-have):
   - Service name
   - When to consider
   - Triggers for engagement
4. Lifecycle-Based Recommendations:
   - Immediate needs (0-3 months)
   - Short-term needs (3-12 months)
   - Long-term planning (1-3 years)
5. Industry-Specific Services
6. Compliance Calendar:
   - Recurring services needed
   - Filing deadlines
   - Review cycles
7. Service Bundles:
   - Package offerings
   - Bundled pricing benefits
8. Value-Added Services:
   - Advisory opportunities
   - Strategic consulting
   - Business support

Format as service recommendation proposal."""

            response = self.gemini_client.generate_content(prompt)
            
            return {
                "status": "success",
                "recommendations": response.text.strip(),
                "business_stage": business_stage,
                "prepared_at": self._get_timestamp()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Service recommendation failed: {str(e)}"
            }

    def _assess_complexity(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess query/engagement complexity
        """
        query = params.get("query", "")
        scope = params.get("scope", "")
        constraints = params.get("constraints", {})
        
        if not self.gemini_client:
            return {
                "status": "error",
                "message": "Gemini AI required for complexity assessment"
            }
        
        try:
            prompt = f"""As a CA practice manager, assess engagement complexity:

Query: {query}
Scope: {scope}
Constraints: {json.dumps(constraints, indent=2)}

Provide complexity assessment:
1. Complexity Rating: Simple/Moderate/Complex/Highly Complex
2. Complexity Factors:
   - Technical complexity
   - Regulatory complexity
   - Volume of transactions
   - Number of entities
   - Cross-border elements
   - Time constraints
   - Stakeholder complexity
3. Resource Requirements:
   - Team size needed
   - Skill levels required
   - Specialist involvement
   - External consultants
4. Time Estimate:
   - Best case
   - Most likely
   - Worst case
5. Risk Assessment:
   - Delivery risks
   - Quality risks
   - Client relationship risks
6. Prerequisites:
   - Systems/access needed
   - Training required
   - Licenses/approvals
7. Success Factors:
   - What could go right
   - Dependencies
8. Failure Modes:
   - What could go wrong
   - Mitigation strategies

Format as professional complexity assessment."""

            response = self.gemini_client.generate_content(prompt)
            
            return {
                "status": "success",
                "complexity_assessment": response.text.strip(),
                "assessed_at": self._get_timestamp()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Complexity assessment failed: {str(e)}"
            }

    def _get_timestamp(self) -> str:
        """Return current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"
