import os
import tkinter as tk
import customtkinter as ctk
from PIL import Image
import time
import threading
import cv2
from watermark import Watermark
from keyboard import Keyboard
from mail import EmailSender

class UserInterface(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.watermark = Watermark()
        self.mail = EmailSender()

        self.screen_width = None
        self.screen_height = None
        self.get_screen_size()  # gets screen_width and screen_height

        self.main_frame = None
        self.home_page()  # initialise home page

        self.preview_frame = None
        self.preview_label = None
        self.review_frame = None
        self.review_label = None
        self.cap = None
        self.square_size = None
        self.timer_label = None
        self.timer_end = None
        self.timer_thread = None
        self.last_frame = None

        self.file_count_path = "saved_pictures/count.txt"

        self.keyboard_page_frame = None
        self.entry_frame = None
        self.keyboard_frame = None
        self.keyboard = None
        self.email_entry = None
        self.email_entry_text = None
        self.user_email = None

        self.image_path = None
        self.email_sender = None

    def home_page(self):
        """
        Set up the Main page
        """
        self.master.title("Darkroom Booth")
        self.master.attributes("-fullscreen", True)  # Make the main window full screen

        # print(f"Screen Size: {self.screen_width}x{self.screen_height}")

        # Create the main frame with 2 rows
        self.main_frame = ctk.CTkFrame(self.master, bg_color="red")
        self.main_frame.pack(expand=True, fill=ctk.BOTH)

        # Divide main_frame into a 2x3 grid
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(2, weight=1)

        # Top Row: Selfie Zone Title
        title_label = ctk.CTkLabel(self.main_frame, text="Selfie Zone", font=("Helvetica", int(self.screen_height/20), "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, self.screen_height/10))

        # Calculate the button width and height based on screen size
        button_width = int(self.screen_width / 6)  # Divide the width equally into 6 parts for 3 buttons and gaps
        button_height = int(self.screen_height / 5)  # Divide the height equally to create a square button

        button_data = [
            {
                "image_path": "./button_images/picture.png",
                "command": self.taking_picture_page
            },
            {
                "image_path": "./button_images/boomerang.png",
                "command": None  # Add the command for the boomerang button
            },
            {
                "image_path": "./button_images/video.png",
                "command": None  # Add the command for the video button
            }
        ]

        for i, data in enumerate(button_data):
            image = ctk.CTkImage(
                light_image=Image.open(data["image_path"]),
                size=(button_width, button_height)
            )
            button = ctk.CTkButton(self.main_frame, text="", image=image, command=data["command"])
            button.grid(row=1, column=i, padx=(self.screen_width / 30, 0))

    def taking_picture_page(self):
        """handles what happens after the picture button is pressed"""
        if self.main_frame:
            self.main_frame.destroy()

        self.preview_frame = ctk.CTkFrame(self.master, width=self.screen_width, height=self.screen_height)
        self.preview_frame.pack(expand=True, fill=ctk.BOTH)

        self.preview_label = ctk.CTkLabel(self.preview_frame, text="", width=self.screen_width, height=self.screen_height)
        self.preview_label.grid(row=0, column=0, columnspan=3)

        self.timer_label = ctk.CTkLabel(self.preview_frame, text="", text_color="red", bg_color="transparent", font=("Helvetica", 25, "bold"))
        self.timer_label.place(relx=0.5, rely=0.5, anchor="center")  # place over preview_label

        # calculate size the image will be when displayed in the label
        self.square_size = self.screen_height * 80/100

        # open camera
        self.cap = cv2.VideoCapture(0)
        # show camera frames in the preview_label
        self.show_picture_frames()

        # timer for 3 seconds
        self.timer_end = time.time() + 3
        self.timer_thread = threading.Thread(target=self.update_timer)
        self.timer_thread.start()

    def review_picture_page(self, image):
        """
        Review the image that was taken
        Show Accept, Retake and Return buttons
        :param image: function takes a PIL image
        """
        if self.preview_frame is not None:
            self.preview_frame.destroy()

        self.review_frame = ctk.CTkFrame(self.master, width=self.screen_width, height=self.screen_height)
        self.review_frame.pack(expand=True, fill=ctk.BOTH)

        # Convert the frame to RGB format
        cv2image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # Convert the NumPy array to PIL Image
        img = Image.fromarray(cv2image)

        # Create a label to display the captured image
        ctk_image = ctk.CTkImage(dark_image=img, size=(self.screen_width, self.screen_height * 0.9 ))
        self.review_label = ctk.CTkLabel(self.review_frame, image=ctk_image, text="")
        self.review_label.grid(row=0, column=0, columnspan=3)

        # Configure the preview_frame for button placement
        self.review_frame.grid_rowconfigure(1, weight=1)
        self.review_frame.grid_columnconfigure(0, weight=1)
        self.review_frame.grid_columnconfigure(1, weight=1)
        self.review_frame.grid_columnconfigure(2, weight=1)

        # Create buttons for accept, retake, and return to main page
        accept_button = ctk.CTkButton(self.review_frame, text="Accept", command=self.accept_picture)
        accept_button.grid(row=1, column=0, padx=(self.screen_width / 30, 0))

        retake_button = ctk.CTkButton(self.review_frame, text="Retake", command=self.retake_picture)
        retake_button.grid(row=1, column=1, padx=(self.screen_width / 30, self.screen_width / 30))

        cancel_button = ctk.CTkButton(self.review_frame, text="Cancel", command=self.cancel_picture)
        cancel_button.grid(row=1, column=2, padx=(0, self.screen_width / 30))

    def keyboard_page(self):
        """shows the keyboard"""
        # cancel button returns to homepage
        if self.review_frame:
            self.review_frame.destroy()

        # calculate the desired dimensions of the keyboard
        keyboard_width = self.screen_width
        keyboard_height = self.screen_height * 70/100

        # create a new frame for keyboard and entry box
        self.keyboard_page_frame = ctk.CTkFrame(self.master, )
        self.keyboard_page_frame.pack(side="bottom", fill=ctk.BOTH, expand=True)

        # keyboard frame
        self.keyboard_frame = ctk.CTkFrame(self.keyboard_page_frame, width=keyboard_width, height=keyboard_height)
        self.keyboard_frame.pack(side="bottom", pady=(0, 10))

        # Entry box for email address
        self.entry_frame = ctk.CTkFrame(self.keyboard_frame)
        self.entry_frame.grid(row=0, column=0, columnspan=11, sticky="nsew")
        # entry box
        self.email_entry_text = tk.StringVar()
        self.email_entry = ctk.CTkEntry(self.entry_frame, textvariable=self.email_entry_text,
                                        width=self.screen_width, height=self.screen_height*10/100)
        self.email_entry.focus()  # cursor goes to this input field
        self.email_entry.pack(side="bottom")

        # make keyboard buttons using Keyboard class
        self.keyboard = Keyboard(master=self.keyboard_frame, width=keyboard_width, height=keyboard_height,
                                 entry_box=self.email_entry, cancel=self.cancel_picture, enter=self.save_picture)

        self.entry_frame.grid_columnconfigure(0, weight=1)

    def show_picture_frames(self):
        """show camera frames in preview_label"""
        # Get the latest frame and convert into Image
        ret, frame = self.cap.read()
        if not ret:
            raise ValueError("Failed to capture video")

        # self.last_frame will eventually be equal to the very last frame which will be displayed in the review
        self.last_frame = frame

        # Convert the latest frame to RGB format
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Convert the NumPy array to PIL Image
        img = Image.fromarray(cv2image)
        ctk_image = ctk.CTkImage(dark_image=img, size=(self.square_size, self.square_size) )
        self.preview_label.ctk_image = ctk_image  # avoid garbage collection
        self.preview_label.configure(image=ctk_image)
        # Repeat after an interval to capture continuously
        self.preview_label.after(17, self.show_picture_frames)

    def update_timer(self):
        """
        Time picture()
        release camera and call review_picture()
        """
        # get remaining time when the function is called again
        while time.time() < self.timer_end:
            remaining_time = int(self.timer_end - time.time())
            self.timer_label.configure(text=f"{remaining_time}s")
            time.sleep(0.1)

        if self.last_frame is not None:
            time.sleep(0.1)
            self.cap.release()  # close the camera
            self.review_picture_page(self.last_frame)  # pass captured image for review
        else:
            raise ValueError("No last frame captured before timer ended")

    def accept_picture(self):
        """pressing the accept button leads to keyboard page"""
        self.keyboard_page()

    def save_picture(self):
        """watermark and save image when accepted when enter key on keyboard is pressed"""
        # get the current file count
        count = self.get_count()
        if self.last_frame is not None:
            # Resize the frame before saving
            resized_frame = cv2.resize(self.last_frame, (
            1280, 853))
            # Convert the frame to RGB format
            frame_rgb = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            # Save the resized frame as an image
            self.image_path = f"saved_pictures/{count}.jpeg"
            cv2.imwrite(filename=self.image_path, img=frame_rgb)
            # Apply watermark to the image
            self.watermark.apply_watermark(accepted_image_path=self.image_path)
            # update the number in count.txt
            self.update_count(count=count)
            # send the email
            self.send_email()
            # Destroy the existing keyboard frame if it exists and return home
            if self.keyboard_page_frame:
                self.keyboard_page_frame.destroy()
                self.home_page()

    def retake_picture(self):
        """Retake the picture"""
        if self.review_frame is not None:
            self.review_frame.destroy()
        self.taking_picture_page()

    def cancel_picture(self):
        """Return to main page"""
        if self.review_frame is not None:
            self.review_frame.destroy()
        if self.keyboard_page_frame is not None:
            self.keyboard_page_frame.destroy()

        self.home_page()

    def send_email(self):
        """send email containing picture"""
        # get email from entry box
        self.user_email = self.email_entry.get()
        # send email using the EmailSender class
        self.mail.send_email(receiver_email=self.user_email, picture_path=self.image_path)

    def get_screen_size(self):
        """screen size based on the master frame"""
        self.screen_width = self.master.winfo_screenwidth()
        self.screen_height = self.master.winfo_screenheight()

    def get_count(self):
        """Read count.txt"""
        if os.path.exists(self.file_count_path):
            with open(self.file_count_path, "r") as file:
                count = int(file.read())
                return count
        else:
            with open(self.file_count_path, "x") as file:  #  create a new file and open it for writing
                count = 0
                file.write(str(count))
                return count

    def update_count(self, count):
        """update the count.txt"""
        with open(self.file_count_path, "w") as file:
            count +=1
            file.write(str(count))
