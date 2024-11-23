#!/usr/bin/env python3

import sys

if len(sys.argv) != 3:
    print("用法: 输入文件.srt 输出文件.srt")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

with open(input_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(len(lines)):
    if lines[i].strip() and lines[i][0].isalpha():
        lines[i] = lines[i][0].upper() + lines[i][1:]

with open(output_file, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"处理完成: {input_file} -> {output_file}")
