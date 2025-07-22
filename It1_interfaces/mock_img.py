# mock_img.py
from img import Img

class MockImg(Img):
    """Headless Img that just records calls."""
    traj     : list[tuple[int,int]]  = []   # every draw_on() position
    txt_traj : list[tuple[tuple[int,int],str]] = []

    def __init__(self):                     # override, no cv2 needed
        self.img = "MOCK-PIXELS"

    # keep the method names identical to Img -------------------------
    def read(self, path, *_, **__):
        # pretend size = (W,H) comes from file name for debug
        self.W = self.H = 1
        return self                        # chain-call compatible

    def draw_on(self, other, x, y):
        MockImg.traj.append((x, y))

    def put_text(self, txt, x, y, font_size, *_, **__):
        MockImg.txt_traj.append(((x, y), txt))

    def show(self): pass                   # do nothing

    # helper for tests
    @classmethod
    def reset(cls):
        cls.traj.clear()
        cls.txt_traj.clear()
