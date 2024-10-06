import json
import os
import re
import math
import mimetypes
import asyncio
import argparse
from telethon import TelegramClient, types
from telethon.errors import FloodWaitError, TimeoutError, FileMigrateError, RPCError
from PIL import Image
from GetChannelDetails import update_channel_info

# Path to store the last message ID for each channel
LAST_MESSAGE_FILE = 'Channel_Details.json'
CONFIG_FILE = 'Telegram_Channels_Config.json'
# Number of concurrent downloads (tweak based on your needs and network speed)
CONCURRENT_DOWNLOADS = 8
# Maximum retries for timeout errors
MAX_RETRIES = 3

# Load the Telegram API configuration from the JSON file
with open(CONFIG_FILE, 'r') as file:
    config_data = json.load(file)

# Access the data
api_id = config_data['api_id']
api_hash = config_data['api_hash']
full_download_channels = config_data['FULL_DOWNLOAD_CHANNELS']
unread_download_channels = config_data['UNREAD_DOWNLOAD_CHANNELS']
n_download_channels = config_data['N_DOWNLOAD_CHANNELS']

# Load the last message IDs from a file
def load_last_message_ids():
    if os.path.exists(LAST_MESSAGE_FILE):
        with open(LAST_MESSAGE_FILE, 'r') as file:
            return json.load(file)
    return {}

# Save last message IDs to the file
def save_last_message_ids(last_message_ids):
    with open(LAST_MESSAGE_FILE, 'w') as file:
        json.dump(last_message_ids, file, indent=4)

def extract_channel_name(key):
    if key.startswith('user_'):
        return key.replace('user_', '', 1)
    #elif key.startswith('id_'):
    #    return key.replace('id_', '', 1)
    return key

# Update the last message ID and last downloaded message ID for a specific channel
def update_message_ids(channel_username, last_message_id=None, last_downloaded_message_id=None, last_message_ids=None):
    if channel_username not in last_message_ids or not isinstance(last_message_ids[channel_username], dict):
        last_message_ids[channel_username] = {}

    if last_message_id:
        last_message_ids[channel_username]['last_message_id'] = last_message_id
    if last_downloaded_message_id:
        last_message_ids[channel_username]['last_downloaded_message_id'] = last_downloaded_message_id

# Sanitize the channel name to create a safe folder name
def sanitize_channel_name(channel_name):
    return re.sub(r'[<>:"/\\|?*]', '_', channel_name)

# Convert size in bytes to a human-readable format
def human_readable_size(size_in_bytes):
    if size_in_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size_in_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_in_bytes / p, 2)
    return f"{s} {size_name[i]}"

# Create the download folder based on the channel name
def create_download_folder(channel_name):
    sanitized_channel_name = sanitize_channel_name(channel_name)
    download_folder = os.path.join('downloads', sanitized_channel_name)
    os.makedirs(download_folder, exist_ok=True)
    return download_folder

