import os
import subprocess

class NightcoreConverter:
    def __init__(self, input_file):
        self.input_file = input_file
        self.output_file = self._generate_output_filename(input_file)

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
        
        try:
            subprocess.run(command, check=True, capture_output=True)
            return self.output_file
        except subprocess.CalledProcessError as e:
            raise Exception(f"FFmpeg conversion failed: {e.stderr.decode()}")
        except FileNotFoundError:
            raise Exception("FFmpeg is not installed on the system")
