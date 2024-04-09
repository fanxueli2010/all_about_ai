import cv2
import os
import base64
import openai
from openai import OpenAI
from pathlib import Path
from moviepy.editor import VideoFileClip, AudioFileClip
import time
import requests
import ffmpeg
import subprocess
import json
from moviepy.editor import CompositeAudioClip
from moviepy.editor import concatenate_audioclips
from moviepy.editor import VideoFileClip
import re
from pytube import YouTube


# Function to open and read the API key file
def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)

# Initialize the OpenAI client with API key
client = OpenAI(api_key=open_file("openaiapikey2.txt"))

# ANSI escape code for colors
PINK = '\033[95m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
RESET_COLOR = '\033[0m'

def main(max_results=5):
    youtube_api_key = "YTAPIKEY"  # Replace with your YouTube API key
    topic = input(f"{YELLOW}Enter the query for a YouTube video search: {RESET_COLOR}")
    video_urls = search_youtube_videos(youtube_api_key, topic, max_results)

    if not video_urls:
        print("No videos found.")
        return

    for url in video_urls:
        success, result = download_youtube_video(url)
        if success:
            print(f"Video downloaded successfully at {result}")
            return result
        else:
            print(f"Failed to download video at {url}: {result}")

    print("All video downloads failed.")
    return None
    
def main2():
    video_path = 'path/ytvid.mp4'
    response_text = response  # The response with the timestamps

    timestamps = parse_timestamps(response_text)

    # List to store all subclips
    subclips = []

    for start, end in timestamps:
        start_sec = timestamp_to_seconds(start)
        end_sec = timestamp_to_seconds(end)
        # Create a subclip for each timestamp pair and add it to the list
        subclip = VideoFileClip(video_path).subclip(start_sec, end_sec)
        subclips.append(subclip)

    # Concatenate all the subclips into one clip
    final_clip = concatenate_videoclips(subclips)

    # Save the final clip
    final_output_path = 'path/final_clip.mp4'
    final_clip.write_videofile(final_output_path, codec="libx264")

    # Close all clips to release resources
    for clip in subclips:
        clip.close()
    final_clip.close()

def search_youtube_videos(api_key, topic, max_results):
    search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={topic}&type=video&maxResults={max_results}&key={api_key}"
    response = requests.get(search_url)

    if response.status_code != 200:
        print("Failed to retrieve YouTube videos")
        return []

    video_ids = [item['id']['videoId'] for item in response.json()['items']]
    video_urls = [f"https://www.youtube.com/watch?v={video_id}" for video_id in video_ids]

    return video_urls

def download_youtube_video(url):
    try:
        yt = YouTube(url)
        video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        if video:
            video_path = video.download(filename="ytvid.mp4")
            return True, video_path
    except Exception as e:
        return False, str(e)

def mp3_to_srt(mp3_file_path):
    # Open the MP3 file in binary mode
    with open(mp3_file_path, 'rb') as audio_file:
        # Make a request to OpenAI's Whisper API
        transcript_response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="srt"  # Request the transcription in SRT format
        )

    # Debug: Print the raw API response
    print("API Response:", transcript_response)

    # Save the SRT content to a file (transcript_response is directly the SRT content here)
    srt_file_path = mp3_file_path.rsplit('.', 1)[0] + '.srt'
    with open(srt_file_path, 'w', encoding='utf-8') as srt_file:
        srt_file.write(transcript_response)

    return srt_file_path
    
def convert_mp4_to_mp3(mp4_file_path, mp3_file_path):
    """
    Convert an MP4 file to MP3 format using moviepy.

    Args:
    mp4_file_path (str): Path to the MP4 file.
    mp3_file_path (str): Desired output path for the MP3 file.

    Returns:
    bool: True if conversion successful, False otherwise.
    """
    try:
        # Load the MP4 file
        video_clip = VideoFileClip(mp4_file_path)

        # Extract audio from the video clip
        audio_clip = video_clip.audio

        # Write the audio to an MP3 file
        audio_clip.write_audiofile(mp3_file_path)

        # Close the clips
        video_clip.close()
        audio_clip.close()

        return True

    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def chatgpt(user_query, system_input):
    """
    Function to send a query to OpenAI's GPT-3.5-Turbo model and return the response.

    :param user_query: The query string from the user.
    :return: The response from the OpenAI GPT model.
    """

    # Send the query to the OpenAI API
    completion = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {"role": "system", "content": system_input},
            {"role": "user", "content": user_query}
        ]
    )

    # Extract and return the response message
    return completion.choices[0].message.content
 
