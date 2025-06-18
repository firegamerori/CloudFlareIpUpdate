import requests, time, configparser, logging, datetime, json

config = configparser.ConfigParser()
config.read('config.ini')

zone_id = config.get('tokens', 'zone_id')
bearer_token = config.get('tokens', 'bearer_token')
record_ids = config.get('tokens', 'record_ids').split(',')
api_webhook = config.get('tokens', 'webhook_url')

record_actual_ips: dict = {
  
}

headers = {
  'Authorization': 'Bearer ' + bearer_token,
  'Content-Type': 'application/json'
}

def send_webhook(message, type):
  data = {
    "username" : "Logs cloudflare",
  }
  
  data["embeds"] = [
    {
        "description" : message,
        "title" : type
    }
  ]
  
  response = requests.post(api_webhook, json=data)
  

def check_ip():
  ip = requests.get('https://api.ipify.org')
  if ip.status_code != 200:
    print('Error getting IP')
    time.sleep(60)
    return check_ip()
  
  print(f'actual ip : {ip.text}')

  return ip.text

def get_actual_ips():
  url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records'
  
  response = requests.get(url, headers=headers)
  data = response.json()

  
  for record in data['result']:
    if record['id'] in record_ids:
      record_actual_ips[record['id']] = record

def get_ip_of_record(record_id):
  url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}'

  response = requests.get(url, headers=headers)
  data = response.json()
  
  print(f'record ip : {data['result']['content']}')

  return data['result']['content']

def log_ip_change(current_ip, old_ip):
  now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  logging.info(f"{now} - IP change from {current_ip} to {old_ip}")

send_webhook('Cloudflare IP updater started', 'Started')

old_ip = get_ip_of_record(record_ids[0])
my_ip = check_ip()

while True:
  
  while my_ip == old_ip:
    print('Waiting for IP change...')
    time.sleep(180)
    my_ip = check_ip()
  
  print('IP changed')
  
  print('Getting actual IPs')
  get_actual_ips()
  
  print('Updating IPs')
  for record_ip in record_actual_ips.values():
    if record_ip['content'] != my_ip:
      print(f'Updating ip of {record_ip["name"]}')
      url =  f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_ip['id']}'

      payload = {
        'content': my_ip,
      }

      resp = requests.patch(url, headers=headers, data=json.dumps(payload))
      if resp.status_code != 200:
        print('Error updating IP')
        send_webhook(f'Error updating IP \n {resp.text}', 'Error')

      time.sleep(20)
  
  log_ip_change(my_ip, old_ip)
  send_webhook(f'IP updated \n from: {old_ip[0:4]+"****"} \n to: {my_ip[0:4]+"****"}', 'IP updated')
  
  old_ip = my_ip

  time.sleep(60)
  pass
