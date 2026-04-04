import cv2
import os
import argparse


def _open_camera():
    if os.name == "nt":
        backends = [cv2.CAP_DSHOW, cv2.CAP_ANY]
    elif hasattr(cv2, "CAP_AVFOUNDATION"):
        backends = [cv2.CAP_AVFOUNDATION, cv2.CAP_ANY]
    else:
        backends = [cv2.CAP_ANY]

    for backend in backends:
        cam_obj = cv2.VideoCapture(0, backend)
        if cam_obj.isOpened():
            return cam_obj
        cam_obj.release()
    return None


base_dir = os.path.dirname(os.path.abspath(__file__))
samples_dir = os.path.join(base_dir, "samples")
if os.path.exists(samples_dir) and not os.path.isdir(samples_dir):
    os.replace(samples_dir, samples_dir + ".bak")
os.makedirs(samples_dir, exist_ok=True)

detector = cv2.CascadeClassifier(os.path.join(base_dir, "haarcascade_frontalface_default.xml"))
#Haar Cascade classifier is an effective object detection approach


def capture_samples(face_id, sample_count=100):
    cam = _open_camera() #create a video capture object which is helpful to capture videos through webcam
    if cam is None:
        raise RuntimeError("Unable to open camera")

    cam.set(3, 640) # set video FrameWidth
    cam.set(4, 480) # set video FrameHeight

    print("Taking samples, look at camera ....... ")
    count = 0 # Initializing sampling face count

    while True:

        ret, img = cam.read() #read the frames using the above created object
        if not ret:
            continue
        converted_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #The function converts an input image from one color space to another
        faces = detector.detectMultiScale(converted_image, 1.3, 5)

        for (x,y,w,h) in faces:

            cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2) #used to draw a rectangle on any image
            count += 1

            file_name = "face." + str(face_id) + '.' + str(count) + ".jpg"
            cv2.imwrite(os.path.join(samples_dir, file_name), converted_image[y:y+h,x:x+w])
            # To capture & Save images into the datasets folder

            cv2.imshow('image', img) #Used to display an image in a window

        k = cv2.waitKey(100) & 0xff # Waits for a pressed key
        if k == 27: # Press 'ESC' to stop
            break
        elif count >= sample_count: # More samples generally improve accuracy
            break

    print("Samples taken now closing the program....")
    cam.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Capture face samples for enrollment")
    parser.add_argument("--id", type=int, help="Numeric user ID")
    parser.add_argument("--count", type=int, default=100, help="Number of samples to capture")
    args = parser.parse_args()

    face_id = args.id
    if face_id is None:
        # Use integer ID for every new face (0,1,2,3...)
        face_id = int(input("Enter a Numeric user ID here: "))

    capture_samples(face_id, sample_count=args.count)