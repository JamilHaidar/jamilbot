from collections import namedtuple
from io import BytesIO
import math
import pkgutil
from typing import Tuple
import os
from PIL import Image, ImageOps, ImageEnhance
import cv2
import numpy as np

__all__ = ('Colour', 'ColourTuple', 'DefaultColours', 'deepfry')

Colour = Tuple[int, int, int]
ColourTuple = Tuple[Colour, Colour]


class DefaultColours:
    """Default colours provided for deepfrying"""
    red = ((254, 0, 2), (255, 255, 15))
    blue = ((36, 113, 229), (255,) * 3)


face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades +'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
# flare_img = Image.open()

flare_opencv = cv2.imread(f'{str(os.path.dirname(os.path.realpath(__file__)))}/../../img/flare.png',-1)

def overlay_image_alpha(img, img_overlay, x, y, alpha_mask):
    """Overlay `img_overlay` onto `img` at (x, y) and blend using `alpha_mask`.

    `alpha_mask` must have same HxW as `img_overlay` and values in range [0, 1].
    """
    # Image ranges
    y1, y2 = max(0, y), min(img.shape[0], y + img_overlay.shape[0])
    x1, x2 = max(0, x), min(img.shape[1], x + img_overlay.shape[1])

    # Overlay ranges
    y1o, y2o = max(0, -y), min(img_overlay.shape[0], img.shape[0] - y)
    x1o, x2o = max(0, -x), min(img_overlay.shape[1], img.shape[1] - x)

    # Exit if nothing to do
    if y1 >= y2 or x1 >= x2 or y1o >= y2o or x1o >= x2o:
        return

    # Blend overlay within the determined ranges
    img_crop = img[y1:y2, x1:x2]
    img_overlay_crop = img_overlay[y1o:y2o, x1o:x2o]
    alpha = alpha_mask[y1o:y2o, x1o:x2o, np.newaxis]
    alpha_inv = 1.0 - alpha

    img_crop[:] = alpha * img_overlay_crop + alpha_inv * img_crop

async def deepfry(img: Image, *, colours: ColourTuple = DefaultColours.red, flares: bool = True,scale: float = 1.0) -> Image:
    """
    Deepfry a given image.
    Parameters
    ----------
    img : `Image`
        Image to manipulate.
    colours : `ColourTuple`, optional
        A tuple of the colours to apply on the image.
    flares : `bool`, optional
        Whether or not to try and detect faces for applying lens flares.
    Returns
    -------
    `Image`
        Deepfried image.
    """
    img = img.copy().convert('RGB')

    if flares:
        opencv_img_gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
        opencv_img = cv2.cvtColor(np.array(img),cv2.COLOR_RGB2BGRA)

        faces = face_cascade.detectMultiScale(opencv_img_gray,1.3,5)
        for (x, y, w, h) in faces:
            face_roi = opencv_img_gray[y:y+h, x:x+w]  # Get region of interest (detected face)

            eyes = eye_cascade.detectMultiScale(face_roi)
            if len(eyes)!=2:continue
            try:
                for (ex, ey, ew, eh) in eyes:
                    
                    new_w = int(ew*scale)
                    new_h = int(eh*scale)
                    
                    temp_flare = cv2.resize(flare_opencv.copy(),(new_w,new_h))
                    
                    corner_y = (ey+y)-int((new_h-eh)/2)
                    corner_x = (ex+x)-int((new_w-ew)/2)
                    
                    y1, y2 = corner_y, corner_y+new_h
                    x1, x2 = corner_x, corner_x+new_h

                    alpha_s = temp_flare[:, :, 3] / 255.0
                    alpha_l = 1.0 - alpha_s
                    for c in range(0, 3):
                        opencv_img[y1:y2, x1:x2, c] = (alpha_s * temp_flare[:, :, c] +
                                                alpha_l * opencv_img[y1:y2, x1:x2, c])
            except Exception as e:
                print(e)
                
    # Crush image to hell and back
    opencv_img = cv2.cvtColor(opencv_img, cv2.COLOR_BGRA2RGB)
    img = Image.fromarray(opencv_img)
    img = img.convert('RGB')
    width, height = img.width, img.height
    img = img.resize((int(width ** .75), int(height ** .75)), resample=Image.LANCZOS)
    img = img.resize((int(width ** .88), int(height ** .88)), resample=Image.BILINEAR)
    img = img.resize((int(width ** .9), int(height ** .9)), resample=Image.BICUBIC)
    img = img.resize((width, height), resample=Image.BICUBIC)
    img = ImageOps.posterize(img, 4)

    # Generate colour overlay
    r = img.split()[0]
    r = ImageEnhance.Contrast(r).enhance(2.0)
    r = ImageEnhance.Brightness(r).enhance(1.5)

    r = ImageOps.colorize(r, colours[0], colours[1])

    # Overlay red and yellow onto main image and sharpen the hell out of it
    img = Image.blend(img, r, 0.75)
    img = ImageEnhance.Sharpness(img).enhance(100.0)
    
    return img