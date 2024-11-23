#!/bin/bash

# 检查并激活虚拟环境
# 参数: $1 - 虚拟环境激活脚本路径
activate_venv() {
    local venv_path="$1"
    
    # 检查虚拟环境激活脚本
    if [ ! -f "${venv_path}" ]; then
        echo "错误：找不到虚拟环境，请检查路径：${venv_path}"
        exit 1
    fi

    # 激活虚拟环境后, 会自动修改当前 shell 会话的环境变量，主要是 PATH
    # 他会把虚拟环境的 bin 目录放到 PATH 的最前面
    # 这样，无论你在哪个目录下，都会优先使用虚拟环境中的 python/pip 等命令
    source "${venv_path}"
}