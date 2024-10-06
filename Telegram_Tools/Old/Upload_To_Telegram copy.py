import os
import mimetypes
import asyncio
import logging
from datetime import datetime
from telegram import Bot, InputMediaPhoto, InputMediaVideo
from telegram.error import TelegramError, RetryAfter
from telegram.ext import Application
import concurrent.futures

# Configuration for photo upload
photo_bot_token = '6797713581:AAEG-JBvTcx2C_wwQI7yjXd5QNPoyStNi54'
photo_channel_id = '@Indian_all_actress2'
photo_directory_path = 'C:\\Users\\sures\\Downloads\\pictures\\less_than_1MB'

# Configuration for video upload
video_bot_token = '7290601780:AAH-MdVsYdXa_6HdDPkR9f_5kd4VFW5w6sU'
video_channel_id = '@IndianActressVideos2'
video_directory_path = 'C:\\Users\\sures\\Downloads\\Videos\\less_than_2MB'

# Configuration for other files upload (non-photo, non-video)
files_bot_token = '6797713581:AAEG-JBvTcx2C_wwQI7yjXd5QNPoyStNi54'
files_channel_id = '@Indian_all_actress2'
files_directory_path = 'C:\\Users\\sures\\Downloads\\pictures\\less_than_1MB'

# Setup logging globally
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file = f'upload_log_{timestamp}.log'
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info('Logging setup complete.')

# Function to upload photos
async def upload_photos():
    bot = Bot(token=photo_bot_token)
    application = Application.builder().token(photo_bot_token).build()
    photo_group = []
    photo_filenames = []

    logging.info("Total photo files in directory: {}".format(len(os.listdir(photo_directory_path))))

    for filename in os.listdir(photo_directory_path):
        file_path = os.path.join(photo_directory_path, filename)
        if os.path.isfile(file_path):
            file_size = os.path.getsize(file_path)
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type and mime_type.startswith('image'):
                if file_size < 2 * 1024 * 1024:
                    with open(file_path, 'rb') as file:
                        photo_group.append(InputMediaPhoto(file.read(), filename=filename))
                        photo_filenames.append(filename)
                        if len(photo_group) == 10:
                            await send_photos(bot, photo_group, photo_filenames)
                            photo_group = []
                            photo_filenames = []
                            await asyncio.sleep(2)

    if photo_group:
        await send_photos(bot, photo_group, photo_filenames)

    logging.info("All photos processed.")
    await application.shutdown()  # Cleanly shut down the application

# Function to upload videos
async def upload_videos():
    bot = Bot(token=video_bot_token)
    application = Application.builder().token(video_bot_token).build()
    video_group = []
    filenames = []

    logging.info("Total video files in directory: {}".format(len(os.listdir(video_directory_path))))

    for filename in os.listdir(video_directory_path):
        file_path = os.path.join(video_directory_path, filename)
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

    logging.info("All videos processed.")
    await application.shutdown()  # Cleanly shut down the application

# Function to upload other files (non-photo, non-video)
async def upload_files():
    bot = Bot(token=files_bot_token)
    application = Application.builder().token(files_bot_token).build()
    file_group = []
    file_filenames = []

    logging.info("Total files in directory: {}".format(len(os.listdir(files_directory_path))))

    for filename in os.listdir(files_directory_path):
        file_path = os.path.join(files_directory_path, filename)
        if os.path.isfile(file_path):
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type and not mime_type.startswith(('image', 'video')):
                with open(file_path, 'rb') as file:
                    file_group.append(file_path)
                    file_filenames.append(filename)
                    if len(file_group) == 10:  # Upload 10 files at a time
                        await send_files(bot, file_group, file_filenames)
                        file_group = []
                        file_filenames = []
                        await asyncio.sleep(2)

    if file_group:
        await send_files(bot, file_group, file_filenames)

    logging.info("All files processed.")
    await application.shutdown()  # Cleanly shut down the application

# Helper functions to send photos, videos, and files
async def send_photos(bot, photo_group, filenames):
    try:
        await bot.send_media_group(chat_id=photo_channel_id, media=photo_group, connect_timeout=5200, write_timeout=5200, read_timeout=5200)
        logging.info(f"Successfully uploaded a group of {len(photo_group)} photos: {', '.join(filenames)}")
    except RetryAfter as e:
        logging.warning(f"Rate limit exceeded. Retrying in {e.retry_after} seconds. Failed files: {', '.join(filenames)}")
        await asyncio.sleep(e.retry_after)
        await send_photos(bot, photo_group, filenames)
    except TelegramError as e:
        logging.error(f"Failed to upload photo group: {', '.join(filenames)}. Error: {str(e)}")

async def send_videos(bot, video_group, filenames):
    try:
        await bot.send_media_group(chat_id=video_channel_id, media=video_group, connect_timeout=6000, write_timeout=6000, read_timeout=6000)
        logging.info(f"Successfully uploaded a group of {len(video_group)} videos: {', '.join(filenames)}")
    except RetryAfter as e:
        logging.warning(f"Rate limit exceeded. Retrying in {e.retry_after} seconds. Failed files: {', '.join(filenames)}")
        await asyncio.sleep(e.retry_after)
        await send_videos(bot, video_group, filenames)
    except TelegramError as e:
        logging.error(f"Failed to upload video group: {', '.join(filenames)}. Error: {str(e)}")

async def send_files(bot, file_group, filenames):
    for file, filename in zip(file_group, filenames):
        try:
            with open(file, 'rb') as f:
                await bot.send_document(chat_id=files_channel_id, document=f, filename=filename, connect_timeout=5200, write_timeout=5200, read_timeout=5200)
            logging.info(f"Successfully uploaded file: {filename}")
        except RetryAfter as e:
            logging.warning(f"Rate limit exceeded. Retrying in {e.retry_after} seconds. Failed file: {filename}")
            await asyncio.sleep(e.retry_after)
            await send_files(bot, [file], [filename])
        except TelegramError as e:
            logging.error(f"Failed to upload file: {filename}. Error: {str(e)}")

# Main function to run either photo or file uploader along with video uploader
def main():
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        tasks = []
        print("Choose an option:")
        print("1. Upload photos and videos")
        print("2. Upload files and videos")
        choice = input("Enter your choice (1 or 2): ").strip()

        if choice == '1' and os.listdir(photo_directory_path):  # Check if photo directory has files
            tasks.append(loop.run_in_executor(executor, asyncio.run, upload_photos()))
        elif choice == '2' and os.listdir(files_directory_path):  # Check if files directory has files
            tasks.append(loop.run_in_executor(executor, asyncio.run, upload_files()))

        if os.listdir(video_directory_path):  # Check if video directory has files
            tasks.append(loop.run_in_executor(executor, asyncio.run, upload_videos()))

        # Wait for all tasks to complete
        loop.run_until_complete(asyncio.gather(*tasks))

if __name__ == '__main__':
    main()