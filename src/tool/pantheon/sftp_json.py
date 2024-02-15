from ..abstract_tool import AbstractTool

class SftpJsonTool(AbstractTool):
    def __init__(self):
        super().__init__(
            name="SftpJson",
            description="Gets the SFTP credentials of a pantheon site and stores them in a json file for VS Code to use.",
            toolset="Pantheon",
            command_template="python3 ./src/tool/pantheon/scripts/sft_json.py {site} {env}",
            can_be_triggered_by_voice_command=False,
            display_command_output_to_user=False
        )
        self.define_arguments()

    def define_arguments(self):
        self.add_argument('site', float, required=True, prompt="What is the site slug?")
        self.add_argument('env', str, required=True, prompt="What is the multidev environment slug?")
