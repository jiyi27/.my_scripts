#!/bin/bash

# $0 表示当前执行的脚本文件的完整路径
# dirname $0 表示当前执行的脚本文件的路径, 不包含文件名
# 所以 config.sh, utils.sh 必须在当前脚本文件的同一目录下
source "$(dirname "$0")/config.sh"
source "$(dirname "$0")/utils.sh"

# 检查并激活虚拟环境
activate_venv "${VENV_ACTIVATE_PATH}"

# 使用虚拟环境中的Python
python "${TTS_SCRIPT_PATH}" "$@"

# 退出虚拟环境
deactivate
