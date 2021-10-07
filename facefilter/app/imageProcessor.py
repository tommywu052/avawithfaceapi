# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import json
import logging
import io
import numpy as np
import cv2 as cv
import requests
import json
import os



class ImageProcessor():
    def __init__(self):
        return
    
    def process_images(self, imgBytes):
        try:
            # Read image raw bytes
            # Load the cascade
            face_cascade = cv.CascadeClassifier('haarcascade_frontalface_default.xml')
            
            imgBuf = io.BytesIO(imgBytes)
            imgBytes = np.frombuffer(imgBuf.getvalue(), dtype=np.uint8)
            # Convert to grayscale
            cvGrayImage = cv.imdecode(imgBytes, cv.COLOR_BGR2RGB)
            faces = face_cascade.detectMultiScale(cvGrayImage, 1.1, 4)
            facecnt = len(faces)
            if (facecnt > 0):
                print("face detected")
                logging.info('Find Faces: {}'.format(facecnt))
                test_url = os.environ['funcappUrl']
                # prepare headers for http request
                content_type = 'image/jpeg'
                headers = {'content-type': content_type}

                #img = cv2.imread('test3.jpg')
                # encode image as jpeg
                _, img_encoded = cv.imencode('.jpg', cvGrayImage)
                # send http request with image and receive response
                response = requests.post(test_url, data=img_encoded.tostring(), headers=headers)
                # decode response
                result = response.text
                print(result)
            else :
                #print("No face detected")
                logging.info('No Face Detected')
                result = ""
            
            return result
        except:
            raise
