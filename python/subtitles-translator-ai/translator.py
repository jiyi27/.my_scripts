import re
import os
import sys
from dataclasses import dataclass
from typing import List, Tuple
from openai import OpenAI
import json
from pathlib import Path


class SubtitleError(Exception):
    """字幕处理相关的异常"""
    pass


class TranslationError(Exception):
    """翻译相关的异常"""
    pass


@dataclass
class SubtitleItem:
    index: int
    timestamp: str
    content: str

    def __str__(self):
        return f"{self.index}\n{self.timestamp}\n{self.content}\n"


class SrtParser:
    @staticmethod
    def parse(file_path: str) -> List[SubtitleItem]:
        if not Path(file_path).exists():
            raise SubtitleError(f"找不到字幕文件: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            raise SubtitleError(f"无法读取字幕文件，请确保文件编码是UTF-8: {file_path}")

        subtitle_blocks = re.split(r'\n\n+', content.strip())
        if not subtitle_blocks:
            raise SubtitleError("字幕文件为空")

        subtitle_items = []
        for block in subtitle_blocks:
            lines = block.split('\n')
            if len(lines) < 3:
                raise SubtitleError(f"格式错误的字幕块: {block}")

            index = int(re.sub(r'\D', '', lines[0].strip()))
            timestamp = lines[1]
            content = '\n'.join(lines[2:])
            subtitle_items.append(SubtitleItem(index, timestamp, content))

        return subtitle_items


class SubtitleTranslator:
    def __init__(self, api_key: str, model: str = "gpt-4o", chunk_size: int = 10):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.chunk_size = chunk_size
        self.system_prompt = """
        你是一个专业的字幕翻译专家, 请严格按照以下要求进行翻译:

翻译过程分为3个阶段：

1. 直译阶段：
    - 逐行翻译
    - 专有名词保持英文

2. 意译阶段：
    - 基于直译结果, 识别并理解完整的句子含义, 考虑上下文关系, 将生硬的直译改写为地道的中文表达
    - 确保相邻行之间逻辑连贯, 避免单独翻译导致的语义矛盾
    - 禁止添加或臆测不存在的信息

3. 校对阶段：

正确示例：

输入：

38. in the House formed the bill, but that process wasn't transparent
39. to the rest of the congress people.

输出：

literal:
38. 在众议院制定了该法案, 但是那个过程并不透明
39. 对其余的国会议员来说

free:
38. 众议院起草了这项法案，但这个过程对其他
39. 国会议员而言并不透明

输入字幕如下, 请开始按以上要求翻译:
        """

    # 把多行字幕合并成一个有序号的字符串
    @staticmethod
    def _format_subtitle_entries(entries: List[SubtitleItem]) -> str:
        formatted_text = ""
        for entry in entries:
            formatted_text += f"{entry.index}. {entry.content.strip()}\n"
        return formatted_text

    # Open AI 翻译字幕
    def translate_subtitle_entry_chunk(self, entries: List[SubtitleItem]) -> str:
        user_prompt = self._format_subtitle_entries(entries)
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )

            return response.choices[0].message.content
        except Exception as e:
            raise TranslationError(f"翻译失败: {str(e)}")

    # 拆解字幕文件, 转给 Open AI 分段翻译, 再合并成新的字幕文件
    def translate_file(self, input_file: str, output_file: str):
        # subtitle_items: List[SubtitleItem]
        subtitle_items = SrtParser.parse(input_file)

        # + self.chunk_size - 1 向上取整, 用于下面显示进度, 如: 1/7, 2/7, 3/7...
        # ‘//’ 在 Python 中是整除运算符（floor division operator）, 它会执行除法并向下取整（floor）到最接近的整数
        # 例如：print(25/10)    # 输出: 2.5, 向上取整(2.5) = 3
        # 等价于: (25 + 10 - 1) // 10 = 34 // 10 = 3, 这也是为什么总要 -1
        total_chunks = (len(subtitle_items) + self.chunk_size - 1) // self.chunk_size
        translated_entries = []

        for i in range(0, len(subtitle_items), self.chunk_size):
            chunk = subtitle_items[i:i + self.chunk_size]
            current_chunk = i // self.chunk_size + 1
            print(f"翻译进度: {current_chunk}/{total_chunks}")

            translated_entries.append(
                self.translate_subtitle_entry_chunk(chunk))

        with open(output_file, 'w', encoding='utf-8') as f:
            for entry in translated_entries:
                f.write(str(entry) + '\n')
        print(f"\n翻译完成! 已保存到: {output_file}")


def main():
    if len(sys.argv) != 3:
        print("请指定两个参数 input.srt output.srt")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        translator = SubtitleTranslator(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4o",
            chunk_size=20
        )
        translator.translate_file(input_file, output_file)
    except SubtitleError as e:
        print(f"字幕处理错误: {str(e)}")
        sys.exit(1)
    except TranslationError as e:
        print(f"翻译错误: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"未知错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
