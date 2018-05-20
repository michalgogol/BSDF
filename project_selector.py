import tkinter as tk

class project_selector(tk.Tk):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Another Page", font=CUSTOM_FONT)
        label.pack(pady=20, padx=20)

        button1 = tk.Button(self, text="Back to 1 page", command=lambda: controller.show_frame(StartPage))

        button1.pack()

