import abc
import subprocess
from typing import Dict, Any

class AbstractTool(abc.ABC):
    """
    Abstract base class for a Tool.
    Each Tool encapsulates information required to execute a command line script and return the output.
    """

    def __init__(self, name: str, description: str, toolset: str, command_template: str, can_be_triggered_by_voice_command: bool, display_command_output_to_user: bool):
        self.name = name
        self.description = description
        self.toolset = toolset
        self.command_template = command_template
        self.can_be_triggered_by_voice_command = can_be_triggered_by_voice_command
        self.display_command_output_to_user = display_command_output_to_user

        self.is_called_by_voice = False
        self.arguments = {}
        self.argument_values = {}

    @abc.abstractmethod
    def define_arguments(self) -> None:
        """
        Abstract method to define required arguments for the tool.
        Each argument should be defined with its properties (name, datatype, required, user prompt).
        """
        pass

    def add_argument(self, name: str, datatype: type, required: bool, prompt: str) -> None:
        """
        Adds an argument to the tool's argument list.
        """
        self.arguments[name] = {'datatype': datatype, 'required': required, 'prompt': prompt}
        self.argument_values[name] = None  # Initialize argument value as None

    def format_command(self) -> str:
        """
        Formats the command string with the provided arguments' values.
        """
        # Ensure that this method correctly replaces placeholders with values from argument_values.
        formatted_command = self.command_template.format(**{arg: self.argument_values[arg] for arg in self.arguments if self.argument_values[arg] is not None})
        return formatted_command

    def run(self, is_called_by_voice: bool) -> str:
        """
        Executes the command using subprocess and returns the output.
        """
        if is_called_by_voice and not self.can_be_triggered_by_voice_command:
            return "This tool cannot be triggered by voice command."
        try:
            result = subprocess.run(self.format_command(), shell=True, check=True, text=True, capture_output=(not self.display_command_output_to_user))
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"An error occurred: {e}"

    def get_next_required_argument_prompt(self) -> tuple:
        """
        Asks user for input for each required argument.
        """
        for arg, properties in self.arguments.items():
            if properties.get('required', False) and not self.argument_values.get(arg, None):
                return arg, properties.get('prompt', '')
        return None, None
