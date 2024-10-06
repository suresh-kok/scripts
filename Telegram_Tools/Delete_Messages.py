from telethon import TelegramClient
from datetime import datetime, timedelta, timezone

# Define your Telegram API credentials
api_id = '22504785'
api_hash = 'da85264ce2cd03b0108c2ade7d55388b'
phone_number = '+919907156350'

# Create a Telegram client
client = TelegramClient('session_name', api_id, api_hash)

# Chat or channel username or ID
chat_id = 'Indian_all_actress2'

# Date to delete messages (year, month, day)
target_date = datetime(2024, 9, 8)


# Calculate the start and end of the target day with UTC timezone (offset-aware)
start_date = target_date.replace(tzinfo=timezone.utc)
end_date = (target_date + timedelta(days=1)).replace(tzinfo=timezone.utc)



async def delete_media_messages_on_date():
    async with client:
        count = 0
        async for message in client.iter_messages(chat_id):
            # Check if the message was sent by the user and is within the target date range
            if start_date <= message.date < end_date and message.media:
                print(f"Deleting media message from {message.date}: {message.media}")
                await message.delete()
                count += 1

            # Stop after deleting the first 5 messages and ask for confirmation
            if count == 5:
                confirm = input("Do you want to continue deleting messages? (yes/no): ").strip().lower()
                if confirm != 'yes':
                    print("Stopping deletion process.")
                    return
                else:
                    count = 0  # Reset counter for the next batch

        print("All matching media messages processed.")

# Run the client
with client:
    client.loop.run_until_complete(delete_media_messages_on_date())