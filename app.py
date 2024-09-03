import os

from flask import Flask, request
import base64
from flask_cors import CORS, cross_origin
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv(".env")

if not os.environ.get("AZURE_OPENAI_API_KEY"):
    raise ValueError(
        "AZURE_OPENAI_API_KEY key not found in environment variables.")

if not os.environ.get("AZURE_OPENAI_ENDPOINT"):
    raise ValueError(
        "AZURE_OPENAI_ENDPOINT key not found in environment variables.")

if not os.environ.get("AZURE_OPENAI_API_VERSION"):
    raise ValueError(
        "AZURE_OPENAI_API_VERSION key not found in environment variables.")

if not os.environ.get("AZURE_OPENAI_DEPLOYMENT"):
    raise ValueError(
        "AZURE_OPENAI_DEPLOYMENT key not found in environment variables.")

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

#openai.api_key = os.environ["OPENAI_API_KEY"]
file_path = './sample_logs/unix_log.log'
file_content = ""

# Load the log file and store it in global variable
def load_local_file(file_path):
    print ("File is loading.. ")
    with open(file_path, 'r') as file:
      global  file_content
      file_content = file.read()
    print ("File is loaded --.. "+file_path)
    
# main method to create a prompt call to AI
def make_prompt_call(promptFromUser, type):
    client = AzureOpenAI(
          azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT"),
          api_key=os.environ.get("AZURE_OPENAI_API_KEY"),  
          api_version=os.environ.get("AZURE_OPENAI_API_VERSION")
      )
    prompt = "Hi there "
    
    if type == "summary":
      prompt= generate_prompt_for_summary ()
    else:
      prompt=  generate_prompt(promptFromUser)


    response = client.chat.completions.create(
    model=os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
    messages=[
      { 
         "role": "system",
         "content": "You are a helpful assistant." 
      },
    {
     "role": "user",
     "content": [
       {"type": "text", "text": prompt},
      
       ]       
      }
    ],
    max_tokens=2000,
    stream = False 
    )
    return response.choices[0].message.content
    
# Generate the Prompt based on the requirement     
def generate_prompt(userPrompt):
      generated_prompt = "Analyze the log data and answer the below questions, if the question is not relevant then ask your own question for clarification:\n\n"+file_content+"\n\n"+userPrompt
      return generated_prompt

# Generate the Prompt based on the requirement     
def generate_prompt_for_summary():
      generated_prompt_summary = "Read the given log file and shorten it by summarizing the messages without loosing vital information in it:\n\n"+file_content+"\n\n"
      return generated_prompt_summary


# Post call for Log Analyzer 
@app.route('/api/logAnalyzer', methods=['POST'])
def log_analyzer():
  # promptFromUser = request.args.get('query')
  messageBody = request.get_json()
  promptFromUser = messageBody['query']
  index = messageBody['queryIndex']
  print(messageBody)
  if len(promptFromUser) != 0:
    response_string =  make_prompt_call(promptFromUser,index)
  else:
    response_string = "User query is empty. Please enter valid prompt"
  print(f"Prompt: {promptFromUser} \n response \n{response_string}")
  
  return response_string


def shortening_log():
    print("Shortening the log entry ")
    shortened_file_content = ""
    shortened_file_content = make_prompt_call("", "summary")
    print("After shortening \n\n "+shortened_file_content)



# Main file to start 
if __name__ == '__main__':
    load_local_file(file_path)
   # shortening_log()
    app.run()