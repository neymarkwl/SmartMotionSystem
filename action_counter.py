import sys
import cv2
import math
import time
import mysql.connector
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from ultralytics import YOLO

# 角度计算
def calc_angle(a, b, c):
    ax, ay = a; bx, by = b; cx, cy = c
    ba = (ax-bx, ay-by)
    bc = (cx-bx, cy-by)
    dot = ba[0]*bc[0] + ba[1]*bc[1]
    mag = math.hypot(*ba)*math.hypot(*bc) + 1e-6
    return math.degrees(math.acos(max(-1, min(1, dot/mag))))

# 数据库
class MotionDB:
    def __init__(self):
        self.conn = mysql.connector.connect(host="localhost",user="root",password="123456",database="motion_db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS records (
            id INT AUTO_INCREMENT PRIMARY KEY,
            motion VARCHAR(30), count INT, duration INT, calorie FLOAT, create_time DATETIME)''')
        self.conn.commit()
    def add(self, m, c, d, cal):
        self.cursor.execute("INSERT INTO records VALUES (null,%s,%s,%s,%s,now())",(m,c,d,cal))
        self.conn.commit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("智能体感运动系统（骨骼版）— 燕山大学")
        self.setFixedSize(1300,800)
        self.setStyleSheet("background:#f5f7fa;")

        # ✅ 姿态模型（关键点）
        self.model = YOLO("yolov8n-pose.pt")
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        # 计数状态
        self.squat=0; self.pushup=0; self.jump=0
        self.sq_state="up"; self.pu_state="up"
        self.sq_time=0; self.pu_time=0
        self.start_time=None
        self.db = MotionDB()
        self.init_ui()

    def init_ui(self):
        # 标题
        title = QLabel("基于YOLO-Pose的居家运动分析系统",self)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:32px; font-weight:bold; color:#2c3e50; padding:15px; background:#e8f4fd; border-radius:10px;")
        title.setGeometry(0,0,1300,70)

        # 视频区
        self.video = QLabel(self)
        self.video.setGeometry(30,90,900,630)
        self.video.setStyleSheet("background:#000; border:3px solid #3498db; border-radius:10px;")

        # 控制面板
        control = QWidget(self)
        control.setGeometry(950,90,320,630)
        lay = QVBoxLayout(control); lay.setSpacing(18)
        self.lb_sq = self.card(f"深蹲：{self.squat} 次")
        self.lb_pu = self.card(f"俯卧撑：{self.pushup} 次")
        self.lb_jp = self.card(f"跳绳：{self.jump} 次")
        lay.addWidget(self.lb_sq); lay.addWidget(self.lb_pu); lay.addWidget(self.lb_jp)
        lay.addStretch()

        # 按钮
        btn_s = """QPushButton{font-size:16px; padding:12px; border-radius:8px; background:#3498db; color:white;}
                   QPushButton:hover{background:#2980b9;}"""
        self.btn_start = QPushButton("▶ 启动"); self.btn_stop = QPushButton("■ 停止")
        self.btn_reset = QPushButton("🔄 重置"); self.btn_save = QPushButton("💾 保存")
        for b in [self.btn_start,self.btn_stop,self.btn_reset,self.btn_save]:
            b.setStyleSheet(btn_s); lay.addWidget(b)
        self.btn_start.clicked.connect(self.start)
        self.btn_stop.clicked.connect(self.stop)
        self.btn_reset.clicked.connect(self.reset)
        self.btn_save.clicked.connect(self.save)

    def card(self,t):
        lb=QLabel(t); lb.setAlignment(Qt.AlignCenter)
        lb.setStyleSheet("font-size:17px; padding:12px; background:white; border-radius:8px; border:1px solid #dce6f0;")
        return lb

    def start(self):
        self.cap=cv2.VideoCapture(0)
        self.start_time=time.time()
        self.timer.start(30)
    def stop(self):
        self.timer.stop(); self.cap.release()
    def reset(self):
        self.squat=self.pushup=self.jump=0
        self.sq_state="up"; self.pu_state="up"
        self.refresh()
    def refresh(self):
        self.lb_sq.setText(f"深蹲：{self.squat} 次")
        self.lb_pu.setText(f"俯卧撑：{self.pushup} 次")
        self.lb_jp.setText(f"跳绳：{self.jump} 次")
    def save(self):
        if not self.start_time: return
        dur=int(time.time()-self.start_time)
        cal=(self.squat+self.pushup+self.jump)*0.3
        self.db.add("综合",self.squat+self.pushup+self.jump,dur,cal)
        QMessageBox.information(self,"成功","记录已保存")

    def update_frame(self):
        ret,fr=self.cap.read()
        if not ret: return
        fr=cv2.resize(fr,(900,630))
        res=self.model(fr,verbose=False)
        ann=res[0].plot() # ✅ 自动画骨骼！

        if len(res[0].keypoints)>0:
            kps=res[0].keypoints[0].xyxy[0].cpu().numpy() # 17点
            # 关键点
            r_sho=kps[6]; r_hip=kps[12]; r_knee=kps[14]
            r_elb=kps[8]; r_wri=kps[10]
            t=time.time()

            # ========== 深蹲（髋-膝角度）==========
            if all([v[0]>0 for v in [r_sho,r_hip,r_knee]]):
                ang=calc_angle(r_sho,r_hip,r_knee)
                cv2.putText(ann,f"膝角:{int(ang)}",(20,60),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
                if self.sq_state=="up" and ang<100:
                    self.sq_state="down"; self.sq_time=t
                elif self.sq_state=="down" and ang>160 and t-self.sq_time>0.5:
                    self.squat+=1; self.sq_state="up"; self.refresh()

            # ========== 俯卧撑（肩-肘-腕）==========
            if all([v[0]>0 for v in [r_sho,r_elb,r_wri]]):
                ang=calc_angle(r_sho,r_elb,r_wri)
                cv2.putText(ann,f"肘角:{int(ang)}",(20,100),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,255),2)
                if self.pu_state=="up" and ang<100:
                    self.pu_state="down"; self.pu_time=t
                elif self.pu_state=="down" and ang>160 and t-self.pu_time>0.5:
                    self.pushup+=1; self.pu_state="up"; self.refresh()

        # 转Qt
        ann=cv2.cvtColor(ann,cv2.COLOR_BGR2RGB)
        h,w,ch=ann.shape
        qimg=QImage(ann.data,w,h,ch*w,QImage.Format_RGB888)
        self.video.setPixmap(QPixmap.fromImage(qimg))

if __name__=="__main__":
    app=QApplication(sys.argv)
    w=MainWindow()
    w.show()
    sys.exit(app.exec_())