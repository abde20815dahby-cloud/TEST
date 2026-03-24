import os

# ==========================================
# 🌟 Vibrant Neon & Animated Style
# ==========================================
# ألوان الواجهة الأمامية (الخلفية ستكون متحركة)
NAV_BG = "#130b29"  # لون ليلي بنفسجي غامق
CARD_BG = "#1a103c"  # لون البطاقات
TEXT_PRIMARY = "#FFFFFF"
TEXT_MUTED = "#00FFFF"  # سماوي حي عوض الرمادي الميت

# ألوان نيون مشعة جداً (Vibrant Accents)
ACCENT_CYAN = "#00E5FF"
ACCENT_MAGENTA = "#FF00FF"
ACCENT_YELLOW = "#FFE600"
ACCENT_GREEN = "#00FF66"

THEMES = {
    "main": {"color": ACCENT_CYAN, "name": "التدقيق والتطهير"},
    "stamper": {"color": ACCENT_MAGENTA, "name": "المصادقة والختم"},
    "pv": {"color": ACCENT_GREEN, "name": "معالج المحاضر"},
    "dxf": {"color": ACCENT_YELLOW, "name": "المحرك الهندسي"},
}

USER_DOCS = os.path.join(os.path.expanduser("~"), "Documents")
TRASH_DIR = os.path.join(USER_DOCS, "ANCFCC_Trash")
BACKUP_DIR = os.path.join(USER_DOCS, "ANCFCC_Backups")

os.makedirs(TRASH_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)
