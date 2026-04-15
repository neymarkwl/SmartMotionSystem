from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from db.db_helper import MotionDBHelper

class HistoryWindow(QDialog):
    """运动历史记录查询窗口，完全匹配开题数据管理模块要求"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("运动历史记录 —— 智能体感运动系统")
        self.setFixedSize(900, 600)
        self.setStyleSheet("background-color: #f5f7fa;")
        self.db = MotionDBHelper()
        self.init_ui()
        self.load_records()

    def init_ui(self):
        # 标题栏
        title = QLabel("运动历史记录", self)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
            background-color: #e8f4fd;
            border-radius: 10px;
        """)
        title.setGeometry(0, 0, 900, 60)

        # 表格显示区
        self.table = QTableWidget(self)
        self.table.setGeometry(30, 90, 840, 450)
        self.table.setStyleSheet("""
            background-color: white;
            border: 2px solid #3498db;
            border-radius: 10px;
        """)
        # 设置表头
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "运动类型", "总次数", "时长(秒)", "消耗热量", "记录时间"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # 刷新按钮
        self.btn_refresh = QPushButton("🔄 刷新记录", self)
        self.btn_refresh.setGeometry(30, 560, 150, 30)
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 6px;
                border-radius: 5px;
                background-color: #3498db;
                color: white;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.btn_refresh.clicked.connect(self.load_records)

    def load_records(self):
        """从数据库加载所有运动记录，显示在表格中"""
        records = self.db.get_all_records()
        self.table.setRowCount(len(records))
        for row, r in enumerate(records):
            for col, val in enumerate(r):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)