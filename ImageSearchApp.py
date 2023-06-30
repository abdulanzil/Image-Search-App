import tkinter as tk
from tkinter import font
from tkinter import filedialog, messagebox

import cv2
import os
from threading import Thread
import psutil
import time

from PIL import Image, ImageTk

partitions = psutil.disk_partitions()

orb = cv2.ORB_create(nfeatures=1700)
bf = cv2.BFMatcher()

list_of_files_to_search = []
excluded_dirs = []
found_images = []
directories = [partition.device for partition in partitions]

# Create a new Tkinter window
window = tk.Tk()

# Set the window title
window.title("Image Search")

# Set the window dimensions
window.geometry("%dx%d" % (window.winfo_screenwidth(), window.winfo_screenheight()))
window.configure(bg="gray")
window.iconbitmap('find_Img_logo.ico')

# Create a custom font
custom_font = font.Font(family="Arial", size=20, weight="bold")

# Add a label to the window
label = tk.Label(window, text="find_Img", font=custom_font, background="yellow")
label.configure(fg="red", padx=20, pady=5)
label.pack(pady=30, anchor="center")

main_frame = tk.Frame(window)
main_frame.pack()

# frame for every selection button
frame = tk.Frame(main_frame, borderwidth=2)
frame.grid(row=0, column=0, pady=10)


# Function to handle images selection
def browse_files():
    global list_of_files_to_search, myFrame
    filetypes = (
        ("Image files", "*.jpg *.jpeg *.png"),
        ("All files", "*.*")
    )
    files = filedialog.askopenfilenames(filetypes=filetypes)
    # Selected file is in the format of 'E:/anz/hai.jpg'
    for file in files:
        list_of_files_to_search.append(file)
        tk.Label(myFrame, text=file, fg='darkgreen').pack(anchor='w')

    print(list_of_files_to_search, 'SEARCH DIRECTORY SELECTED\n')


# Exclude folders action
def exclude_dirs():
    global excluded_dirs, myFrame1

    while True:
        dire = filedialog.askdirectory()
        # After selection, it is in the format 'E:\\', 'E:/anz/hello/hai' like this
        if dire:
            # changing to the format 'E:\', 'E:\anz\hello\hai' like this
            dire = dire.replace('/', '\\')
            if dire not in excluded_dirs:
                excluded_dirs.append(dire)
                tk.Label(myFrame1, text=dire, fg='indigo').pack(anchor='w')
        else:
            break

    print(excluded_dirs, 'EXCLUDED\n')


# This function makes list of descriptors from the list of images to search
def make_kp_and_des(reference_images):
    global orb

    ref_ds = []
    for i, imgFile in enumerate(reference_images):
        try:
            img = cv2.imread(imgFile, 0)
            _, des = orb.detectAndCompute(img, None)
            ref_ds.append(des)
        except:
            print('NO images selected')

    return ref_ds


# This function returns the Boolean value of similarity of two images
def similar_images(des1, des2):
    global bf

    good = []
    try:
        matches = bf.knnMatch(des1, des2, k=2)
        for m, n in matches:
            if m.distance < 0.75 * n.distance:
                good.append([m])
    except:
        pass

    if len(good) > 60:
        return True, len(good)
    else:
        return False, len(good)


# The path is copied when we doubleclick on it in the results section
def open_link(event):
    text = event.widget.cget("text")
    window.clipboard_clear()
    window.clipboard_append(text)


# Display image label creation
image_label = tk.Label(window)


# Function to display the image when mouse enters the label
def show_image(event):
    global image_label
    # Get the path from the label
    path = event.widget.cget("text")
    try:
        # Open the image using PIL
        image = Image.open(path)
        # Resize the image to a smaller size
        image.thumbnail((200, 200))
        # Create a Tkinter-compatible photo image
        photo = ImageTk.PhotoImage(image)
        # Update the image label with the new photo
        image_label.config(image=photo)
        # Keep a reference to the photo to prevent it from being garbage collected
        image_label.image = photo
        if not image_label.winfo_ismapped():
            # Position the image label above the pointer
            image_label.place(x=event.x_root, y=event.y_root, anchor="w")
    except Exception as e:
        print("Error loading image:", e)


# Function to hide the image when mouse leaves the label
def hide_image(event):
    global image_label
    image_label.config(image="")


