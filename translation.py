import argparse
import speech_recognition as sr
from faster_whisper import WhisperModel
from queue import Queue
from tempfile import NamedTemporaryFile
from datetime import datetime, timedelta
import io
import os
from time import sleep


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--show_microphones", action='store_true',
                        help="Show available microphones.")
    parser.add_argument("-m", "--microphone", default=None,
                        help="Microphone index to use.", type=int)
    parser.add_argument("-e", "--energy_threshold", default=1000,
                        help="Energy level for mic to detect.", type=int)
    parser.add_argument("--translation_lang", default='English',
                        help="Which language should we translate into.", type=str)
    parser.add_argument("--record_timeout", default=2,
                        help="How real time the recording is in seconds.", type=float)
    parser.add_argument("--phrase_timeout", default=3,
                        help="How much empty space between recordings before we "
                             "consider it a new line in the transcription.", type=float)
    args = parser.parse_args()

    if args.show_microphones:
        show_microphones()
        return

    # The last time a recording was retreived from the queue.
    phrase_time = None
    # Current raw audio bytes.
    last_sample = bytes()
    # Thread safe Queue for passing data from the threaded recording callback.
    data_queue = Queue()

    recorder = sr.Recognizer()
    recorder.energy_threshold = args.energy_threshold
    # Definitely do this, dynamic energy compensation lowers the energy threshold dramtically to a point where the SpeechRecognizer never stops recording.
    recorder.dynamic_energy_threshold = False

    if args.microphone is not None:
        source = sr.Microphone(sample_rate=16000)
    else:
        source = sr.Microphone(sample_rate=16000, device_index=args.microphone)

    model_size = "large-v3"
    audio_model = WhisperModel(model_size, device="cpu", compute_type="int8")

    record_timeout = args.record_timeout
    phrase_timeout = args.phrase_timeout

    temp_file = NamedTemporaryFile().name
    transcription = ['']

    recognizer = sr.Recognizer()
    with source as source:
        recorder.adjust_for_ambient_noise(source)

    def record_callback(_, audio: sr.AudioData) -> None:
        """
        Threaded callback function to recieve audio data when recordings finish.
        audio: An AudioData containing the recorded bytes.
        """
        # Grab the raw bytes and push it into the thread safe queue.
        data = audio.get_raw_data()
        data_queue.put(data)

    # Create a background thread that will pass us raw audio bytes.
    # We could do this manually but SpeechRecognizer provides a nice helper.
    recorder.listen_in_background(
        source, record_callback, phrase_time_limit=record_timeout)

    # Cue the user that we're ready to go.
    print("Model loaded.\n")

    while True:
        try:
            now = datetime.now()
            # Pull raw recorded audio from the queue.
            if not data_queue.empty():

                phrase_complete = False
                # If enough time has passed between recordings, consider the phrase complete.
                # Clear the current working audio buffer to start over with the new data.
                if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout):
                    last_sample = bytes()
                    phrase_complete = True
                # This is the last time we received new audio data from the queue.
                phrase_time = now

                # Concatenate our current audio data with the latest audio data.
                while not data_queue.empty():
                    data = data_queue.get()
                    last_sample += data

                # Use AudioData to convert the raw data to wav data.
                audio_data = sr.AudioData(
                    last_sample, source.SAMPLE_RATE, source.SAMPLE_WIDTH)
                wav_data = io.BytesIO(audio_data.get_wav_data())

                # #Write wav data to the temporary file as bytes.
                # with open(temp_file, "wb") as f:
                #     f.write(wav_data.read())

                # Write wate to backup.wav file
                # with open("backup.wav", "wb") as f:
                #     f.write(wav_data.read())

                # Read the transcription.
                text = ""

                # segments, info = audio_model.transcribe("backup.wav")
                segments, info = audio_model.transcribe(wav_data)
                for segment in segments:
                    text += segment.text

                # If we detected a pause between recordings, add a new item to our transcripion.
                # Otherwise edit the existing one.
                if phrase_complete:
                    transcription.append(text)
                else:
                    transcription[-1] = text

                # Clear the console to reprint the updated transcription.
                # os.system('cls' if os.name == 'nt' else 'clear')
                for line in transcription:
                    print(line)
                # Flush stdout.
                print('', end='', flush=True)

                last_four_elements = transcription[-10:]
                result = ''.join(last_four_elements)
            else:
                sleep(0.25)

        except KeyboardInterrupt:
            print("Exiting...")
            break


def show_microphones():
    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        print(f"Microphone with name \"{
              name}\" found for `Microphone(device_index={index})`")


if __name__ == "__main__":
    main()
