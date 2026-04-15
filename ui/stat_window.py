from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from ui.style import *

class StatWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("运动数据统计")
        self.setFixedSize(900, 600)
        self.setStyleSheet(WINDOW_STYLE)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40,40,40,40)
        layout.setSpacing(30)

        # 标题
        title = QLabel("📊 个人运动数据统计")
        title.setFont(FONT_TITLE)
        title.setStyleSheet(f"color:{COLOR_PRIMARY}")
        layout.addWidget(title, alignment=Qt.AlignCenter)

        # 统计卡片
        card_layout = QHBoxLayout()

        def make_card(title_txt, value_txt):
            w = QWidget()
            w.setStyleSheet(CARD_STYLE)
            ly = QVBoxLayout(w)
            t = QLabel(title_txt)
            t.setFont(FONT_BODY)
            t.setStyleSheet(f"color:{COLOR_TEXT_SUB}")  # 这里修复了
            v = QLabel(value_txt)
            v.setFont(FONT_HEADING)
            v.setStyleSheet(f"color:{COLOR_PRIMARY}")
            ly.addWidget(t)
            ly.addWidget(v)
            ly.setAlignment(Qt.AlignCenter)
            return w

        self.card_total = make_card("总运动次数", "0")
        self.card_days  = make_card("运动天数", "0")
        self.card_cal   = make_card("消耗热量(kcal)", "0")

        card_layout.addWidget(self.card_total)
        card_layout.addWidget(self.card_days)
        card_layout.addWidget(self.card_cal)
        layout.addLayout(card_layout)

        # 历史记录表格
        group = QGroupBox("历史运动记录")
        group.setStyleSheet(GROUP_BOX_STYLE)
        g_layout = QVBoxLayout(group)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["类型","次数","时长(s)","热量","时间"])
        self.table.setStyleSheet(f"""
            QTableWidget {{
                border-radius:10px;
                background:{COLOR_CARD};
                gridline-color:#eee;
            }}
        """)
        g_layout.addWidget(self.table)
        layout.addWidget(group)

        self._load_data()

    def _load_data(self):
        self.table.setRowCount(0)