# Action when terminate button is clicked while in a search
def terminate_search():
    global is_thr1_running, thr1, terminate_button, progress_label, progress_path, frame2
    result = messagebox.askyesno("Confirmation", "Are you sure to cancel the Search ?")
    if result:
        is_thr1_running = False
        thr1.join()
        progress_label.configure(text='SEARCH CANCELLED !')

        progress_path.destroy()
        terminate_button.destroy()

        tk.Button(frame2, text='Reset', command=reset_entire_window).pack(side=tk.LEFT)


# Creation of these widgets
terminate_button = tk.Button()      # Terminate button
progress_label = tk.Label()         # To show whether searching, cancelled, completed
progress_path = tk.Label()          # To show current searching path


# After completion or termination, RESET button is shown
# This function reset the app to default
def reset_entire_window():
    global frame2, wrapper2, mycanvas2, xscrollbar2, yscrollbar2, myFrame2, image_label,\
        var, myFrame1, myFrame

    # emptying the following three lists
    found_images.clear()
    list_of_files_to_search.clear()
    excluded_dirs.clear()

    # not necessary to destroy these five
    # myFrame2.destroy()
    # xscrollbar2.destroy()
    # yscrollbar2.destroy()
    # mycanvas2.destroy()
    # wrapper2.destroy()

    # destroy the image_label and the results column frame completely
    image_label.destroy()
    frame2.destroy()

    # CREATING RESULTS SECTION WIDGETS AGAIN

    image_label = tk.Label(window)
    frame2 = tk.Frame(main_frame, borderwidth=2)
    tk.Label(frame2, text='Results (similarity score, image path)', font='Helvetica 15').pack()

    wrapper2 = tk.LabelFrame(frame2)
    wrapper2.pack(fill='both', expand=True, pady=20)
    mycanvas2 = tk.Canvas(wrapper2)
    mycanvas2.pack(side=tk.LEFT, fill='both', expand=True)
    xscrollbar2 = tk.Scrollbar(wrapper2, orient='horizontal', command=mycanvas2.xview)
    xscrollbar2.pack(side=tk.BOTTOM, fill='x')
    yscrollbar2 = tk.Scrollbar(wrapper2, orient='vertical', command=mycanvas2.yview)
    yscrollbar2.pack(side=tk.RIGHT, fill='y')
    mycanvas2.configure(xscrollcommand=xscrollbar2.set, yscrollcommand=yscrollbar2.set)
    myFrame2 = tk.Frame(mycanvas2)
    mycanvas2.create_window((0, 0), window=myFrame2, anchor="nw")

    myFrame2.bind('<Configure>', update_scroll_region_2)

    # CHANGES TO 1st COLUMN

    # Change the radiobutton state
    var.set(1)
    handle_radiobutton_change()

    # Destroy frames within Exclusions and Images_to_search fields, and recreation of them
    myFrame1.destroy()
    myFrame.destroy()
    myFrame1 = tk.Frame(mycanvas1)
    mycanvas1.create_window((0, 0), window=myFrame1, anchor="nw")
    myFrame = tk.Frame(mycanvas)
    mycanvas.create_window((0, 0), window=myFrame, anchor="nw")


