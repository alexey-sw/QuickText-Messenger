import os
import subprocess
from threading import Timer


def restart_function():
    subprocess.Popen(["python","C:/Users/alexe/Desktop/EasyText/server.py"])
    os._exit(0)

timer = Timer(2.0,restart_function)
timer.start()
