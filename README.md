# .my_scripts

## Usage

-   **Edit the `config.sh` file to set the following variables**

BASE_DIR: The base directory where this project folder is located.

-   **Add .my_scripts to your PATH by adding the following line to your `.bashrc` or `.bash_profile` file**

```bash
# $HOME is a shortcut for your home directory
export PATH="$HOME/.my_scripts:$PATH"
```

-   **Run the following command to install the scripts**

```bash
chmod +x my_scripts_install.sh
./my_scripts_install.sh
```

-   **Add new scripts**

因为已经把 `~/.my_scripts` 加入到 PATH 了, 所以只要把新的脚本放到项目根目录下就可以了.

## Scripts

-  **`translate_subtitles.sh`**

```bash
translate_subtitles.sh subtitle.srt <openai | gemini>
````

翻译字幕文件, 有两种翻译方式, `openai` 和 `gemini`, 需要设置 `OPENAI_API_KEY` 环境变量, `gemini` 是调用 `gemini` 的 API, 需要设置 `GEMINI_API_KEY` 环境变量.

翻译的文件需要手动校对, 为了机器翻译在相邻行之间逻辑连贯, 避免单独翻译导致的语义矛盾, 机器可能会有合并行的操作, 这会导致有的英文句子对应翻译内容为空, 或者缺少行.

-   **`merge_subtitle.py`**

```bash
$merge_subtitle.py subtitle.srt translation.srt
```

字幕文件格式 srt, 翻译文件纯文本就行, 如

`en.srt`

```
1
00:00:00,000 --> 00:00:02,959
Congress failed to pass a budget bill, and it looks like we might be

2
00:00:02,959 --> 00:00:07,667
heading for a government shutdown, and in large part this is due to the influence of Elon Musk.
```

`zh.txt`

```
国会未能通过预算案，看起来我们可能会
面临政府关门，这在很大程度上是由于Elon Musk的影响
```

合并后的文件内容:

```
1
00:00:00,000 --> 00:00:02,959
国会未能通过预算案，看起来我们可能会

2
00:00:02,959 --> 00:00:07,667
面临政府关门，这在很大程度上是由于Elon Musk的影响
```

-   **`capitalize.py`**

```bash
$capitalize.py input_file
```

将文件中每句话开头的首字母大写(如果是英文)

-   **`tts.sh`**

```bash
tts.sh en transcript.txt
```

将 `transcript.txt` 中的文本转为语音, 生成 `.wav`文件, 语言为英文, 可选参数为 `zh` 中文