def get_video_dimensions(video_path):
    """Get the dimensions of the video."""
    cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "json", video_path]
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    dimensions = json.loads(result.stdout)
    width = dimensions['streams'][0]['width']
    height = dimensions['streams'][0]['height']
    return width, height
    
def calculate_crop_dimensions(width, height, aspect_width, aspect_height):
    """Calculate dimensions for cropping to a specific aspect ratio."""
    target_ratio = aspect_height / aspect_width
    current_ratio = height / width

    if current_ratio > target_ratio:
        # Crop height
        new_height = int(width * target_ratio)
        crop_height = (height - new_height) // 2
        return f"{width}:{new_height}:{0}:{crop_height}"
    else:
        # Crop width
        new_width = int(height / target_ratio)
        crop_width = (width - new_width) // 2
        return f"{new_width}:{height}:{crop_width}:{0}"   
 
def srt_to_txt(srt_file_path):
    """
    Convert a .srt file to a .txt file.

    Args:
    srt_file_path (str): Path to the .srt file.

    Returns:
    str: Path to the created .txt file.
    """
    txt_file_path = srt_file_path.rsplit('.', 1)[0] + '.txt'
    
    try:
        # Read from .srt file
        with open(srt_file_path, 'r', encoding='utf-8') as file:
            srt_content = file.read()

        # Write to .txt file
        with open(txt_file_path, 'w', encoding='utf-8') as file:
            file.write(srt_content)

        return txt_file_path

    except Exception as e:
        print(f"An error occurred while converting .srt to .txt: {e}")
        return None        

