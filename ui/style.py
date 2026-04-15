from PyQt5.QtGui import QFont

# 蓝白现代风配色（GitHub同款）
COLOR_PRIMARY     = "#165DFF"
COLOR_SECONDARY   = "#36CFC9"
COLOR_SUCCESS     = "#27AE60"
COLOR_WARNING     = "#FF7D00"
COLOR_DANGER      = "#E53935"
COLOR_BACKGROUND  = "#F5F7FA"
COLOR_CARD        = "#FFFFFF"
COLOR_TEXT_MAIN   = "#1D2129"
COLOR_TEXT_SUB    = "#86909C"

# 字体
FONT_TITLE    = QFont("Microsoft YaHei", 22, QFont.Bold)
FONT_HEADING  = QFont("Microsoft YaHei", 16, QFont.Bold)
FONT_BODY     = QFont("Microsoft YaHei", 14)
FONT_SMALL    = QFont("Microsoft YaHei", 12)

# 全局
WINDOW_STYLE = f"""
QMainWindow, QWidget {{
    background-color: {COLOR_BACKGROUND};
}}
"""

# 卡片
CARD_STYLE = f"""
QWidget {{
    background-color: {COLOR_CARD};
    border-radius: 16px;
    border: 1px solid rgba(0,0,0,0.05);
}}
"""

# 分组框
GROUP_BOX_STYLE = f"""
QGroupBox {{
    font: {FONT_BODY.toString()};
    color: {COLOR_TEXT_MAIN};
    border: 1px solid #eee;
    border-radius: 12px;
    margin-top: 8px;
}}
QGroupBox::title {{
    left:10px; padding:0 8px;
}}
"""

# 按钮
BTN_PRIMARY_STYLE = f"""
QPushButton {{
    background:{COLOR_PRIMARY};color:white;
    border-radius:10px; padding:10px 20px;
    font:{FONT_BODY.toString()}; font-weight:bold;
    border:none;
}}
QPushButton:hover {{background:#0D50E0}}
"""

BTN_SECONDARY_STYLE = f"""
QPushButton {{
    background:{COLOR_CARD};color:{COLOR_PRIMARY};
    border:1px solid {COLOR_PRIMARY};
    border-radius:10px; padding:10px 20px;
    font:{FONT_BODY.toString()}; font-weight:bold;
}}
"""

# 输入框
INPUT_STYLE = f"""
QLineEdit, QComboBox {{
    padding:10px 14px; border-radius:10px;
    border:1px solid #DCDFE6;
    font:{FONT_BODY.toString()};
}}
QLineEdit:focus {{border:2px solid {COLOR_PRIMARY}}}
"""

# 数字显示样式
DIGIT_DISPLAY_STYLE = f"""
QLabel {{
    font-size:70px;
    font-weight:bold;
    color:{COLOR_PRIMARY};
    background:rgba(22,93,255,0.05);
    border:2px solid {COLOR_PRIMARY};
    border-radius:16px;
    padding:18px;
}}
"""