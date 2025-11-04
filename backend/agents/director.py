"""
Director Agent - Orchestrates all specialist agents.

The Director is the highest-level agent that:
1. Receives high-level prediction requests
2. Delegates subtasks to specialist agents
3. Synthesizes results from all agents
4. Makes final prediction decisions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent
from typing import Dict, Any, List


class DirectorAgent(BaseAgent):
    """
    Director Agent - Coordinates all specialist agents for flight predictions.
    
    Capabilities:
    - Task decomposition (break complex requests into subtasks)
    - Agent coordination (delegate to Weather, Flight, Location specialists)
    - Result synthesis (combine insights from all agents)
    - Risk assessment (final go/no-go decisions)
    """
    
    def __init__(self):
        system_prompt = """You are the Director Agent for PreFlight AI flight delay prediction system.

Your responsibilities:
1. Analyze flight prediction requests
2. Decompose tasks and delegate to specialist agents:
   - Weather Specialist: Analyzes meteorological conditions
   - Flight Specialist: Analyzes historical flight patterns
   - Location Specialist: Analyzes geographic factors
   - Prediction Specialist: Runs ML models
3. Synthesize results from all specialists
4. Make final prediction with confidence level
5. Provide actionable recommendations

You have autonomous decision-making authority. Think step-by-step and justify your decisions.

Output Format (JSON):
{
  "task_analysis": "Your understanding of the request",
  "subtasks": [
    {"agent": "weather_specialist", "task": "Analyze weather for DXB-LHR"},
    {"agent": "flight_specialist", "task": "Get route history DXB-LHR"}
  ],
  "coordination_strategy": "How you'll combine results",
  "expected_timeline": "Estimated completion time"
}
"""
        
        super().__init__(
            name="Director",
            role="Chief Coordinator",
            system_prompt=system_prompt,
            model="mistral"
        )
        
        # Specialist agents will be registered here
        self.specialists: Dict[str, BaseAgent] = {}
    
    def register_specialist(self, name: str, agent: BaseAgent):
        """Register a specialist agent under Director's coordination."""
        self.specialists[name] = agent
    
    def coordinate_prediction(
        self,
        flight_number: str,
        origin: str,
        destination: str,
        departure_time: str
    ) -> Dict[str, Any]:
        """
        Main entry point: Coordinate multi-agent flight delay prediction.
        
        Args:
            flight_number: Flight IATA code (e.g., "EK230")
            origin: Origin airport IATA code
            destination: Destination airport IATA code
            departure_time: ISO format datetime
        
        Returns:
            Comprehensive prediction with insights from all agents
        """
        # Step 1: Analyze and decompose task
        task_description = f"""
Predict delay probability for flight {flight_number}:
- Route: {origin} → {destination}
- Departure: {departure_time}

Coordinate with specialist agents to gather:
1. Weather conditions at origin and destination
2. Historical performance of this route
3. Geographic factors (timezone, distance, nearby airports)
4. ML model prediction

Synthesize all data and provide final assessment.
"""
        
        decision = self.decide_and_act(task_description)
        
        # Step 2: Delegate to specialist agents
        agent_results = {}
        
        # Weather Specialist
        if "weather_specialist" in self.specialists:
            weather_agent = self.specialists["weather_specialist"]
            weather_task = f"Analyze current and forecast weather for {origin} and {destination}"
            agent_results["weather"] = weather_agent.decide_and_act(weather_task)
        
        # Flight Specialist
        if "flight_specialist" in self.specialists:
            flight_agent = self.specialists["flight_specialist"]
            flight_task = f"Analyze historical delays for route {origin}-{destination}"
            agent_results["flight_history"] = flight_agent.decide_and_act(flight_task)
        
        # Location Specialist
        if "location_specialist" in self.specialists:
            location_agent = self.specialists["location_specialist"]
            location_task = f"Analyze geographic factors for route {origin}-{destination}"
            agent_results["location"] = location_agent.decide_and_act(location_task)
        
        # Prediction Specialist
        if "prediction_specialist" in self.specialists:
            prediction_agent = self.specialists["prediction_specialist"]
            prediction_task = f"Run ML prediction with all gathered data for {flight_number}"
            agent_results["prediction"] = prediction_agent.decide_and_act(prediction_task)
        
        # Step 3: Synthesize all results
        synthesis_prompt = f"""
You coordinated a multi-agent prediction for flight {flight_number}.

Agent Results:
{self._format_agent_results(agent_results)}

Synthesize these findings into:
1. Overall delay probability (0-1)
2. Risk level (LOW/MODERATE/HIGH/CRITICAL)
3. Top 3 contributing factors
4. Confidence in prediction (0-100%)
5. Actionable recommendations
6. Alternative actions if delay occurs

Output as JSON:
```json
{{
  "delay_probability": 0.72,
  "risk_level": "HIGH",
  "contributing_factors": [
    {{"factor": "crosswind", "impact": 0.23, "severity": "high"}},
    {{"factor": "route_history", "impact": 0.18, "severity": "medium"}}
  ],
  "confidence": 85,
  "recommendations": [
    "Notify crew 2 hours before departure",
    "Prepare alternate airport"
  ],
  "alternatives": ["Divert to alternate", "Delay departure by 3 hours"]
}}
```
"""
        
        final_assessment = self.call_llm(synthesis_prompt, temperature=0.3)
        
        # Parse final assessment
        import json
        try:
            start = final_assessment.find("{")
            end = final_assessment.rfind("}") + 1
            if start != -1 and end > start:
                assessment_json = json.loads(final_assessment[start:end])
            else:
                assessment_json = {
                    "delay_probability": 0.5,
                    "risk_level": "MODERATE",
                    "confidence": 50
                }
        except json.JSONDecodeError:
            assessment_json = {
                "delay_probability": 0.5,
                "risk_level": "MODERATE",
                "confidence": 50
            }
        
        # Return comprehensive report
        return {
            "flight_number": flight_number,
            "route": f"{origin} → {destination}",
            "departure_time": departure_time,
            "director_analysis": decision,
            "specialist_reports": agent_results,
            "final_assessment": assessment_json,
            "timestamp": decision["timestamp"],
            "coordinated_by": self.name
        }
    
    def _format_agent_results(self, results: Dict[str, Any]) -> str:
        """Format agent results for LLM consumption."""
        import json
        formatted = []
        for agent_name, result in results.items():
            formatted.append(f"\n=== {agent_name.upper()} ===")
            formatted.append(json.dumps(result.get("conclusion", {}), indent=2))
        return "\n".join(formatted)
