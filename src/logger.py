import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
LOG_DIR = PROJECT_ROOT / "temp" / "logs"


def setup_logger(name="BiliTranscribe"):
    """
    配置并返回一个全局 logger。
    输出到控制台和文件。
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # 生成带有时间戳的日志文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOG_DIR / f"run_{timestamp}.log"

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # 格式化器：时间 - 级别 - 模块 - 消息
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # 文件处理器
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # 避免重复添加处理器
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger


# 创建默认 logger 实例
logger = setup_logger()
