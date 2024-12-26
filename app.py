from flask import Flask, request, send_file, jsonify, render_template
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from nightcore_converter import NightcoreConverter
import tempfile
import subprocess
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure upload settings
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['TEMPLATES_AUTO_RELOAD'] = True

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def check_ffmpeg():
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        logger.info(f"FFmpeg version check: {result.stdout[:100]}...")
        return True
    except FileNotFoundError:
        logger.error("FFmpeg not found in system path")
        return False
    except Exception as e:
        logger.error(f"Error checking FFmpeg: {str(e)}")
        return False

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_to_nightcore():
    logger.info("Starting conversion request")
    
    if not check_ffmpeg():
        logger.error("FFmpeg is not installed")
        return jsonify({'error': 'FFmpeg is not installed on the server'}), 500

    if 'file' not in request.files:
        logger.error("No file provided in request")
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        logger.error("No selected file")
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        logger.error(f"File type not allowed: {file.filename}")
        return jsonify({'error': 'File type not allowed'}), 400

    input_path = None
    output_path = None

    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        logger.info(f"Saving uploaded file to: {input_path}")
        file.save(input_path)

        # Convert the file
        logger.info("Starting nightcore conversion")
        converter = NightcoreConverter(input_path)
        output_path = converter.convert()
        logger.info(f"Conversion completed: {output_path}")

        # Send the processed file
        return send_file(output_path, as_attachment=True, download_name=os.path.basename(output_path))

    except Exception as e:
        logger.error(f"Error during conversion: {str(e)}")
        return jsonify({'error': str(e)}), 500

    finally:
        # Clean up temporary files
        try:
            if input_path and os.path.exists(input_path):
                os.remove(input_path)
                logger.info(f"Cleaned up input file: {input_path}")
            if output_path and os.path.exists(output_path):
                os.remove(output_path)
                logger.info(f"Cleaned up output file: {output_path}")
        except Exception as e:
            logger.error(f"Error cleaning up files: {str(e)}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
