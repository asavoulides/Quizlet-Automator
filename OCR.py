from tkinter import Tk, Canvas, PhotoImage, filedialog
from PIL import Image, ImageTk
import easyocr
import numpy as np

# Initialize global variables
rect_start = None
rect_end = None
rect = None


def on_press(event):
    global rect_start
    rect_start = (event.x, event.y)


def on_drag(event):
    global rect, rect_start
    if rect:
        canvas.delete(rect)
    rect = canvas.create_rectangle(
        rect_start[0], rect_start[1], event.x, event.y, outline='red')


def on_release(event):
    global rect_end
    rect_end = (event.x, event.y)
    perform_ocr()


def perform_ocr():
    global rect_start, rect_end
    x1, y1 = rect_start
    x2, y2 = rect_end
    cropped_image = image.crop((x1, y1, x2, y2))

    # Convert PIL Image to numpy array
    cropped_image_np = np.array(cropped_image)

    reader = easyocr.Reader(lang_list=['en'])
    results = reader.readtext(cropped_image_np, detail=1)

    # Initialize an empty string to store the final text
    final_text = ""

    # Initialize a variable to store the last y-coordinate
    last_y = None

    for result in results:
        top_left, top_right, bottom_right, bottom_left = result[0]
        text = result[1]

        # Calculate the y-coordinate of the current text block
        current_y = (top_left[1] + bottom_left[1]) / 2

        # If this is not the first block and the y-coordinate has changed significantly, add a new line
        if last_y is not None and abs(current_y - last_y) > 10:
            final_text += "\n"

        final_text += text + " "
        last_y = current_y

    print("Extracted Text:", final_text.strip())


# Initialize Tkinter window
root = Tk()
root.title("Image OCR")

# Load an image
file_path = filedialog.askopenfilename()
image = Image.open(file_path)
tk_image = ImageTk.PhotoImage(image)

# Create canvas and display image
canvas = Canvas(root, width=image.width, height=image.height)
canvas.pack()
canvas.create_image(0, 0, anchor="nw", image=tk_image)

# Bind mouse events
canvas.bind("<ButtonPress-1>", on_press)
canvas.bind("<B1-Motion>", on_drag)
canvas.bind("<ButtonRelease-1>", on_release)

root.mainloop()
