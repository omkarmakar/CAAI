from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAgent(ABC):
    """
    Abstract base class for all specialized agents.
    """
    def __init__(self, agent_name: str):
        self.agent_name = agent_name

    @abstractmethod
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a given task.

        Args:
            task (Dict[str, Any]): The task to be executed.

        Returns:
            Dict[str, Any]: The result of the task execution.
        """
        pass