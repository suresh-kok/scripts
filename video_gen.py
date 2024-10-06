import os
from moviepy.editor import VideoFileClip, ImageClip, TextClip, concatenate_videoclips, CompositeVideoClip, AudioFileClip
from moviepy.audio.AudioClip import concatenate_audioclips
from moviepy.config import change_settings
from gtts import gTTS

# Specify the path to the ImageMagick binary
change_settings({"IMAGEMAGICK_BINARY": "C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"})

# Function to create a text clip
def create_text_clip(text, duration, font_size=140, color='white'):
    txt_clip = TextClip(text, fontsize=font_size, color=color, font='Amiri-Bold')
    txt_clip = txt_clip.set_duration(duration)
    return txt_clip

# Function to create audio from text
def create_audio_clip(text, filename):
    tts = gTTS(text=text, lang='en')
    tts.save(filename)
    return AudioFileClip(filename)

# Load images and set duration
image1 = ImageClip("C:\\Users\\sures\\Downloads\\Telegram Desktop\\1719027444582.jpg").set_duration(15)
image2 = ImageClip("C:\\Users\\sures\\Downloads\\Telegram Desktop\\Untitled (4).jpg").set_duration(15)

# Create text clips
text1 = create_text_clip("Yoga is good for Improving flexibility, strength, balance, and joint health", duration=15)
text2 = create_text_clip("Going to the gym can have several benefits for your physical and mental health. These benefits include Boosting your health and energy levels", duration=15)

# Generate audio clips
audio1 = create_audio_clip("Yoga is good for Improving flexibility, strength, balance, and joint health", "audio1.mp3")
audio2 = create_audio_clip("Going to the gym can have several benefits for your physical and mental health. These benefits include Boosting your health and energy levels", "audio2.mp3")

# Set positions of text clips
text1 = text1.set_position(("center", "center"))
text2 = text2.set_position(("center", "center"))

# Create composite clips with text overlay
video1 = CompositeVideoClip([image1, text1])
video2 = CompositeVideoClip([image2, text2])

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
