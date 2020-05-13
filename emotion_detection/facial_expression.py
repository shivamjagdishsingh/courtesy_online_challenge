import numpy as np
from cv2 import cv2
from keras.preprocessing import image
from keras.models import model_from_json
import time

face_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_frontalface_default.xml')
emotions = ('angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral')
model = model_from_json(open("haarcascades/facial_expression_model_structure.json", "r").read())
model.load_weights('haarcascades/facial_expression_model_weights.h5')  # load weights


def emotion_detector():
    for i in range(10):
        cap = cv2.VideoCapture(i)
        time.sleep(5)
        cap.release()
        cv2.destroyAllWindows()


emotion_detector()