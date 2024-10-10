# WhisperFlow-cli


## Installation

### Requirements

To use WhisperFlow-cli, you need to have the following installed:

- Python 3.8+ (required)

### MacOS

- install PortAudio using [Homebrew](https://brew.sh/) : `brew install portaudio`
- use pip install requirements package : `pip install -r requirements.txt`

### Windows

- use pip install requirements package : `pip install -r requirements.txt`

### Running WhisperFlow-cli

- Run the following command to start the WhisperFlow-cli: `python whisperflow.py`

#### Command Line Arguments
This script accepts the following command line arguments:

* -s, --show_microphones (action: store_true)
  *  Description: Show available microphones.
  * Usage: If this flag is provided, the script will list all available microphones.
* -m, --microphone (type: int, default: None)
  * Description: Microphone index to use.
  * Usage: Specify the index of the microphone to use for recording. If not provided, the default microphone will be used.
* -e, --energy_threshold (type: int, default: 1000)
  * Description: Energy level for mic to detect.
  * Usage: Set the energy threshold level for the microphone to detect sound. Higher values make the microphone less sensitive.
* --translation_lang (type: str, default: English)
  * Description: Which language should we translate into.
  * Usage: Specify the target language for translation. The default language is English
* --record_timeout (type: float, default: 2)
  * Description: How real-time the recording is in seconds.
  * Usage: Set the timeout for recording in seconds. This determines how frequently the recording is processed.
* --phrase_timeout (type: float, default: 3)
  * Description: How much empty space between recordings before we consider it a new line in the transcription.
  * Usage: Set the timeout for detecting a new phrase in seconds. This determines how much silence is required to consider the start of a new line in the transcription.

