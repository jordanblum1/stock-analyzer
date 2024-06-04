import os
import time
import sys

def loading_indicator(stop_event):
    while not stop_event.is_set():
        print(".", end="")
        sys.stdout.flush()
        time.sleep(1)
    print()

def cleanup_files(symbol):
    os.remove(f"{symbol}_analysis.json")
    os.remove(f"{symbol}_analysis.txt")
    os.remove(f"{symbol}_historical_chart.png")
