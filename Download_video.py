from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from pytube import YouTube
import time

# Set up WebDriver (ensure the correct path to your WebDriver)
webdriver_path = 'C:\\chromedriver-win64\\chromedriver.exe'  # Replace with the path to your WebDriver
service = Service(webdriver_path)
driver = webdriver.Chrome(service=service)

# URL of the page containing the video
url = 'https://hianime.to/watch/dragon-ball-z-325?ep=7399&ep=7399'  # Replace with the URL of the page with the video

# Browse the page
driver.get(url)

# Wait for the page to load (adjust the time if necessary)
time.sleep(5)

# Get the video URL from the page (YouTube example)
video_url = driver.current_url

# Close the browser
driver.quit()

# Download the video using pytube
def download_highest_quality_video(video_url):
    yt = YouTube(video_url)
    stream = yt.streams.get_highest_resolution()
    print(f"Downloading: {yt.title}")
    stream.download()
    print(f"Downloaded: {yt.title}")

download_highest_quality_video(video_url)
