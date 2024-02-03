import abc
import subprocess
from typing import Dict, Any

class AbstractLLMDriver(abc.ABC):
    """
    Abstract base class for an LLM Driver.
    """

    def __init__(self, name: str):
        self.name = name

    #we need a method for choosing a toolset given a query, context and list of toolsets
    #we need a method for choosing a tool given a chosen toolset, query and context
    #we need a method for applying personality to a given message, with a given personality
    

    @abc.abstractmethod
    def generate_response(self, text) -> str:
        """
        Returns the response. Include any prompt formatting code you want.
        """
        pass

    @abc.abstractmethod
    def decide_toolset(self, toolsets, query, context) -> str:
        """
        Given the query and context, choose one of the available toolsets
        To find a relevant tool.
        """
        pass

    @abc.abstractmethod
    def decide_tool(self, toolset, query, context):
        """
        Given the toolset, query and context,
        Choose the most relevant tool.
        """
        pass
        
    @abc.abstractmethod
    def decide_arguments(self, tool_code, query, context):
        """
        Decide the arguments to set given the tool code, 
        user query and context.
        """
        pass
   