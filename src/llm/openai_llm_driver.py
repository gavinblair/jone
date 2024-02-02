from .abstract_llm_driver import AbstractLLMDriver

class OpenAILLMDriver(AbstractLLMDriver):
    def __init__(self):
        super().__init__(
            name="OpenAI"
        )

    #todo: writeme
    def process_text(self, text):
        return text