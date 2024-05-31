# Separate collected messages into files by thread, while optionally downloading attached files.

import json
import os
import re
from datetime import datetime
import requests

# Sort files by size of combined number (instead of individual numbers)
def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

aws = "https://yuzudiscordbackup.s3.us-west-2.amazonaws.com/"
channel_name = "media" # Name of the channel being archived
download_attachments = False # Download any attachments found on messages to local drive
link_attachments = True # If True, use paths to AWS files. If False, use the file's Discord URL
page_path = f'pages-{channel_name}/' # Path to archived page files
escape_chars = "\\`_{{}}[]<>()+-.!" # Special characters that should be escaped in messages (exception being #, *, and |)
encoding = 'utf-8'
thread_name_len = 32 # Maximum length a thread file 

output = open(f'{channel_name}.md', 'wb')
output.write(f"## Threads index (Sorted by last update)\n\n".encode(encoding))

messages_list = []
thread_ids = []
thread_names = []
thread_files = []

for file in sorted(os.listdir(page_path), key=natural_keys):
    file_data = open(os.path.join(page_path, file), 'rb').read()
    json_data = json.loads(file_data)
    
    for thread in json_data['threads']:
        thread_names.append(thread['name'])
        thread_file_name = (thread['name'][:thread_name_len] + '..') if len(thread['name']) > thread_name_len else thread['name']
        thread_file_name = "".join(c for c in thread_file_name if c.isalpha() or c.isdigit() or c==' ').rstrip().replace(' ', '_')
        thread_file_path = f"threads-{channel_name}/{thread_file_name}_{thread['id']}.md"
        
        thread_file = open(thread_file_path, 'wb')
        thread_file.write(f"# {thread['name']}\n".encode(encoding))
        thread_files.append(thread_file)

        if thread['id'] not in thread_ids:
            output.write(f"### [{thread['name']}]({thread_file_path})\n".encode(encoding))
            print(f"Added thread to list: {thread['name']} ({thread['id']})")
        thread_ids.append(thread['id'])
        
output.close()

for file in reversed(sorted(os.listdir(page_path), key=natural_keys)):
    print(file)
    file_data = open(os.path.join(page_path, file), 'rb').read()
    json_data = json.loads(file_data)

    for message in reversed(json_data['messages']):
        timestamp = message[0]['timestamp']
        username = message[0]['author']['username']
        global_name = message[0]['author']['global_name']
        thread_id = None
        thread_name = None
        thread_file = None
        reply_to = None
        
        if 'message_reference' in message[0]:
            reply_to = message[0]['message_reference']['message_id']

        if message[0]['channel_id'] in thread_ids:
            thread_id = message[0]['channel_id']
            thread_name = thread_names[thread_ids.index(thread_id)]
            thread_file = thread_files[thread_ids.index(thread_id)]

            print(f"Message is part of thread \"{thread_name}\"")
        
        if global_name is None:
            global_name = ""
        
        message_text = message[0]['content']

        for character in escape_chars:
            if character in message_text:
                message_text.replace(character, f"\{character}")
        

        date = datetime.strptime(timestamp[:18], "%Y-%m-%dT%H:%M:%S").strftime("%m/%d/%Y %H:%M")
        formatted_message = ""
        for line in message_text.split('\n'):
            formatted_message += f"\n> {line}"
        
        message_content = f"### {message[0]['id']}\n"
        if reply_to != None:
            message_content += f"### [Replying to {reply_to}](#{reply_to})\n"
            
        message_content += f"## {global_name} ({username}) {date} \n{formatted_message}\n"

        if len(message[0]['attachments']) > 0:
            message_content += "### Attachments: \n"
            for attachment in message[0]['attachments']:
                attachment_downloaded_size = None
                if f"{message[0]['id']}_{attachment['filename']}" in os.listdir(F"files-{channel_name}/"):
                    attachment_downloaded_size = os.stat(f"files-{channel_name}/{message[0]['id']}_{attachment['filename']}").st_size
                    
                if download_attachments == True and f"{message[0]['id']}_{attachment['filename']}" not in os.listdir(F"files-{channel_name}/") and (attachment_downloaded_size < 1024 or attachment_downloaded_size is None):
                    print(f"Downloading attachment: {attachment['url']}")
                    attachment_data = requests.get(attachment['url'])
                    attachment_file = open(f"files-{channel_name}/{message[0]['id']}_{attachment['filename']}", 'wb')
                    attachment_file.write(attachment_data.content)
                    attachment_file.close()
                if link_attachments == True:
                    message_content += f"![{attachment['filename']}]({aws}files-{channel_name}/{message[0]['id']}_{attachment['filename']})\n"
                else:
                    message_content += f"![{attachment['filename']}]({attachment['url']})\n"
        message_content += "\n"
        
        if thread_file != None:
            thread_file.write(message_content.encode(encoding))

for file in thread_files:
    file.close()