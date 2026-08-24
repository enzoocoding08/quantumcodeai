"""Brand-Konstanten fuer die Story-Highlight-Cover. Dunkles Terminal-Theme,
passend zum Rest des QuantCode-AI-Accounts (nicht der Creme-Editorial-Look
des anderen Accounts)."""

from pathlib import Path

WIDTH, HEIGHT = 1080, 1920

BG = (11, 14, 17)          # 0b0e11
CARD_BG = (18, 22, 27)     # 12161b
BORDER = (35, 40, 48)      # 232830
TEXT = (238, 241, 243)     # eef1f3
MUTED = (107, 117, 128)    # 6b7580
FAINT = (74, 81, 88)       # 4a5158
ACCENT = (20, 184, 166)    # 14b8a6

FONTS_DIR = Path(__file__).parent / "fonts"
FONT_DISPLAY_BOLD = str(FONTS_DIR / "DejaVuSans-Bold.ttf")
FONT_BODY = str(FONTS_DIR / "DejaVuSans.ttf")
FONT_MONO = str(FONTS_DIR / "DejaVuSansMono.ttf")
FONT_MONO_BOLD = str(FONTS_DIR / "DejaVuSansMono-Bold.ttf")

MARGIN_X = 84
DISCLAIMER = "Keine Anlageberatung · keine Kauf-/Verkaufsempfehlung"
HANDLE = "@quantcode.ai"
