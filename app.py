import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
import yt_dlp

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Define paths
d_drive_path = os.path.join("D:\\", "Downloads")
c_drive_path = os.path.join(os.path.expanduser("~"), "Downloads")

# Check if D drive exists
if os.path.exists("D:\\"):
    if not os.path.exists(d_drive_path):
        os.makedirs(d_drive_path)
    DEFAULT_SAVE_PATH = d_drive_path
else:
    DEFAULT_SAVE_PATH = c_drive_path

current_save_path = DEFAULT_SAVE_PATH

# Progress tracking
progress = {
    'status': 'idle',  # Initial status when no download is in progress
    'percent': '0%',
    'speed': 'N/A',
    'eta': 'N/A'
}

def my_hook(d):
    """Track download progress using yt_dlp hooks."""
    if d['status'] == 'downloading':
        progress['status'] = 'downloading'
        progress['percent'] = d['_percent_str']
        progress['speed'] = d['_speed_str']
        progress['eta'] = d['_eta_str']
    elif d['status'] == 'finished':
        progress['status'] = 'finished'

def download_video(video_url):
    """Download video using yt_dlp and track progress."""
    ydl_opts = {
        'outtmpl': os.path.join(current_save_path, '%(title)s.%(ext)s'),  # Save to current save path
        'format': 'best',
        'noplaylist': True,
        'progress_hooks': [my_hook], 
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([video_url])
        except Exception as e:
            progress['status'] = 'error'
            progress['error_message'] = str(e)

@app.route('/')
def index():
    return render_template('index.html', save_path=current_save_path)

@app.route('/download', methods=['POST'])
def download():
    video_url = request.form.get('video_url')

    if not video_url:
        return jsonify({'status': 'error', 'message': "Please provide a valid video URL."})

    try:
        # Attempt the video download with yt_dlp
        download_video(video_url)
        return jsonify({'status': 'success', 'message': "Download completed successfully!"})
    except yt_dlp.DownloadError as e:
        # Handle yt_dlp-specific errors
        return jsonify({'status': 'error', 'message': f"An error occurred while downloading the video: {str(e)}"})
    except Exception as e:
        # Handle other unexpected errors
        return jsonify({'status': 'error', 'message': f"An unexpected error occurred: {str(e)}"})


@app.route('/progress')
def get_progress():
    """Get the current download progress."""
    return jsonify(progress)

if __name__ == '__main__':
    app.run(debug=True)
