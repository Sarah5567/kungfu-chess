import pathlib
import pytest
from types import SimpleNamespace
from Graphics import Graphics

# ─── Fake Classes ──────────────────────────────────────────────────────────

class FakeImg:
    """A fake Img class to simulate loaded images."""
    def __init__(self, name):
        self.name = name

# נחליף את הפונקציה _load_sprites בזמן הטסט, כדי שלא נצטרך תמונות אמיתיות
def fake_load_sprites(self, folder):
    return [FakeImg("frame0"), FakeImg("frame1"), FakeImg("frame2")]

# ─── Fixtures / Arrange Helpers ────────────────────────────────────────────

@pytest.fixture
def graphics():
    Graphics._load_sprites = fake_load_sprites
    g = Graphics(pathlib.Path("."), board=SimpleNamespace(), loop=True, fps=2.0)
    return g

# ─── Tests ─────────────────────────────────────────────────────────────────

def test_WhenReset_ThenStartTimeAndFrameReset(graphics):
    # Arrange
    cmd = SimpleNamespace(timestamp=1000)  # Fake Command

    # Act
    graphics.reset(cmd)

    # Assert
    assert graphics.start_time == 1000
    assert graphics.current_frame == 0

def test_WhenUpdateBeforeStart_ThenFrameZero(graphics):
    # Arrange
    graphics.start_time = 500

    # Act
    graphics.update(now_ms=400)  # לפני תחילת הזמן

    # Assert
    assert graphics.current_frame == 0

def test_WhenUpdateLooping_ThenFrameCycles(graphics):
    # Arrange
    graphics.start_time = 0

    # Act
    graphics.update(now_ms=2000)  # fps=2 => frame_time_ms=500 => 2000/500=4

    # Assert
    # יש 3 פריימים => 4 % 3 = 1
    assert graphics.current_frame == 1

def test_WhenUpdateNotLooping_ThenFrameStops():
    # Arrange
    Graphics._load_sprites = fake_load_sprites
    g = Graphics(pathlib.Path("."), board=SimpleNamespace(), loop=False, fps=2.0)
    g.start_time = 0

    # Act
    g.update(now_ms=5000)  # הרבה אחרי הסוף

    # Assert
    assert g.current_frame == 2  # נשאר בפריים האחרון

def test_WhenGetImg_ThenReturnsCorrectFrame(graphics):
    # Arrange
    graphics.current_frame = 2

    # Act
    img = graphics.get_img()

    # Assert
    assert isinstance(img, FakeImg)
    assert img.name == "frame2"
