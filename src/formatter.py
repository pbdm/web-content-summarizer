from pathlib import Path
import datetime

class MarkdownFormatter:
    def _format_timestamp(self, seconds: float) -> str:
        td = datetime.timedelta(seconds=seconds)
        s = str(td).split(".")[0]
        if s.startswith("0:"):
            s = "0" + s
        return s

    def save(self, segments, output_path: Path, title: str, source_url: str):
        print(f"Saving markdown to {output_path}...")
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        clean_url = source_url.split("?")[0] if "?" in source_url else source_url
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("---\n")
            f.write(f"created: {current_time}\n")
            f.write(f"source: {source_url}\n")
            f.write("tags:\n  - bilibili\n  - transcript\n  - inbox\n")
            f.write("---\n\n")
            f.write(f"# {title}\n\n")
            f.write("> [!ai]+ AI 整理指令\n")
            f.write("> 复制以下 Prompt 发送给 ChatGPT/Claude 进行整理：\n")
            f.write("> \n")
            f.write("> `请阅读这篇 Bilibili 视频的逐字稿，完成以下任务：`\n")
            f.write("> `1. 用一句话总结核心观点。`\n")
            f.write("> `2. 提取 3-5 个关键概念，并解释其在文中的含义。`\n")
            f.write("> `3. 生成一份层级分明的逻辑大纲。`\n")
            f.write("> `4. 识别文中提到的任何书籍、工具或重要人物，生成 [[WikiLink]] 格式。`\n\n")
            f.write("---\n\n")
            for item in segments:
                item_type = getattr(item, "type", "speech")
                start_str = self._format_timestamp(item.start)
                start_seconds = int(item.start)
                text = item.text.strip()
                timestamp_link = f"{clean_url}?t={start_seconds}"
                if item_type == "ocr":
                    f.write(f"> [!abstract] 📺 画面文字 ({start_str})\n")
                    for line in text.split("\n"):
                        f.write(f"> {line}\n")
                    f.write("\n")
                else:
                    f.write(f"- [{start_str}]({timestamp_link}) {text}\n")
        print("Markdown saved successfully.")
