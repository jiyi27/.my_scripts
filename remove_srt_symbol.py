#!/usr/bin/env python3

import sys

"""
知识点1:
- rstrip() 去掉结尾空白字符(whitespace characters), 空格 (space), 换行符 (newline \n)
- strip() 去掉开头和结尾的空白字符

知识点2:
在 Python 中,任何非空字符串(即使只包含空白字符)在布尔上下文中都会被认为是 True,
因此空格字符串 " " 以及换行符 "\n" 等都会被认为是 True
只有空字符串 "" 会被认为是 False

name = "\n"
if name:
    print("Hello, " + name)
else:
    print("name is empty")
"""

# 检查命令行参数
if len(sys.argv) != 3:
    print("去掉字幕结尾中的标点符号, 使用方法: remove_srt_symbol.py 输入文件.srt 输出文件.srt")
    sys.exit(1)

# 获取输入输出文件名
input_file = sys.argv[1]
output_file = sys.argv[2]

# 读取文件内容
with open(input_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 处理每一行
processed_lines = []
for line in lines:
    content = line.strip()
    # 如果行不为空且末尾是标点符号，则去掉标点
    if content and content[-1] in '.。!！?？,，':
        content = content[:-1]
    # 保持原有的换行格式
    processed_lines.append(content + '\n')

# 写入处理后的内容到新文件
with open(output_file, 'w', encoding='utf-8') as f:
    f.writelines(processed_lines)