# Function to get video duration in seconds, rounded to the nearest whole number
def get_video_duration(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return 0

    fps = cap.get(cv2.CAP_PROP_FPS)  # Get frame rate
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # Get total frame count
    duration = round(frame_count / fps) if fps > 0 else 0  # Round the duration

    cap.release()
    return duration
   
def parse_timestamps(response_text):
    """
    Parse timestamps from response text in SRT format.
    """
    timestamps = re.findall(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', response_text)
    return timestamps

def timestamp_to_seconds(timestamp):
    """
    Convert a timestamp to seconds.
    """
    hours, minutes, seconds = map(float, timestamp.replace(',', '.').split(':'))
    return hours * 3600 + minutes * 60 + seconds

def cut_video(video_path, start_time, end_time, output_path):
    """
    Cut a segment from a video.
    """
    try:
        clip = VideoFileClip(video_path).subclip(start_time, end_time)
        clip.write_videofile(output_path, codec="libx264")
    except Exception as e:
        print(f"Error cutting video: {e}")    

main()
video_path = 'path/ytvid.mp4'
mp3_file_path = 'path/Python/aivideo/aud.mp3'
convert_mp4_to_mp3(video_path, mp3_file_path)
srt_file = mp3_to_srt("path/aivideo/aud.mp3")
txt_file = srt_to_txt(srt_file)
txt_file2 = open_file("aud.txt")
system_input = open_file("youtube.txt")
abt = input(f"{CYAN}Enter what you want the clip to be about: {RESET_COLOR}")
time = input(f"{YELLOW}Enter how long you want the clip in Seconds: {RESET_COLOR}")    
user_input = open_file("video.txt").replace("<<SRT>>", txt_file2).replace("<<TIME>>", time).replace("<<ABT>>", abt)
print(user_input)
response = chatgpt(user_input, system_input)
print(response)
main2()
srt_file_path = "aud2.srt"
video_inpath2 = 'path/final_clip.mp4'
video_output_path2 = 'path/final_clip2.mp4'
subtitles_style = (
    "force_style='Alignment=2,"  # Bottom center alignment
    "Fontsize=20,"
    "MarginL=0,"  # Left margin, set to 0 for center alignment
    "MarginV=20,"  # Bottom margin, adjust as needed
    "PrimaryColour=&H00FFFF00,"  # Semi-transparent black for shadow
    "BackColour=&H80000000,"     # Semi-transparent black for background
    "BorderStyle=1,"             # Single border style
    "Outline=2'"                 # 2-pixel outline for visible shadow effect
)

subtitles_style2 = (
    "force_style='Alignment=0,"
    "Fontsize=16,"
    "MarginL=5,"
    "MarginV=130,"
    "OutlineColour=&H80000000,"  # Semi-transparent black for shadow
    "BackColour=&H80000000,"     # Semi-transparent black for background
    "BorderStyle=1,"             # Single border style
    "Outline=2'"                 # 2-pixel outline for visible shadow effect
)

# User input for subtitles
# Refactor user input handling
video_format_choice = input(f"{CYAN}Choose video format - Original (1) or 9:16 Cropped (2): {RESET_COLOR}").strip()
subtitles_choice = input(f"{CYAN}Do you want to add subtitles? (yes/no): {RESET_COLOR}").strip().lower()

# Step 1: Ensure correct video dimensions are obtained
video_input_path = 'path/final_clip.mp4'
width, height = get_video_dimensions(video_input_path)
print(f"Original Video Dimensions: {width}x{height}")

# Step 2: Recalculate the crop area
aspect_ratio_width = 9
aspect_ratio_height = 16
crop_area1 = calculate_crop_dimensions(width, height, aspect_ratio_width, aspect_ratio_height)
print(f"Crop Area: {crop_area1}")

# Only format subtitles if user inputs '2'
if video_format_choice == '2' and subtitles_choice == 'yes':
    video_input_path = 'path/final_clip.mp4'
    width, height = get_video_dimensions(video_input_path)
    print(f"Original Video Dimensions: {width}x{height}")
    print(f"Crop Area: {crop_area1}")
    video_output_path = "path/cropped_video.mp4"
    crop_area2 = crop_area1
    mp3_file_path = 'path/aud2.mp3'
    convert_mp4_to_mp3(video_input_path, mp3_file_path)
    srt_file = mp3_to_srt("path/aud2.mp3")
    txt_file = srt_to_txt(srt_file)
    styled_subtitles = f"{srt_file_path}:force_style={subtitles_style2}"
    filter_complex_arg = f"[0:v]crop={crop_area2}[cropped];[cropped]subtitles={styled_subtitles}[out]"
elif video_format_choice == '2' and subtitles_choice == 'no':
    video_input_path = 'path/final_clip.mp4'
    width, height = get_video_dimensions(video_input_path)
    print(f"Original Video Dimensions: {width}x{height}")
    print(f"Crop Area: {crop_area1}")
    video_output_path = "path/cropped_video.mp4"
    crop_area2 = crop_area1
    filter_complex_arg = f"[0:v]crop={crop_area2}[out]"
elif video_format_choice == '1' and subtitles_choice == 'yes':
    video_input_path = 'path/final_clip.mp4'
    video_output_path = video_output_path2
    mp3_file_path = 'path/aud2.mp3'
    convert_mp4_to_mp3(video_input_path, mp3_file_path)
    srt_file = mp3_to_srt("path/aud2.mp3")
    txt_file = srt_to_txt(srt_file)
    styled_subtitles = f"{srt_file_path}:force_style={subtitles_style}"
    filter_complex_arg = f"subtitles={styled_subtitles}[out]"  
else:
    video_output_path = 'path/final_clip3.mp4'
    filter_complex_arg = "[0:v]copy[out]"

# Step 3: Assemble the ffmpeg Command
ffmpeg_command = [
    "ffmpeg",
    "-i", video_input_path,
    "-filter_complex", filter_complex_arg,
    "-map", "[out]", "-map", "0:a",  # Map the video and audio streams
    "-c:a", "copy",  # Copy audio without re-encoding
    video_output_path
]

# Step 4: Execute the Command
subprocess.run(ffmpeg_command, shell=False)
        