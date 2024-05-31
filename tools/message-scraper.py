#
# This script will not work since the Yuzu Discord has been deleted.
#

# Used to batch collect message data from a server's channel.

import requests
import json
import time
import os
import re
from auth import auth

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

wait_time = 2.8
rate_limit_time = 30
channel_name = "game-mods"
already_archived = sorted(os.listdir(f"pages-{channel_name}/"), key=natural_keys)
current_message = 0
if len(already_archived) > 0:
    current_message = int(already_archived[len(already_archived) - 2].replace('.json', ''))
    
json_data_last = None
request_url = None

headers = {
    'authorization': auth
}

channel_link = "https://discord.com/api/v9/guilds/398318088170242053/messages/search?channel_id=495758692495523854&has=file"
total_messages = json.loads(requests.get(channel_link, headers=headers).content)['total_results']

while current_message < total_messages or total_messages == 0:
    if json_data_last is None and current_message != 0:
        print("Loading last archives JSON to continue where it left off...")
        json_data_last = json.loads(open(f"pages-{channel_name}/{already_archived[len(already_archived) - 1]}", 'rt').read())
        max_id = int(json_data_last['messages'][len(json_data_last['messages']) - 1][0]['id'])
        
        print(f"Done! We left off at a max ID of {max_id}.")
    elif current_message != 0:
        max_id = int(json_data_last['messages'][len(json_data_last['messages']) - 1][0]['id'])
    
    if current_message < 5000:
        # We can request messages at a set date offset this way, but only up to an offset of 5,000.
        request_url = f"{channel_link}&offset={current_message}"
    else:
        # Past an offset of 5k, we'll need to specify our message ID cutoff from the last ID of the last JSON archived.
        request_url = f"{channel_link}&max_id={max_id}"
        
    try: # Try to request page from Discord
        req = requests.get(request_url, headers=headers)
        json_data = json.loads(req.content)
        current_message += len(json_data['messages'])
        # total_messages = json_data['total_results']
    except Exception as e:
        # We are likely being rate limited by Discord's servers, wait a moment and try again.
        print(f"Request exception (likely rate limit reached): \n{e}")
        print(json_data)
        time.sleep(rate_limit_time)
        continue
    file = open(f'pages-{channel_name}/{current_message}.json', 'wb')
    file.write(req.content)
    print(f"{current_message} of {total_messages} messages archived ({round((current_message * 100) / total_messages, 2)}% complete)")
    time.sleep(wait_time)
    json_data_last = json_data
