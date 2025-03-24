from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
import re
import requests
import os
from urllib.parse import urlparse
from pathlib import Path

def extract_video_id(url):
    """Extract the YouTube video ID from the URL."""
    # Handle different URL formats (regular videos and shorts)
    if 'youtu.be' in url:
        # Handle URL parameters in youtu.be links
        return url.split('/')[-1].split('?')[0]
    elif 'youtube.com/shorts' in url:
        return url.split('/')[-1].split('?')[0]
    else:
        # Regular YouTube URL
        video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
        if video_id_match:
            return video_id_match.group(1)
        
        # Try another pattern for v= parameter
        params_match = re.search(r'[?&]v=([0-9A-Za-z_-]{11})', url)
        if params_match:
            return params_match.group(1)
            
    return None

def extract_video_info(url):
    """Extract video information like title, thumbnail, etc."""
    try:
        video_id = extract_video_id(url)
        if not video_id:
            raise ValueError("Could not extract video ID from the provided URL")
        
        # Try using pytube
        try:
            yt = YouTube(url)
            
            return {
                'id': video_id,
                'title': yt.title,
                'channel': yt.author,
                'thumbnail': f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
                'duration': yt.length,
                'view_count': yt.views
            }
        except Exception as pytube_error:
            print(f"Pytube error: {str(pytube_error)}")
            
            # Fallback to a simpler approach with just the video ID
            return {
                'id': video_id,
                'title': f"YouTube Video (ID: {video_id})",
                'channel': "Unknown Channel",
                'thumbnail': f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
                'duration': 0,
                'view_count': 0
            }
            
    except Exception as e:
        print(f"Error in extract_video_info: {str(e)}")
        raise Exception(f"Error extracting video information: {str(e)}")

def get_transcript(url):
    """Get the transcript of a YouTube video."""
    try:
        video_id = extract_video_id(url)
        if not video_id:
            raise ValueError("Could not extract video ID from the provided URL")
        
        try:
            # First try to get the English transcript (most common)
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            
            # Concatenate transcript texts with timestamps
            full_transcript = ""
            for item in transcript_list:
                full_transcript += item['text'] + " "
                
            return full_transcript.strip()
        except Exception as transcript_error:
            print(f"Error getting English transcript: {str(transcript_error)}")
            
            # Try getting available transcripts
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                
                # First try to find a manually created transcript
                manual_transcript = None
                for transcript in transcript_list:
                    if not transcript.is_generated:
                        manual_transcript = transcript
                        break
                
                # If no manual transcript found, try to get any generated transcript
                if manual_transcript:
                    transcript_data = manual_transcript.fetch()
                else:
                    # Get first available transcript (likely auto-generated)
                    available_transcript = next(transcript_list._transcripts.values().__iter__())
                    
                    # Try to translate it to English if it's not in English
                    if available_transcript.language_code != 'en':
                        try:
                            transcript_data = available_transcript.translate('en').fetch()
                            print(f"Translated transcript from {available_transcript.language_code} to English")
                        except Exception as translation_error:
                            print(f"Translation error: {str(translation_error)}")
                            # Fall back to original language if translation fails
                            transcript_data = available_transcript.fetch()
                            print(f"Using original {available_transcript.language_code} transcript")
                    else:
                        transcript_data = available_transcript.fetch()
                
                full_transcript = ""
                for item in transcript_data:
                    full_transcript += item['text'] + " "
                    
                return full_transcript.strip()
            except Exception as second_error:
                print(f"Second attempt error: {str(second_error)}")
                
                # Last resort: try explicitly getting auto-generated Hindi transcript 
                # as mentioned in the error message
                try:
                    transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['hi'])
                    print("Successfully retrieved Hindi transcript")
                    
                    # Try to translate to English
                    try:
                        from googletrans import Translator
                        translator = Translator()
                        
                        full_transcript = ""
                        for item in transcript_list:
                            full_transcript += item['text'] + " "
                        
                        # Translate to English
                        translated = translator.translate(full_transcript.strip(), src='hi', dest='en')
                        return translated.text
                    except Exception as translation_error:
                        print(f"Translation error: {str(translation_error)}")
                        
                        # If translation fails, return Hindi transcript
                        full_transcript = ""
                        for item in transcript_list:
                            full_transcript += item['text'] + " "
                        return full_transcript.strip()
                except Exception as hindi_error:
                    print(f"Hindi transcript error: {str(hindi_error)}")
                    raise ValueError(f"Could not retrieve transcript in any language: {str(transcript_error)}")
                
    except Exception as e:
        print(f"Outer error in get_transcript: {str(e)}")
        raise Exception(f"Error retrieving transcript: {str(e)}")

def download_thumbnail(url, output_dir='static/thumbnails'):
    """
    Download high-quality thumbnail from a YouTube video.
    
    Args:
        url (str): YouTube video URL
        output_dir (str): Directory to save the thumbnail
        
    Returns:
        str: Path to the downloaded thumbnail file
    """
    try:
        video_id = extract_video_id(url)
        if not video_id:
            raise ValueError("Could not extract video ID from the provided URL")
        
        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Try different thumbnail quality options (from highest to lowest)
        thumbnail_qualities = [
            f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",  # HD (1080p)
            f"https://img.youtube.com/vi/{video_id}/sddefault.jpg",      # SD (640p)
            f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",      # HQ (480p)
            f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg",      # MQ (320p)
            f"https://img.youtube.com/vi/{video_id}/default.jpg"         # Default (120p)
        ]
        
        # Try each thumbnail URL until we find one that works
        for thumb_url in thumbnail_qualities:
            try:
                response = requests.get(thumb_url, stream=True)
                
                # Check if the request was successful and the content is an image
                if response.status_code == 200 and response.headers.get('content-type', '').startswith('image'):
                    # Generate a filename based on the video ID
                    filename = f"{video_id}.jpg"
                    file_path = os.path.join(output_dir, filename)
                    
                    # Save the image to the file
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)
                    
                    print(f"Downloaded thumbnail for video {video_id} to {file_path}")
                    return file_path
            except Exception as e:
                print(f"Error downloading thumbnail from {thumb_url}: {str(e)}")
                continue
        
        # If all thumbnail URLs failed, raise an exception
        raise Exception("Could not download thumbnail from any available source")
        
    except Exception as e:
        print(f"Error in download_thumbnail: {str(e)}")
        raise Exception(f"Error downloading thumbnail: {str(e)}")

