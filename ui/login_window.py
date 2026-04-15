from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal
from ui.style import *

class LoginWindow(QWidget):
    login_success = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("智能健身助手")
        self.setFixedSize(900, 550)
        self.setStyleSheet(WINDOW_STYLE)

        # 布局
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(40,40,40,40)
        main_layout.setSpacing(30)

        # 左侧
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setAlignment(Qt.AlignCenter)

        icon = QLabel("🏃")
        icon.setStyleSheet("font-size:100px;")
        icon.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(icon)

        title = QLabel("智能健身助手")
        title.setFont(FONT_TITLE)
        title.setStyleSheet(f"color:{COLOR_PRIMARY}")
        left_layout.addWidget(title, alignment=Qt.AlignCenter)

        main_layout.addWidget(left, stretch=1)

        # 右侧登录卡片
        right = QWidget()
        right.setStyleSheet(CARD_STYLE)
        right_layout = QVBoxLayout(right)
        right_layout.setSpacing(20)
        right_layout.setContentsMargins(40,50,40,50)

        right_layout.addWidget(QLabel("用户登录"))

        self.user = QLineEdit()
        self.user.setPlaceholderText("请输入用户名")
        self.user.setStyleSheet(INPUT_STYLE)
        right_layout.addWidget(self.user)

        self.pwd = QLineEdit()
        self.pwd.setPlaceholderText("请输入密码")
        self.pwd.setEchoMode(QLineEdit.Password)
        self.pwd.setStyleSheet(INPUT_STYLE)
        right_layout.addWidget(self.pwd)

        btn = QPushButton("登录")
        btn.setStyleSheet(BTN_PRIMARY_STYLE)
        btn.clicked.connect(self.do_login)
        right_layout.addWidget(btn)

        main_layout.addWidget(right, stretch=1)

    def do_login(self):
        username = self.user.text().strip()
        if username:
            self.login_success.emit(username)
        else:
            self.login_success.emit("user")

    def get_credentials(self):
        return self.user.text(), self.pwd.text()