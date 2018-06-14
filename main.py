import tkinter as tk
from  tkinter import ttk
from tkinter import filedialog
import image_processing
from visual_results import  visual_results
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
        scale = np.ceil(height/650) + 1
        width = width / scale
        height = height / scale
        load = load.resize((int(width), int(height)), Image.ANTIALIAS)
        render = ImageTk.PhotoImage(load)

        img= tk.Label(self, image=render)
        img.image = render
        canvas.delete("all")
        temp = canvas.create_image(canvas.winfo_width()/2,canvas.winfo_height()/2,anchor="center",image= render)
        print(canvas.coords(temp))
        img_prc.getCanvasDetails(canvas.winfo_width(),canvas.winfo_height(),render.width(),render.height(),scale)

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
            self.geometry("950x650")

        self.frame = self.frames[cont]
        if(cont == SecondPage):
            self.frame.update_listbox()
        self.frame.tkraise()

    def show_plot(self):
        img_prc.plot_show()

    def calculate_img(self):
        img_prc.fill_calculate_area(self.rectangle_coordinates)
        img_prc.calaculate()

    def angle_dep(self,light_pos,cam_pos_norm,cam_pos_plain,angle,real_tare):
        if(light_pos == ""):
            tkMessagebox.showerror(title="error", message="Insert corect Light distance value", parent=self)
        elif(cam_pos_norm == ""):
            tkMessagebox.showerror(title="error", message="Insert corect Camera distance value", parent=self)
        else:
            self.calculate_img()
            img_prc.angle_dependency(light_pos,cam_pos_norm,cam_pos_plain,angle,real_tare)

    def excel(self):
        excel_path = filedialog.asksaveasfilename(defaultextension=".xls")
        img_prc.save_to_excel(excel_path)

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

    def save_picture(self, cam_pos_norm, cam_pos_plain, light_pos,angle,real_tare):
        self.name_window = ImgNamePopupPage(self)
        self.name_window.wait_window()
        proceededImg = image_processing.proceededImg()
        proceededImg.img_name = self.name_window.img_name
        proceededImg.camera_dist_plain = cam_pos_plain
        proceededImg.camera_dist_norm = cam_pos_norm
        proceededImg.light_dist = light_pos
        proceededImg.angle = angle
        proceededImg.tare = img_prc.tare
        proceededImg.real_tare = real_tare
        proceededImg.directory = self.file_path
        proceededImg.proceededLumi_array = img_prc.lumi_array
        proceededImg.calaculate_area = img_prc.calaculate_area
        proceededImg.f_a1_a2_tab = img_prc.f_a1_a2_tab
        proceededImg.alfa1_tab = img_prc.alfa1_tab
        proceededImg.alfa2_tab = img_prc.alfa2_tab
        proceededImg.book = img_prc.book

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


    def remove_from_dataset(self,delete_position):
        try:
            with open(self.current_dataset + ".p", "rb") as curr_ds:
                saved_image_list = pickle.load(curr_ds)
        except  (OSError, IOError) as e:
            saved_image_list = []
        saved_image_list.pop(delete_position[0])
        pickle.dump(saved_image_list, open(self.current_dataset + ".p", "wb"))
        self.frame.update_listbox()


    def change_img(self,selected_position,cam_pos_norm, cam_pos_plain, light_pos,angle,real_tare):
        for img in self.saved_img:
            if(img.img_name == selected_position):
                new_img = img
                break
        self.file_path = new_img.directory
        self.showImg(self.file_path, self.canvas)
        img_prc.lumi_array =  new_img.proceededLumi_array
        img_prc.calaculate_area = new_img.calaculate_area
        img_prc.tare = new_img.tare
        img_prc.f_a1_a2_tab = new_img.f_a1_a2_tab
        img_prc.alfa1_tab = new_img.alfa1_tab
        img_prc.alfa2_tab = new_img.alfa2_tab
        img_prc.book = new_img.book
        cam_pos_norm.delete(0,"end")
        cam_pos_norm.insert(0,new_img.camera_dist_norm)
        cam_pos_plain.delete(0,"end")
        cam_pos_plain.insert(0,new_img.camera_dist_plain)
        light_pos.delete(0,"end")
        light_pos.insert(0,new_img.light_dist)
        angle.delete(0,"end")
        angle.insert(0,new_img.angle)
        real_tare.delete(0,"end")
        real_tare.insert(0,new_img.real_tare)



    def set_canvas(self,canvas):
        self.canvas = canvas

    def enable_select(self,select_button):
        select_button.configure(state="normal")

    def set_rec_coordinates(self, rect_co):
        self.rectangle_coordinates =  rect_co

    def get_tare(self,real_tare):
        img_prc.fil_tare_area(self.rectangle_coordinates)
        img_prc.get_tare(real_tare)

    def visual_3d(self):
        epsilon_value = valuePopup(self)
        epsilon_value.wait_window()
        vis_results = visual_results()
        vis_results.show3d_gauss(img_prc.alfa1_tab,img_prc.alfa2_tab,img_prc.f_a1_a2_tab,epsilon_value.value,epsilon_value.type_value)

    def visual_2d(self):
        vis_results = visual_results()
        vis_results.show2d_quad(img_prc.alfa2_tab,img_prc.f_a1_a2_tab)

