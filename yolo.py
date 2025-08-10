import pygame
import numpy as np
import cv2
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

def surface_to_numpy(surface): #transform ths image to numpy array

    raw = pygame.image.tostring(surface, "RGB")
    image = np.frombuffer(raw, dtype=np.uint8).reshape((surface.get_height(), surface.get_width(), 3))
    return image

def contains_human(surface): #Check image if it contains human


    image = surface_to_numpy(surface)

    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_CUBIC)  # Daha kaliteli büyütme

    results = model.predict(image, verbose=False)
    for r in results:
        for box in r.boxes:
            conf = None

            if int(box.cls[0]) == 0:  #human id is 0
                conf = float(box.conf[0])
                return conf
    return False
