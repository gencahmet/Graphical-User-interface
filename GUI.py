from tkinter import *
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import Tk, Canvas, messagebox
import serial
import math
from scipy.interpolate import make_interp_spline

class GraphDrawer:
    def __init__(self, master):
        # Ana pencere
        self.master = master
        master.title("Copy Cat")
        
        # Çizim alanlarını oluşturma
        self.fig1, self.ax1 = plt.subplots()
        self.ax1.set_xlim(-200, 200)
        self.ax1.set_ylim(-200, 200)
        self.ax1.set_xlabel('X')
        self.ax1.set_ylabel('Y')
        self.ax1.set_xticks(range(-200, 201, 25))  # X eksenini 25 birim aralıklarla böler
        self.ax1.set_yticks(range(-200, 201, 25))  # Y eksenini 25 birim aralıklarla böler
        self.ax1.grid(True)
        self.line1, = self.ax1.plot([], [], '-o', color='blue')
        
        self.fig2, self.ax2 = plt.subplots()
        self.ax2.set_xlim(0, 25)
        self.ax2.set_ylim(14, 26)
        self.ax2.set_xlabel('t')
        self.ax2.set_ylabel('Speed(m/s)')
        self.ax2.set_yticks(range(14, 27, 1))  # Y eksenini 25 birim aralıklarla böler
        self.ax2.grid(True)
        self.line2, = self.ax2.plot([], [], '-o', color='blue')
        
        # Çizim alanlarını Tkinter penceresine yerleştirme
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=master)
        self.canvas1.get_tk_widget().pack(side=LEFT, fill=BOTH, expand=1)
        self.canvas1.mpl_connect('button_press_event', self.on_button_press1)
        #self.canvas1.mpl_connect('motion_notify_event', self.on_mouse_move1)
        #self.canvas1.mpl_connect('button_release_event', self.on_button_release1)
        
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=master)
        self.canvas2.get_tk_widget().pack(side=LEFT, fill=BOTH, expand=1)
        self.canvas2.mpl_connect('button_press_event', self.on_button_press2)
        self.canvas2.mpl_connect('motion_notify_event', self.on_mouse_move2)
        self.canvas2.mpl_connect('button_release_event', self.on_button_release2)
        
        # Yol çizme
        self.draw_button1 = Button(master, text="Draw path 1", command=self.draw_path1)
        self.draw_button1.pack(side=TOP, padx=10, pady=10)

        # Temizle
        self.clear_button1 = Button(master, text="Clear 1", command=self.clear_path1)
        self.clear_button1.pack(side=TOP, padx=10, pady=10)
        
        self.draw_button2 = Button(master, text="Draw path 2", command=self.draw_path2)
        self.draw_button2.pack(side=TOP, padx=10, pady=10)
        
        self.clear_button2 = Button(master, text="Clear 2", command=self.clear_path2)
        self.clear_button2.pack(side=TOP, padx=10, pady=10)

        self.bluetooth_button1 = Button(master, text="Send data", command=self.bluetooth)
        self.bluetooth_button1.pack(side=TOP, padx=10, pady=10)

        # Yol verilerini depolayacak x ve y listeleri
        self.x1 = []
        self.y1 = []
        self.x1new=[]
        self.y1new=[]
        self.x2 = []
        self.y2 = []
        self.angle = []
        self.anglenew =[]
        self.anay2 =[]
        self.dis = []
        
        # Fare işlemleri için kullanılacak değişkenler
        self.is_pressed1 = False
        self.prev_x1 = None
        self.prev_y1 = None
        
        self.is_pressed2 = False
        self.prev_x2 = None
        self.prev_y2 = None
        
    def on_button_press1(self, event):
        # Fare düğmesi basıldığında çağrılır
        x = event.xdata
        y = event.ydata

        if x is None or y is None:
            return

        # Yeni noktayı ekleyin
        self.x1.append(x)
        self.y1.append(y)

        # Noktayı çiz
        self.line1.set_data(self.x1, self.y1)
        self.canvas1.draw()

    def draw_path1(self):
        t = np.linspace(0, 1, len(self.x1))
        t_smooth = np.linspace(0, 1, 100000)

        
        
        # Spline eğrilerini kullanarak smooth birleştirme
        spline_x = make_interp_spline(t, self.x1)
        spline_y = make_interp_spline(t, self.y1)
        x1_smooth = spline_x(t_smooth)
        y1_smooth = spline_y(t_smooth)

        # Yolu toplam uzunluğunu bul
        total_distance = 0.0
        for i in range(len(x1_smooth) - 1):
            distance = math.sqrt((x1_smooth[i + 1] - x1_smooth[i]) ** 2 + (y1_smooth[i + 1] - y1_smooth[i]) ** 2)
            total_distance += distance
        
        target_distance = total_distance/76.0 #100 eşit parçaya böl yani 99 tane nokta olsun.
        self.x1new.append(x1_smooth[0]) #ilk x ve y değerleri kaydet buna göre işlem yapabilmek için 
        self.y1new.append(y1_smooth[0])
        
        current_distance = 0
        
        for i in range(len(x1_smooth) - 1):
            distance = math.sqrt((x1_smooth[i + 1] - x1_smooth[i]) ** 2 + (y1_smooth[i + 1] - y1_smooth[i]) ** 2)
            if current_distance + distance >= target_distance:#target adrese ulaşınca o adresteki x ve y yi kaydet
                new_x = x1_smooth[i] 
                new_y = y1_smooth[i] 
                self.x1new.append(new_x)
                self.y1new.append(new_y)
                current_distance=0
                
            else: # target addrese ulaşmadıysa current distancı arttır.
                current_distance += distance

        

        self.ax1.plot(self.x1new, self.y1new, '-o', color='red')
        
        
        print("x değerleri:", self.x1new)
        print("y değerleri:", self.y1new)

        for i in range(len(self.x1new) - 1):
            distance = math.sqrt((self.x1new[i + 1] - self.x1new[i]) ** 2 + (self.y1new[i + 1] - self.y1new[i]) ** 2)
            
        self.dis.append(round(distance,1))
        print("dis: ", self.dis)
        print("length: ",len(self.dis))

        #self.angle.append(0)
        for i in range(len(self.x1new) - 1):
            angle = math.atan2((self.x1new[i + 1] - self.x1new[i]), (self.y1new[i + 1] - self.y1new[i]))
            angle = math.degrees(angle)
            self.angle.append(round(angle, 2))
        print("self angle: ", self.angle)
        self.anglenew.append(0)
        for i in range(len(self.angle) - 1):
            angle = self.angle[i+1]- self.angle[i]
            self.anglenew.append(round(angle,1))
        print("angle: ",self.anglenew)
        print("dis angle: ",len(self.anglenew))
        #print("distance: ", self.dis)
        #print("angle değerleri:", self.anglenew)
        #print("angle uzunluk:", len(self.anglenew) ) #49 deger var 
        #print("distance uzunluk:",len(self.dis)) #49 deger var
        #print("distance: ", self.dis) 
        #print("target distance: ",target_distance)
        print("total dis: ", total_distance)
        self.fig1.canvas.draw() 
    
    




    def clear_path1(self):
            # x ve y değerlerini sıfırlama
            self.x1 = []
            self.y1 = []
            self.x1new = []
            self.y1new = []
            x1_smooth =[]
            y1_smooth =[]
            self.dis = []
            self.angle = []
            self.anglenew =[]
            # Çizim alanındaki yol silme
            self.ax1.lines[-1].remove()
            self.fig1.canvas.draw() 

    
    def on_button_press2(self, event):
    # Fare düğmesi basıldığında çağrılır
        self.is_pressed2 = True
        self.prev_x2 = event.xdata
        self.prev_y2 = event.ydata
    
    def on_button_release2(self, event):
    # Fare düğmesi bırakıldığında çağrılır
        self.is_pressed2 = False
    
    def on_mouse_move2(self, event):
    # Fare hareket ettiğinde çağrılır
        if not self.is_pressed2:
            return
    
        if self.prev_x2 is None:
            self.prev_x2 = event.xdata
            self.prev_y2 = event.ydata
            return
    
        x = event.xdata
        y = event.ydata
    
        if x is None or y is None:
            return
        step_size = 10  # her eksen için 10 birim artıracağız
        new_x = np.linspace(self.prev_x2, x, step_size)
        new_y = np.linspace(self.prev_y2, y, step_size)

        self.x2.extend(new_x)
        self.y2.extend(new_y)
        #self.x2.append(x)
        #self.y2.append(y)
        
        #self.x2 = [int(round(num)) for num in self.x2]
        #self.y2 = [int(round(num)) for num in self.y2]
        

        self.line2.set_data(self.x2, self.y2)
        self.canvas2.draw()
    
        self.prev_x2 = x
        self.prev_y2 = y
    
    def draw_path2(self):
        # Yolu n adet parçaya ayırma
        n = 75
        x2_interp = np.interp(np.linspace(0, len(self.x2)-1, n), np.arange(len(self.x2)), self.x2)
        y2_interp = np.interp(np.linspace(0, len(self.y2)-1, n), np.arange(len(self.y2)), self.y2)

        # x ve y değerlerini kaydetme
        self.x2 = x2_interp.tolist()
        self.y2 = y2_interp.tolist()
        self.x2 = [round(num,2) for num in self.x2]
        self.y2 = [round(num,0) for num in self.y2]

        

        
        
         # Çizim alanına yol ekleme
        self.ax2.plot(self.x2, self.y2, '-o', color='red')
        #print("x değerleri:", self.x2)
        print("speed:", self.y2)
        print("speed:", len(self.y2))
        #print("speed length: ", len(self.y2))
        
        

        self.fig2.canvas.draw()

    # Yol çizme butonuna basıldığında çağ
    def clear_path2(self):
        # x ve y değerlerini sıfırlama
        self.x2 = []
        self.y2 = []
        self.anay2 =[]
    # Çizim alanındaki yol silme
        self.ax2.lines[-1].remove()
        self.fig2.canvas.draw() 
    
    def bluetooth(self):
        # HC-05 modülüne bağlanmak için seri port ayarları,,self.dis
        data_str = ",".join([str(i) for sublist in [self.anglenew, self.y2,self.dis] for i in sublist]) #147 elemanlı 49 açı 49 distance, 49 hız analog degerleri 99 distance.
        print("angle: ",self.anglenew)
        print("distance: ",self.dis)
        print("speed: ",self.y2)

        print("data: ", data_str)
        ser = serial.Serial('COM10', 9600) # Burada 'com3' yerine kullanmakta olduğunuz seri portu belirtmelisiniz.
         # 2 adet listeyi tek bir liste haline getirip virgülle ayrılmış bir stringe dönüştürme
        
        ser.write(data_str.encode())
        ser.flush() # verinin gönderilmesini bekler
        #data_str = ",".join([str(i) for i in self.x1])
        #ser.write(data_str.encode())
        #ser.flush() # verinin gönderilmesini bekler
        
        # Seri port bağlantısını kapat
        ser.close()



root = Tk()
drawer = GraphDrawer(root)





root.mainloop()

