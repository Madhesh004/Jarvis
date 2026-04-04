import os
import cv2
import json


def _open_camera():
    backends = []
    if os.name == "nt":
        backends = [cv2.CAP_DSHOW, cv2.CAP_ANY]
    elif hasattr(cv2, "CAP_AVFOUNDATION"):
        backends = [cv2.CAP_AVFOUNDATION, cv2.CAP_ANY]
    else:
        backends = [cv2.CAP_ANY]

    for backend in backends:
        cam = cv2.VideoCapture(0, backend)
        if cam.isOpened():
            return cam
        cam.release()

    return None


def _load_user_map(base_dir):
    users_path = os.path.join(base_dir, "users.json")
    if not os.path.exists(users_path):
        return {}

    try:
        with open(users_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {int(k): str(v) for k, v in data.items()}
    except Exception:
        return {}


def AuthenticateFace():
    flag = 0
    base_dir = os.path.dirname(os.path.abspath(__file__))
    trainer_path = os.path.join(base_dir, "trainer", "trainer.yml")
    cascadePath = os.path.join(base_dir, "haarcascade_frontalface_default.xml")

    recognizer = None
    # Prefer LBPH recognition when cv2.face is available and model exists.
    if hasattr(cv2, "face") and os.path.exists(trainer_path):
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(trainer_path)

    # initializing haar cascade for object detection approach
    faceCascade = cv2.CascadeClassifier(cascadePath)
    if faceCascade.empty():
        print("Face auth error: cascade file not found or failed to load:", cascadePath)
        return 0

    font = cv2.FONT_HERSHEY_SIMPLEX  # denotes the font type


    user_map = _load_user_map(base_dir)

    cam = _open_camera()
    if cam is None:
        print("Face auth error: unable to open camera device")
        return 0

    cam.set(3, 640)  # set video FrameWidht
    cam.set(4, 480)  # set video FrameHeight

    # Define min window size to be recognized as a face
    minW = 0.1*cam.get(3)
    minH = 0.1*cam.get(4)

    # flag = True

    while True:

        ret, img = cam.read()  # read the frames using the above created object
        if not ret or img is None:
            continue

        # The function converts an input image from one color space to another
        converted_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(
            converted_image,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(int(minW), int(minH)),
        )

        for(x, y, w, h) in faces:

            # used to draw a rectangle on any image
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # to predict on every single image
            if recognizer is not None:
                face_id, accuracy = recognizer.predict(converted_image[y:y+h, x:x+w])
                if accuracy < 70:
                    label = user_map.get(face_id, f"User {face_id}")
                    accuracy_text = "  {0}%".format(round(100 - accuracy))
                    flag = 1
                else:
                    label = "unknown"
                    accuracy_text = "  {0}%".format(round(100 - accuracy))
                    flag = 0
            else:
                # Fallback mode: authenticate when a face is steadily detected.
                label = "face detected"
                accuracy_text = "  fallback"
                flag = 1

            cv2.putText(img, str(label), (x+5, y-5), font, 1, (255, 255, 255), 2)
            cv2.putText(img, str(accuracy_text), (x+5, y+h-5),
                        font, 1, (255, 255, 0), 1)

        cv2.imshow('camera', img)

        k = cv2.waitKey(10) & 0xff  # Press 'ESC' for exiting video
        if k == 27:
            break
        if flag == 1:
            break
            

    # Do a bit of cleanup
    
    cam.release()
    cv2.destroyAllWindows()
    return flag
 