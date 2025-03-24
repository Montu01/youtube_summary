from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from youtube_utils import extract_video_info, get_transcript, download_thumbnail, upscale_thumbnail
from summarizer import generate_summary, translate_text

app = Flask(__name__, static_folder='static')
CORS(app)

# Configuration for production
if os.environ.get('FLASK_ENV') == 'production':
    # In production, set the frontend URL to the deployed URL
    frontend_url = os.environ.get('FRONTEND_URL', '*')
    CORS(app, resources={r"/api/*": {"origins": frontend_url}})
else:
    # In development, allow all origins
    CORS(app)

# Ensure the static directories exist
if os.environ.get('RENDER') == 'true':
    # On Render, use the RENDER_EXTERNAL_HOSTNAME as part of the path
    # This helps us create a unique path for each deployment
    app.config['UPLOAD_FOLDER'] = os.path.join('static', 'thumbnails')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join('static', 'thumbnails', 'upscaled'), exist_ok=True)
else:
    # Local development
    os.makedirs('static/thumbnails', exist_ok=True)
    os.makedirs('static/thumbnails/upscaled', exist_ok=True)

@app.route('/api/summarize', methods=['POST'])
def summarize_video():
    try:
        data = request.get_json()
        video_url = data.get('video_url')
        
        if not video_url:
            return jsonify({'error': 'Missing video URL'}), 400
            
        # Extract video information (title, thumbnail, etc.)
        video_info = extract_video_info(video_url)
        
        # Get video transcript
        transcript_text = get_transcript(video_url)
        
        if not transcript_text:
            return jsonify({'error': 'Could not retrieve transcript for this video'}), 400
            
        # Generate English summary
        english_summary = generate_summary(transcript_text)
        
        # Use placeholder translation function
        hindi_summary = translate_text(english_summary, target_language="hi")
        
        response = {
            'video_info': video_info,
            'english_summary': english_summary,
            'hindi_summary': hindi_summary
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/thumbnail', methods=['GET'])
def get_thumbnail():
    try:
        video_url = request.args.get('url')
        
        if not video_url:
            return jsonify({'error': 'Missing video URL'}), 400
        
        # Download the thumbnail
        thumbnail_path = download_thumbnail(video_url)
        
        # Return the file
        return send_file(thumbnail_path, mimetype='image/jpeg')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download-thumbnail', methods=['POST'])
def download_video_thumbnail():
    try:
        data = request.get_json()
        video_url = data.get('video_url')
        
        if not video_url:
            return jsonify({'error': 'Missing video URL'}), 400
            
        # Download the high-quality thumbnail
        thumbnail_path = download_thumbnail(video_url)
        
        # Return the path to the saved thumbnail
        return jsonify({
            'success': True,
            'thumbnail_path': thumbnail_path,
            'url': f"/static/thumbnails/{os.path.basename(thumbnail_path)}"
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upscale-thumbnail', methods=['POST'])
def upscale_video_thumbnail():
    try:
        data = request.get_json()
        video_url = data.get('video_url')
        scale_factor = data.get('scale_factor', 2)  # Default to 2x upscaling
        target_resolution = data.get('target_resolution')  # Optional: '4K' or '8K'
        
        if not video_url:
            return jsonify({'error': 'Missing video URL'}), 400
            
        # First download the thumbnail if not already downloaded
        thumbnail_path = download_thumbnail(video_url)
        
        # Then upscale it
        upscaled_path = upscale_thumbnail(thumbnail_path, scale_factor, target_resolution=target_resolution)
        
        # Return the path to the upscaled thumbnail
        return jsonify({
            'success': True,
            'original_thumbnail_path': thumbnail_path,
            'upscaled_thumbnail_path': upscaled_path,
            'original_url': f"/static/thumbnails/{os.path.basename(thumbnail_path)}",
            'upscaled_url': f"/static/{os.path.relpath(upscaled_path, 'static')}",
            'resolution': target_resolution or f"{scale_factor}x"
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

# Make the static folder accessible
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_file(os.path.join('static', filename))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
