import requests
from .abstract_llm_driver import AbstractLLMDriver

class OllamaLLMDriver(AbstractLLMDriver):
  def __init__(self, api_url='http://localhost:11434'):
    super().__init__(name="Ollama")
    self.api_url = api_url

  def generate_response(self, prompt, max_tokens=200, temperature=0, stop_token=""):
    # Construct the API request payload
    payload = {
      "prompt": prompt,
      "max_tokens": max_tokens,
      "temperature": temperature,
      "stop": stop_token,
    }
    # Send a POST request to the Ollama API endpoint
    response = requests.post(f"{self.api_url}/generate", json=payload)
    
    if response.status_code == 200:
      # Parse the response from the API
      response_data = response.json()
      return response_data['choices'][0]['text']
    else:
      # Handle error or unsuccessful request
      print(f"Error: Received status code {response.status_code} from Ollama API")
      return None

    # The other methods (decide_toolset, decide_tool, decide_arguments, parse_llm_response_to_dict, personality)
    # would similarly need to call self.generate_response, perhaps with slight adjustments
    # to their implementation to accommodate any specific requirements or differences in how
    # the Ollama API handles prompts, arguments, etc.

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
    argument_values = self.parse_llm_response_to_dict(llm_response)
    return argument_values

  def parse_llm_response_to_dict(self, llm_response):
    # Trim leading and trailing whitespace
    llm_response = llm_response.strip()

    # If initial parsing fails, attempt corrective measures
    corrected_response = llm_response

    # Replace single quotes with double quotes if necessary
    if "'" in corrected_response:
        corrected_response = corrected_response.replace("'", '"')

    # Remove lines containing ": None", and remove Python comments if it's indeed necessary
    corrected_response_lines = [re.sub(r'#.*$', '', line).strip() for line in corrected_response.split('\n') if ": None" not in line]
    corrected_response = '\n'.join(corrected_response_lines)

    # Attempt to parse again after corrections
    try:
        response_dict = json.loads(f"{{ {corrected_response} }}")
        return response_dict
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON after corrections: {e}\{llm_response} -> {corrected_response}")
        return None
        
  def personality(self, text, query, context):
      prompt = f"""<|im_start|>system
A personality translating machine gives personality to the output of a tool.
Personality: Rewrite the tool output as a helpful programmer's assistant.
<|im_start|>user
Contextual information: {context}
Original user query: {query}
Tool output: {text}<|im_end|>
<|im_start|>assistant
Rewritten tool output with personality:
"""
  
      # Ask the LLM to generate a response based on the prompt to get the toolset recommendation
      llm_response = self.generate_response(prompt, stop_token='"')
      # Assuming generate_response will return a string response containing the name of the best toolset
      return llm_response
