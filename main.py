import tkinter as tk
from  tkinter import ttk
from tkinter import filedialog
import image_processing
from PIL import ImageTk, Image
import numpy as np
from tkinter import messagebox as tkMessagebox
import pickle
import os

CUSTOM_FONT = ("Arial",12)
img_prc = image_processing.ImageProces()

class mainOfMT(tk.Tk):
    def import_dir(self,canvas):
        self.canvas = canvas
        self.file_path = filedialog.askopenfilename()
        img_prc.loadImages(self.file_path)
        self.showImg(self.file_path, self.canvas)


    def showImg(self,path,canvas):
        load = Image.open(path)
        width, height = load.size
        test = np.ceil(height/600) + 1
        width = width / test
        height = height / test
        load = load.resize((int(width), int(height)), Image.ANTIALIAS)
        render = ImageTk.PhotoImage(load)

        img= tk.Label(self, image=render)
        img.image = render
        x_cor = np.ceil((800-width)/2)
        y_cor = np.ceil((600-height)/2)
        canvas.delete("all")
        canvas.create_image(canvas.winfo_width()/2,canvas.winfo_height()/2,anchor="center",image= render)



    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.grid()
        container.grid_rowconfigure(0,weight=1)
        container.grid_columnconfigure(0,weight=1)
        container.winfo_toplevel().title("BSDF")

        self.frames = {}

        for N in (StartPage, SecondPage):
            self.frame = N(container, self)
            self.frames[N] = self.frame
            self.frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage,"")

    def show_frame(self, cont,project_name):
        self.current_dataset = project_name
        if(cont == StartPage):
            self.geometry("450x450")
        else:
            self.geometry("1000x650")

        self.frame = self.frames[cont]
        if(cont == SecondPage):
            self.frame.update_listbox()
        self.frame.tkraise()


    def show_plot(self):
        img_prc.plot_show()

    def excel(self,light_pos,cam_pos):
        if(light_pos == ""):
            tkMessagebox.showerror(title="error", message="Insert corect Light distance value", parent=self)
        elif(cam_pos == ""):
            tkMessagebox.showerror(title="error", message="Insert corect Camera distance value", parent=self)
        else:
            excel_path = filedialog.asksaveasfilename(defaultextension=".xls")
            img_prc.angle_dependency(light_pos,cam_pos,15,31,excel_path)

    def get_datasets(self):
        try:
            with open("projects.p","rb") as proj:
                projects = pickle.load(proj)
        except  (OSError, IOError) as e:
            return []

        return projects

    def create_new_project(self,freeze_button):
        self.p_window = NewDataSetPopupPage(self,self.get_datasets())
        freeze_button["state"] = "disabled"
        self.p_window.wait_window()
        freeze_button["state"] = "normal"
        self.frame.update_dataset_list(self)

    def save_picture(self, cam_pos, light_pos):
        self.name_window = ImgNamePopupPage(self)
        self.name_window.wait_window()
        proceededImg = image_processing.proceededImg()
        proceededImg.img_name = self.name_window.img_name
        proceededImg.camera_dist = cam_pos
        proceededImg.light_dist = light_pos
        proceededImg.directory = self.file_path
        proceededImg.proceededLumi_array = img_prc.lumi_array
        try:
            with open(self.current_dataset+".p","rb") as curr_ds:
                saved_image_list = pickle.load(curr_ds)
        except  (OSError, IOError) as e:
            saved_image_list = []
        saved_image_list.append(proceededImg)
        pickle.dump(saved_image_list,open(self.current_dataset+".p", "wb"))
        self.frame.update_listbox()

    def get_saved_img(self):
        self.saved_img = pickle.load(open(self.current_dataset+".p","rb"))
        return self.saved_img

    def remove_dataset(self,set_to_delete):
        datasets = self.get_datasets()
        datasets.remove(set_to_delete)
        pickle.dump(datasets, open("projects.p", "wb"))
        set_to_delete = set_to_delete + ".p"
        os.remove(set_to_delete)
        self.frame.update_dataset_list(self)

    def change_img(self,selected_position):
        for img in self.saved_img:
            if(img.img_name == selected_position):
                new_img = img
                break
        self.file_path = new_img.directory
        self.showImg(self.file_path, self.canvas)
        img_prc.lumi_array =  new_img.proceededLumi_array

    def set_canvas(self,canvas):
        self.canvas = canvas

    def enable_select(self,select_button):
        select_button.configure(state="normal")



