from os import listdir
from PIL import Image as PImage
import numpy as np
from numba import jit
from scipy.misc import fromimage
from itertools import product, chain
import time
import matplotlib.pyplot as plt
import xlwt
import math


class ImageProces:

    luminace = []
    lumi_array = []
    data = None
    calaculate_area = []
    tare_area = []

    def maxIntensity(self,array,size,step):

        maxLumi = []
        for e in range(step,size):
            lumi=0
            for n in range(e-size,e+size):
                lumi += array[n]
            maxLumi.append(lumi)
        return max(maxLumi)


    def addLuminance(self, x, y):
        r_sum = g_sum = b_sum = 0
        [r, g, b] = self.data[x, y]
        r_sum += r
        g_sum += g
        b_sum += b
        return 0.2126 * r_sum + 0.7152 * g_sum + 0.0722 * b_sum
        #lumi_array.append(self.luminance)

    def getCanvasDetails(self,c_width,c_height,render_width,render_height,scale):
        self.c_width = c_width
        self.c_height = c_height
        self.render_width = render_width
        self.render_height = render_height
        self.scale = scale

    def rescaleImg(self,selectRectangle):
        return [int((selectRectangle[0]-(self.c_width-self.render_width)/2)*self.scale) ,int((selectRectangle[2]-(self.c_width-self.render_width)/2)*self.scale),
        int((selectRectangle[1]-(self.c_height-self.render_height)/2)*self.scale), int((selectRectangle[3]-(self.c_height-self.render_height)/2)*self.scale)]

    def fill_calculate_area(self,selectRectangle):
        self.calaculate_area = self.rescaleImg(selectRectangle)

    def fil_tare_area(self,selectRectangle):
        self.tare_area = self.rescaleImg(selectRectangle)

    def loadImages(self,path):
        self.img = PImage.open(path)
        self.data = self.img.load()
        self.rgb_img = self.img.convert('RGB')

    def set_new_calc_area(self):
        lumi_array_vert = []
        width =  abs(self.calaculate_area[1]-self.calaculate_area[0])
        for y in range(self.calaculate_area[2], self.calaculate_area[3]):
            r_sum = g_sum = b_sum = 0
            for x in range(self.calaculate_area[0], self.calaculate_area[1]):
                [r, g, b] = self.data[x, y]
                r_sum += r
                g_sum += g
                b_sum += b
            r_sum = r_sum / width
            g_sum = g_sum / width
            b_sum = b_sum / width
            luminance = 0.2126 * r_sum + 0.7152 * g_sum + 0.0722 * b_sum
            lumi_array_vert.append(luminance)

        max_lum_vert = max((lumi_array_vert))
        max_line = self.calaculate_area[2] + lumi_array_vert.index(max_lum_vert)

        self.calaculate_area[2] = int(max_line - ((100*self.tare)/self.real_tare)/2)
        self.calaculate_area[3] = int(max_line + ((100 * self.tare) / self.real_tare)/2)


    def calaculate(self):
        self.set_new_calc_area()
        x_axis, y_axis = self.rgb_img.size
        t0 = time.time()
        midle = y_axis/2
        self.lumi_array = []
        if self.calaculate_area!= []:
            h = abs(self.calaculate_area[2]-self.calaculate_area[3])
            for x in range(self.calaculate_area[0],self.calaculate_area[1]):
                r_sum = g_sum = b_sum = 0
                for y in range(self.calaculate_area[2],self.calaculate_area[3]):
                    [r, g, b] = self.data[x, y]
                    r_sum += r
                    g_sum += g
                    b_sum += b
                r_sum = r_sum/h
                g_sum = g_sum/h
                b_sum = b_sum/h
                luminance = 0.2126 * r_sum + 0.7152 * g_sum + 0.0722 * b_sum
                self.lumi_array.append(luminance)
        else:
            w, h = self.img.size
            for x in range(x_axis-1):
                r_sum = g_sum = b_sum = 0
                for y in range(y_axis-1):
                    [r, g, b] = self.data[x, y]
                    r_sum += r
                    g_sum += g
                    b_sum += b
                r_sum = r_sum/h
                g_sum = g_sum/h
                b_sum = b_sum/h
                luminance = 0.2126 * r_sum + 0.7152 * g_sum + 0.0722 * b_sum
                self.lumi_array.append(luminance)


        t1 = time.time()
        print(t1-t0)

    def get_tare(self,real_tare):
        self.real_tare = real_tare
        x_axis, y_axis = self.rgb_img.size
        t0 = time.time()
        midle = y_axis / 2
        tare_begin = tare_end = 0
        luminance_old = 1000
        h = abs(self.tare_area[2]- self.tare_area[3])
        for x in range(self.tare_area[0], self.tare_area[1],10):
            r_sum = g_sum = b_sum = 0
            for y in range(self.tare_area[2], self.tare_area[3]):
                [r, g, b] = self.data[x, y]
                r_sum += r
                g_sum += g
                b_sum += b
            r_sum = r_sum / h
            g_sum = g_sum / h
            b_sum = b_sum / h
            luminance_new = 0.2126 * r_sum + 0.7152 * g_sum + 0.0722 * b_sum
            if tare_begin == 0:
                if (luminance_new - luminance_old)> 30:
                    tare_begin = x
                else:
                     luminance_old = luminance_new
            else:
                if (luminance_old)- luminance_new> 30:
                    tare_end = x
                    break
                else:
                    luminance_old = luminance_new
        self.tare = tare_end - tare_begin
        self.middle_point = int(tare_begin + self.tare/2)
        print(self.tare)


    def plot_show(self):
        plt.plot(self.lumi_array)
        plt.show()


    def angle_dependency(self,light_dist,camera_dist_norm,camera_dist_plain,angle,real_tare):
        max_lum = max((self.lumi_array))
        max_point = self.lumi_array.index(max_lum)

        self.book = xlwt.Workbook(encoding="utf-8")
        sheet1 = self.book.add_sheet("Sheet 1")

        self.alfa1_tab = []
        self.alfa2_tab = []
        self.f_a1_a2_tab = []
        row = 0
        sheet1.write(row, 0, "alfa1")
        sheet1.write(row, 1, "alfa2")
        sheet1.write(row, 2,"f(a1,a2)")
       # current_point = self.middle_point - self.calaculate_area[2]
        current_lumin = self.lumi_array[max_point]
        current_point = max_point
        alfa1 = 90
        alfa2 = 90 - angle
        alfa_t = 0
        alfa2_base = (np.sqrt(camera_dist_plain ** 2 - camera_dist_norm ** 2))  # przyprostokątna
        alfa2_base_digit = alfa2_base * (self.tare/real_tare)
        row = 1
        sheet1.write(row, 0, 90- alfa1)
        sheet1.write(row, 1, alfa2)
        sheet1.write(row, 2, current_lumin)
        alfa2_old = 0
        alfa2_flag = 0
        while True:

            row+=1
            alfa1 = alfa1-0.5
            alfa_t = alfa_t+0.5
            real_shift =(np.sin(np.deg2rad(alfa_t))*light_dist)/np.sin(np.deg2rad(alfa1))
            digit_shift = real_shift*(self.tare/real_tare)
            current_point= int(current_point+digit_shift)

            try:
                current_lumin=self.lumi_array[current_point]
            except IndexError:
                break

            alfa2_base-=real_shift
            hypotenuse = np.sqrt(alfa2_base**2+camera_dist_norm**2)
            alfa2 = math.degrees(math.asin((np.sin(np.deg2rad(90))*camera_dist_norm)/hypotenuse))


            if alfa2_old > alfa2:
                alfa2_flag = 1
            alfa2_old = alfa2

            if alfa2_flag == 1:
                alfa2_var = alfa2-90
            else:
                alfa2_var = 90-alfa2


            self.alfa1_tab.append(90-alfa1)
            self.alfa2_tab.append(alfa2_var)
            self.f_a1_a2_tab.append(current_lumin)

            sheet1.write(row, 0, 90 -alfa1)
            sheet1.write(row, 1, alfa2_var)
            sheet1.write(row, 2, current_lumin)

        alfa1=90
        alfa_t = 0
        #current_point = self.middle_point - self.calaculate_area[2]
        current_point = max_point
        alfa2_base = (np.sqrt(camera_dist_plain ** 2 - camera_dist_norm ** 2))
        alfa2_flag = 0
        alfa2_old = 90
        while True:

            row+=1
            alfa1 = alfa1-0.5
            alfa_t = alfa_t+0.5
            real_shift =(np.sin(np.deg2rad(alfa_t))*light_dist)/np.sin(np.deg2rad(alfa1))
            digit_shift = real_shift*(self.tare/real_tare)
            if current_point-digit_shift < 0:
                break
            current_point= int(current_point-digit_shift)

            try:
                current_lumin=self.lumi_array[current_point]
            except IndexError:
                break

            alfa2_base+=real_shift
            hypotenuse = np.sqrt(alfa2_base**2+camera_dist_norm**2)
            alfa2 = math.degrees(math.asin((np.sin(np.deg2rad(90))*camera_dist_norm)/hypotenuse))

            if alfa2_old < alfa2:
                alfa2_flag = 1
            alfa2_old = alfa2

            if alfa2_flag == 1:
                alfa2_var = alfa2 - 90
            else:
                alfa2_var = 90 - alfa2

            self.alfa1_tab.append(alfa1-90)
            self.alfa2_tab.append(alfa2_var)
            self.f_a1_a2_tab.append(current_lumin)

            sheet1.write(row, 0, alfa1-90)
            sheet1.write(row, 1, alfa2_var)
            sheet1.write(row, 2, current_lumin)

    def save_to_excel(self,directory):
        self.book.save(directory)

class proceededImg:

    img_name = ""
    proceededLumi_array = []
    calaculate_area = []
    camera_dist_norm = ""
    camera_dist_plain = ""
    light_dist = ""
    angle = ""
    tare = ""
    real_tare = ""
    object_length = ""
    directory = ""
    alfa1_tab = []
    alfa2_tab = []
    f_a1_a2_tab = []
    book = None





