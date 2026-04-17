import cv2
import time
from core.utils import calculate_angle


class MotionCounter:
    def __init__(self):
        # 计数变量
        self.squat_count = 0
        self.pushup_count = 0
        self.jump_count = 0

        # 状态机
        self.squat_state = "UP"  # UP/DOWN
        self.pushup_state = "UP"  # UP/DOWN
        self.jump_buffer = []

        # 防抖时间
        self.squat_time = 0
        self.pushup_time = 0

    def reset(self):
        """重置所有计数"""
        self.squat_count = 0
        self.pushup_count = 0
        self.jump_count = 0
        self.squat_state = "UP"
        self.pushup_state = "UP"
        self.jump_buffer = []
        self.squat_time = 0
        self.pushup_time = 0

    def update_squat(self, knee_angle, now):
        """深蹲计数：膝盖角度<90°下蹲，>140°站起计数"""
        if self.squat_state == "UP" and knee_angle < 90:
            self.squat_state = "DOWN"
            self.squat_time = now
        elif self.squat_state == "DOWN" and knee_angle > 140:
            if now - self.squat_time > 0.4:
                self.squat_count += 1
                self.squat_state = "UP"

    def update_pushup(self, elbow_angle, now):
        """俯卧撑计数：手肘角度<80°下，>130°上计数"""
        if self.pushup_state == "UP" and elbow_angle < 80:
            self.pushup_state = "DOWN"
            self.pushup_time = now
        elif self.pushup_state == "DOWN" and elbow_angle > 130:
            if now - self.pushup_time > 0.4:
                self.pushup_count += 1
                self.pushup_state = "UP"

    def update_jump(self, hip_y):
        """跳绳计数：髋部垂直位移>55px判定一次跳跃"""
        self.jump_buffer.append(hip_y)
        if len(self.jump_buffer) > 10:
            self.jump_buffer.pop(0)
        if len(self.jump_buffer) >= 8:
            max_y = max(self.jump_buffer)
            min_y = min(self.jump_buffer)
            if max_y - min_y > 55:
                self.jump_count += 1
                self.jump_buffer.clear()

    def update(self, keypoints, now, frame):
        """更新计数，同时绘制角度"""
        if keypoints is None or len(keypoints) < 17:
            return

        # 提取关键点（COCO格式）
        r_sho = keypoints[6]
        r_el = keypoints[8]
        r_wr = keypoints[10]
        r_hi = keypoints[12]
        r_kn = keypoints[14]
        r_an = keypoints[16]

        # 计算角度
        elbow_angle = calculate_angle(r_sho, r_el, r_wr)
        knee_angle = calculate_angle(r_hi, r_kn, r_an)

        # 绘制角度（对齐GoodGYM显示）
        cv2.putText(frame, f"Knee: {int(knee_angle)}°", (20, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
        cv2.putText(frame, f"Elbow: {int(elbow_angle)}°", (20, 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)

        # 更新各动作计数
        if r_kn[0] > 0 and r_hi[0] > 0 and r_an[0] > 0:
            self.update_squat(knee_angle, now)
        if r_el[0] > 0 and r_sho[0] > 0 and r_wr[0] > 0:
            self.update_pushup(elbow_angle, now)
        if r_hi[0] > 0:
            self.update_jump(r_hi[1])

    def get_counts(self):
        return self.squat_count, self.pushup_count, self.jump_count