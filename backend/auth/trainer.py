import cv2
import numpy as np
from PIL import Image #pillow package
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(base_dir, 'samples') # Path for samples already taken
if os.path.exists(path) and not os.path.isdir(path):
    os.replace(path, path + ".bak")
os.makedirs(path, exist_ok=True)

recognizer = cv2.face.LBPHFaceRecognizer_create() # Local Binary Patterns Histograms
detector = cv2.CascadeClassifier(os.path.join(base_dir, "haarcascade_frontalface_default.xml"))
#Haar Cascade classifier is an effective object detection approach


def Images_And_Labels(path): # function to fetch the images and labels

    imagePaths = [os.path.join(path,f) for f in os.listdir(path)]     
    faceSamples=[]
    ids = []

    for imagePath in imagePaths: # to iterate particular image path

        gray_img = Image.open(imagePath).convert('L') # convert it to grayscale
        img_arr = np.array(gray_img,'uint8') #creating an array

        id = int(os.path.split(imagePath)[-1].split(".")[1])
        faces = detector.detectMultiScale(img_arr)

        for (x,y,w,h) in faces:
            faceSamples.append(img_arr[y:y+h,x:x+w])
            ids.append(id)

    return faceSamples,ids

def train_model():
    print ("Training faces. It will take a few seconds. Wait ...")

    faces,ids = Images_And_Labels(path)
    if not faces:
        raise RuntimeError("No face samples found. Capture samples first.")

    recognizer.train(faces, np.array(ids))

    trainer_dir = os.path.join(base_dir, "trainer")
    os.makedirs(trainer_dir, exist_ok=True)
    recognizer.write(os.path.join(trainer_dir, 'trainer.yml'))  # Save the trained model as trainer.yml

    print("Model trained, Now we can recognize your face.")


if __name__ == "__main__":
    train_model()
 