# Download media from a message
async def download_media(message, client, download_folder, retries=0):
    file_name = None
    file_extension = None
    new_size = None

    if isinstance(message.media, types.MessageMediaPhoto):
        file_extension = ".jpg"
        file_name = f"photo_{message.id}{file_extension}"
    elif isinstance(message.media, types.MessageMediaDocument):
        file_extension = mimetypes.guess_extension(message.media.document.mime_type) or ".bin"
        new_size = message.media.document.size  # Get the size for documents
        for attribute in message.media.document.attributes:
            if isinstance(attribute, types.DocumentAttributeFilename):
                file_name = attribute.file_name
                break
        if not file_name:
            file_name = f"document_{message.id}{file_extension}"
    elif isinstance(message.media, types.MessageMediaWebPage):
        print(f"Skipping web page preview: {message.id}")
        return  # Skip web page previews
    elif isinstance(message.media, types.MessageMediaPoll):
        print(f"Skipping poll: {message.id}")
        return  # Skip polls
    elif isinstance(message.media, types.MessageMediaUnsupported):
        print(f"Skipping unsupported media type: {message.id}")
        return  # Skip unsupported media types
    else:
        print(f"Skipping unknown media type: {message.id}")
        return  # Skip any other unknown media types

    file_path = os.path.join(download_folder, file_name)

    # Check if the file already exists
    if os.path.exists(file_path):
        existing_size = os.path.getsize(file_path)

        # For images, compare dimensions
        if isinstance(message.media, types.MessageMediaPhoto):
            with Image.open(file_path) as img:
                width, height = img.size
            if width == message.media.photo.sizes[-1].w and height == message.media.photo.sizes[-1].h:
                print(f"Skipping duplicate image: {file_path}")
                return

        # For other files, compare sizes
        if new_size is not None:
            existing_size_hr = human_readable_size(existing_size)
            new_size_hr = human_readable_size(new_size)

            if existing_size == new_size:
                print(f"Existing file size: {existing_size_hr}, new file size: {new_size_hr} Skipping duplicate file: {file_path}")
                return
        else:
            print(f"Skipping file comparison for types that don't have size metadata.")

    original_file_name = file_name
    file_path = os.path.join(download_folder, file_name)
    counter = 1
    while os.path.exists(file_path):
        file_name_without_ext, file_ext = os.path.splitext(original_file_name)
        file_name = f"{file_name_without_ext}_{counter}{file_ext}"
        file_path = os.path.join(download_folder, file_name)
        counter += 1

    if new_size is not None:
        if new_size > 300000000: # 300MB
            print(f"Skipping large file: {file_path} of size {human_readable_size(new_size)}")
            return
        else:
            print(f'Downloading {file_name} ({human_readable_size(new_size)}) to {file_path}...')
    else:
        print(f'Downloading {file_name} to {file_path}...')

    try:
        await client.download_media(message.media, file_path)
        print(f'Download complete: {file_name}')
    except FloodWaitError as e:
        print(f'Rate limit exceeded, sleeping for {e.seconds} seconds...')
        await asyncio.sleep(e.seconds)
        await download_media(message, client, download_folder)
    except FileMigrateError as e:
        print(f'File is located in DC {e.new_dc}, reconnecting and retrying...')
        await client.disconnect()
        client = TelegramClient('session_name', api_id, api_hash, dc_id=e.new_dc)
        await client.start()
        await download_media(message, client, download_folder)
    except TimeoutError as e:
        if retries < MAX_RETRIES:
            print(f'Timeout occurred. Retrying {retries + 1}/{MAX_RETRIES} for {file_name}...')
            await asyncio.sleep(2 ** retries)  # Exponential backoff
            await download_media(message, client, download_folder, retries + 1)
        else:
            print(f'Failed to download {file_name} after {MAX_RETRIES} retries due to timeout.')
    except RPCError as e:
        print(f'RPCError encountered: {str(e)}. Retrying...')
        if retries < MAX_RETRIES:
            await asyncio.sleep(2 ** retries)  # Exponential backoff
            await download_media(message, client, download_folder, retries + 1)
        else:
            print(f'Failed to download {file_name} after {MAX_RETRIES} retries due to RPCError.')

async def download_files(client, channel_username, limit=None, min_id=0):
    download_folder = create_download_folder(channel_username)

    try:
        # Check if the channel is an ID or a username
        if channel_username.startswith("id_"):
            # If it starts with 'id_', strip the prefix and convert the rest to an integer
            channel_id = int(channel_username.replace("id_", ""))
            entity = await client.get_input_entity(channel_id)
        elif channel_username.startswith("user_"):
            # If it's a username, pass it as it is (without 'user_' prefix)
            username = channel_username.replace("user_", "")
            entity = await client.get_input_entity(username)
        else:
            # Otherwise, just use it as-is (for normal usernames or IDs)
            entity = await client.get_input_entity(channel_username)
    except ValueError as e:
        # Handle the case where the entity does not exist or is not accessible
        print(f"Error: Cannot find any entity corresponding to {channel_username}. Details: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while fetching the entity for {channel_username}: {e}")
        return None

    # Separate messages into images, files, and videos
    image_messages = []
    file_messages = []
    video_messages = []
    other_messages = [] 
    
    # Fetch messages with the given limit or min_id
    async for message in client.iter_messages(entity, limit=limit, min_id=min_id):
        if isinstance(message.media, types.MessageMediaPhoto):
            image_messages.append(message)
        elif isinstance(message.media, types.MessageMediaDocument):
            file_messages.append(message)
        elif isinstance(message.media, types.MessageMediaUnsupported):
            other_messages.append(message)  # Track unsupported messages to mark them as read
        elif isinstance(message.media, types.MessageMediaWebPage):
            other_messages.append(message)  # Track web page messages to mark them as read
        else:
            video_messages.append(message)

    print(f"Image Messages Count: %d" % len(image_messages))
    print(f"File Messages Count: %d" % len(file_messages))
    print(f"Video Messages Count: %d" % len(video_messages))
    print(f"Other Messages Count: {len(other_messages)}")

    # Function to handle concurrent downloads
    async def download_messages(messages, download_folder, message_type):
        for i in range(0, len(messages), CONCURRENT_DOWNLOADS):
            batch = messages[i:i + CONCURRENT_DOWNLOADS]
            print(f"Downloading {len(batch)} {message_type}... Remaining: {len(messages) - (i+CONCURRENT_DOWNLOADS) if (len(messages) - (i+CONCURRENT_DOWNLOADS)) > 0 else 0}")
            await asyncio.gather(*(download_media(msg, client, download_folder) for msg in batch))
            await client.send_read_acknowledge(entity, message=batch)

    # Download images first
    if image_messages:
        await download_messages(image_messages, download_folder, 'images')
    
    # Download files next
    if file_messages:
        await download_messages(file_messages, download_folder, 'files')
    
    # Download videos last
    if video_messages:
        await download_messages(video_messages, download_folder, 'videos')

    # If there are no media files to download, mark the other messages as read
    if not (image_messages or file_messages or video_messages):
        if other_messages:
            print(f"Marking {len(other_messages)} other messages as read...")
            await client.send_read_acknowledge(entity, message=other_messages)
        else:
            # If no other messages, mark up to the min_id as read
            await client.send_read_acknowledge(entity, max_id=min_id)

    # Return the last downloaded message ID
    if image_messages or file_messages or video_messages:
        return max(msg.id for msg in (image_messages + file_messages + video_messages))
    return None

