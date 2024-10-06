import os
from moviepy.editor import VideoFileClip, concatenate_videoclips

def get_recent_videos_same_resolution(directory, num_videos=6):
    resolution_counts = {}

    for f in sorted(os.listdir(directory), key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True):
        if f.endswith('.mp4'):
            try:
                filepath = os.path.join(directory, f)
                clip = VideoFileClip(filepath)
                resolution = tuple(clip.size)  # Convert list to tuple
                clip.close()  # Close the clip to free resources

                # Update resolution counts
                resolution_counts[resolution] = resolution_counts.get(resolution, []) + [filepath]

                # Check if we have enough videos of the same resolution
                if len(resolution_counts[resolution]) == num_videos:
                    return resolution_counts[resolution]

            except Exception as e:
                print(f"Error processing file {f}: {e}")
                continue

    # If not enough videos of the same resolution were found, return an empty list
    return []

def create_video_mashup(video_paths, output_path, transition_duration=1):
    """
    Create a video mashup from a list of video paths, with a transition effect between each video.

    :param video_paths: List of paths to video files.
    :param output_path: Path to save the mashup video.
    :param transition_duration: Duration of the transition effect in seconds.
    """
    clips = []

    for path in video_paths:
        clip = VideoFileClip(path)
        clips.append(clip.crossfadein(transition_duration))

    final_clip = concatenate_videoclips(clips, method="compose")
    final_clip.write_videofile(output_path, codec="libx264", fps=24)

# Directory containing the video files
video_directory = 'c:\\Users\\sures\\Downloads\\Telegram Desktop'

# Get the most recent videos with the same resolution
recent_videos = get_recent_videos_same_resolution(video_directory)

# Create the mashup
output_file = 'c:\\Users\\sures\\Downloads\\Telegram Desktop\\mashup_output.mp4'
create_video_mashup(recent_videos, output_file)
