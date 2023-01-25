import cv2
from threading import Thread
from time import time

from random import randint

from debug import Debug

DEBUG = Debug(True, True)


class Engine:
    def __init__(self, img : str, vid : str, key : str = 'orb') -> None:
        self.source = [img, vid]
        self.img = cv2.imread(img)
        self.vid = cv2.VideoCapture(vid)
        self.threads = []
        self.rtn = []
        self.full_frame = int(self.vid.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = int(self.vid.get(cv2.CAP_PROP_FPS))
        self.width = int(self.vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        if 28 < self.fps < 30: # 29.97fps --> 30fps
            DEBUG.print(f"[INFO] fps: {self.fps}(29.97)fps cannot be handdled. Converted to 30fps")
            self.fps = 30
        if 22 < self.fps < 24: # 23.976fps --> 24fps
            DEBUG.print(f"[INFO] fps: {self.fps}(23.976)fps cannot be handdled. Converted to 24fps")
            self.fps = 24
        if 58 < self.fps < 60: # 59.94fps --> 60fps
            DEBUG.print(f"[INFO] fps: {self.fps}(59.94)fps cannot be handdled. Converted to 60fps")
            self.fps = 60

        self.skip_frames = [self.fps, int(self.fps / 3), int(int(self.fps / 3)/2), 1]

        self.brute = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        self.orb = cv2.ORB_create(
            nfeatures=40000,
            scaleFactor=1.2,
            nlevels=8,
            edgeThreshold=31,
            firstLevel=0,
            WTA_K=2,
            scoreType=cv2.ORB_HARRIS_SCORE,
            patchSize=31,
        )
        self.sift = cv2.SIFT_create()
        self.bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        self.algorithms = {
            'brute': self.brute,
            'orb': self.orb,
            'sift': self.sift,
        }
        self.matchers = {
            'brute': self.bf,
            'orb': self.bf,
            'sift': self.bf,
        }

        self.keys = ['brute', 'orb', 'sift']
        self.key = self.keys[1] # default key is orb
        if key in self.keys:
            self.key = key
        self._des = None
        self._kp, self._des = self._extract(self.img)
        
    def start(self) -> None:
        start = time()

        DEBUG.print(f"[INFO] full frame: {self.full_frame} | fps: {self.fps} | width: {self.width} | height: {self.height} | key: {self.key} | skip frames: {self.skip_frames}")
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
            
            while vid.isOpened():
                ret, frame = vid.read()
                if not ret:
                    break
                if cnt > ep:
                    break
                if cnt % fps == 0:
                    if sp <= cnt <= ep:
                        DEBUG.print(f"cnt: {cnt} | sp: {sp} | ep: {ep} | fps: {fps} | frame: {frame.shape} | process start")
                        thread = Thread(target=self.process, args=(cnt, frame,), daemon=True)
                        self.threads.append(thread)
                        thread.start()
                cnt += 1
            
            DEBUG.print(f"finished reading video {cnt}")
            
            for thread in self.threads:
                thread.join()
            self.threads = []
            DEBUG.print(f"[RESULT] finished joining threads {self.rtn}")
            self.max_frame()
            
            _end = time()
            DEBUG.print(f'Temporal time: {_end - _start}')
        
        end = time()
        
        DEBUG.print(f'Total time: {end - start}')
        
    def process(self, cnt, frame) -> int:
        if frame is None:
            return 0
        else:
            try:
                self._enqueue(cnt, self._compute(frame))
            except Exception as e:
                DEBUG.print(f"[ERROR] | {e}")
            return 1

    def max_frame(self) -> int:
        j = (0, 0)
        for i in self.rtn:
            if i[1] > j[1]:
                j = i
        self._clear()
        self._enqueue(j[0],j[1])
        DEBUG.print(f"max frame: {self.rtn}")

    def _enqueue(self, x : int, y : int) -> None:
        self.rtn.append((int(x), int(y)))
    
    def _clear(self) -> None:
        self.rtn = []

    def _index(self, vid : cv2, t : int):
        vid.set(cv2.CAP_PROP_POS_FRAMES, t)

    def _compute(self, frame : cv2):
        brute = self.bf
        des = self._des
        _, des2 = self._extract(frame)
        matches = brute.match(des, des2)
        matches = sorted(matches, key=lambda x: x.distance)
        return len(matches)

    def _extract(self, img : cv2):
        algorithm = self.algorithms[self.key]
        return algorithm.detectAndCompute(img, None)
        
if __name__ == "__main__":
    engine = Engine("img.png", "vid.mp4")
    engine.start()
