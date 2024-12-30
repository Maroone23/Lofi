import os
import subprocess
import logging

logger = logging.getLogger(__name__)

class NightcoreConverter:
    def __init__(self, input_file, speed=1.3, pitch=4, volume=1.0, bass_boost=0, treble=0, reverb=0, echo=0):
        self.input_file = input_file
        self.output_file = self._generate_output_filename(input_file)
        self.speed = max(1.0, min(2.0, float(speed)))  # Clamp between 1.0 and 2.0
        self.pitch = max(0, min(12, int(pitch)))       # Clamp between 0 and 12
        self.volume = max(0.0, min(2.0, float(volume))) # Clamp between 0.0 and 2.0
        self.bass_boost = max(-10, min(10, int(bass_boost))) # Clamp between -10 and 10
        self.treble = max(-10, min(10, int(treble)))   # Clamp between -10 and 10
        self.reverb = max(0, min(100, int(reverb)))    # Clamp between 0 and 100
        self.echo = max(0, min(100, int(echo)))        # Clamp between 0 and 100
        logger.info(f"Initializing NightcoreConverter with parameters: speed={self.speed}, pitch={self.pitch}, "
                   f"volume={self.volume}, bass={self.bass_boost}, treble={self.treble}, "
                   f"reverb={self.reverb}, echo={self.echo}")
        logger.info(f"Initializing NightcoreConverter with input: {input_file}")
        logger.info(f"Output will be saved to: {self.output_file}")

    def _generate_output_filename(self, input_file):
        directory = os.path.dirname(input_file)
        filename = os.path.basename(input_file)
        name, ext = os.path.splitext(filename)
        return os.path.join(directory, f"nightcore_{name}{ext}")

    def convert(self):
        """Convert the input file to nightcore version using ffmpeg with customizable parameters"""
        # Build the complex audio filter string
        filters = []
        
        # Speed and pitch control
        if self.speed != 1.0 or self.pitch != 0:
            # Combine speed and pitch effects
            speed_factor = self.speed
            pitch_semitones = self.pitch
            filters.append(f"rubberband=pitch-scale={2**(pitch_semitones/12)}:tempo={speed_factor}")
        
        # Volume adjustment
        if self.volume != 1.0:
            filters.append(f"volume={self.volume}")
            
        # Bass and treble control using equalizer
        if self.bass_boost != 0 or self.treble != 0:
            filters.append(f"equalizer=f=100:t=h:w=200:g={self.bass_boost}") # Bass
            filters.append(f"equalizer=f=10000:t=h:w=200:g={self.treble}")  # Treble
            
        # Reverb effect
        if self.reverb > 0:
            filters.append(f"aecho=0.8:0.88:{60*self.reverb/100}:0.4")
            
        # Echo effect
        if self.echo > 0:
            delay = self.echo / 1000  # Convert percentage to seconds
            filters.append(f"aecho=0.8:0.9:{delay}:0.3")
        
        # Join all filters
        filter_string = ','.join(filters) if filters else 'anull'
        
        command = [
            'ffmpeg',
            '-i', self.input_file,
            '-af', filter_string,
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
