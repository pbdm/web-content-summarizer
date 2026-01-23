from pathlib import Path
import datetime

class MarkdownFormatter:
    def _format_timestamp(self, seconds: float) -> str:
        """将秒数转换为 HH:MM:SS 格式"""
        td = datetime.timedelta(seconds=seconds)
        # 去掉微秒，保留到秒
        s = str(td).split('.')[0]
        if s.startswith("0:"):
            s = "0" + s  # 补齐格式为 00:00:00
        return s

    def save(self, segments, output_path: Path, title: str, source_url: str):
        """
        将转录片段保存为 Obsidian 友好的 Markdown 文件
        """
        print(f"Saving markdown to {output_path}...")
        
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        
        # 处理 Bilibili URL，确保是干净的 base url 用于拼接时间戳
        # 简单处理：去掉 ? 及其后面的参数，防止叠加
        clean_url = source_url.split('?')[0] if '?' in source_url else source_url

        with open(output_path, 'w', encoding='utf-8') as f:
            # 1. 写入 YAML Frontmatter (Obsidian 核心元数据)
            f.write("---
")
            f.write(f"created: {current_time}
")
            f.write(f"source: {source_url}
")
            f.write("tags:\n  - bilibili\n  - transcript\n  - inbox\n")
            f.write("---

")
            
            # 2. 写入标题和 AI 整理提示区域 (Callout)
            f.write(f"# {title}\n\n")
            
            f.write("> [!ai]+ AI 整理指令\n")
            f.write("> 复制以下 Prompt 发送给 ChatGPT/Claude 进行整理：\n")
            f.write("> \n")
            f.write("> `请阅读这篇 Bilibili 视频的逐字稿，完成以下任务：`\n")
            f.write("> `1. 用一句话总结核心观点。`\n")
            f.write("> `2. 提取 3-5 个关键概念，并解释其在文中的含义。`\n")
            f.write("> `3. 生成一份层级分明的逻辑大纲。`\n")
            f.write("> `4. 识别文中提到的任何书籍、工具或重要人物，生成 [[WikiLink]] 格式。`\n\n")
            
            f.write("---

")
            
            # 3. 写入内容 (带时间戳跳转链接)
            for segment in segments:
                start_str = self._format_timestamp(segment.start)
                start_seconds = int(segment.start)
                text = segment.text.strip()
                
                # Bilibili 时间戳链接格式: url?t=秒数
                # 兼容处理: 如果原 url 已有参数，可能需要用 &t=，但 B站通常支持直接拼接
                # 为了保险，我们使用 clean_url 拼接
                timestamp_link = f"{clean_url}?t={start_seconds}"
                
                # 格式：- [00:00:15](url) 文本内容
                f.write(f"- [{start_str}]({timestamp_link}) {text}\n")
                
        print("Markdown saved successfully.")