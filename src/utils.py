import time
import functools
from .logger import logger

def time_it(func):
    """
    一个计时装饰器，用于测量函数的执行时间并将其记录在日志中。
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        duration = end_time - start_time
        logger.info(f"⏱️  Task '{func.__name__}' finished in {duration:.2f} seconds.")
        return result
    return wrapper