class SecondPage(tk.Frame):

    def __init__(self, parent, controller):
        self.controller = controller
        tk.Frame.__init__(self, parent)
        menuBar = tk.Menu(parent)
        filemenu = tk.Menu(menuBar, tearoff=0)
        filemenu.add_command(label="Import file", command=lambda: controller.import_dir(canvas))
        filemenu.add_command(label="Save file", command=lambda: controller.save_picture(int(cam_pos_entry.get()), int(light_pos_entry.get())))
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=quit)
        menuBar.add_cascade(label="File", menu=filemenu)

        tk.Tk.config(controller, menu=menuBar)

        button1 = tk.Button(self, text="Show plot", command=lambda: controller.show_plot())
        button1.grid(row=0, column=0)

        button2 = tk.Button(self, text="Export to excel",
                            command=lambda: controller.excel(int(cam_pos_entry.get()), int(light_pos_entry.get())))
        button2.grid(row=1, column=0)

        canvas = tk.Canvas(self, bg="whitesmoke", height=630, width=750)
        canvas.grid(row=0, column=1, columnspan=5, rowspan=10, sticky="wens", padx=(15, 5), pady=10)
        controller.set_canvas(canvas)

        list_frame = tk.Frame(self)
        list_frame.grid(row=0, columnspan =2, column=6,pady=10)

        photos_list = tk.Listbox(list_frame,width=20, height=35)
        photos_list.grid()
        photos_list.bind('<Double-Button-1>',lambda x: controller.change_img(photos_list.get("anchor")))
        self.photos_list = photos_list

        cam_pos_entry = tk.Entry(self)
        cam_pos_entry.grid(row=10, column=2)
        cam_pos_label = tk.Label(self, text="Camera distance")
        cam_pos_label.grid(row=11, column=2)
        light_pos_entry = tk.Entry(self)
        light_pos_entry.grid(row=10, column=3)
        light_pos_label = tk.Label(self, text="Light distance")
        light_pos_label.grid(row=11, column=3)



    def update_listbox(self):
        self.photos_list.delete(0,"end")
        saved =  self.controller.get_saved_img()
        for idx, P in enumerate(saved):
                self.photos_list.insert(idx, P.img_name)


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        select_label = tk.Label(self,text="Select dataset")
        select_label.grid(row=0,column=0)

        inner_frame = tk.Frame(self)
        inner_frame.grid(row=1,columnspan=3,sticky="nw",padx=70)
        self.dataset_list = tk.Listbox(inner_frame,width=50, height=20)
        self.update_dataset_list(controller)

        self.dataset_list.grid(row=1,column=0)
        self.dataset_list.bind('<<ListboxSelect>>',lambda x:controller.enable_select(self.run_button))

        self.run_button = tk.Button(self, text="Select", command=lambda: controller.show_frame(SecondPage,self.dataset_list.get("anchor")))
        self.run_button.grid(row=2,column=0)
        self.run_button.configure(state="disabled")

        delete_button = tk.Button(self,text="Delete Dataset", command=lambda: controller.remove_dataset(self.dataset_list.get("anchor")))
        delete_button.grid(row=2,column =1)

        create_button = tk.Button(self, text="Create new", command=lambda: controller.create_new_project(create_button))
        create_button.grid(row=2,column=2)

    def update_dataset_list(self, controller):
        self.dataset_list.delete(0,"end")
        for idx,P in enumerate(controller.get_datasets()):
            self.dataset_list.insert(idx,P)



class NewDataSetPopupPage(tk.Toplevel):

    def __init__(self,parent, old_datasets):
        tk.Toplevel.__init__(self,parent)
        self.parent = parent
        self.datasets = old_datasets
        self.test = tk.Label(self, text = "Insert name of new dataset")
        self.test.pack()
        self.name = tk.Entry(self)
        self.name.pack()
        self.ok_button = tk.Button(self,text="Ok",command=lambda: self.proceed())
        self.ok_button.pack()


    def proceed(self):
        self.datasets.append(self.name.get())
        pickle.dump(self.datasets, open("projects.p", "wb"))
        empty_dataset = []
        pickle.dump(empty_dataset,open(self.name.get()+".p","wb"))
        self.destroy()


class ImgNamePopupPage(tk.Toplevel):

    img_name = ""
    def __init__(self, parent):
        tk.Toplevel.__init__(self,parent)
        self.parent = parent
        self.label = tk.Label(self, text = "Insert name of image")
        self.label.pack()
        self.name = tk.Entry(self)
        self.name.pack()
        self.ok_button = tk.Button(self,text="Ok",command=lambda: self.proceed())
        self.ok_button.pack()

    def proceed(self):
        self.img_name = self.name.get()
        self.destroy()



if __name__ == "__main__":
    app = mainOfMT()
    app.eval('tk::PlaceWindow %s center' % app.winfo_pathname(app.winfo_id()))
    app.mainloop()