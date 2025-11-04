"""
Base Agent class with memory, tools, and autonomous decision-making.

Implements core agent functionality:
- Tool registration and execution
- Conversation memory
- LLM integration (Ollama)
- Error handling and retries
"""

import os
import json
import requests
from typing import List, Dict, Optional, Callable, Any
from datetime import datetime


class AgentTool:
    """
    Represents a tool that an agent can use.
    
    Attributes:
        name: Tool identifier
        description: What the tool does (used by LLM to decide when to use it)
        function: Callable that executes the tool
        parameters: JSON schema of parameters
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        function: Callable,
        parameters: Dict[str, Any]
    ):
        self.name = name
        self.description = description
        self.function = function
        self.parameters = parameters
    
    def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters."""
        try:
            return self.function(**kwargs)
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}


class BaseAgent:
    """
    Base class for all autonomous agents in the system.
    
    Features:
    - Tool registration and autonomous tool use
    - Conversation memory (last 10 messages)
    - LLM-powered decision making via Ollama
    - Structured prompts for consistent outputs
    """
    
    def __init__(
        self,
        name: str,
        role: str,
        system_prompt: str,
        model: str = "mistral",
        ollama_url: str = None
    ):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.model = model
        self.ollama_url = ollama_url or os.getenv("OLLAMA_URL", "http://localhost:11434")
        
        # Agent memory (conversation history)
        self.memory: List[Dict[str, str]] = []
        self.max_memory = 10
        
        # Registered tools
        self.tools: Dict[str, AgentTool] = {}
        
        # Agent state
        self.task_history: List[Dict] = []
    
    def register_tool(
        self,
        name: str,
        description: str,
        function: Callable,
        parameters: Dict[str, Any]
    ):
        """
        Register a tool that this agent can use.
        
        Args:
            name: Tool identifier
            description: What the tool does (LLM uses this to decide)
            function: Callable to execute
            parameters: JSON schema of parameters
        """
        tool = AgentTool(name, description, function, parameters)
        self.tools[name] = tool
    
    def add_to_memory(self, role: str, content: str):
        """
        Add message to conversation memory.
        
        Maintains sliding window of last 10 messages.
        """
        self.memory.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 10 messages
        if len(self.memory) > self.max_memory:
            self.memory = self.memory[-self.max_memory:]
    
    def get_tools_description(self) -> str:
        """
        Generate description of available tools for LLM.
        
        Returns JSON-formatted tool list that LLM can parse.
        """
        tools_info = []
        for name, tool in self.tools.items():
            tools_info.append({
                "name": name,
                "description": tool.description,
                "parameters": tool.parameters
            })
        
        return json.dumps(tools_info, indent=2)
    
    def call_llm(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Call Ollama LLM for decision making.
        
        Args:
            prompt: User/system prompt
            temperature: Creativity (0=deterministic, 1=creative)
        
        Returns:
            LLM response text
        """
        try:
            # Build conversation context
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            # Add recent memory
            messages.extend([
                {"role": msg["role"], "content": msg["content"]}
                for msg in self.memory[-5:]  # Last 5 messages
            ])
            
            # Add current prompt
            messages.append({"role": "user", "content": prompt})
            
            # Call Ollama API
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": 512
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("message", {}).get("content", "")
            else:
                return f"Error: Ollama returned {response.status_code}"
        
        except Exception as e:
            return f"Error calling LLM: {str(e)}"
    
    def decide_and_act(self, task: str) -> Dict[str, Any]:
        """
        Autonomous decision-making: Analyze task, choose tools, execute.
        
        This is the core of agent autonomy:
        1. Analyze the task
        2. Decide which tools to use
        3. Execute tools in sequence
        4. Synthesize results
        
        Args:
            task: High-level task description
        
        Returns:
            Dict with:
                - reasoning: Agent's thought process
                - actions: List of tools used
                - results: Tool execution results
                - conclusion: Final analysis
        """
        # Add task to memory
        self.add_to_memory("user", task)
        
        # Build decision prompt
        tools_desc = self.get_tools_description()
        decision_prompt = f"""
Task: {task}

Available Tools:
{tools_desc}

Instructions:
1. Analyze the task carefully
2. Decide which tools to use and in what order
3. Provide your reasoning
4. Output your plan in JSON format:

```json
{{
  "reasoning": "Your thought process",
  "tools_to_use": [
    {{"tool": "tool_name", "parameters": {{"param1": "value1"}}}},
  ],
  "expected_outcome": "What you expect to learn"
}}
```
"""
        
        # Get LLM decision
        decision = self.call_llm(decision_prompt, temperature=0.3)
        
        # Parse decision (extract JSON)
        try:
            # Try to extract JSON from response
            start = decision.find("{")
            end = decision.rfind("}") + 1
            if start != -1 and end > start:
                decision_json = json.loads(decision[start:end])
            else:
                # Fallback: no tools to use
                decision_json = {
                    "reasoning": decision,
                    "tools_to_use": [],
                    "expected_outcome": "Manual analysis required"
                }
        except json.JSONDecodeError:
            decision_json = {
                "reasoning": decision,
                "tools_to_use": [],
                "expected_outcome": "Could not parse decision"
            }
        
        # Execute tools
        tool_results = []
        for tool_plan in decision_json.get("tools_to_use", []):
            tool_name = tool_plan.get("tool")
            params = tool_plan.get("parameters", {})
            
            if tool_name in self.tools:
                result = self.tools[tool_name].execute(**params)
                tool_results.append({
                    "tool": tool_name,
                    "parameters": params,
                    "result": result
                })
        
        # Synthesize results
        synthesis_prompt = f"""
You executed the following tools:
{json.dumps(tool_results, indent=2)}

Based on these results, provide:
1. Key findings
2. Patterns or insights
3. Recommendations
4. Confidence level (0-100%)

Format as JSON:
```json
{{
  "key_findings": ["finding1", "finding2"],
  "insights": "Your analysis",
  "recommendations": ["rec1", "rec2"],
  "confidence": 85
}}
```
"""
        
        synthesis = self.call_llm(synthesis_prompt, temperature=0.5)
        
        # Parse synthesis
        try:
            start = synthesis.find("{")
            end = synthesis.rfind("}") + 1
            if start != -1 and end > start:
                synthesis_json = json.loads(synthesis[start:end])
            else:
                synthesis_json = {"insights": synthesis, "confidence": 50}
        except json.JSONDecodeError:
            synthesis_json = {"insights": synthesis, "confidence": 50}
        
        # Record in task history
        task_record = {
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "decision": decision_json,
            "tool_results": tool_results,
            "synthesis": synthesis_json
        }
        self.task_history.append(task_record)
        
        # Add to memory
        self.add_to_memory(
            "assistant",
            f"Completed task. Confidence: {synthesis_json.get('confidence', 'N/A')}%"
        )
        
        return {
            "agent": self.name,
            "reasoning": decision_json.get("reasoning", ""),
            "actions": tool_results,
            "conclusion": synthesis_json,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status and capabilities."""
        return {
            "name": self.name,
            "role": self.role,
            "model": self.model,
            "tools_available": list(self.tools.keys()),
            "memory_size": len(self.memory),
            "tasks_completed": len(self.task_history)
        }
