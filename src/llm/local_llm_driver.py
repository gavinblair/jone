from llama_cpp import Llama
import os
import sys
from contextlib import contextmanager
import json

from .abstract_llm_driver import AbstractLLMDriver

@contextmanager
def suppress_output():
  with open(os.devnull, 'w') as devnull:
    original_stdout, original_stderr = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = devnull, devnull
    try:
      yield
    finally:
      sys.stdout, sys.stderr = original_stdout, original_stderr


class LocalLLMDriver(AbstractLLMDriver):
  def __init__(self):
    super().__init__(
      name="Local"
    )
    with suppress_output():
      self.llm = Llama(
        model_path="./src/llm/models/capybarahermes-2.5-mistral-7b.Q4_K_M.gguf",  # Download the model file first
        n_ctx=32768,  # The max sequence length to use - note that longer sequence lengths require much more resources
        n_threads=8,            # The number of CPU threads to use, tailor to your system and the resulting performance
        n_gpu_layers=35,         # The number of layers to offload to GPU, if you have GPU acceleration available
        verbose=True
      )

  def generate_response_in_format(self,prompt,system="You are a helpful assistant.",assistant_preface=""):
    text = f"""
<|im_start|>system
{system}<|im_end|>
<|im_start|>user
{prompt}<|im_end|>
<|im_start|>assistant
{assistant_preface}"""
    return self.generate_response(text)
  
  def generate_response(self, prompt, stop_token="<|im_end|>"):
    with suppress_output():
      output = self.llm(
        prompt,
        max_tokens=200,
        temperature=0,
        stop=[stop_token],
        echo=False,        # Whether to echo the prompt
      )
    return output['choices'][0]['text']
  
  def decide_toolset(self, toolsets, query, context):
      prompt = f"""<|im_start|>system
A helpful toolset-choosing assistant chooses the correct toolset given the context and user query.<|im_end|>
<|im_start|>user
Toolsets: pantheon, financial, commpro
Context: i'm working on pantheon, on the abc-123 site. I'm on the dev2 environment.
User query: clear the caches<|im_end|>
<|im_start|>assistant
(pantheon)<|im_end|>
<|im_start|>user
Toolsets: pantheon, financial, commpro
Context: i'm working on pantheon, on the abc-123 site. I'm on the dev2 environment.
User query: convert 100USD to CAD please<|im_end|>
<|im_start|>assistant
(financial)<|im_end|>
<|im_start|>user
Toolsets: {toolsets}
Context: {context}
User query: {query}<|im_end|>
<|im_start|>assistant
("""
  
      # Ask the LLM to generate a response based on the prompt to get the toolset recommendation
      llm_response = self.generate_response(prompt, stop_token=")")
      # Assuming generate_response will return a string response containing the name of the best toolset
      recommended_toolset = llm_response.strip()
  
      # If the recommended toolset is one of the provided toolsets, return it
      if recommended_toolset in toolsets:
          return recommended_toolset
      return None
  
  def decide_tool(self, toolset_code, query, context):
    #the toolset_code is a string that contains the code of all tool objects in the toolset
    class_name = False
    #todo: use self.generate_response(text_prompt) to ask the llm which tool in the given code is most appropriate given the user's query and the context content
    prompt = f"""<|im_start|>system
A helpful tool-choosing assistant chooses the correct tool (if any), given the context and user query.
Tool classes:
{toolset_code}<|im_end|>
<|im_start|>user
Context: i'm working on pantheon, on the abc-123 site. I'm on the dev2 environment.
User query: clear the caches<|im_end|>
<|im_start|>assistant
(ClearCachesTool)<|im_end|>
<|im_start|>user
Context: i'm working on pantheon, on the abc-123 site. I'm on the dev2 environment.
User query: convert 100USD to CAD please<|im_end|>
<|im_start|>assistant
(CurrencyConverterTool)<|im_end|>
<|im_start|>user
Context: {context}
User query: {query}<|im_end|>
<|im_start|>assistant
("""
  
    # Ask the LLM to generate a response based on the prompt to get the toolset recommendation
    llm_response = self.generate_response(prompt, stop_token=")")
    # Assuming generate_response will return a string response containing the name of the best toolset
    class_name = llm_response.strip().replace('(', '').replace(')', '')
  
    return class_name
  
  def decide_arguments(self, tool_code, query, context):
    prompt = f"""<|im_start|>system
A helpful argument-filling assistant supplies the given tool with relevant arguments values, gleaned from the context and user query. arguments_gleaned_from_query_and_context only contains arguments that are known.
Tool code: {tool_code}<|im_end|>
<|im_start|>user
Context: {context}
User query: {query}
<|im_end|>
<|im_start|>assistant
arguments_gleaned_from_query_and_context = {{"""
    llm_response = self.generate_response(prompt, stop_token="}")
    llm_response = "{" + llm_response.strip() + "}"
    llm_response = llm_response.replace("'", '"')
    # Remove any lines containing ": None"
    llm_response_lines = llm_response.split('\n')
    llm_response_lines = [line for line in llm_response_lines if ": None" not in line]
    llm_response = '\n'.join(llm_response_lines)
    
    argument_values = json.loads(llm_response)

    return argument_values
  
