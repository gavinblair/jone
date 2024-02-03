from ..abstract_tool import AbstractTool

class ClearCachesTool(AbstractTool):
    def __init__(self):
        super().__init__(
            name="ClearCaches",
            description="Clears the caches for a site.",
            toolset="Pantheon",
            command_template="./src/tool/pantheon/scripts/clear_caches.sh {site} {env}",
            can_be_triggered_by_voice_command=False,
            display_command_output_to_user=False
        )
        self.define_arguments()

    def define_arguments(self):
        self.add_argument('site', float, required=True, prompt="What is the site slug?")
        self.add_argument('env', str, required=True, prompt="What is the multidev environment slug?")
