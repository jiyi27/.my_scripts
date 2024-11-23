#!/bin/bash

# 下面这种写法是错误的，cd 是根据当前 shell 的工作目录来的，不是脚本文件所在的目录, cd 也不一定能成功
# cd python
# python3 -m venv .venv
# source .venv/bin/activate
# pip install -r requirements.txt
# deactivate


# $0 表示当前执行的脚本文件的完整路径
# dirname $0 表示当前执行的脚本文件的路径, 不包含文件名
# 所以 config.sh, utils.sh 必须在当前脚本文件的同一目录下
source "$(dirname "$0")/config.sh"
source "$(dirname "$0")/utils.sh"

# 记住当前目录
CURRENT_DIR=$(pwd)

# 确保 python 目录存在并进入
mkdir -p "${BASE_PATH}/python"
cd "${BASE_PATH}/python"

# 如果虚拟环境不存在，创建一个
if [ ! -f "${VENV_ACTIVATE_PATH}" ]; then
    echo "创建虚拟环境: ${VENV_PATH}"
    python3 -m venv .venv
fi

# 返回之前的目录
cd "${CURRENT_DIR}"

# 检查并激活虚拟环境
activate_venv "${VENV_ACTIVATE_PATH}"

echo "Using Python: $(which python)"
echo "Using pip: $(which pip)"

# 安装依赖
pip install -r "${REQUIREMENTS_PATH}"

# 退出虚拟环境
deactivate