# Function thread after search button clicked (from search_it())
def search_images():
    global list_of_files_to_search, excluded_dirs, directories, myFrame2, found_images,\
        is_thr1_running, terminate_button, progress_label, progress_path

    # Note the time from here for the calculation of total time taken for search
    start_time = time.time()

    # Creation of widgets
    progress_label = tk.Label(frame2, text='SEARCH IN PROGRESS..', fg='goldenrod', font='Arial 16')
    progress_label.pack(pady=20, anchor='w')
    terminate_button = tk.Button(frame2, text='Terminate', command=terminate_search)
    terminate_button.pack(side=tk.LEFT)
    progress_path = tk.Label(frame2, text=directories[0])
    progress_path.pack(pady=5, anchor='w', padx=15)

    # show whole frame2 widget created
    frame2.grid(row=0, column=1, pady=20, padx=50, sticky='n')

    # Get list of descriptors from the list of images
    ref_ds = make_kp_and_des(list_of_files_to_search)

    # File extensions to consider
    image_extensions = ['.jpg', '.jpeg', '.png']

    # Iterate through each directory in the directories
    for directory in directories:
        # Walk through the directory and compare with similar_images()
        for root, dirs, files in os.walk(directory):

            # If any one of the excluded directories is matched with the root,
            # that root and its sub-files and sub-folders are deleted from searching
            # Excluded dirs are in the format E:\anz\hello\hai
            if any(excluded_dir == root for excluded_dir in excluded_dirs):
                dirs[:] = []
                files[:] = []
                continue

            # Action through files
            for file in files:
                # Check if the stop signal of thread is not triggered
                if is_thr1_running:

                    if os.path.splitext(file)[1].lower() in image_extensions:
                        file_path = os.path.join(root, file)
                        # file_path now in format 'E:\anz\hello.jpg'
                        file_path = file_path[: 2] + file_path[2:].replace('\\', '/')
                        # file_path changed to format 'E:/anz/hello.jpg' to handle the opencv errors
                        progress_path.configure(text=file_path[: 50] + '...')

                        # Get the descriptor of the file_path image
                        try:
                            img = cv2.imread(file_path, 0)
                            _, des2 = orb.detectAndCompute(img, None)
                        except:
                            des2 = None

                        # des1, des2 are descriptors of image in the reference, file_path image respectively
                        for des1 in ref_ds:
                            try:
                                result, score = similar_images(des1, des2)
                                if result:
                                    # Widget temp_frame for showing similarity score, file_path
                                    temp_frame = tk.Frame(myFrame2)
                                    temp_label1 = tk.Label(temp_frame, text=score, fg='green')
                                    temp_label2 = tk.Label(temp_frame, text=file_path, fg='blue')
                                    temp_label1.grid(row=0, column=0)
                                    temp_label2.grid(row=0, column=1)

                                    # Doubleclick on path to copy the path
                                    temp_label2.bind("<Double-Button-1>", open_link)

                                    # show image of respective path when mouse is hovered on top
                                    temp_label2.bind("<Enter>", show_image)
                                    # hide when mouse leaves
                                    temp_label2.bind("<Leave>", hide_image)

                                    # Display the temp_frame
                                    temp_frame.pack(anchor='w')

                                    # Add the image path to the found_images list
                                    found_images.append(file_path)

                                    break

                            except:
                                pass

                # to complete the thr1 thread function
                else:
                    return

    # After completion of search
    progress_path.destroy()
    terminate_button.destroy()

    progress_label.configure(text=f'SEARCH COMPLETED in {round((time.time() - start_time) / 60, 2)} minutes',
                             fg='darkgreen')
    tk.Button(frame2, text='Reset', command=reset_entire_window).pack(side=tk.LEFT)


# Declaring thr1, is_thr1_running for global usage
thr1 = Thread()
is_thr1_running = False


# Search button click action
def search_it():
    global thr1, is_thr1_running
    thr1 = Thread(target=search_images)
    is_thr1_running = True
    thr1.start()


# Handle the radiobutton actions
def handle_radiobutton_change():
    global directories

    if var.get() == 1:  # Full search option selected
        directories = [partition.device for partition in partitions]
        select_directory_button.config(state=tk.DISABLED)
        select_directory_label.configure(text='[ ' + ', '.join(directories) + ' ]')
    else:
        select_directory_button.config(state=tk.NORMAL)


# Select directory button action
def select_directory():
    global directories, select_directory_label

    dire = filedialog.askdirectory()
    # After selection, it is in the format 'E:\\', 'E:/anz/hello/hai' like this
    if dire:
        # changing to the format 'E:\', 'E:\anz\hello\hai' like this
        directories = [dire.replace('/', '\\')]
        select_directory_label.configure(text='[ ' + ', '.join(directories) + ' ]')


# Create a frame for the radio-buttons
radiobutton_frame = tk.Frame(frame)
radiobutton_frame.pack(pady=10, padx=20, anchor="w")

# Create a variable to store the radiobutton choice
var = tk.IntVar(value=1)  # Full option selected by default

# Create the radio-buttons
full_radiobutton = tk.Radiobutton(radiobutton_frame, text="Full Search", variable=var, value=1,
                                  command=handle_radiobutton_change)
full_radiobutton.pack(side=tk.LEFT, padx=10)
half_radiobutton = tk.Radiobutton(radiobutton_frame, text="Search from a directory", variable=var, value=2,
                                  command=handle_radiobutton_change)
half_radiobutton.pack(side=tk.LEFT)

# Create a frame for the buttons
buttons_frame = tk.Frame(frame)
buttons_frame.pack(pady=5, anchor="w", padx=30, expand=False)

# Create the Select Directory button
select_directory_button = tk.Button(buttons_frame, text="Select Directory", command=select_directory)
select_directory_button.pack(anchor='w', pady=5)
select_directory_label = tk.Label(buttons_frame, text='[ ' + ', '.join(directories) + ' ]')
select_directory_label.configure(fg='indigo')
select_directory_label.pack(anchor='w', padx=30)

# Create the Choose Exclusions button
choose_exclusions_button = tk.Button(buttons_frame, text="Choose Exclusions (Optional)", command=exclude_dirs)
choose_exclusions_button.pack(anchor='w', pady=15)

