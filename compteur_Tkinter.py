import tkinter as tk

root = tk.Tk()
root.title("Compteur Tkinter")
root.geometry("250x150")

counter = tk.IntVar()
counter.set(0) 

def increment():
    counter.set(counter.get() + 1)
    update_label_color()

def decrement():
    counter.set(counter.get() - 1)
    update_label_color()

def reset():
    counter.set(0)
    update_label_color()

def update_label_color():
    if counter.get() > 0:
        label.config(fg="green")
    elif counter.get() < 0:
        label.config(fg="red")
    else:
        label.config(fg="black")

label = tk.Label(root, textvariable=counter, font=("Arial", 30))
label.pack(pady=20)

button_frame = tk.Frame(root)
button_frame.pack()

tk.Button(button_frame, text="+1", command=increment, width=5).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="-1", command=decrement, width=5).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Reset", command=reset, width=5).pack(side=tk.LEFT, padx=5)

root.mainloop()