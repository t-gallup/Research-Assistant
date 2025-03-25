import os
import boto3
import uuid

class PollyAudioSummarizer:
    def __init__(self):
        # Initialize Polly client
        self.polly_client = boto3.client('polly')
        
    def text_to_speech(self, text, output_file):
        """Convert text to speech using Amazon Polly"""
        try:
            response = self.polly_client.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId='Brian',  # Similar to the Azure voice you were using
                Engine='neural'  # Use the neural engine for better quality
            )
            
            # Write the audio stream to a file
            if "AudioStream" in response:
                with open(output_file, 'wb') as file:
                    file.write(response['AudioStream'].read())
                return True
            else:
                return False
        except Exception as e:
            print(f"Error in text_to_speech: {str(e)}")
            return False
    
    def process_file(self, url, final_summary, output_file="summary.mp3"):
        """Generate audio from the summary text"""
        try:
            # Generate a unique filename
            if not output_file:
                output_file = f"audio/audio_{uuid.uuid4()}.mp3"
            
            # Generate audio
            success = self.text_to_speech(final_summary, output_file)
            
            if success:
                return {
                    "success": True,
                    "audio_file": os.path.basename(output_file),
                    "final_summary": final_summary
                }
            else:
                return {"success": False, "error": "Failed to generate audio"}
                
        except Exception as e:
            print(f"Error processing file: {str(e)}")
            return {"success": False, "error": str(e)}