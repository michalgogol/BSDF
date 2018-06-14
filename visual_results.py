from scipy.interpolate import Rbf
import matplotlib.pyplot as plt
import numpy as np
import numpy.polynomial.polynomial as poly
from mpl_toolkits.mplot3d import axes3d, Axes3D

class visual_results:

    def show3d_gauss(self,a1,a2,fa,eps,type):
        x=a2
        y=a1
        d=fa

        rbf = Rbf(x, y, d, function=type,epsilon=int(eps))
        xnew, ynew = np.mgrid[-90:90:100j,-45:45:100j]
        fnew = rbf(xnew, ynew)

        fig = plt.figure()
        ax = Axes3D(fig)
        cset = ax.contour(xnew, ynew, fnew, 256, extend3d=True)
        plt.savefig('image.jpg')
        plt.show()

    def show2d_quad(self,a,fa):
        x=a
        y=fa
        z = np.polyfit(x, y, 2)
        xi = np.linspace(-80,80,100)
        plt.plot(x, y, 'bo')
      #  plt.plot(xi, fi, 'r')
        coefs = poly.polyfit(x, y, 2)
        ffit = poly.polyval(xi, coefs)
        plt.plot(xi, ffit)
        plt.show()
