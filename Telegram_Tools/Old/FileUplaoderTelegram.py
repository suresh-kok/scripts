from datetime import datetime
import os
import mimetypes
import asyncio
import logging
from telegram import Bot, InputMediaPhoto
from telegram.error import TelegramError, RetryAfter
from telegram.ext import Application

# Configuration
bot_token = '6797713581:AAEG-JBvTcx2C_wwQI7yjXd5QNPoyStNi54'
channel_id = '@Indian_all_actress2'
directory_path = 'C:\\Users\\sures\\Downloads\\pictures\\less_than_1MB'

# Setup logging
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_filename = f'upload_log_{timestamp}.log'
logging.basicConfig(filename=log_filename, level=logging.INFO)

async def send_photos(bot, photo_group, filenames):
    try:
        await bot.send_media_group(chat_id=channel_id, media=photo_group, connect_timeout=5200, write_timeout=5200, read_timeout=5200)
        logging.info(f"Successfully uploaded a group of {len(photo_group)} photos: {', '.join(filenames)}")
        print(f"Successfully uploaded a group of {len(photo_group)} photos: {', '.join(filenames)}")
        print("----------------------------------------------------------------")
        logging.info("----------------------------------------------------------------")
    except RetryAfter as e:
        logging.warning(f"Rate limit exceeded. Retrying in {e.retry_after} seconds. Failed files: {', '.join(filenames)}")
        print(f"Rate limit exceeded. Retrying in {e.retry_after} seconds. Failed files: {', '.join(filenames)}")
        await asyncio.sleep(e.retry_after)
        await send_photos(bot, photo_group, filenames)
    except TelegramError as e:
        logging.error("*******************************************************************************")
        logging.error(f"Failed to upload photo group: {', '.join(filenames)}. Error: {str(e)}")
        logging.error("*******************************************************************************")
        print(f"Failed to upload photo group: {', '.join(filenames)}. Error: {str(e)}")
        print("*******************************************************************************")

async def send_files(bot, files, filenames):
    for file, filename in zip(files, filenames):
        try:
            with open(file, 'rb') as f:
                await bot.send_document(chat_id=channel_id, document=f, filename=filename, connect_timeout=5200, write_timeout=5200, read_timeout=5200)
            logging.info(f"Successfully uploaded file: {filename}")
            print(f"Successfully uploaded file: {filename}")
        except RetryAfter as e:
            logging.warning(f"Rate limit exceeded. Retrying in {e.retry_after} seconds. Failed file: {filename}")
            print(f"Rate limit exceeded. Retrying in {e.retry_after} seconds. Failed file: {filename}")
            await asyncio.sleep(e.retry_after)
            await send_files(bot, [file], [filename])
        except TelegramError as e:
            logging.error(f"Failed to upload file: {filename}. Error: {str(e)}")
            print(f"Failed to upload file: {filename}. Error: {str(e)}")

async def upload_files():
    bot = Bot(token=bot_token)
    application = Application.builder().token(bot_token).build()
    print("*******************************************************************************")
    photo_group = []
    photo_filenames = []
    file_group = []
    file_filenames = []
    print("Total files in directory: {}".format(len(os.listdir(directory_path))))

    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
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
                else:
                    file_group.append(file_path)
                    file_filenames.append(filename)
                    if len(file_group) == 10:
                        await send_files(bot, file_group, file_filenames)
                        file_group = []
                        file_filenames = []
                        await asyncio.sleep(2)

    if photo_group:
        await send_photos(bot, photo_group, photo_filenames)

    if file_group:
        await send_files(bot, file_group, file_filenames)
    
    logging.info("All files processed.")
    await application.shutdown()  # Cleanly shut down the application

if __name__ == '__main__':
    asyncio.run(upload_files())