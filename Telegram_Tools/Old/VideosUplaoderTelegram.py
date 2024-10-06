from datetime import datetime
import os
import mimetypes
import asyncio
import logging
from telegram import Bot, InputMediaVideo
from telegram.error import TelegramError, RetryAfter
from telegram.ext import Application

# Configuration
bot_token = '7290601780:AAH-MdVsYdXa_6HdDPkR9f_5kd4VFW5w6sU'
channel_id = '@IndianActressVideos2'
directory_path = 'C:\\Users\\sures\\Downloads\\Videos\\less_than_2MB'

# Setup logging
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_filename = f'video_upload_log_{timestamp}.log'
logging.basicConfig(filename=log_filename, level=logging.INFO)

async def send_videos(bot, video_group, filenames):
    start_time = datetime.now()
    try:
        await bot.send_media_group(chat_id=channel_id, media=video_group, connect_timeout=6000, write_timeout=6000, read_timeout=6000)
        logging.info(f"Successfully uploaded a group of {len(video_group)} videos: {', '.join(filenames)}")
        print(f"Successfully uploaded a group of {len(video_group)} videos: {', '.join(filenames)}")
        print("----------------------------------------------------------------")
        logging.info("----------------------------------------------------------------")
    except RetryAfter as e:
        logging.warning(f"Rate limit exceeded. Retrying in {e.retry_after} seconds. Failed files: {', '.join(filenames)}")
        print(f"Rate limit exceeded. Retrying in {e.retry_after} seconds. Failed files: {', '.join(filenames)}")
        await asyncio.sleep(e.retry_after)
        await send_videos(bot, video_group, filenames)
    except TelegramError as e:
        print("*******************************************************************************")
        logging.error("*******************************************************************************")
        logging.error(f"Failed to upload video group: {', '.join(filenames)}. Error: {str(e)}")
        logging.error("*******************************************************************************")
        print(f"Failed to upload video group: {', '.join(filenames)}. Error: {str(e)}")
        print("*******************************************************************************")
    finally:
        end_time = datetime.now()
        time_taken = (end_time - start_time).total_seconds()
        logging.info(f"Time taken to upload batch: {time_taken} seconds")
        print(f"Time taken to upload batch: {time_taken} seconds")
        print("----------------------------------------------------------------")
        logging.info("----------------------------------------------------------------")

async def upload_files():
    bot = Bot(token=bot_token)
    application = Application.builder().token(bot_token).build()

    video_group = []
    filenames = []
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            file_size = os.path.getsize(file_path)
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type and mime_type.startswith('video') and file_size < 50 * 1024 * 1024:  # Ensure file size is less than 50MB
                with open(file_path, 'rb') as file:
                    video_group.append(InputMediaVideo(file.read(), filename=filename))
                    filenames.append(filename)
                    if len(video_group) == 10:  # Upload 10 videos at a time
                        await send_videos(bot, video_group, filenames)
                        video_group = []
                        filenames = []
                        await asyncio.sleep(2)

    if video_group:
        await send_videos(bot, video_group, filenames)
    
    logging.info("All files processed.")
    await application.shutdown()  # Cleanly shut down the application

if __name__ == '__main__':
    asyncio.run(upload_files())
