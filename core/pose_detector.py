from ultralytics import YOLO


class PoseDetector:
    """YOLOv8-Pose 姿态检测封装类"""

    def __init__(self, model_path="models/yolov8n-pose.pt"):
        self.model = YOLO(model_path)

    def detect(self, frame):
        results = self.model(frame, verbose=False)
        annotated_frame = results[0].plot()

        # ✅ 修复关键点提取逻辑
        if results[0].keypoints is not None and len(results[0].keypoints) > 0:
            keypoints = results[0].keypoints[0].xy[0].cpu().numpy()
            return annotated_frame, keypoints
        return annotated_frame, None