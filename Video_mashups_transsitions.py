import os
from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip, ColorClip
import random
import cv2

def slide_transition(clip1, clip2, transition_duration=3):
    # Slide clip2 over clip1 from the right
    slide_clip = clip2.set_position(lambda t: ('right' if t < transition_duration else 'center'))
    composite_clip = CompositeVideoClip([clip1, slide_clip], size=clip1.size)
    return composite_clip.set_duration(clip1.duration + transition_duration)

def fade_to_black_transition(clip1, clip2, transition_duration=3):
    # Fade to black between clips
    black_clip = ColorClip(clip1.size, color=(0, 0, 0)).set_duration(transition_duration)
    return CompositeVideoClip([clip1, black_clip, clip2.set_start(clip1.duration + transition_duration)], size=clip1.size)

def apply_random_transition(clip1, clip2, transition_duration=3):
    transitions = ['crossfade', 'slide', 'fade_to_black']
    transition_type = random.choice(transitions)
    print(f"Applying {transition_type} transition.")

    if transition_type == 'crossfade':
        return [clip1.crossfadeout(transition_duration), clip2.crossfadein(transition_duration)]
    elif transition_type == 'concatenate':
        return [clip1, clip2.set_start(clip1.duration)]
    elif transition_type == 'slide':
        return [slide_transition(clip1, clip2, transition_duration)]
    elif transition_type == 'fade_to_black':
        return [fade_to_black_transition(clip1, clip2, transition_duration)]
    
def resize_clip(clip, target_size):
    return clip.resize(newsize=target_size)

def upscale_video(input_path, output_path, scale_factor=2):
    # Capture the input video
    cap = cv2.VideoCapture(input_path)

    # Get video properties
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) * scale_factor)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) * scale_factor)

    # Video writer object
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Read and upscale each frame
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        resized_frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_LINEAR)
        out.write(resized_frame)

    # Release resources
    cap.release()
    out.release()


def get_recent_videos_same_resolution(directory, num_videos=5):
    resolution_counts = {}

    for f in sorted(os.listdir(directory), key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True):
        if f.endswith('.mp4'):
            try:
                filepath = os.path.join(directory, f)
                clip = VideoFileClip(filepath)
                resolution = tuple(clip.size)
                clip.close()
                
                resolution_counts[resolution] = resolution_counts.get(resolution, []) + [filepath]
                if len(resolution_counts[resolution]) == num_videos:
                    return resolution_counts[resolution]

            except Exception as e:
                print(f"Error processing file {f}: {e}")
                continue

    return []

def add_background(clip, bg_color=(0, 0, 0)):
    if clip.size[0] < clip.size[1]:  # Portrait video
        print(f"Adding background to portrait video: {clip.filename}")
        bg_clip = ColorClip(size=(1000, clip.size[1]), color=bg_color, duration=clip.duration)
        return CompositeVideoClip([bg_clip.set_position("center"), clip.set_position("center")])
    return clip

def create_video_mashup(video_paths, output_path, transition_duration=3, max_duration=300, pre_video=None, post_video=None):
    clips = [VideoFileClip(path) for path in video_paths]
    print(f"Total clips before processing: {len(clips)}")

    # Apply background and limit clip duration
    processed_clips = []
    total_duration = 0
    for clip in clips:
        clip_with_bg = add_background(clip)
        remaining_duration = max_duration - total_duration
        if remaining_duration <= 0:
            break
        clip_duration = min(clip_with_bg.duration, remaining_duration)
        processed_clip = clip_with_bg.subclip(0, clip_duration)
        processed_clips.append(processed_clip)
        total_duration += clip_duration
        print(f"Processed clip: {clip.filename}, Duration: {clip_duration} seconds")

    # Determine target size for resizing (if needed)
    target_size = [1920, 1080]  # Example target size

    # Initialize transition_clips
    transition_clips = []

    # Add pre-video if provided and resized
    if pre_video:
        pre_clip = VideoFileClip(pre_video)
        pre_clip_resized = resize_clip(pre_clip, target_size)
        transition_clips.append(pre_clip_resized)
        print(f"Added pre-video: {pre_video}")

    # Add transitions
    for i in range(len(processed_clips) - 1):
        transition = apply_random_transition(processed_clips[i], processed_clips[i + 1], transition_duration)
        transition_clips.extend(transition)

    # Add the last clip since it's not included in the loop
    transition_clips.append(processed_clips[-1])

    # Add post-video if provided and resized
    if post_video:
        post_clip = VideoFileClip(post_video)
        post_clip_resized = resize_clip(post_clip, target_size)
        transition_clips.append(post_clip_resized)
        print(f"Added post-video: {post_video}")

    final_clip = concatenate_videoclips(transition_clips, method="compose")
    final_clip.write_videofile(output_path, codec="libx264", fps=24)
    print("Mashup video created.")

# Directory containing the video files
video_directory = 'c:\\Users\\sures\\Downloads\\Telegram Desktop'

# Get the most recent videos with the same resolution
recent_videos = get_recent_videos_same_resolution(video_directory)

# Create the mashup
output_file = 'c:\\Users\\sures\\Downloads\\Telegram Desktop\\Mashups\\mashup_output.mp4'
pre_video_path = 'c:\\Users\\sures\\Downloads\\Telegram Desktop\\Mashups\\Intro.mp4'
post_video_path = 'c:\\Users\\sures\\Downloads\\Telegram Desktop\\Mashups\\Outro.mp4'
final_output = 'c:\\Users\\sures\\Downloads\\Telegram Desktop\\Mashups\\mashup_output_final.mp4'

create_video_mashup(recent_videos, output_file, pre_video=pre_video_path, post_video=post_video_path)
#upscale_video(output_file, final_output)