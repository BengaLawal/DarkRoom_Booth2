import gphoto2 as gp
import cv2
import time
from PIL import Image, ImageTk

class Camera:
    def __init__(self):
        self.video_capture = None
        self.last_image_frame = None

    def open_camera(self):
        """open laptop camera"""
        # Open the default camera (0 represents the first available camera)
        self.video_capture = cv2.VideoCapture(0)
        if not self.video_capture.isOpened():
            raise ValueError("Failed to open the camera")

    def close_camera(self):
        """close laptop camera"""
        if self.video_capture is not None:
            self.video_capture.release()
            self.video_capture = None

    def take_picture(self, duration):
        """
        Settings for taking a picture
        :param duration: amount in seconds
        :return: All frames taken in 3 seconds
        """
        if self.video_capture is None:
            self.open_camera()

        frames = []
        start_time = cv2.getTickCount()

        # while (cv2.getTickCount() - start_time) / cv2.getTickFrequency() < duration:
        cv2image = cv2.cvtColor(self.video_capture.read()[1], cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        # convert image to PhotoImage
        # imgtk = ImageTk.PhotoImage(image=img)
        return img


        #     # Capture a frame from the camera
        #     ret, frame = self.video_capture.read()
        #
        #     if not ret:
        #         raise ValueError("Failed to capture video")
        #
        #     # Convert the frame to RGB format
        #     frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #
        #     # Perform any additional image processing if needed
        #
        #     # Add the frame to the video frames
        #     frames.append(frame_rgb)
        #
        # # Release the camera capture
        # self.close_camera()
        #
        # self.last_image_frame = frames[-1]

        # Return the captured video frames
        # return frames

    def accept_picture(self):
        """save image when accepted"""
        if self.last_image_frame is not None:
            # Resize the frame before saving
            resized_frame = cv2.resize(self.last_image_frame, (
            1280, 853))
            # Convert the frame to RGB format
            frame_rgb = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            # Save the resized frame as an image
            cv2.imwrite(filename="saved_pictures/test.jpeg", img=frame_rgb)

    def take_video(self, duration):
        pass

    # def __init__(self):
    #     self.camera = None
    #
    # def connect(self):
    #     # TODO: Connect to the Canon EOS 2000D camera.
    #     pass
    #
    # def disconnect(self):
    #     # TODO: Disconnect from the camera.
    #     pass
    #
    # def capture_image(self):
    #     # TODO: Capture an image using the connected camera and return the captured image.
    #     pass