# Download unread messages for a list of channels
async def download_unread_messages(client, last_message_ids, update_info=False):
    if update_info:
        print("Updating unread messages for channels")
        await update_channel_info(client)
    else:
        print("Downloading unread messages for channels")
    
    last_message_ids = load_last_message_ids()

    """Download unread messages for channels specified in DEFAULT_CHANNELS."""
    for key, data in last_message_ids.items():
        # Extract the actual channel name
        extracted_channel_name = extract_channel_name(key)
        # Check if the extracted channel name is in the DEFAULT_CHANNELS list
        if extracted_channel_name in unread_download_channels:
            # Check if the channel has the necessary fields
            if 'last_message_id' in data and 'unread_count' in data:
                total_messages = data['last_message_id']
                last_downloaded_message_id = data['last_downloaded_message_id']
                unread_count = data['unread_count']

                # Calculate the ID to start downloading from
                if total_messages and unread_count > 0:
                    start_message_id = last_downloaded_message_id
                    print(f"Channel: {data['Channel_Name']}({extracted_channel_name}) - Total messages: {total_messages}, Unread count: {unread_count}")
                    print(f"Starting download from message ID: {start_message_id + 1}")
                    
                    # Download messages after the calculated last downloaded message ID
                    await download_files(client, extracted_channel_name, min_id=start_message_id)
                    
                    # Update the last downloaded message ID to the most recent one
                    update_message_ids(key, last_downloaded_message_id=total_messages, last_message_ids=last_message_ids)
                    save_last_message_ids(last_message_ids)
                else:
                    print(f"No unread messages for {extracted_channel_name} or invalid data.")
            else:
                print(f"Skipping {extracted_channel_name} due to missing necessary data (last_message_id or unread_count).")
            print(f"--------------------------------Processed channel {extracted_channel_name} --------------------------------------------")

# Download all messages from a channel
async def download_all_messages(client, last_message_ids):
    for channel_username in full_download_channels:
        print(f"Downloading unread messages from: {channel_username}")
        last_downloaded_message_id = await download_files(client, channel_username)
        if last_downloaded_message_id:
            update_message_ids(channel_username, last_downloaded_message_id=last_downloaded_message_id, last_message_ids=last_message_ids)
        save_last_message_ids(last_message_ids)

# Download the last N messages from a channel
async def download_last_n_messages(client, last_message_ids, n):
    for channel_username in n_download_channels:
        print(f"Downloading unread messages from: {channel_username}")
        last_downloaded_message_id = await download_files(client, channel_username, limit=n)
        if last_downloaded_message_id:
            update_message_ids(channel_username, last_downloaded_message_id=last_downloaded_message_id, last_message_ids=last_message_ids)
        save_last_message_ids(last_message_ids)

# Main function
async def main(mode, num_messages=None, update_info=False):
    client = TelegramClient('session_name', api_id, api_hash)
    await client.start()

    # Load last message IDs from file
    last_message_ids = load_last_message_ids()

    if mode == 'unread':
        await download_unread_messages(client, last_message_ids, update_info=update_info)
    elif mode == 'all':
        await download_all_messages(client, last_message_ids)
    elif mode == 'last_n':
        await download_last_n_messages(client, last_message_ids, num_messages)
    elif mode == 'update_info':
        await update_channel_info(client)

    await client.disconnect()

# Entry point for the script
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Telegram Channel Media Downloader")
    parser.add_argument('--mode', required=True, choices=['all', 'last_n', 'unread', 'update_info'], help="Select mode to download files")
    parser.add_argument('--num', type=int, help="Number of messages to download (only for 'last_n' mode)")
    parser.add_argument('--update', action='store_true', help="Update channel information before downloading unread messages")
    args = parser.parse_args()

    if args.mode == 'last_n' and not args.num:
        parser.error('You must specify --num when using "last_n" mode.')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args.mode, args.num, update_info=args.update))
