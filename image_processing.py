from os import listdir
from PIL import Image as PImage
import numpy as np
from numba import jit
from scipy.misc import fromimage
from itertools import product, chain
import time
import matplotlib.pyplot as plt
import xlwt


class ImageProces:

    luminace = []
    lumi_array = []
    data = None

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


    def loadImages(self,path):
        img = PImage.open(path)
        self.data = img.load()
        rgb_img = img.convert('RGB')
        x_axis, y_axis = rgb_img.size
        w, h = img.size
        t0 = time.time()
        midle = y_axis/2
        self.lumi_array = []
      #  t = np.frompyfunc(self.addLuminance,2,1).outer(np.arange(w-1),np.arange(h-1))
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
    #    x_new = np.arange(x_axis-1)
     #   y_new = np.array(self.lumi_array)
      #  self.lumi_array = np.polyfit(x_new,y_new,45)

        t1 = time.time()
        print(t1-t0)


    def plot_show(self):

        plt.plot(self.lumi_array)
        plt.show()

    def angle_dependency(self,light_dist,camera_dist,angle,object_length,directory):
        max_lum = max((self.lumi_array))
        max_point = self.lumi_array.index(max_lum)
        real_factor = object_length/len(self.lumi_array)

        book = xlwt.Workbook(encoding="utf-8")
        sheet1 = book.add_sheet("Sheet 1")

        bottom_alfa1 = 0
        bottom_alfa2 = max_point*real_factor
        row = 0
        sheet1.write(row, 0, "alfa1")
        sheet1.write(row, 1, "alfa2")
        sheet1.write(row, 2,"f(a1,a2)")
        for x in range(max_point,0,-25):
            row += 1
            if(x==max_point):
                alfa1 = 90
                alfa2 = 90 - angle
                sheet1.write(row,0,alfa1)
                sheet1.write(row,1,alfa2)
                sheet1.write(row,2,max((self.lumi_array)))
                continue

            bottom_alfa1 += 50*real_factor
            hypotenuse = np.sqrt(light_dist**2+(bottom_alfa1**2))
            area = light_dist*bottom_alfa1/2
            sin_alfa1 = (2*area)/(bottom_alfa1*hypotenuse)
            alfa1 = np.arcsin(sin_alfa1)*57.2958

            bottom_alfa2 -= 50*real_factor
            hypotenuse = np.sqrt(camera_dist**2+(bottom_alfa2**2))
            area = camera_dist*bottom_alfa2/2
            sin_alfa2 = (2*area)/(bottom_alfa2*hypotenuse)
            alfa2 = np.arcsin(sin_alfa2)*57.2958

            sheet1.write(row, 0, alfa1)
            sheet1.write(row, 1, alfa2)
            sheet1.write(row, 2, self.lumi_array[x])


        book.save(directory)

class proceededImg:

    img_name = ""
    proceededLumi_array = []
    camera_dist = ""
    light_dist = ""
    angle = ""
    object_length = ""
    directory = ""






