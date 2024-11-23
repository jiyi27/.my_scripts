#!/bin/bash

VENV_PATH="/Users/david/Codes/PyCharm/subtitles-translator-ai/.venv/bin/activate"
if [ ! -f "$VENV_PATH" ]; then
    echo "错误：找不到虚拟环境，请检查路径：$VENV_PATH"
    exit 1
fi

# 激活虚拟环境
source "$VENV_PATH"

# 使用虚拟环境中的Python
python "/Users/david/Codes/PyCharm/subtitles-translator-ai/translator.py" "$@"

# 退出虚拟环境
deactivate
