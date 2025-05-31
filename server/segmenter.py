import os
import subprocess
import glob

VIDEO_NAME = "test"
INPUT_DIR = os.path.join("data", "raw")
OUTPUT_DIR = os.path.join("data", "segments")
DURATION = 5
PROFILES = [
    ("480p", "854x480", 1500),
    ("720p", "1280x720", 3000),
    ("1080p", "1920x1080", 8000),
]

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def segment_video(resolution_label, resolution_size, bitrate_kbps, video_name, input_dir, output_dir, duration):
    
    '''
    Segments a video into multiple parts based on the specified resolution and bitrate.
    Args:
        resolution_label (str): Label for the resolution (e.g., "480p", "720p", "1080p").
        resolution_size (str): Resolution size in the format "widthxheight" (e.g., "854x480").
        bitrate_kbps (int): Bitrate in kbps for the video stream.
        video_name (str): Name of the video file without extension.
        input_dir (str): Directory containing the input video file.
        output_dir (str): Directory where the segmented files will be saved.
        duration (int): Duration of each segment in seconds.
        
    Returns:
        None
    
    '''
    
    print(f"[Segmenter] Processing: {resolution_label}, {bitrate_kbps}k")
    input_path = os.path.join(input_dir, f"{video_name}.mp4")
    output_path = os.path.join(output_dir, video_name)
    ensure_dir(output_path)

    ts_base = os.path.join(output_path, f"{video_name}-{resolution_label}-{bitrate_kbps}k-%04d.ts")

    pattern = os.path.join(output_path, f"{video_name}-{resolution_label}-{bitrate_kbps}k-*.ts")
    existing_segments = glob.glob(pattern)
    if existing_segments:
        for segment in existing_segments:
            print(f"[Segmenter] Segments already exist: {os.path.basename(segment)}, may be overwritten.")

    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-s", resolution_size,
        "-c:v", "libx264",
        "-b:v", f"{bitrate_kbps}k",
        "-c:a", "aac",
        "-f", "segment",
        "-segment_time", str(duration),
        "-reset_timestamps", "1",
        ts_base
    ]

    try:
        result = subprocess.Popen(
            cmd,
            #check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True  
        )
        # print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("[Segmenter] ffmpeg error:")
        print(e.stderr)

def batch_segment_videos(input_dir, output_dir, duration, profiles):
    '''
    Segments all videos in the input directory into multiple parts based on the specified profiles.
    Args:
        input_dir (str): Directory containing the input video files. Default is "data/raw".
        output_dir (str): Directory where the segmented files will be saved. Default is "data/segments".
        duration (int): Duration of each segment in seconds. Default is 5 seconds.
        profiles (list): List of tuples containing resolution label, resolution size, and bitrate.
    Returns:
        None
    '''
    
    for video_file in glob.glob(os.path.join(input_dir, "*.mp4")):
        video_name = os.path.splitext(os.path.basename(video_file))[0]
        print(f"[Segmenter] Processing video: {video_name}")
        for res_label, res_size, bitrate in profiles:
            segment_video(res_label, res_size, bitrate, input_dir=input_dir, output_dir=output_dir, video_name=video_name, duration=duration)
        print(f"[Segmenter] Finished processing video: {video_name}")
        


def main():
    # input_path= os.path.join(INPUT_DIR, f"{VIDEO_NAME}.mp4")
    # print(f"[Segmenter] Input video: {input_path}")
    # for res_label, res_size, bitrate in PROFILES:
    #     segment_video(res_label, res_size, bitrate)
    # print(f"[Segmenter] All Segments are saved at {os.path.join(OUTPUT_DIR, VIDEO_NAME)}")
    batch_segment_videos(INPUT_DIR, OUTPUT_DIR, DURATION, PROFILES)

if __name__ == "__main__":
    main()