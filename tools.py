import os
import time
from datetime import datetime, timedelta
import functools

def format_dt():
    dt = datetime.now()
    return dt.strftime("%#I:%M:%S %p %Y-%m-%d") if os.name == 'nt' else dt.strftime("%-I:%M:%S %p %Y-%m-%d")

def format_exec_time(seconds):
    td = timedelta(seconds=seconds)
    minutes, seconds = divmod(td.seconds, 60)
    return f"{minutes:02d}:{seconds:05.2f}"

def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_dt = format_dt()
        print(f"Starting {func.__name__} at: {start_dt}")
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        end_dt = format_dt()
        print(f"Ending {func.__name__} at: {end_dt}")
        
        execution_time = end_time - start_time
        formatted_time = format_exec_time(execution_time)
        print(f"Total execution time for {func.__name__}: {formatted_time}")
        
        return result
    return wrapper

def print_returns(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned: {result}")
        return result
    return wrapper

def count_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.count += 1
        print(f"{func.__name__} calls: {wrapper.count}")
        return func(*args, **kwargs)
    wrapper.count = 0
    return wrapper