import re
import os
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
from openai import OpenAI
import google.generativeai as genai
import json
from pathlib import Path
from datetime import datetime
from sys_prompt import system_prompt_gemini

_openai_model = "gpt-40"
_gemini_model = "gemini-2.0-flash-exp"
_chunk_size = 20

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


def parse_file(file_path: str) -> List[SubtitleItem]:
    if not Path(file_path).exists():
        raise SubtitleError(f"找不到字幕文件: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        raise SubtitleError(f"无法读取字幕文件，请确保文件编码是UTF-8: {file_path}")

    # 2个或更多连续空行分割字幕块
    subtitle_blocks = re.split(r'\n\n+', content.strip())
    if not subtitle_blocks:
        raise SubtitleError("字幕文件为空")

    subtitle_items = []
    for block in subtitle_blocks:
        # 分割每个字幕块包含索引、时间戳和内容
        lines = block.split('\n')
        if len(lines) < 3:
            raise SubtitleError(f"格式错误的字幕块: {block}")

        index = int(re.sub(r'\D', '', lines[0].strip()))
        timestamp = lines[1]
        content = '\n'.join(lines[2:])
        subtitle_items.append(SubtitleItem(index, timestamp, content))

    return subtitle_items


def format_system_prompt() -> str:
    system_prompt = '''
    你是一个负责翻译字幕的程序, 要翻译的字幕内容, 它是 JSON 数组, 你按照以下步骤进行翻译:

    step1 直译：
        - 逐行翻译
        - 专有名词保持英文

    step2 意译：
        - 基于直译结果, 识别并理解完整的句子含义, 考虑上下文关系, 将生硬的直译改写为地道的中文表达
        - 确保相邻行之间逻辑连贯, 避免单独翻译导致的语义矛盾
        - 禁止添加或臆测不存在的信息

    step3 分配翻译:
      - 根据输入的 json 数组, 将 step2 的意译结果一一拆分
      - 以 "{原序号}. {原文} {原文对应的拆分后的译文}" 格式输出每个项目的内容

    不要输出多余信息, 以 json 数组格式返回, 字幕数组如下:
    '''
    return system_prompt


def _format_subtitle_items(items: List[SubtitleItem]) -> str:
    formatted_items = [
        f"{item.index}. {item.content.strip()}"
        for item in items
    ]
    return json.dumps(formatted_items, ensure_ascii=False)


# ABC (Abstract Base Class), 是 Python 标准库中的 abc 模块提供的一个类
class TranslationService(ABC):
    @abstractmethod
    def translate_chunk(self, subtitle_items: List[SubtitleItem]) -> str:
        """翻译一组字幕"""
        pass


class OpenAITranslationService(TranslationService):
    """OpenAI翻译服务实现"""

    def __init__(self, api_key: str, model: str = _openai_model):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def translate_chunk(self, subtitle_items: List[SubtitleItem]) -> str:
        system_prompt = format_system_prompt()
        user_prompt = _format_subtitle_items(subtitle_items)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            raise TranslationError(f"OpenAI翻译失败: {str(e)}")


class GeminiTranslationService(TranslationService):
    """Google Gemini翻译服务实现"""

    def __init__(self, api_key: str, model: str = _gemini_model):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)

    def translate_chunk(self, subtitle_items: List[SubtitleItem]) -> str:
        system_prompt = system_prompt_gemini
        user_prompt = _format_subtitle_items(subtitle_items)

        try:
            response = self.model.generate_content(
                [
                    system_prompt,
                    user_prompt
                ]
            )
            return response.text
        except Exception as e:
            raise TranslationError(f"Gemini翻译失败: {str(e)}")


class SubtitleTranslator:
    """字幕翻译器，支持多种翻译服务"""

    def __init__(self, translation_service: TranslationService, chunk_size: int = 10):
        self.translation_service = translation_service
        self.chunk_size = chunk_size

    def translate_subtitle_entry_chunk(self, subtitle_items: List[SubtitleItem]) -> str:
        return self.translation_service.translate_chunk(subtitle_items)

    def translate_file(self, input_file: str, output_file: str):
        """拆解字幕文件, 分段转给 AI 分段翻译, 再合并成新的字幕文件"""
        subtitle_items = parse_file(input_file)  #  subtitle_items: List[SubtitleItem]

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
    if len(sys.argv) < 3:
        print("用法: <input.srt> <service>")
        print("service 可选值: openai 或 gemini")
        sys.exit(1)

    input_file = sys.argv[1]
    service_type = sys.argv[2].lower()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = f"{Path(input_file).stem}_{timestamp}.srt"

    try:
        if service_type == "openai":
            translation_service = OpenAITranslationService(
                api_key=os.getenv("OPENAI_API_KEY"),
                model="gpt-4"
            )
        elif service_type == "gemini":
            translation_service = GeminiTranslationService(
                api_key=os.getenv("GOOGLE_API_KEY"),
                model="gemini-pro"
            )
        else:
            print(f"不支持的翻译服务: {service_type}")
            sys.exit(1)

        translator = SubtitleTranslator(
            translation_service=translation_service,
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