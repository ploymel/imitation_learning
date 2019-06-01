import sys
import cv2, os
import numpy as np

def resize(image):
    """
    Resize the image to the input shape used by the network model
    """
    IMAGE_HEIGHT, IMAGE_WIDTH, IMAGE_CHANNELS = 180, 300, 3
    return cv2.resize(image, (IMAGE_WIDTH, IMAGE_HEIGHT), cv2.INTER_AREA)

