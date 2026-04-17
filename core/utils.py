import math
import cv2


def calculate_angle(a, b, c):
    """
    计算a-b-c三点形成的夹角（单位：度）
    用于深蹲（髋-膝-踝）、俯卧撑（肩-肘-腕）计数
    """
    ax, ay = a
    bx, by = b
    cx, cy = c

    ba = (ax - bx, ay - by)
    bc = (cx - bx, cy - by)
    dot_product = ba[0] * bc[0] + ba[1] * bc[1]
    mag_ba = math.hypot(*ba)
    mag_bc = math.hypot(*bc)

    if mag_ba * mag_bc == 0:
        return 0

    cos_angle = dot_product / (mag_ba * mag_bc)
    cos_angle = max(-1, min(1, cos_angle))
    return math.degrees(math.acos(cos_angle))


def preprocess_frame(frame):
    """图像预处理：亮度调整+降噪，提升姿态检测鲁棒性"""
    # 亮度调整
    frame = cv2.convertScaleAbs(frame, alpha=1.1, beta=10)
    # 高斯模糊降噪
    frame = cv2.GaussianBlur(frame, (3, 3), 0)
    return frame