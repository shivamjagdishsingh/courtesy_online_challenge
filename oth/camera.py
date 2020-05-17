import numpy as np
import os, urllib.request
from cv2 import cv2
from django.conf import settings
from keras.preprocessing import image
from keras.models import model_from_json
import tensorflow as tf

graph = tf.get_default_graph()

face_cascade = cv2.CascadeClassifier(os.path.join(
    settings.BASE_DIR, 'opencv_haarcascade_data/haarcascade_frontalface_default.xml'))

model = model_from_json(open(os.path.join(
    settings.BASE_DIR, 'opencv_haarcascade_data/facial_expression_model_structure.json'), "r").read())

model.load_weights(os.path.join(
    settings.BASE_DIR, 'opencv_haarcascade_data/facial_expression_model_weights.h5'))  # load weights

emotions = ('angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral')

emotion_main = ''


class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()

    # def get_frame(self):
    #     success, image = self.video.read()
    #     # We are using Motion JPEG, but OpenCV defaults to capture raw images,
    #     # so we must encode it into JPEG in order to correctly display the
    #     # video stream.
    #
    #     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #     faces_detected = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
    #     for (x, y, w, h) in faces_detected:
    #         cv2.rectangle(image, pt1=(x, y), pt2=(x + w, y + h), color=(255, 0, 0), thickness=2)
    #     frame_flip = cv2.flip(image, 1)
    #     ret, jpeg = cv2.imencode('.jpg', frame_flip)
    #     return jpeg.tobytes()

    def get_frame(self):
        ret, img = self.video.read()

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)  # draw rectangle to main image

            detected_face = img[int(y):int(y + h), int(x):int(x + w)]  # crop detected face
            detected_face = cv2.cvtColor(detected_face, cv2.COLOR_BGR2GRAY)  # transform to gray scale
            detected_face = cv2.resize(detected_face, (48, 48))  # resize to 48x48

            img_pixels = image.img_to_array(detected_face)
            img_pixels = np.expand_dims(img_pixels, axis=0)

            img_pixels /= 255  # pixels are in scale of [0, 255]. normalize all pixels in scale of [0, 1]

            with graph.as_default():
                predictions = model.predict(img_pixels)  # store probabilities of 7 expressions

            # find max indexed array 0: angry, 1:disgust, 2:fear, 3:happy, 4:sad, 5:surprise, 6:neutral
            max_index = np.argmax(predictions[0])

            emotion = emotions[max_index]

            # img = cv2.flip(img, 1)
            # write emotion text above rectangle
            cv2.putText(img, emotion, (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            if emotion is not "neutral":
                global emotion_main
                emotion_main = emotion

        # frame_flip = cv2.flip(img, 1)
        ret, jpeg = cv2.imencode('.jpg', img)
        jpeg_tobytes = jpeg.tobytes()
        return jpeg_tobytes, emotion_main
