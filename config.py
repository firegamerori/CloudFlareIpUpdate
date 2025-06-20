import configparser

import requests


config = configparser.ConfigParser()
config.read('config.ini')

class Question:
  def __init__(self, question, print_answers = True):
    self.question = question
    self.print_answers = print_answers
    self.answers = []
    self.answers_text = []
    
  def add_answer(self, answer, answer_text):
    self.answers.append(answer)
    self.answers_text.append(answer_text)
    return self
  
  def print_question(self):
    print(self.question)
    if self.print_answers and len(self.answers) != 0:
      print(self.answers)
  
  def get_response(self):
    resp = input()
    
    if len(self.answers) != 0:
      valid = self.valid_response(resp)
      if valid:
        return resp
      
      provable_resp = self.get_provavel_response(resp)
      if provable_resp != None:
        return provable_resp
      
      print('Invalid response')
      return None
    
    return resp

  def valid_response(self, response : str):
    return response in self.answers
  
  def get_provavel_response(self, response : str):
    check_ansewers : list[str] = self.answers
    
    respose_slice : str = ''
    for i in response:
      respose_slice += i
      for ansewer in check_ansewers:
        if not ansewer.startswith(respose_slice):
          check_ansewers.remove(ansewer)
    
      if len(check_ansewers) == 1:
        return check_ansewers[0]

    return None

def get_response_yes_or_no(question):
  print(question)
  input_str = input()
  
  return input_str.capitalize() == 'Y';

def get_response(question : Question):
  question.print_question()
  response = question.get_response()
  
  return response

def is_config_valid():
  if not config.has_section('tokens'):
    print('Error: config.ini does not have a [tokens] section')
    return False

  if not config.has_option('tokens', 'zone_id') or config.get('tokens', 'zone_id').count('*') >= 1:
    print('Error: config.ini does not have a zone_id option in the [tokens] section')
    return False

  if not config.has_option('tokens', 'bearer_token') or config.get('tokens', 'bearer_token').count('*') >= 1:
    print('Error: config.ini does not have a bearer_token option in the [tokens] section')
    return False

  if not config.has_option('tokens', 'record_ids') or config.get('tokens', 'record_ids').count('*') >= 1:
    print('Error: config.ini does not have a record_ids option in the [tokens] section')
    return False

  if not config.has_option('tokens', 'webhook_url') or config.get('tokens', 'webhook_url').count('*') >= 1:
    print('Error: config.ini does not have a webhook_url option in the [tokens] section')
    return False

  return True

def check_zone_and_bearer_token(zone_id, bearer_token):
  
  headers = {
    'Authorization': 'Bearer ' + bearer_token,
    'Content-Type': 'application/json'
  }
  
  print('Checking zone_id and bearer_token...')
  resp = requests.get(f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records', headers=headers)
  
  
  if resp.status_code != 200:
    print('Error: zone_id or bearer_token is invalid')
    return False
  
  print('zone_id and bearer_token are valid')
  
  return resp.json()["result"]
  
  pass

def get_all_records(zone_id, bearer_token):
  headers = {
    'Authorization': 'Bearer ' + bearer_token,
    'Content-Type': 'application/json'
  }
  
  print('Records...')
  resp = requests.get(f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records', headers=headers)
  
  if resp.status_code != 200:
    print('Error: cant get records')
    if get_response_yes_or_no('Sems a error ocurred, want to try again? (y/N)'):
      return get_all_records(bearer_token, zone_id)
    
    return []
  
  results = resp.json()["result"]
  
  ret = []
  
  for record in results:
    if record['type'] == 'A':
      r = {
        'id': record['id'],
        'name': record['name'],
        'content': record['content'],
      }
      ret.append(r)
  
  return ret
  pass

def create_config(zone_id, bearer_token, record_ids, webhook_url):
  config = configparser.ConfigParser()
  config.add_section('tokens')
  config.set('tokens', 'zone_id', zone_id)
  config.set('tokens', 'bearer_token', bearer_token)
  config.set('tokens', 'record_ids', record_ids)
  config.set('tokens', 'webhook_url', webhook_url)

  with open('config.ini', 'w') as configfile:
    config.write(configfile)

  pass

def get_zone_id_and_bearer_token():
  zone_id = get_response(Question('What is your zone_id?'))
  bearer_token = get_response(Question('What is your bearer_token?'))

  resp = check_zone_and_bearer_token(zone_id, bearer_token)
  
  if resp == False:
    if get_response_yes_or_no("Sems your zone_id or bearer_token is invalid, want to try again? (y/N)"):
      return get_zone_id_and_bearer_token()
    print('Ok, exiting...')
    exit()
  
  return zone_id, bearer_token

if __name__ == '__main__':
  if is_config_valid():
    print("Sems your config is valid")
    exit()
  
  if not get_response_yes_or_no('Sems your config isnt valid, want to create a new one? (y/N)'):
    print('Ok, exiting...')
    exit()
  
  zone_id, bearer_token = get_zone_id_and_bearer_token()
  print('Sems your zone_id and bearer_token are valid')
  
  record_ids = get_all_records(zone_id, bearer_token)
  if len(record_ids) == 0:
    print('Sems your zone_id and bearer_token are valid, but you dont have any records type A')
    exit()
  
  print('Sems your zone_id and bearer_token are valid, and you have records type A')
  
  for i in record_ids:
    print(f'id:{i['id']} name: {i["name"]} ip: {i["content"]}')
  
  record_ids = get_response(Question('What are the ids of the records you want to update? (comma separated)'))
  record_ids.replace(' ', '')
  
  discord_web_hook = get_response(Question('What is your discord webhook?'))
  
  create_config(zone_id, bearer_token, record_ids, discord_web_hook)


