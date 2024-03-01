
from PIL import ImageTk
import PIL.Image
from tkinter import Tk, Label, Button, Frame, Canvas, Scrollbar, DISABLED, Menu
import sys
import os
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
import user_page as up
import login_page as ip

original_list, processed_list, augmented_list = [], [], []

def open_user_window(wind):
    wind.destroy()
    up.main()


def open_login_window(wind):
    wind.destroy()
    ip.main()


def get_photo_folder(type_photo):
    dir_path = ''
    if type_photo == "Original Photos":
        dir_path = './Augmentation_Project/original_images'
    if type_photo == "Processed Photos":
        dir_path = './Augmentation_Project/processed_images'
    if type_photo == "Augmented Photos":
        dir_path = './Augmentation_Project/augmented_images'
    folder = os.listdir(dir_path)
    image_list = []
    num_images = 0
    for num_images, file in enumerate(folder):
        img_path = os.path.join(dir_path, file)
        image = PIL.Image.open(img_path)
        resized_img = image.resize((500, 400))
        img = ImageTk.PhotoImage(resized_img)
        image_list.append(img)
    return num_images, image_list


def back(img_no, label, tot_img, btn_fwd, btn_back, frame):
    global original_list, processed_list, augmented_list
    label.grid_forget()
    btn_fwd.grid_forget()
    btn_back.grid_forget()
    # for changing image that is displayed, resetting buttons
    if frame == orig_frame:
        label = Label(frame, image=original_list[img_no])
    if frame == process_frame:
        label = Label(frame, image=processed_list[img_no])
    if frame == augmented_frame:
        label = Label(frame, image=augmented_list[img_no])
    btn_fwd = Button(frame, text="Forward", command=lambda: forward(img_no+1, label, tot_img, btn_fwd, btn_back, frame))
    btn_back = Button(frame, text="Back", command=lambda: back(img_no-1, label, tot_img, btn_fwd, btn_back, frame))

    # whenever the first image, have the back button disabled
    if img_no == 0:
        btn_back = Button(frame, text="Back", state=DISABLED)
    label.grid(row=1, column=0, columnspan=3, padx=20)
    btn_back.grid(row=5, column=0)
    btn_fwd.grid(row=5, column=2)


def forward(img_no, label, tot_img, btn_fwd, btn_back, frame):
    global original_list, processed_list, augmented_list
    label.grid_forget()
    btn_fwd.grid_forget()
    btn_back.grid_forget()

    # for getting image that is displayed, resetting buttons
    if frame == orig_frame:
        label = Label(frame, image=original_list[img_no])
    if frame == process_frame:
        label = Label(frame, image=processed_list[img_no])
    if frame == augmented_frame:
        label = Label(frame, image=augmented_list[img_no])
    # img_no+1 as we want the next image to pop up when clik forward
    btn_fwd = Button(frame, text="Forward", command=lambda: forward(img_no+1, label, tot_img, btn_fwd, btn_back, frame))
    # disable button for first and last photo
    if img_no == tot_img:
        btn_fwd = Button(frame, text="Forward", state=DISABLED)
    if img_no == 0:
        btn_back = Button(frame, text="Back", state=DISABLED)
    # img_no-1 as we want previous image when click back
    btn_back = Button(frame, text="Back", command=lambda: back(img_no-1, label, tot_img, btn_fwd, btn_back, frame))
    # Placing the button in new grid
    label.grid(row=1, column=0, columnspan=3, padx=20)
    btn_back.grid(row=5, column=0)
    btn_fwd.grid(row=5, column=2)


def jump_to_photo(img_no, label, btn_fwd, btn_back, tot_img, frame):
    global original_list, processed_list, augmented_list
    label.grid_forget()
    btn_fwd.grid_forget()
    btn_back.grid_forget()

    # for getting the image that is displayed, resetting buttons
    if frame == orig_frame:
        label = Label(frame, image=original_list[img_no])
    if frame == process_frame:
        label = Label(frame, image=processed_list[img_no])
    if frame == augmented_frame:
        label = Label(frame, image=augmented_list[img_no])
    if img_no == tot_img:
        btn_fwd = Button(frame, text="Forward", state=DISABLED)
    else:
        btn_fwd = Button(frame, text="Forward", command=lambda: forward(img_no+1, label, tot_img, btn_fwd, btn_back, frame))
    if img_no == 0:
        btn_back = Button(frame, text="Back", state=DISABLED)
    else:
        btn_back = Button(frame, text="Back", command=lambda: back(img_no-1, label, tot_img, btn_fwd, btn_back, frame))
    # Placing the button in new grid
    label.grid(row=1, column=0, columnspan=3, padx=20)
    btn_back.grid(row=5, column=0)
    btn_fwd.grid(row=5, column=2)


