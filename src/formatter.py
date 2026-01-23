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
        将转录片段保存为 Markdown 文件
        """
        print(f"Saving markdown to {output_path}...")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # 写入 Frontmatter 和 标题
            f.write(f"# {title}\n\n")
            f.write(f"**Source**: [{source_url}]({source_url})\n")
            f.write(f"**Date**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            # 写入内容
            for segment in segments:
                start = self._format_timestamp(segment.start)
                text = segment.text.strip()
                
                # 格式：[00:00:15] 文本内容
                f.write(f"- **[{start}]** {text}\n")
                
        print("Markdown saved successfully.")

