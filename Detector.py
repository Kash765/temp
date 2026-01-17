from ultralytics import YOLO

class Detector:
    def __init__(self, model_path="yolov8n.pt", confidence=0.4):
        self.model = YOLO(model_path)
        self.confidence = confidence

    def detect(self, frame):
        results = self.model(frame, conf=self.confidence, verbose=False)[0]

        detections = {
            "phones": [],
            "faces": []
        }

        for box, cls in zip(results.boxes.xyxy, results.boxes.cls):
            cls = int(cls)
            label = self.model.names[cls]

            if label == "cell phone":
                detections["phones"].append(box.cpu().numpy())
            elif label == "person":
                detections["faces"].append(box.cpu().numpy())

        return detections
