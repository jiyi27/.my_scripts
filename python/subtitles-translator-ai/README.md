# subtitles-translator-ai

## Installation

Add the OpenAI and Gemini API key to your .bashrc file in the root of your home folder (.zshrc if you use zsh).

```bash
export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
export GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
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
## Usage

```bash
python translator.py <input_srt_file> <openai | gemini>
```