import os
import asyncio
from moviepy.editor import VideoFileClip, ImageClip, TextClip, concatenate_videoclips, CompositeVideoClip, AudioFileClip
from moviepy.config import change_settings
from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment

# Specify the path to the ImageMagick binary
change_settings({"IMAGEMAGICK_BINARY": "C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"})

# Function to create a text clip
def create_text_clip(text, duration, font_size=70, color='white', bg_color='black'):
    txt_clip = TextClip(text, fontsize=font_size, color=color, font='Amiri-Bold', bg_color=bg_color)
    txt_clip = txt_clip.set_duration(duration)
    return txt_clip

# Function to create timed text clips based on AI timings
def create_timed_text_clips(timings, font_size=70, color='white', bg_color='black'):
    clips = []
    for word, start, end in timings:
        clip = TextClip(word, fontsize=font_size, color=color, font='Amiri-Bold', bg_color=bg_color)
        clip = clip.set_position(("center", "center")).set_start(start).set_duration(end - start)
        clips.append(clip)
    return clips

# Function to create audio from text
def create_audio_clip(text, filename):
    tts = gTTS(text=text, lang='en')
    tts.save(filename)
    return AudioFileClip(filename)

# Function to get word timings using speech_recognition
def get_word_timings(audio_path):
    r = sr.Recognizer()
    audio = AudioSegment.from_file(audio_path)
    audio.export("temp.wav", format="wav")

    with sr.AudioFile("temp.wav") as source:
        audio_data = r.record(source)
        response = r.recognize_google(audio_data, show_all=True)

    timings = []
    if 'alternative' in response:
        for word_info in response['alternative'][0]['words']:
            word = word_info['word']
            start = word_info['startTime']['seconds'] + word_info['startTime']['nanos'] * 1e-9
            end = word_info['endTime']['seconds'] + word_info['endTime']['nanos'] * 1e-9
            timings.append((word, start, end))

    os.remove("temp.wav")
    return timings

# Load images and set duration, resizing to fit the screen
def load_and_resize_image(image_path, duration, screen_size):
    img = ImageClip(image_path).set_duration(duration)
    img = img.resize(height=screen_size[1]).margin(color=(0,0,0))
    return img

screen_size = (1280, 720)
image1 = load_and_resize_image("C:\\Users\\sures\\Downloads\\Telegram Desktop\\1719027444582.jpg", 10, screen_size)
image2 = load_and_resize_image("C:\\Users\\sures\\Downloads\\Telegram Desktop\\Untitled (4).jpg", 10, screen_size)

# Text and audio content
text1 = "Yoga is good for Improving flexibility, strength, balance, and joint health"
text2 = "Going to the gym can have several benefits for your physical and mental health. These benefits include Boosting your health and energy levels"

# Generate audio clips
audio1_path = "audio1.mp3"
audio2_path = "audio2.mp3"
audio1 = create_audio_clip(text1, audio1_path)
audio2 = create_audio_clip(text2, audio2_path)

# Get word timings using speech_recognition
timings1 = get_word_timings(audio1_path)
timings2 = get_word_timings(audio2_path)

# Create timed text clips
text1_clips = create_timed_text_clips(timings1)
text2_clips = create_timed_text_clips(timings2)

# Create composite clips with text overlay
video1 = CompositeVideoClip([image1, *text1_clips])
video2 = CompositeVideoClip([image2, *text2_clips])

# Add audio to each video clip
video1 = video1.set_audio(audio1)
video2 = video2.set_audio(audio2)

# Add transition effect
transition = lambda clip: clip.crossfadein(1)

# Concatenate the clips with transitions
final_clip = concatenate_videoclips([transition(video1), transition(video2)], method="compose")

# Write the final video to a file
final_clip.write_videofile("final_video.mp4", fps=24)

print("Video created successfully!")
