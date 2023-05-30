import time
import azure.cognitiveservices.speech as speechsdk

from uglygpt.base import config
from uglygpt.provider.speech_recognizer.base import SpeechRecongnizerProvider

class AzureSpeechRecongnizerProvider(SpeechRecongnizerProvider):
    def __init__(self):
        self.speech_config = speechsdk.SpeechConfig(subscription=config.azure_key, region=config.azure_region)

    def recognition(self, file_path: str, language: str = "zh-CN") -> str:
        self.speech_config.speech_recognition_language=language
        #audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

        audio_config = speechsdk.AudioConfig(filename=file_path)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=self.speech_config, audio_config=audio_config)

        res = ""

        def handle_final_result(evt):
            if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                nonlocal res
                res += ' ' + evt.result.text

        done = False

        def stop_cb(_):
            nonlocal done
            done = True
            speech_recognizer.stop_continuous_recognition()
            print('Continuous recognition stopped.')

        speech_recognizer.recognized.connect(handle_final_result)
        speech_recognizer.session_stopped.connect(stop_cb)
        speech_recognizer.canceled.connect(stop_cb)

        speech_recognizer.start_continuous_recognition()
        print('Continuous Recognition is now running, Please wait.')
        while not done:
            time.sleep(0.5)

        return res