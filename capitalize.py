#!/usr/bin/env python3

import sys
from datetime import datetime
from pathlib import Path

if len(sys.argv) != 2:
    print("使每行内容开头首字母大写, 用法: 输入文件.srt")
    sys.exit(1)

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
input_file_path = sys.argv[1]
output_file_path = f"{Path(input_file_path)}_cap_{timestamp}.srt"

with open(input_file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(len(lines)):
    if lines[i].strip() and lines[i][0].isalpha():
        lines[i] = lines[i][0].upper() + lines[i][1:]

with open(output_file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"处理完成: {input_file_path} -> {output_file_path}")
