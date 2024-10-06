from telethon import TelegramClient, events, sync
import os

# Replace these with your own values
api_id = '22504785'
api_hash = 'da85264ce2cd03b0108c2ade7d55388b'
source_channel_username = 'source_channel_username'  # e.g., @sourcechannel
destination_channel_username = 'destination_channel_username'  # e.g., @destinationchannel

# Create the client and connect
client = TelegramClient('session_name', api_id, api_hash)

async def main():
    await client.start()

    # Get the source and destination channels
    source_channel = await client.get_entity(source_channel_username)
    destination_channel = await client.get_entity(destination_channel_username)

    # Iterate through the messages in the source channel
    async for message in client.iter_messages(source_channel):
        # If the message has a file (photo, document, etc.)
        if message.media:
            # Forward the message with the media to the destination channel
            await client.send_message(destination_channel, message)

# Start the event loop to run the main function
with client:
    client.loop.run_until_complete(main())

print("All files have been copied successfully!")
