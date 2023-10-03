import openai
import tkinter as tk
from tkinter import ttk, filedialog, Canvas, PhotoImage, messagebox
import threading
import os
from PIL import Image, ImageTk
import easyocr
import numpy as np


class OCRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OCR Text Formatter v1.0")

        self.frame = ttk.Frame(self.root, padding="10")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.canvas = Canvas(self.frame, width=300, height=300)
        self.canvas.grid(row=0, column=3, rowspan=6)

        self.load_image_button = ttk.Button(
            self.frame, text="Load Image", command=self.load_image)
        self.load_image_button.grid(row=6, column=3)

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.term_label = ttk.Label(self.frame, text="Term:")
        self.term_label.grid(row=0, column=0)
        self.term_entry = ttk.Entry(self.frame, width=30)
        self.term_entry.grid(row=0, column=1)

        self.definition_label = ttk.Label(self.frame, text="Definition:")
        self.definition_label.grid(row=1, column=0)
        self.definition_entry = ttk.Entry(self.frame, width=30)
        self.definition_entry.grid(row=1, column=1)

        self.text_label = ttk.Label(self.frame, text="Text to Convert:")
        self.text_label.grid(row=2, column=0)
        self.text_entry = tk.Text(self.frame, width=40, height=10)
        self.text_entry.grid(row=2, column=1)

        self.submit_button = ttk.Button(
            self.frame, text="Submit", command=self.submit)
        self.submit_button.grid(row=4, column=0)

        self.result_label = ttk.Label(self.frame, text="Result:")
        self.result_label.grid(row=4, column=1)

        self.copy_button = ttk.Button(
            self.frame, text="Copy Result", command=self.copy_result)
        self.copy_button.grid(row=4, column=2)

        self.progress_bar = ttk.Progressbar(
            self.frame, orient='horizontal', length=200, mode='indeterminate')
        self.progress_bar.grid(row=5, column=0, columnspan=3, sticky='ew')
        self.progress_bar.grid_remove()

    def on_press(self, event):
        self.rect_start = (event.x, event.y)

    def on_drag(self, event):
        if hasattr(self, 'rect'):
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(
            self.rect_start[0], self.rect_start[1], event.x, event.y, outline='red')

    def on_release(self, event):
        self.rect_end = (event.x, event.y)
        self.perform_ocr()

    def perform_ocr(self):
        x1, y1 = self.rect_start
        x2, y2 = self.rect_end
        cropped_image = self.image.crop((x1, y1, x2, y2))

        cropped_image_np = np.array(cropped_image)

        reader = easyocr.Reader(lang_list=['en'])
        results = reader.readtext(cropped_image_np, detail=1)

        final_text = ""
        last_y = None

        for result in results:
            top_left, top_right, bottom_right, bottom_left = result[0]
            text = result[1]

            current_y = (top_left[1] + bottom_left[1]) / 2

            if last_y is not None and abs(current_y - last_y) > 10:
                final_text += "\n"

            final_text += text + " "
            last_y = current_y

        self.text_entry.delete("1.0", tk.END)
        self.text_entry.insert(tk.END, final_text.strip())

    def load_image(self):
        file_path = filedialog.askopenfilename()
        self.image = Image.open(file_path)
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

    def submit(self):
        self.progress_bar.grid(row=5, column=0, columnspan=3, sticky='ew')
        self.progress_bar.start(10)
        threading.Thread(target=self.fetch_result).start()

    def fetch_result(self):
        a = self.term_entry.get()
        b = self.definition_entry.get()
        c = self.text_entry.get("1.0", tk.END).strip()

        prompt = f""" 
        lets play a game where I will give you a list of both {a} and {b} and you will return the same list except you will add a comma between the {a} and {b}.

        For example if the list contained Spanish and English, I would give you
        "Hola Hello"
        And you would return:
        "Hola, Hello"

        Here is the text to convert:

        {c}
        """

        result = GPT4Req(prompt)
        self.result_label.config(text=f"Result: \n{result}")
        self.progress_bar.stop()
        self.progress_bar.grid_remove()

    def copy_result(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.result_label.cget("text")[8:])
        self.root.update()
        messagebox.showinfo("Copied", "Result copied to clipboard")


def GPT4Req(msg):
    openai.api_key = "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"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": msg}],
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response["choices"][0]["message"]["content"]


if __name__ == "__main__":
    root = tk.Tk()
    app = OCRApp(root)
    root.mainloop()
