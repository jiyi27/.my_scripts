# Azure TTS Python

## Installation

Create AI Speech - Text to Speech resource in Azure, and you can get the key and region from the resource.

![](https://pub-2a6758f3b2d64ef5bb71ba1601101d35.r2.dev/blogs/2024/12/cfea5a00b7c1fbc739513249755dc2a1.png)

```bash
export SPEECH_KEY="YOUR_SPEECH_KEY"
export SPEECH_REGION="YOUR_SPEECH_REGION"
```

Create a virtual environment using the following command.

```bash
python3 -m venv .venv
```

Activate the virtual environment using the following command.

```bash
source .venv/bin/activate
```

Then run the following command to install the required packages.

```bash
pip install -r requirements.txt
```

> requirements.txt file is located in the root of the project folder.

## Usage

```bash
python tts.py <input_srt_file>
```