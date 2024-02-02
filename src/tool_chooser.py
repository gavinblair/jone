import os
import importlib
import importlib.util
import re

from .tool.tool_runner import ToolRunner
from .tool.financial.currency_converter_tool import CurrencyConverterTool
from .tool.pantheon.clear_caches_tool import ClearCachesTool

class ToolChooser:
    def __init__(self, question, context, llm_driver, is_called_by_voice):
        self.question = question
        self.context = context
        self.llm_driver = llm_driver
        self.is_called_by_voice = is_called_by_voice

    def find_toolsets(self):
        return [name for name in os.listdir('./src/tool') 
            if os.path.isdir(os.path.join('./src/tool', name)) and name != "__pycache__"]
    
    def choose_tool(self):
    # Toolsets should be listing the packages inside './tool'
        toolsets = self.find_toolsets()
        toolset = self.llm_driver.decide_toolset(toolsets, self.question, self.context)
        if not toolset:
            return None
        
        # toolset is the name of the package.
        toolset_package = f'src.tool.{toolset}'
        
        # We find the correct tool based on the code of all files inside "./src/tool/{toolset}/" that end in "_tool.py"
        
        toolset_code = ''
        toolset_path = os.path.join('src/tool', toolset)
        for filename in os.listdir(toolset_path):
            if filename.endswith('_tool.py'):
                filepath = os.path.join(toolset_path, filename)
                with open(filepath, 'r') as file:
                    toolset_code += file.read() + '\n\n'
        
        tool_class_name = self.llm_driver.decide_tool(toolset_code, self.question, self.context)
        # tool_class_name is the class name of the tool.
    
        # Convention to transform class name to module name: CurrencyConverterTool -> currency_converter_tool
        if(not tool_class_name):
            return None

        tool_name = '_'.join([word.lower() for word in re.findall('[A-Z][^A-Z]*', tool_class_name)])
        tool_module_name = f"{tool_name}"
        # Properly import the class from the tool package using module name and class name
        tool_module = importlib.import_module(f'.{tool_module_name}', toolset_package)
        tool_class = getattr(tool_module, tool_class_name)()
        
        return tool_class

    def configure_tool(self, tool):
        # Set the arguments of the tool using the provided mappings
        #todo: use the llm along with the query and context
        # to try to answer some of the argument questions
        tool.argument_values = self.llm_driver.decide_arguments(tool, self.question, self.context)

    def execute_tool(self, tool):
        #here the toolrunner will ask questions about any remaining required arguments
        runner = ToolRunner(tool, self.is_called_by_voice)
        return runner.output

    def choose_and_run(self):
        tool = self.choose_tool()
        if(not tool):
            return None
        self.configure_tool(tool)
        return self.execute_tool(tool)