# Scrollbar part for Excluding folders
wrapper1 = tk.LabelFrame(buttons_frame)
wrapper1.pack(fill='both', expand=True)
mycanvas1 = tk.Canvas(wrapper1, height=40)
mycanvas1.pack(side=tk.LEFT, fill='both', expand=True)
xscrollbar1 = tk.Scrollbar(wrapper1, orient='horizontal', command=mycanvas1.xview)
xscrollbar1.pack(side=tk.BOTTOM, fill='x')
yscrollbar1 = tk.Scrollbar(wrapper1, orient='vertical', command=mycanvas1.yview)
yscrollbar1.pack(side=tk.RIGHT, fill='y')
mycanvas1.configure(xscrollcommand=xscrollbar1.set, yscrollcommand=yscrollbar1.set)
myFrame1 = tk.Frame(mycanvas1)
mycanvas1.create_window((0, 0), window=myFrame1, anchor="nw")


def update_scroll_region_1(event):
    mycanvas1.configure(scrollregion=mycanvas1.bbox("all"))


myFrame1.bind('<Configure>', update_scroll_region_1)

# frame for image upload and view
ref_img_frame = tk.Frame(frame)
ref_img_frame.pack(pady=10, anchor='w')

# Create the choose images button
choose_images_button = tk.Button(ref_img_frame, text="Upload image samples", command=browse_files)
choose_images_button.pack(pady=15, padx=30, anchor='w')

# Scrollbar part for Image selections to search
wrapper = tk.LabelFrame(ref_img_frame)
wrapper.pack(fill='both', expand=True, padx=30)
mycanvas = tk.Canvas(wrapper, height=40)
mycanvas.pack(side=tk.LEFT, fill='both', expand=True)
xscrollbar = tk.Scrollbar(wrapper, orient='horizontal', command=mycanvas.xview)
xscrollbar.pack(side=tk.BOTTOM, fill='x')
yscrollbar = tk.Scrollbar(wrapper, orient='vertical', command=mycanvas.yview)
yscrollbar.pack(side=tk.RIGHT, fill='y')
mycanvas.configure(xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set)
myFrame = tk.Frame(mycanvas)
mycanvas.create_window((0, 0), window=myFrame, anchor="nw")


def update_scroll_region(event):
    mycanvas.configure(scrollregion=mycanvas.bbox("all"))


myFrame.bind('<Configure>', update_scroll_region)

# Disable the Select Directory button if Full option is selected initially
if var.get() == 1:
    select_directory_button.config(state=tk.DISABLED)

# Search button to start the search
search_button = tk.Button(frame, text="Search", command=search_it)
search_button.configure(padx=100, pady=5)
search_button.pack(pady=20)

# FRAME2 WIDGET CREATION - 2ND COLUMN

frame2 = tk.Frame(main_frame, borderwidth=2)

tk.Label(frame2, text='Results (similarity score, image path)', font='Helvetica 15').pack()

# Scrollbar part for showing results
wrapper2 = tk.LabelFrame(frame2)
wrapper2.pack(fill='both', expand=True, pady=20)
mycanvas2 = tk.Canvas(wrapper2)
mycanvas2.pack(side=tk.LEFT, fill='both', expand=True)
xscrollbar2 = tk.Scrollbar(wrapper2, orient='horizontal', command=mycanvas2.xview)
xscrollbar2.pack(side=tk.BOTTOM, fill='x')
yscrollbar2 = tk.Scrollbar(wrapper2, orient='vertical', command=mycanvas2.yview)
yscrollbar2.pack(side=tk.RIGHT, fill='y')
mycanvas2.configure(xscrollcommand=xscrollbar2.set, yscrollcommand=yscrollbar2.set)
myFrame2 = tk.Frame(mycanvas2)
mycanvas2.create_window((0, 0), window=myFrame2, anchor="nw")


def update_scroll_region_2(event):
    mycanvas2.configure(scrollregion=mycanvas2.bbox("all"))


myFrame2.bind('<Configure>', update_scroll_region_2)


# Action on window closing
def on_closing():
    global thr1, is_thr1_running
    is_thr1_running = False
    # Stop the thread and close the window
    try:
        thr1.join()  # Wait for the thread to finish
        # this will occur fast, because we are triggering by making is_thr1_running = False
    except:
        pass
    window.destroy()


# Configure the close button to stop the thread and close the window
window.protocol("WM_DELETE_WINDOW", on_closing)

# Start the Tkinter event loop
window.mainloop()

