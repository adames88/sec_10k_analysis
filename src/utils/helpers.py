import os
from dotenv import load_dotenv

def load_env():
    """Load environment variables from the .env file."""
    load_dotenv()

def get_openai_api_key() -> str:
    """Retrieve the OpenAI API Key from environment variables."""
    load_env()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set in the environment.")
    return openai_api_key

def get_serper_api_key() -> str:
    """Retrieve the Serper API Key from environment variables."""
    load_env()
    serper_api_key = os.getenv("SERPER_API_KEY")
    if not serper_api_key:
        raise ValueError("SERPER_API_KEY is not set in the environment.")
    return serper_api_key



# break line every 80 characters if line is longer than 80 characters
# don't break in the middle of a word
def pretty_print_result(result):
  parsed_result = []
  for line in result.split('\n'):
      if len(line) > 80:
          words = line.split(' ')
          new_line = ''
          for word in words:
              if len(new_line) + len(word) + 1 > 80:
                  parsed_result.append(new_line)
                  new_line = word
              else:
                  if new_line == '':
                      new_line = word
                  else:
                      new_line += ' ' + word
          parsed_result.append(new_line)
      else:
          parsed_result.append(line)