import cv2
from threading import Thread
from time import time

from random import randint

from debug import Debug

DEBUG = Debug(True, True)


class Engine:
    def __init__(self, img : str, vid : str) -> None:
        self.skip_frames = [30, 10, 5, 1]
        self.source = [img, vid]
        self.img = cv2.imread(img)
        self.vid = cv2.VideoCapture(vid)
        self.threads = []
        self.rtn = []
        self.full_frame = int(self.vid.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = int(self.vid.get(cv2.CAP_PROP_FPS))
        self.width = int(self.vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def start(self) -> None:
        start = time()
        for fps in self.skip_frames:
            _start = time()
            cnt = 0
            vid = cv2.VideoCapture(self.source[1])

            sp = 0
            ep = self.full_frame

            if self.rtn == []:
                pass
            else:
                if self.rtn[0][0] - fps**2 >= 0:
                    sp = self.rtn[0][0] - fps**2
                else:
                    sp = 0
                if self.rtn[0][0] + fps**2 < self.full_frame:
                    ep = self.rtn[0][0] + fps**2
                else:
                    ep = self.full_frame
            
            self._index(vid, sp)
            cnt = sp
            
            DEBUG.print(f"starting point: {sp} | end point: {ep} | fps: {fps} | frame: {self.full_frame} | cnt: {cnt}")
            
            while vid.isOpened():
                ret, frame = vid.read()
                if not ret:
                    break
                if cnt > ep:
                    break
                if cnt % fps == 0:
                    if sp <= cnt <= ep:
                        DEBUG.print(f"cnt: {cnt} | sp: {sp} | ep: {ep} | fps: {fps} | frame: {frame.shape} | process start")
                        thread = Thread(target=self.process, args=(cnt, fps, frame,), daemon=True)
                        self.threads.append(thread)
                        thread.start()
                cnt += 1
            
            DEBUG.print(f"finished reading video {cnt}")
            
            for thread in self.threads:
                thread.join()
            self.threads = []

            self.max_frame()
            
            _end = time()
            DEBUG.print(f'Temporal time: {_end - _start}')
        
        end = time()
        
        DEBUG.print(f'Total time: {end - start}')
        
    def process(self, cnt, fps, frame) -> int:
        if frame is None:
            return 0
        else:
            self._enqueue(cnt, randint(0, 100) / 100)
            return 1
    
    def max_frame(self) -> int:
        j = (0, 0)
        for i in self.rtn:
            if i[1] > j[1]:
                j = i
        self._clear()
        self._enqueue(j[0],j[1])
        DEBUG.print(f"max frame: {self.rtn}")

    def _enqueue(self, x : int, y : float) -> None:
        self.rtn.append((int(x), y))
    
    def _clear(self) -> None:
        self.rtn = []

    def _index(self, vid : cv2, t : int):
        vid.set(cv2.CAP_PROP_POS_FRAMES, t)
if __name__ == "__main__":
    engine = Engine("img.webp", "vid.webm")
    engine.start()