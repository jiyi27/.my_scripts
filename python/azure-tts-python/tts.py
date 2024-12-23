import os
import sys
from datetime import datetime
from pathlib import Path
import azure.cognitiveservices.speech as speechsdk


class AzureTTS:
    def __init__(self, english=False):
        """
        Initialize Azure TTS client using environment variables
        """
        self.subscription_key = os.environ.get('SPEECH_KEY')
        self.region = os.environ.get('SPEECH_REGION')

        if not self.subscription_key or not self.region:
            print("Error: SPEECH_KEY and SPEECH_REGION environment variables must be set")
            sys.exit(1)

        self.speech_config = speechsdk.SpeechConfig(
            subscription=self.subscription_key,
            region=self.region
        )
        # other options: zh-CN-XiaochenMultilingualNeural, zh-CN-XiaoxiaoMultilingualNeural, en-US-AndrewMultilingualNeural
        self.speech_config.speech_synthesis_voice_name = "en-US-AndrewMultilingualNeural" if english else "zh-CN-XiaoxiaoMultilingualNeural"
        self.language = "en-US" if english else "zh-CN"
        self.voice_role = None
        self.voice_style = None

    def set_voice(self, voice_name):
        """Set the voice for synthesis"""
        self.speech_config.speech_synthesis_voice_name = voice_name

    def _create_ssml(self, text, role=None, style=None, language="zh-CN"):
        """
        Create SSML with role, style and language support
        """
        ssml = f"""
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="{language}">
            <voice name="{self.speech_config.speech_synthesis_voice_name}">
        """

        # Build express-as tag if role or style is provided
        if role or style:
            express_as_attrs = []
            if role:
                express_as_attrs.append(f'role="{role}"')
            if style:
                express_as_attrs.append(f'style="{style}"')
            ssml += f'<mstts:express-as {" ".join(express_as_attrs)}>'

        ssml += f"{text}"

        if role or style:
            ssml += '</mstts:express-as>'

        ssml += """
            </voice>
        </speak>
        """
        return ssml

    def text_to_speech(self, text, output_path, role=None, style=None, language=None):
        """Convert text to speech and save to file"""
        audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.speech_config,
            audio_config=audio_config
        )

        if role or style:
            ssml = self._create_ssml(text, role, style, language)
            result = synthesizer.speak_ssml_async(ssml).get()
        else:
            result = synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print(f"Audio saved to: {output_path}")
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print(f"Speech synthesis canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print(
                        f"Error details: {cancellation_details.error_details}")
                    print(
                        "Did you set the speech resource key and region values correctly?")
            sys.exit(1)

    def file_to_speech(self, input_file_path, output_file_path):
        """Convert text file to speech file"""
        try:
            input_path = Path(input_file_path)
            if not input_path.is_file():
                print(f"Error: Input file not found: {input_file_path}")
                sys.exit(1)

            with input_path.open('r', encoding='utf-8') as f:
                text = f.read().strip()

            if not text:
                print(f"Error: Input file is empty: {input_file_path}")
                sys.exit(1)

            self.text_to_speech(text, str(output_file_path), role=self.voice_role, style=self.voice_style,
                                language=self.language)

        except Exception as e:
            print(f"Error during file processing: {str(e)}")
            sys.exit(1)


def main():
    """Main function to handle command line arguments and execute conversion"""
    if len(sys.argv) != 3:
        print("请提供语言以及台词文件")
        print("语言可选值: zh 或 en")
        sys.exit(1)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    try:
        if sys.argv[1] == "en":
            tts = AzureTTS(english=True)
        else:
            tts = AzureTTS()

        input_file_path = sys.argv[2]
        output_file_path = f"{Path(input_file_path).stem}_{timestamp}.wav"

        tts.file_to_speech(input_file_path, output_file_path)

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
