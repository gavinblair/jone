class ToolRunner:
    def __init__(self, tool, is_called_by_voice=False):
        self.tool = tool
        # Start the process as soon as the object is created
        self.collect_required_arguments()
        self.output = self.run_tool(is_called_by_voice=is_called_by_voice)

    def collect_required_arguments(self):
        while True:
            next_required_argument, next_required_argument_prompt = self.tool.get_next_required_argument_prompt()
            if next_required_argument is None:
                break  # Exit loop if no more required arguments
            
            # Use a method to get user input, could be replaced with actual GUI/Web input method
            answer = self.get_user_input(next_required_argument_prompt)
            # Store the provided answer
            self.tool.argument_values[next_required_argument] = answer

    def run_tool(self, is_called_by_voice):
        # Execute the tool with the arguments collected
        return self.tool.run(is_called_by_voice=is_called_by_voice)

    def get_user_input(self, prompt):
        # Placeholder method for user input, replace as needed
        return input(prompt)