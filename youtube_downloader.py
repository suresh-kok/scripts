import os
import requests
from pytube import YouTube

def sanitize_filename(filename):
    """
    Sanitize the filename by removing or replacing invalid characters.
    """
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    return filename

def extract_hashtags(title):
    """
    Generate possible hashtags from the title.
    """
    words = title.split()
    hashtags = ['#' + word.strip(',.!?') for word in words if word.lower() not in ['and', 'or', 'the', 'in', 'on', 'for', 'with']]
    return ' '.join(hashtags[:5])  # Limit to first 5 hashtags

def download_youtube_video(url, save_path):
    """
    Download the highest resolution of a YouTube video, its thumbnail,
    and save its title, description, and hashtags in a text file.
    
    :param url: URL of the YouTube video.
    :param save_path: Path where the video, thumbnail, and text file will be saved.
    """
    yt = YouTube(url)

    # Download the highest resolution video
    video_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    if video_stream:
        video_filename = sanitize_filename(video_stream.default_filename)
        video_stream.download(save_path, filename=video_filename)
        print(f"Video downloaded: {video_filename}")
    else:
        print("No suitable video stream found.")

    # Download the thumbnail
    thumbnail_url = yt.thumbnail_url
    if thumbnail_url:
        response = requests.get(thumbnail_url)
        if response.status_code == 200:
            sanitized_title = sanitize_filename(yt.title)
            thumbnail_path = os.path.join(save_path, sanitized_title + '.jpg')
            with open(thumbnail_path, 'wb') as file:
                file.write(response.content)
            print(f"Thumbnail downloaded: {thumbnail_path}")
        else:
            print("Failed to download thumbnail.")
    else:
        print("No thumbnail URL found.")

    # Save title, description, and hashtags to a text file
    # Save title, description, and hashtags to a text file
    text_file_path = os.path.join(save_path, sanitized_title + '.txt')
    with open(text_file_path, 'w', encoding='utf-8') as file:
        file.write("Title: \n" + yt.title + "\n\n")
        
        # Check if the description is None and handle it
        description = yt.description or "No description available."
        file.write("Description: \n" + description + "\n\n")
        
        hashtags = extract_hashtags(yt.title)
        file.write("Possible Hashtags: \n" + hashtags)
        file.write("Link: \n" + url + "\n\n")
    print(f"Details saved: {text_file_path}")


# List of YouTube video URLs
video_urls = [
    'https://www.youtube.com/watch?v=Lh93IVFQU-Q&pp=ygULYmFieSByaHltZXM%3D',
    'https://www.youtube.com/watch?v=HD7MGnQdk5w&pp=ygULYmFieSByaHltZXM%3D',
    'https://www.youtube.com/watch?v=SBoW30afTjU&pp=ygULYmFieSByaHltZXM%3D',
    'https://www.youtube.com/watch?v=eEKtlJbA868&pp=ygULYmFieSByaHltZXM%3D',
    'https://www.youtube.com/watch?v=eEKtlJbA868&pp=ygULYmFieSByaHltZXM%3D',
    'https://www.youtube.com/watch?v=sB4WXg7KYWE&pp=ygULYmFieSByaHltZXM%3D',
    'https://www.youtube.com/watch?v=CprNa5NrrUo&pp=ygULYmFieSByaHltZXM%3D',
    'https://www.youtube.com/watch?v=NjaCF2mxAmY&pp=ygULYmFieSByaHltZXM%3D',
    'https://www.youtube.com/watch?v=Wfg0p3HTZ2o&pp=ygULYmFieSByaHltZXM%3D',
    'https://www.youtube.com/watch?v=p5zqbg-HF2E&pp=ygULYmFieSByaHltZXM%3D',
    'https://www.youtube.com/watch?v=iOos6lMDpMg&pp=ygULYmFieSByaHltZXM%3D',
    'https://www.youtube.com/watch?v=a3h7FdJuCpw&pp=ygULYmFieSByaHltZXM%3D',
    'https://www.youtube.com/watch?v=0wJtGT8e7I8&pp=ygULYmFieSByaHltZXM%3D',
    'https://www.youtube.com/watch?v=f7I4xsQtOH0&pp=ygULYmFieSByaHltZXM%3D',
    'https://www.youtube.com/watch?v=8-8Fnme0b3M&pp=ygULYmFieSByaHltZXM%3D',
    'https://www.youtube.com/watch?v=S8t8U7aOc9s&pp=ygULYmFieSByaHltZXM%3D',
    'https://www.youtube.com/watch?v=ppWS86eYyJE&pp=ygULYmFieSByaHltZXM%3D',
    'https://www.youtube.com/watch?v=A2vBJbh87Wk&pp=ygULYmFieSByaHltZXM%3D',
]

destination_folder = 'C:\\Users\\sures\\OneDrive\\Desktop\\scripts\\YouTube Videos'  # Replace with your destination folder path

if not os.path.exists(destination_folder):
    os.makedirs(destination_folder)

# Process each video URL
for url in video_urls:
    download_youtube_video(url, destination_folder)
