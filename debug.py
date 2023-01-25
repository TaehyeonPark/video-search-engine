from datetime import datetime
from time import time
class Debug:
    def __init__(self, on : bool, writable : bool) -> None:
        self.on = on
        self.writable = writable
        self.clear_file()
    def write(self, *args):
        if not self.on:
            return None
        text = '[DEBUG] | '
        for arg in args:
            text += str(arg) + ' | '
        print(text)
        self.write_file(text)

    def print(self, *args):
        if not self.on:
            return None
        text = '[DEBUG] '
        for arg in args:
            text += str(arg)
        print(text)
        self.write_file(text)
    
    def write_file(self, text : str):
        if not self.writable:
            return None
        with open(f'debug.log', 'a') as f:
            f.write(f'[{datetime.fromtimestamp(time()).strftime("%Y-%m-%d %H:%M:%S")}] - {text}\n')
    
    def clear_file(self):
        with open(f'debug.log', 'w') as f:
            f.write('')
            

if __name__ == "__main__":
    DEBUG = Debug(True, True)
    DEBUG.write("test", "test", "test")
    DEBUG.print("test", "test", "test")