def upscale_thumbnail(input_path, scale_factor=2, output_dir='static/thumbnails/upscaled', target_resolution=None):
    """
    Upscale a thumbnail image to enhance its quality.
    
    Args:
        input_path (str): Path to the input thumbnail image
        scale_factor (int): Factor by which to upscale the image (default: 2)
        output_dir (str): Directory to save the upscaled thumbnail
        target_resolution (str): Target resolution (e.g., '4K', '8K') to override scale_factor
        
    Returns:
        str: Path to the upscaled thumbnail file
    """
    try:
        from PIL import Image
        import numpy as np
        
        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Open the image
        img = Image.open(input_path)
        
        # Get the original size
        original_width, original_height = img.size
        
        # Handle target_resolution parameter (for 4K, 8K, etc.)
        if target_resolution:
            if target_resolution.upper() == '4K':
                # 4K is typically 3840x2160
                target_width = 3840
                target_height = 2160
                
                # Calculate aspect ratio-preserving dimensions
                if original_width / original_height > target_width / target_height:
                    # Width-constrained
                    new_width = target_width
                    new_height = int(original_height * (target_width / original_width))
                else:
                    # Height-constrained
                    new_height = target_height
                    new_width = int(original_width * (target_height / original_height))
                    
                # Override scale factor for naming
                effective_scale = max(new_width / original_width, new_height / original_height)
                scale_factor = round(effective_scale, 1)
                
            elif target_resolution.upper() == '8K':
                # 8K is typically 7680x4320
                target_width = 7680
                target_height = 4320
                
                # Calculate aspect ratio-preserving dimensions
                if original_width / original_height > target_width / target_height:
                    # Width-constrained
                    new_width = target_width
                    new_height = int(original_height * (target_width / original_width))
                else:
                    # Height-constrained
                    new_height = target_height
                    new_width = int(original_width * (target_height / original_height))
                
                # Override scale factor for naming
                effective_scale = max(new_width / original_width, new_height / original_height)
                scale_factor = round(effective_scale, 1)
                
            else:
                # Default behavior using scale_factor
                new_width = int(original_width * scale_factor)
                new_height = int(original_height * scale_factor)
        else:
            # Default behavior using scale_factor
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)
        
        print(f"Upscaling from {original_width}x{original_height} to {new_width}x{new_height}")
        
        # Create the output filename
        filename = os.path.basename(input_path)
        base_name, ext = os.path.splitext(filename)
        resolution_label = f"{target_resolution}_" if target_resolution else ""
        upscaled_filename = f"{base_name}_upscaled_{resolution_label}{new_width}x{new_height}{ext}"
        output_path = os.path.join(output_dir, upscaled_filename)
        
        # Use a two-step approach for large upscaling to maintain quality
        if scale_factor > 4:
            # For large upscaling, do it in steps for better quality
            intermediate_scale = min(2, scale_factor / 2)
            intermediate_width = int(original_width * intermediate_scale)
            intermediate_height = int(original_height * intermediate_scale) 
            intermediate_img = img.resize((intermediate_width, intermediate_height), Image.LANCZOS)
            
            # Final upscale from intermediate to target size
            upscaled_img = intermediate_img.resize((new_width, new_height), Image.LANCZOS)
        else:
            # For smaller upscaling, do it in one step
            upscaled_img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Enhanced upscaling with sharpening
        # This is a simple enhancement technique - for production, 
        # consider using more advanced ML-based upscaling models
        try:
            # Convert to numpy array
            img_array = np.array(upscaled_img)
            
            # Apply a simple sharpening kernel
            from scipy.ndimage import convolve
            
            # Only apply sharpening if the image has 3 channels (RGB)
            if len(img_array.shape) == 3 and img_array.shape[2] >= 3:
                # Use a gentler sharpening for large upscales
                if scale_factor > 4:
                    kernel = np.array([[-0.5, -0.5, -0.5],
                                      [-0.5,  5.0, -0.5],
                                      [-0.5, -0.5, -0.5]]) / 5.0
                else:
                    kernel = np.array([[-1, -1, -1],
                                      [-1,  9, -1],
                                      [-1, -1, -1]]) / 9.0
                
                # Apply to each RGB channel
                for i in range(3):  # RGB channels
                    img_array[:, :, i] = convolve(img_array[:, :, i], kernel)
                
                # Convert back to PIL Image
                enhanced_img = Image.fromarray(np.uint8(np.clip(img_array, 0, 255)))
                enhanced_img.save(output_path, quality=95, optimize=True)
            else:
                # If not RGB, just save the upscaled image
                upscaled_img.save(output_path, quality=95, optimize=True)
                
        except ImportError:
            # If scipy is not available, just use the basic Lanczos upscaling
            upscaled_img.save(output_path, quality=95, optimize=True)
        
        print(f"Upscaled thumbnail saved to {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Error in upscale_thumbnail: {str(e)}")
        # If upscaling fails, return the original image path
        return input_path
