# Download messages into chunks of Markdown files, while optionally downloading attached files.

import json
import os
import re
from datetime import datetime
import requests
from urllib.parse import urlparse

# Sort files by size of combined number (instead of individual numbers)
def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

aws = "https://yuzudiscordbackup.s3.us-west-2.amazonaws.com/"
channel_name = "yuzu-updates" # Name of the channel being archived (without the pound sign)
download_attachments = False # Download any attachments found on messages to local drive
link_attachments = True # If True, use paths to AWS files. If False, use the file's Discord URL
page_path = f'pages-{channel_name}/' # Path to archived page files
escape_chars = "\\`_{{}}[]<>()+-.!" # Special characters that should be escaped in messages (exception being #, *, and |)
encoding = 'utf-8'
max_messages = 100 # Number of messages that can be included on a single page
message_num = 0 # Do not change
file_message_num = 0 # Do not change
index_num = 0 # Do not change
output = None # Do not change
embed_attachments = True # Embed any attachments included in messages (will not work for all file types)
only_messages_with_files = False # Only includes messages that have (whitelisted) attachments
create_table_of_contents = True # Creates a Table of Contents file at the root of the repo for easy browsing
file_whitelist = None # Set to None to include all files
# Whitelist possibly important files: ['.zip', '.rar', '.7z', '.txt', '.pchtxt']

embed = ''
if embed_attachments:
    embed = '!'

for file in reversed(sorted(os.listdir(page_path), key=natural_keys)):
    print(file)
    file_data = open(os.path.join(page_path, file), 'rb').read()
    json_data = json.loads(file_data)

    for message in reversed(json_data['messages']):
        if file_message_num >= max_messages or output == None:
            if output != None:
                output.write(f"[Next page]({index_num}.md)".encode(encoding))
                output.close()

            path = f'index-{channel_name}/{index_num}.md'
            output = open(path, 'wb')
            output.write(f"# \# {channel_name} (page {index_num})\n\n".encode(encoding))
            file_message_num = 0
            index_num += 1

            print(f"Created new file \"{path}\"")

        timestamp = message[0]['timestamp']
        username = message[0]['author']['username']
        global_name = message[0]['author']['global_name']
        reply_to = None
        num_of_attachments = 0
        
        if 'message_reference' in message[0]:
            reply_to = message[0]['message_reference']['message_id']

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
                if file_whitelist != None:
                    if os.path.splitext(attachment['filename'])[1] not in file_whitelist:
                        continue

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
                    message_content += f"{embed}[{attachment['filename']}]({aws}files-{channel_name}/{message[0]['id']}_{attachment['filename']})\n"
                else:
                    message_content += f"{embed}[{attachment['filename']}]({attachment['url']})\n"
                num_of_attachments += 1
                print(f"Attachment name: {attachment['filename']}")
        message_content += "\n"
        if num_of_attachments > 0 or only_messages_with_files == False:
            output.write(message_content.encode(encoding))
            message_num += 1
            file_message_num += 1

if create_table_of_contents:
    toc = open(f"{channel_name}.md", 'wt', encoding=encoding)
    toc.write(f"# Table of contents for #{channel_name}\n\n")
    for i in range(index_num):
        toc.write(f"### [Page {i}](index-{channel_name}/{i}.md)\n")
    toc.close()

print(f"Added {message_num} messages.")
output.close()