def make_frame_btns(frame):
    # makes buttons that switch to other frames
    orig_butt = Button(frame, text="Original Photos", command=lambda: orig_frame.tkraise())
    process_butt = Button(frame, text="Processed Photos", command=lambda: process_frame.tkraise())
    aug_butt = Button(frame, text="Augmented Photos", command=lambda: augmented_frame.tkraise())
    # disables button for current frame
    if frame == orig_frame:
        orig_butt = Button(frame, text="Original Photos", state=DISABLED)
    if frame == process_frame:
        process_butt = Button(frame, text="Processed Photos", state=DISABLED)
    if frame == augmented_frame:
        aug_butt = Button(frame, text="Augmented Photos", state=DISABLED)
    # puts buttons on grid
    orig_butt.grid(row=0, column=1, sticky="nw")
    process_butt.grid(row=0, column=1, sticky="ne")
    aug_butt.grid(row=0, column=2, sticky="nw", padx=1)


def make_frame(frame):
    global original_list, processed_list, augmented_list
    # make original photo, processed photo, and augmented photo buttons
    make_frame_btns(frame)
    # put images in list, display first image
    num_img = 0
    if frame == orig_frame:
        num_img, original_list = get_photo_folder("Original Photos")
        label = Label(orig_frame, image=original_list[0])
        label.grid(row=1, column=0, columnspan=3, padx=20)
    if frame == process_frame:
        num_img, processed_list = get_photo_folder("Processed Photos")
        label = Label(process_frame, image=processed_list[0])
        label.grid(row=1, column=0, columnspan=3, padx=20)
    if frame == augmented_frame:
        num_img, augmented_list = get_photo_folder("Augmented Photos")
        label = Label(augmented_frame, image=augmented_list[0])
        label.grid(row=1, column=0, columnspan=3, padx=20)

    # We will have button back, and forward
    button_back = Button(frame, text="Back", command=back, state=DISABLED)
    button_forward = Button(frame, text="Forward", command=lambda: forward(0, label, num_img, button_forward,
                                                                           button_back, frame))
    # grid function is for placing the buttons in the frame
    button_back.grid(row=5, column=0)
    button_forward.grid(row=5, column=2)
    # Create a frame for the canvas
    frame_canvas = Frame(frame)
    frame_canvas.grid(row=1, column=6, pady=(5, 0), sticky='nw')
    frame_canvas.grid_rowconfigure(0, weight=1)
    frame_canvas.grid_columnconfigure(0, weight=1)
    frame_canvas.grid_propagate(False)

    # canvas
    canvas = Canvas(frame_canvas)
    canvas.grid(row=0, column=0, sticky="news")
    # make scrollbar for image numbers on canvas
    scrollbar = Scrollbar(frame_canvas, orient="vertical", command=canvas.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")
    canvas.configure(yscrollcommand=scrollbar.set)
    btn_frame = Frame(canvas, bg="blue")
    canvas.create_window((0, 0), window=btn_frame, anchor='nw')
    # make button number for num images and allow button to jump to photo
    button = list(range(0, num_img+1))
    for i in range(0, num_img+1):
        button[i] = Button(btn_frame, text=i+1, command=lambda i=i: jump_to_photo(i, label, button_forward, button_back, num_img, frame))
        button[i].grid(row=i, column=0, sticky="news")
    btn_frame.update_idletasks()
    btn_width = 2*(button[0].winfo_width())
    # set scroll bar to only display 14 num buttons, otherwise need to scroll
    if num_img <= 14:
        btn_height = sum(button[i].winfo_height() for i in range(0, num_img+1))
    else:
        btn_height = sum(button[i].winfo_height() for i in range(0, 15))
    frame_canvas.config(width=btn_width, height=btn_height)
    canvas.config(scrollregion=canvas.bbox("all"))


# Main #
def main():
    global orig_frame, process_frame, augmented_frame
    # create window
    window = Tk()
    window.title('Facial Feature Augmentation using GAN')
    mb = Menu(window)
    mb_dropdown = Menu(mb, tearoff=0)
    mb_dropdown.add_command(label="Logout",  command=lambda: open_login_window(window))
    mb_dropdown.add_command(label="About")
    mb_dropdown.add_command(label="Main Page",  command=lambda: open_user_window(window))
    mb.add_cascade(label="Menu", menu=mb_dropdown)
    window.config(menu=mb)
    orig_frame = Frame(window)
    process_frame = Frame(window)
    augmented_frame = Frame(window)
    make_frame(orig_frame)
    make_frame(process_frame)
    make_frame(augmented_frame)
    orig_frame.grid(row=1, column=0)
    process_frame.grid(row=1, column=0)
    augmented_frame.grid(row=1, column=0)
    orig_frame.tkraise()
    window.geometry("590x500")
    window.mainloop()


if __name__ == "__main__":
    main()
