from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QPixmap, QImage
import cv2
import time
from core.pose_detector import PoseDetector
from core.counter import MotionCounter
from core.utils import preprocess_frame, calculate_angle
from db.db_helper import MotionDBHelper
from config.settings import *
from ui.stat_window import StatWindow
from ui.style import *

class MainWindow(QMainWindow):
    def __init__(self, username="user"):
        super().__init__()
        self.username = username
        self.setWindowTitle(f"智能健身助手 - {username}")
        self.setMinimumSize(1280, 768)
        self.setStyleSheet(WINDOW_STYLE)

        self.detector = PoseDetector(MODEL_PATH)
        self.counter = MotionCounter()
        self.db = MotionDBHelper(**DB_CONFIG)

        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.start_time = None
        self.current_motion = "深蹲"

        self._init_menu()
        self._init_ui()

    def _init_menu(self):
        bar = self.menuBar()
        bar.setStyleSheet(f"background:{COLOR_CARD};font:{FONT_BODY.toString()}")
        menu_user = bar.addMenu(f"👤 {self.username}")
        menu_user.addAction("退出登录", self.close)

        menu_tool = bar.addMenu("工具")
        menu_tool.addAction("启动摄像头", self._start_camera)
        menu_tool.addAction("停止摄像头", self._stop_camera)
        menu_tool.addAction("重置计数", self._reset_count)

        menu_mode = bar.addMenu("运动模式")
        menu_mode.addAction("深蹲", lambda: self._set_motion("深蹲"))
        menu_mode.addAction("俯卧撑", lambda: self._set_motion("俯卧撑"))
        menu_mode.addAction("跳绳", lambda: self._set_motion("跳绳"))

        menu_data = bar.addMenu("数据")
        menu_data.addAction("查看统计", self._show_stat)

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(20,20,20,20)
        main_layout.setSpacing(20)

        # 左侧视频
        video_card = QWidget()
        video_card.setStyleSheet(CARD_STYLE)
        v_layout = QVBoxLayout(video_card)
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background:#000; border-radius:12px; color:#fff;")
        self.video_label.setText("🎥 点击【工具→启动摄像头】")
        self.video_label.setMinimumSize(720, 680)
        v_layout.addWidget(self.video_label)
        main_layout.addWidget(video_card, stretch=3)

        # 右侧控制面板
        control = QWidget()
        control.setStyleSheet(CARD_STYLE)
        c_layout = QVBoxLayout(control)
        c_layout.setSpacing(20)
        c_layout.setContentsMargins(30,30,30,30)

        title = QLabel("智能健身助手")
        title.setFont(FONT_TITLE)
        title.setStyleSheet(f"color:{COLOR_PRIMARY}")
        c_layout.addWidget(title, alignment=Qt.AlignCenter)

        # 计数卡片
        self.count_lab = QLabel("0")
        self.count_lab.setStyleSheet(DIGIT_DISPLAY_STYLE)
        self.count_lab.setAlignment(Qt.AlignCenter)
        c_layout.addWidget(self.count_lab)

        tip = QLabel("当前运动次数")
        tip.setStyleSheet(f"color:{COLOR_TEXT_SUB}")
        tip.setAlignment(Qt.AlignCenter)
        c_layout.addWidget(tip)

        # 控制
        g = QGroupBox("运动控制")
        g.setStyleSheet(GROUP_BOX_STYLE)
        f = QFormLayout(g)
        self.cb_mode = QComboBox()
        self.cb_mode.addItems(["深蹲","俯卧撑","跳绳"])
        self.cb_mode.setStyleSheet(INPUT_STYLE)
        f.addRow("运动模式", self.cb_mode)

        self.cb_pose = QCheckBox("显示骨骼")
        self.cb_pose.setChecked(True)
        f.addRow("显示", self.cb_pose)

        # 按钮
        btn_layout = QHBoxLayout()
        self.btn_reset = QPushButton("重置")
        self.btn_save = QPushButton("保存")
        self.btn_stat = QPushButton("统计")
        self.btn_reset.setStyleSheet(BTN_SECONDARY_STYLE)
        self.btn_save.setStyleSheet(BTN_PRIMARY_STYLE)
        self.btn_stat.setStyleSheet(BTN_PRIMARY_STYLE)
        btn_layout.addWidget(self.btn_reset)
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_stat)
        f.addRow("", btn_layout)
        c_layout.addWidget(g)

        # 状态
        status = QGroupBox("运动状态")
        status.setStyleSheet(GROUP_BOX_STYLE)
        s_layout = QVBoxLayout(status)
        self.stage_lab = QLabel("准备")
        self.stage_lab.setFont(FONT_HEADING)
        self.stage_lab.setStyleSheet(f"color:{COLOR_PRIMARY}")
        self.stage_lab.setAlignment(Qt.AlignCenter)
        s_layout.addWidget(self.stage_lab)
        c_layout.addWidget(status)

        c_layout.addStretch()
        main_layout.addWidget(control, stretch=2)

        self.btn_reset.clicked.connect(self._reset_count)
        self.btn_save.clicked.connect(self._save_record)
        self.btn_stat.clicked.connect(self._show_stat)
        self.cb_mode.currentTextChanged.connect(self._set_motion)

    def _set_motion(self, m):
        self.current_motion = m
        self._reset_count()

    def _start_camera(self):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.start_time = time.time()
        self.timer.start(30)

    def _stop_camera(self):
        self.timer.stop()
        if self.cap:
            self.cap.release()
            self.cap = None

    def _reset_count(self):
        self.counter.reset()
        self.count_lab.setText("0")
        self.stage_lab.setText("准备")

    def _save_record(self):
        if not self.start_time:
            QMessageBox.warning(self,"提示","请先启动摄像头")
            return
        d = int(time.time()-self.start_time)
        sq,pu,jp = self.counter.get_counts()
        t = {"深蹲":sq,"俯卧撑":pu,"跳绳":jp}[self.current_motion]
        cal = t*0.3
        self.db.add_record(self.current_motion,t,d,cal)
        QMessageBox.information(self,"成功","保存成功")

    def _show_stat(self):
        self.stat = StatWindow(self.db)
        self.stat.show()

    def update_frame(self):
        if not self.cap: return
        ret, f = self.cap.read()
        if not ret: return

        f = cv2.flip(f,1)
        f = preprocess_frame(f)
        show = f.copy()
        kps = None

        if self.cb_pose.isChecked():
            show, kps = self.detector.detect(f)

        if kps is not None and len(kps)>0:
            k = kps[0]
            if len(k)>=17:
                self.counter.update(kps, time.time(), show)
                sq,pu,jp = self.counter.get_counts()
                cnt = {"深蹲":sq,"俯卧撑":pu,"跳绳":jp}[self.current_motion]
                self.count_lab.setText(str(cnt))

        rgb = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)
        h,w,ch = rgb.shape
        qimg = QImage(rgb.data, w,h,ch*w, QImage.Format_RGB888)
        pix = QPixmap.fromImage(qimg).scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.video_label.setPixmap(pix)

    def closeEvent(self,e):
        self._stop_camera()
        e.accept()