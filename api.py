import openai
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading
import os



def GPT4Req(msg):
    openai.api_key = "OPENAI Api Key"  # Replace with your actual API key
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

def submit():
    progress_bar.grid(row=5, column=0, columnspan=3, sticky='ew')  # Centered
    progress_bar.start(10)  # Start the animation
    threading.Thread(target=fetch_result).start()

def fetch_result():
    a = term_entry.get()
    b = definition_entry.get()
    c = text_entry.get("1.0", tk.END).strip()
    prompt = f""" 
    lets play a game where I will give you a list of both {a} and {b} and you will return the same list except you will add a comma between the spanish and english.

    For example if the list contained Spanish and English, I would give you
    "Hola Hello"
    And you would return:
    "Hola, Hello"

    Here is the text to convert:

    {c}
    """
    result = GPT4Req(prompt)
    result_label.config(text=f"Result: \n {result}")
    progress_bar.stop()  # Stop the animation
    progress_bar.grid_remove()

def copy_result():
    root.clipboard_clear()
    root.clipboard_append(result_label.cget("text")[8:])
    root.update()
    messagebox.showinfo("Copied", "Result copied to clipboard")

root = tk.Tk()
root.title("GPT-4 Request")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

term_label = ttk.Label(frame, text="Term:")
term_label.grid(row=0, column=0)
term_entry = ttk.Entry(frame, width=30)
term_entry.grid(row=0, column=1)

definition_label = ttk.Label(frame, text="Definition:")
definition_label.grid(row=1, column=0)
definition_entry = ttk.Entry(frame, width=30)
definition_entry.grid(row=1, column=1)

text_label = ttk.Label(frame, text="Text to Convert:")
text_label.grid(row=2, column=0)
text_entry = tk.Text(frame, width=40, height=10)
text_entry.grid(row=2, column=1)

submit_button = ttk.Button(frame, text="Submit", command=submit)
submit_button.grid(row=4, column=0)

result_label = ttk.Label(frame, text="Result:")
result_label.grid(row=4, column=1)

copy_button = ttk.Button(frame, text="Copy Result", command=copy_result)
copy_button.grid(row=4, column=2)

progress_bar = ttk.Progressbar(frame, orient='horizontal', length=200, mode='indeterminate')
progress_bar.grid(row=5, column=0, columnspan=3, sticky='ew')  # Centered
progress_bar.grid_remove()

root.mainloop()
