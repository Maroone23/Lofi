import os
import subprocess
import logging

logger = logging.getLogger(__name__)

class NightcoreConverter:
    def __init__(self, input_file):
        self.input_file = input_file
        self.output_file = self._generate_output_filename(input_file)
        logger.info(f"Initializing NightcoreConverter with input: {input_file}")
        logger.info(f"Output will be saved to: {self.output_file}")

    def _generate_output_filename(self, input_file):
        directory = os.path.dirname(input_file)
        filename = os.path.basename(input_file)
        name, ext = os.path.splitext(filename)
        return os.path.join(directory, f"nightcore_{name}{ext}")

    def convert(self):
        """Convert the input file to nightcore version using ffmpeg"""
        command = [
            'ffmpeg',
            '-i', self.input_file,
            '-af', 'asetrate=44100*1.25,aresample=44100,atempo=1',  # Increase pitch and speed
            '-y',  # Overwrite output file if it exists
            self.output_file
        ]
        
        logger.info(f"Starting FFmpeg conversion with command: {' '.join(command)}")
        
        try:
            process = subprocess.run(command, check=True, capture_output=True, text=True)
            logger.info("FFmpeg conversion completed successfully")
            logger.debug(f"FFmpeg output: {process.stdout}")
            
            if not os.path.exists(self.output_file):
                raise Exception("Output file was not created")
                
            file_size = os.path.getsize(self.output_file)
            logger.info(f"Output file size: {file_size} bytes")
            
            return self.output_file
            
        except subprocess.CalledProcessError as e:
            error_msg = f"FFmpeg conversion failed: {e.stderr}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except FileNotFoundError:
            error_msg = "FFmpeg is not installed on the system"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error during conversion: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