class SecondPage(tk.Frame):

    def __init__(self, parent, controller):
        self.controller = controller
        tk.Frame.__init__(self, parent)
        self.parent = parent
        menuBar = tk.Menu(parent)
        filemenu = tk.Menu(menuBar, tearoff=0)
        filemenu.add_command(label="Import file", command=lambda: controller.import_dir(self.canvas))
        filemenu.add_command(label="Save file", command=lambda: controller.save_picture(int(self.cam_pos_norm_entry.get()),int(self.cam_pos_plain_entry.get()),
                                                                                        int(self.light_pos_entry.get()),int(self.angle_entry.get()),int(self.real_tare_entry.get()),))
        filemenu.add_separator()
        filemenu.add_command(label="Get tare", command=lambda: self.controller.get_tare(int(self.real_tare_entry.get())))
        filemenu.add_command(label="Show plot",command=lambda: self.controller.show_plot())
        filemenu.add_command(label="Calculate values", command=lambda: controller.angle_dep(int(self.light_pos_entry.get()),int(self.cam_pos_norm_entry.get()),
                                                                                       int(self.cam_pos_plain_entry.get()),int(self.angle_entry.get()),int(self.real_tare_entry.get())))
        filemenu.add_command(label="Export to xls",command=lambda: controller.excel())
        filemenu.add_separator()
        filemenu.add_command(label="Select calculate area", command=lambda: self.calcuateRec())
        filemenu.add_separator()
        filemenu.add_command(label="Back", command=lambda: self.controller.show_frame(StartPage,""))
        filemenu.add_command(label="Exit", command=quit)
        menuBar.add_cascade(label="File", menu=filemenu)

        filemenu = tk.Menu(menuBar, tearoff=0)
        filemenu.add_command(label="F(a1)", command=lambda: controller.visual_2d())
        filemenu.add_command(label="F(a1,a2)", command=lambda: controller.visual_3d())

        menuBar.add_cascade(label="Visualisation", menu=filemenu)

        self.defineCanvas()
        self.defineEntries()
        self.defineRClickPopup()

        tk.Tk.config(controller, menu=menuBar)
        list_frame = tk.Frame(self)
        list_frame.grid(row=0, columnspan =2, column=6,pady=10)

        photos_list = tk.Listbox(list_frame,width=20, height=35)
        photos_list.grid()
        photos_list.bind('<Double-Button-1>',lambda x: controller.change_img(photos_list.get("anchor"),self.light_pos_entry,self.cam_pos_norm_entry,
                                                                                       self.cam_pos_plain_entry, self.angle_entry, self.real_tare_entry))
        photos_list.bind('<Button-3>', self.popup)


        self.photos_list = photos_list



    def defineCanvas(self):
        self.canvas = tk.Canvas(self, bg="whitesmoke", height=530, width=780)
        self.canvas.grid(row=0, column=1, columnspan=5, rowspan=2, sticky="wens", padx=(15, 5), pady=10)
        self.controller.set_canvas(self.canvas)
        self.move = False
        self.calculateRect = False
        self.createMouseBinding()

    def defineEntries(self):
        self.cam_pos_norm_entry = tk.Entry(self)
        self.cam_pos_norm_entry.grid(row=10, column=1)
        self.cam_pos_norm_label = tk.Label(self, text="Normal camera distance")
        self.cam_pos_norm_label.grid(row=11, column=1)
        self.cam_pos_plain_entry = tk.Entry(self)
        self.cam_pos_plain_entry.grid(row=10, column=2)
        self.cam_pos_plain_label = tk.Label(self, text="Plain camera distance")
        self.cam_pos_plain_label.grid(row=11, column=2)
        self.light_pos_entry = tk.Entry(self)
        self.light_pos_entry.grid(row=10, column=3)
        self.light_pos_label = tk.Label(self, text="Light distance")
        self.light_pos_label.grid(row=11, column=3)
        self.angle_entry = tk.Entry(self)
        self.angle_entry.grid(row=10,column=4)
        self.angle_label = tk.Label(self, text="Angle")
        self.angle_label.grid(row=11, column=4)
        self.real_tare_entry = tk.Entry(self)
        self.real_tare_entry.grid(row=10,column=5)
        self.real_tare_label = tk.Label(self, text="Tare")
        self.real_tare_label.grid(row=11, column=5)


    def defineRClickPopup(self):
        self.popup_menu = tk.Menu(self, tearoff=0)
        self.popup_menu.add_command(label='Delete')
      #  self.right_click = RightClick(self.parent)

    def createMouseBinding(self):
        self.canvas.bind("<Button-1>",self.startCreateCropp)
        self.canvas.bind("<ButtonRelease-1>", self.endCreateCropp)
        self.canvas.bind("<Motion>",self.moveCropp)

    def startCreateCropp(self,event):
        if self.calculateRect == True:
            self.move = True
            self.rectX =self.canvas.canvasx(event.x)#get location on canvas
            self.rectY = self.canvas.canvasy(event.y)

            self.rectangle = self.canvas.create_rectangle(self.rectX,self.rectY,self.rectX,self.rectY)
            self.rectangleId = self.canvas.find_closest(self.rectX,self.rectY,halo=2)

    def endCreateCropp(self,event):
        if self.calculateRect == True:
            self.move = False
            self.rectY1 = self.canvas.canvasy(event.y)
            self.rectX1 = self.canvas.canvasx(event.x)
            self.canvas.coords(self.rectangleId, self.rectX, self.rectY, self.rectX1, self.rectY1)
            coordinates = [self.rectX, self.rectY, self.rectX1, self.rectY1]
            self.controller.set_rec_coordinates(coordinates)
            self.calculateRect = False


    def moveCropp(self,event):
        if self.move:
            self.rectY1 = self.canvas.canvasy(event.y)
            self.rectX1 = self.canvas.canvasx(event.x)
            self.canvas.coords(self.rectangleId,self.rectX,self.rectY,self.rectX1,self.rectY1)

    def deleteRectangle(self):
        self.canvas.delete(self.rectangle)

    def calcuateRec(self):
         self.calculateRect = True


    def update_listbox(self):
        self.photos_list.delete(0,"end")
        saved =  self.controller.get_saved_img()
        for idx, P in enumerate(saved):
                self.photos_list.insert(idx, P.img_name)

    def popup(self,event):
        self.popup_menu.tk_popup(event.x_root, event.y_root, 0)
        self.controller.remove_from_dataset(self.photos_list.curselection())



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

class valuePopup(tk.Toplevel):

    types =   [("Gaussian","gaussian"),
               ("Cubic","cubic"),
               ("Inverse","inverse"),
               ("Multiquadric","multiquadric"),
               ("Thin plate","thin_plate")]

    def __init__(self, parent):
        tk.Toplevel.__init__(self,parent)
        self.parent = parent
        self.label = tk.Label(self, text = "Epsilon value:")
        self.label.pack()
        self.value_rec = tk.Entry(self)
        self.value_rec.pack()

        self.select = tk.StringVar()
        self.select.set("gaussian")
        for text,type in self.types:
            self.rb = tk.Radiobutton(self,text=text,variable=self.select,value=type)
            self.rb.pack(anchor = "w")

        self.ok_button = tk.Button(self,text="Ok",command=lambda: self.proceed())
        self.ok_button.pack()

    def proceed(self):
        try:
            self.value = int(self.value_rec.get())
        except ValueError:
            print("Wrong input")

        self.value = self.value_rec.get()
        self.type_value = self.select.get()
        self.destroy()


if __name__ == "__main__":
    app = mainOfMT()
    app.eval('tk::PlaceWindow %s center' % app.winfo_pathname(app.winfo_id()))
    app.mainloop()