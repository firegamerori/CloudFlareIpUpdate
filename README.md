<h1 align="center">Simple CloudFlare updater</h1> <p align="center"><a href="#project-description">Project Description</a> - <a href="#key-features">Key Features</a> - <a href="#technology-stack">Tech Stack</a></p>

## Project Description

This project was mainly created for those who enjoy self-hosting simple applications on a Raspberry Pi or an old computer. By using the Cloudflare API (DNS provider) and the Discord API (for notifications), it allows updating the IP address of specific Cloudflare DNS records and sending notifications whenever this change occurs.
Key Features

## The main features are:

- **Send Discord notifications**: Using the Discord API
- **Update the IP of multiple records**: Using the Cloudflare API and record_id

## Installation

Update the config
```
    [tokens]
    zone_id=****************
    bearer_token=*******************
    record_ids=********,********* #comma separated
    webhook_url=***************** #Discord webhook URL
```

Install using Python

Note that you may need to use the Python virtual environment
```bash
  git clone https://github.com/firegamerori/CloudFlareIpUpdate.git
  cd CloudFlareIpUpdate
  pip install -r requirements.txt
  python main.py
```

## Probable update

In the future, it is probable that I will add an automatic script to get the record_ids

## Help
### Where can I find the zone_id?

- Open the Cloudflare DNS you want to edit
- Go to Overview

### Where can I find the bearer_token?

- https://dash.cloudflare.com/profile/api-tokens
- Create your token with the permission to edit your records

### Where can I find the record_ids?

```bash
curl https://api.cloudflare.com/client/v4/zones/{Your zone_id}/dns_records \
    -H 'Authorization: Bearer {Your bearer_token}' \
```
This will return a JSON file; find your record_ids there

### Where can I find the webhook_url?

- Create a Discord server
- Edit a chat channel
- Go to Webhooks
- Create and copy the URL
