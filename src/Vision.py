from imageai.Detection import ObjectDetection


class Vision:

    def __init__(self, model="model/yolo-tiny.h5"):
        self.model_path = model

    def detectImage(self, input_path, output_path):

        self.detector = ObjectDetection()
        self.detector.setModelTypeAsTinyYOLOv3()
        self.detector.setModelPath(self.model_path)
        self.detector.loadModel()

        detection = self.detector.detectObjectsFromImage(
            input_image=input_path,
            output_image_path=output_path
        )

        return detection
