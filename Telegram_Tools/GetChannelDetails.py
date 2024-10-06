import json
import os
import asyncio
import time
from telethon import errors, functions

# Path to store the last message ID and last downloaded message ID for each channel
LAST_MESSAGE_FILE = 'Channel_Details.json'

# Load the last message IDs from a file
def load_last_message_ids():
    if os.path.exists(LAST_MESSAGE_FILE):
        print("Loading last message IDs from file...")
        with open(LAST_MESSAGE_FILE, 'r') as file:
            return json.load(file)
    print("No last message IDs file found. Starting fresh.")
    return {}

# Save last message IDs to the file
def save_last_message_ids(last_message_ids):
    print(f"Saving last message IDs to {LAST_MESSAGE_FILE}...")
    with open(LAST_MESSAGE_FILE, 'w') as file:
        json.dump(last_message_ids, file, indent=4)

# Helper function to create unique keys for channel names and numeric IDs
def get_channel_key(channel_entity):
    # If the entity has a username, use it as the key
    if channel_entity.username:
        return f"user_{channel_entity.username}"
    # If the entity is numeric (ID), prefix it with 'id_'
    return f"id_{channel_entity.id}"

# Update the last message ID, last downloaded message ID, and unread count for a specific channel
def update_message_ids(channel_key, channel_id, channel_name, description=None, last_message_id=None, last_downloaded_message_id=None, unread_count=None, last_message_ids=None, dialog_id=None):
    # Ensure that the value for this channel is a dictionary
    if channel_key not in last_message_ids or not isinstance(last_message_ids[channel_key], dict):
        last_message_ids[channel_key] = {}

    # Update the fields for the channel
    last_message_ids[channel_key].update({
        "id": channel_id,
        "Channel_Name": channel_name,
        "Description": description,
        "last_message_id": last_message_id,
        "last_downloaded_message_id": last_downloaded_message_id,
        "unread_count": unread_count,
        "dialog_id": dialog_id
    })

# Retry mechanism with exponential backoff
async def retry_fetch(fetch_func, retries=3, delay=1):
    for attempt in range(retries):
        try:
            return await fetch_func()
        except (errors.FloodWaitError, errors.TimeoutError, errors.RPCError) as e:
            print(f"Error: {e}. Retrying in {delay} seconds...")
            await asyncio.sleep(delay)
            delay *= 2  # Exponential backoff
    print(f"Failed to fetch data after {retries} retries.")
    return None

# Get all channels and fetch the last message ID and unread count for each channel
async def get_all_channels(client):
    channels = []
    failed_channels = []
    last_message_ids = load_last_message_ids()  # Load existing data from the file

    print("Fetching your joined channels...")
    async for dialog in client.iter_dialogs():
        if dialog.is_channel:  # Filter for channels only
            channel_name = dialog.name
            channel_entity = dialog.entity  # Get the channel entity (ID, username, etc.)
            unread_count = dialog.unread_count
            dialog_id = dialog.id
            
            # Create a unique key for the channel (using username or ID with prefix)
            channel_key = get_channel_key(channel_entity)
            channel_id = channel_entity.id
            
            print(f"Processing channel: {channel_name} (Key: {channel_key})...")
            
            # Fetch the channel description
            async def fetch_description():
                # Some channels might not have a description; handle gracefully
                try:
                    full_channel = await client(functions.channels.GetFullChannelRequest(channel_entity))
                    return full_channel.full_chat.about or "No description available."
                except Exception as e:
                    print(f"Failed to fetch description for {channel_name}: {e}")
                    return "Description not available."

            description = await retry_fetch(fetch_description, retries=3, delay=2)

            # Function to fetch the last message
            async def fetch_last_message():
                return await client.get_messages(dialog.id, limit=1)

            # Try to fetch the last message using retry mechanism
            last_message = await retry_fetch(fetch_last_message, retries=3, delay=2)

            if last_message:
                last_message_id = last_message[0].id
                #print(f"Last message ID for {channel_name}: {last_message_id}")
            else:
                print(f"Failed to fetch last message for {channel_name}. Adding to failed channels list.")
                failed_channels.append(channel_name)
                continue  # Skip updating the JSON if fetching failed

            # Check if this channel is new in the JSON, initialize last_downloaded_message_id
            if channel_key not in last_message_ids:
                last_downloaded_message_id = last_message_id
                print(f"New channel detected. Setting last_downloaded_message_id to {last_message_id} for {channel_name}.")
            else:
                last_downloaded_message_id = last_message_ids[channel_key].get('last_downloaded_message_id', last_message_id)

            print(f"Unread Count for {channel_name}: {unread_count}")

            # Update the JSON data with last message ID, last downloaded message ID, and unread count
            update_message_ids(
                channel_key, 
                channel_id=channel_id, 
                channel_name=channel_name, 
                description=description,
                last_message_id=last_message_id, 
                last_downloaded_message_id=last_downloaded_message_id-unread_count,  
                unread_count=unread_count, 
                last_message_ids=last_message_ids,
                dialog_id=dialog_id
            )

            # Append channel details to list
            channels.append({
                "channel_name": channel_name,
                "channel_key": channel_key,
                "description": description,
                "last_message_id": last_message_id,
                "last_downloaded_message_id": last_downloaded_message_id-unread_count,
                "unread_count": unread_count,
                "dialog_id": dialog_id
            })

    print("Finished processing channels.")
    save_last_message_ids(last_message_ids)  # Save the updated data to the file
    return channels, failed_channels

async def update_channel_info(client):
    start_time = time.time()  # Start tracking time
    print("Fetching channel details...")
    channels, failed_channels = await get_all_channels(client)

    # Print out the names, last message IDs, unread counts, and last downloaded message IDs of the channels
    print("\nJoined Channels with Last Message Info:")
    for channel in channels:
        if channel["unread_count"] > 0:
            print(f"Channel Name: {channel['channel_name']}, "
                  f"Key: {channel['channel_key']}, "
                  f"Last Message ID: {channel['last_message_id']}, "
                  f"Last Downloaded Message ID: {channel['last_downloaded_message_id']}, "
                  f"Unread Count: {channel['unread_count']}, "
                  f"Dialog ID: {channel['dialog_id']}")

    # Print out channels where fetching details failed
    if failed_channels:
        print("\nChannels where fetching details failed:")
        for channel in failed_channels:
            print(f"Channel Name: {channel}")

    # Calculate and print the elapsed time
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\nTotal time elapsed: {elapsed_time:.2f} seconds.")

