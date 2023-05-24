import cv2
import numpy as np


class Yolo:
    labels = None

    # neural network
    net = None

    def __init__(self):
        path = "./src/object_tracker/"
        self.scale = 0.00392
        with open(path+"yolo.txt", 'r') as f:
            self.labels = [line.strip() for line in f.readlines()]

        self.net = cv2.dnn.readNet(path+"yolov3-tiny.weights", path+"yolo.cfg")


    def get_output_layers(self):
        layer_names = self.net.getLayerNames()
        try:
            output_layers = [layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]
        except:
            output_layers = [layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]

        return output_layers

    def draw_prediction(img, label, confidence, left, bottom, right, top):
        cv2.rectangle(img, (left, bottom), (right, top), [0, 0, 0], 2)
        cv2.putText(img, label, (left-10,bottom-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, [0, 0, 0], 2)


    def get_bounding_boxes_image(self, image):
        Width = image.shape[1]
        Height = image.shape[0]
        blob = cv2.dnn.blobFromImage(image, self.scale, (416,416), (0,0,0), True, crop=False)
        self.net.setInput(blob)
        outs = self.net.forward(self.get_output_layers())

        class_ids = []
        confidences = []
        boxes = []
        conf_threshold = 0.5

        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > conf_threshold:
                    center_x = int(detection[0] * Width)
                    center_y = int(detection[1] * Height)
                    w = int(detection[2] * Width)
                    h = int(detection[3] * Height)
                    x = center_x - w / 2
                    y = center_y - h / 2
                    class_ids.append(class_id)
                    confidences.append(float(confidence))
                    boxes.append([x, y, w, h])

        nms_threshold = 0.6
        indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

        for i in indices:
            try:
                box = boxes[i]
            except:
                i = i[0]
                box = boxes[i]
            x = box[0]
            y = box[1]
            w = box[2]
            h = box[3]
            draw_prediction(image, self.labels[class_ids[i]], confidences[i], round(x), round(y), round(x+w), round(y+h))

        return image


    def get_bounding_boxes(self, image):
        Width = image.shape[1]
        Height = image.shape[0]
        blob = cv2.dnn.blobFromImage(image, self.scale, (416,416), (0,0,0), True, crop=False)
        self.net.setInput(blob)
        outs = self.net.forward(self.get_output_layers())

        confidences = []
        boxes = []

        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    center_x = int(detection[0] * Width)
                    center_y = int(detection[1] * Height)
                    w = int(detection[2] * Width)
                    h = int(detection[3] * Height)
                    x = center_x - w / 2
                    y = center_y - h / 2
                    boxes.append([x, y, w, h])
