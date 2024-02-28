import os
import importlib
import importlib.util
import re

from .tool.abstract_tool import AbstractTool
from .tool.tool_runner import ToolRunner
from .tool.financial.currency_converter_tool import CurrencyConverterTool
from .tool.pantheon.clear_caches_tool import ClearCachesTool

class ToolChooser:
    def __init__(self, query, context, llm_driver, is_called_by_voice, debug=False):
        self.query = query
        self.context = context
        self.llm_driver = llm_driver
        self.is_called_by_voice = is_called_by_voice
        self.debug = debug

    def find_toolsets(self):
        return [name for name in os.listdir('./src/tool') 
            if os.path.isdir(os.path.join('./src/tool', name)) and name != "__pycache__"]
    
    def get_tool_code_by_class_name(self, toolset, tool_class_name):
        """
        Retrieves the Python code for a specific tool based on the tool's class name.
        Assumes that the file naming follows the convention that the file name is
        the snake_case version of the class name and ends with '_tool.py'.
        """

        if(self.debug):
            print(f"get_tool_code_by_class_name:toolset {toolset},tool_class_name {tool_class_name}")
        
        tool_name = '_'.join([word.lower() for word in re.findall('[A-Z][^A-Z]*', tool_class_name)])
        tool_filename = f'{tool_name}.py'
        toolset_path = os.path.join('src/tool', toolset)
        filepath = os.path.join(toolset_path, tool_filename)
        
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"No such file: {filepath}")
        
        with open(filepath, 'r') as file:
            tool_code = file.read()
        return tool_code

    def get_class_names_for_toolset(self, toolset):
        if(self.debug):
            print(f"get_class_names_for_toolset:toolset {toolset}")
        # Assuming toolset refers to a directory within the 'src/tool' package
        toolset_path = f'./src/tool/{toolset}'
        if not os.path.isdir(toolset_path):
            raise FileNotFoundError(f'The toolset path {toolset_path} does not exist.')
    
        class_names = []
        for file in os.listdir(toolset_path):
            # We only want `.py` files and we ignore `__init__.py`
            if file.endswith('.py') and not file.startswith('__'):
                module_name = file[:-3]
                # Construct the full module path
                full_module_path = f'src.tool.{toolset}.{module_name}'
                spec = importlib.util.spec_from_file_location(full_module_path, os.path.join(toolset_path, file))
                module = importlib.util.module_from_spec(spec)
    
                try:
                    spec.loader.exec_module(module)  # Load the module into memory
                except Exception as e:
                    # Handle possible import errors e.g. syntax errors, ImportError, etc.
                    raise ImportError(f'An error occurred when trying to import {module_name}: {e}')
                
                # Add classes defined in the module that are subclasses of a given Base class (if applicable)
                # Here we assume that the base class is named 'AbstractTool', and all tool classes inherit from it
                for attribute_name in dir(module):
                    attribute = getattr(module, attribute_name)
                    if isinstance(attribute, type) and issubclass(attribute, AbstractTool) and attribute.__module__ == module.__name__:
                        class_names.append(attribute_name)
                        
        return class_names
    
    def choose_tool(self):
        
        # Toolsets should be listing the packages inside './tool'
        toolsets = self.find_toolsets()
        if(self.debug):
            print(f"deciding toolset...")
        toolset = self.llm_driver.decide_toolset(toolsets, self.query, self.context)
        if(self.debug):
            print(f"chose: {toolset}")
        if not toolset:
            return None
        
        # toolset is the name of the package.
        toolset_package = f'src.tool.{toolset}'
    
        # Assuming we can list class names per toolset from some method `get_class_names_for_toolset`
        tool_class_names = self.get_class_names_for_toolset(toolset)
        
        # Concatenating the code for each tool in the toolset
        toolset_code = ""
        for tool_class_name in tool_class_names:
            toolset_code += self.get_tool_code_by_class_name(toolset, tool_class_name)
        
        if(self.debug):
            print(f"deciding tool...")
        tool_class_name = self.llm_driver.decide_tool(toolset_code, self.query, self.context)
        if not tool_class_name:
            return None
        if(self.debug):
            print(f"chose: {tool_class_name}")
    
        # Convention to transform class name to module name: CurrencyConverterTool -> currency_converter_tool
        tool_module_name = '_'.join([word.lower() for word in re.findall('[A-Z][^A-Z]*', tool_class_name)])
        
        # Properly import the class from the tool package using module name and class name
        tool_module = importlib.import_module(f'.{tool_module_name}', toolset_package)
        tool_class = getattr(tool_module, tool_class_name)()
        
        return tool_class

    def configure_tool(self, tool):
        # Get the class name of the tool
        tool_class_name = tool.__class__.__name__
        # Retrieve the code for the tool by its class name
        tool_code = self.get_tool_code_by_class_name(tool.toolset, tool_class_name)
        
        # Set the arguments of the tool using the LLM and the provided query and context
        if(self.debug):
            print(f"deciding arguments...")
        tool.argument_values = self.llm_driver.decide_arguments(tool_code, self.query, self.context)
        if(self.debug):
            print(f"args:")
            print(tool.argument_values);
    
    def execute_tool(self, tool):
        if(self.debug):
            print(f"running the tool...")
        #here the toolrunner will ask questions about any remaining required arguments
        runner = ToolRunner(tool, self.is_called_by_voice)
        if(self.debug):
            print(f"finished running the tool.")
        return runner.output

    def choose_and_run(self):
        tool = self.choose_tool()
        if(not tool):
            return None
        self.configure_tool(tool)
        return self.execute_tool(tool)