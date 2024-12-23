#!/usr/bin/env python3

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List
import sys


class SubtitleError(Exception):
    """字幕处理相关的异常"""
    pass


@dataclass
class SubtitleItem:
    index: int
    timestamp: str
    content: str

    def __str__(self):
        return f"{self.index}\n{self.timestamp}\n{self.content}\n"


def parse_srt(file_path: str) -> List[SubtitleItem]:
    if not Path(file_path).exists():
        raise SubtitleError(f"找不到字幕文件: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        raise SubtitleError(f"无法读取字幕文件，请确保文件编码是UTF-8: {file_path}")

    # 以2个或更多连续空行分割字幕块
    # strip(): 去掉字符串首尾的空白字符(whitespace), 包括空格、换行符...
    subtitle_blocks = re.split(r'\n\n+', content.strip())
    if not subtitle_blocks:
        raise SubtitleError("字幕文件为空")

    subtitle_items = []
    for block in subtitle_blocks:
        # 以换行分割每个字幕块包含索引 时间戳 内容
        lines = block.split('\n')
        if len(lines) < 3:
            raise SubtitleError(f"格式错误的字幕块: {block}")

        index = int(re.sub(r'\D', '', lines[0].strip()))
        timestamp = lines[1].strip()
        content = '\n'.join(lines[2:])
        subtitle_items.append(SubtitleItem(index, timestamp, content))

    return subtitle_items


def parse_translations(file_path: str) -> List[str]:
    """
    解析翻译文件, 以行为单位分割, 返回数组
    """
    if not Path(file_path).exists():
        raise SubtitleError(f"找不到翻译文件: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        raise SubtitleError(f"无法读取翻译文件，请确保文件编码是UTF-8: {file_path}")

    lines = re.split(r'\n', content.strip())
    if not lines:
        raise SubtitleError("翻译文件为空")

    # 确保每个翻译都去掉首尾空白字符
    return [t.strip() for t in lines if t.strip()]


def create_translated_srt(subtitles: List[SubtitleItem], translations: List[str], output_path: str):
    """
    创建新的字幕文件，使用翻译内容替换原字幕内容
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        for subtitle, translation in zip(subtitles, translations):
            new_subtitle = SubtitleItem(
                subtitle.index, subtitle.timestamp, translation)
            f.write(str(new_subtitle) + '\n')


def main():
    if len(sys.argv) < 3:
        print("请提供字幕和翻译文件的路径")
        print("用法: merge_subtitle.py <subtitle_file> <translation_file>")
        sys.exit(1)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    subtitle_file_path = sys.argv[1]
    translation_file_path = sys.argv[2]
    output_file = f"ch{Path(subtitle_file_path).stem}_{timestamp}.srt"

    try:
        # 解析原始字幕和翻译
        # subtitle_items: List[SubtitleItem]
        subtitle_items = parse_srt(subtitle_file_path)
        translation_lines = parse_translations(
            translation_file_path)  # translation_lines: List[str]

        # 检查数量是否匹配
        if len(subtitle_items) != len(translation_lines):
            print(f"错误：字幕数量 ({len(subtitle_items)}) 与翻译行数 ({len(translation_lines)}) 不匹配")
            sys.exit(1)

        # 创建新的字幕文件
        create_translated_srt(subtitle_items, translation_lines, output_file)
        print(f"成功创建翻译后的字幕文件：{output_file}")

    except SubtitleError as e:
        print(f"字幕处理错误: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"未知错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
