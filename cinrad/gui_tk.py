# -*- coding: utf-8 -*-
# Author: Puyuan Du

from cinrad import io
from cinrad.visualize.ppi import norm_plot, cmap_plot
from cinrad.visualize.basicfunc import add_shp

import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
plt.style.use('dark_background')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import cartopy.crs as ccrs

class RadarGUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        #self.geometry('860x770')
        self.title('CINRAD Radar Display')
        self.menu = tk.Menu()
        self.__menu()
        self.frame_info = tk.Frame(self)
        self.frame_button = tk.Frame(self)
        self.frame_pic = tk.Frame(self)
        self.frame_pic.grid(column=5, rowspan=16, sticky=tk.N+tk.E+tk.W)
        # Test config
        self.dtype = 'REF'
        self.drange = 230

    def __open(self):
        if hasattr(self, 'cinrad'):
            return
        fp = filedialog.askopenfilename()
        # TODO: Auto detect file type
        try:
            self.cinrad = io.CinradReader(fp)
        except Exception:
            try:
                self.cinrad = io.StandardData(fp)
            except Exception:
                self.cinrad = io.NexradL2Data(fp)
        button = self.frame_button
        button.grid(row=0, rowspan=15, columnspan=5)
        self.frame_info.geoinfo = tk.Label(self.frame_info, text='站名: {}\n扫描时间: {}'.format(self.cinrad.name, self.cinrad.timestr))
        self.frame_info.radius = tk.Entry(self.frame_info, textvariable=tk.StringVar(self, '230'))
        self.frame_info.grid(row=15, rowspan=5, columnspan=5, sticky=tk.N)
        self.frame_info.geoinfo.grid(row=19, rowspan=5, columnspan=5, sticky=tk.N)
        self.frame_info.radius_text = tk.Label(self.frame_info, text='绘图半径')
        self.frame_info.update_button = tk.Button(self.frame_info, text='更新', command=self.__get_radius)
        self.frame_info.update_button.grid(row=17, columnspan=1, column=2)
        self.frame_info.radius_text.grid(row=15, columnspan=5)
        self.frame_info.radius.grid(row=16, columnspan=5)
        self.button_list = list()
        for index, var in enumerate(self.cinrad.el):
            b = tk.Button(button, text='Tilt {}: {:.2f}'.format(index, var), command=lambda x=index: self.__draw(x))
            b.grid(row=index, columnspan=5, sticky=tk.N)
            self.button_list.append(b)

    def __get_radius(self):
        self.drange = float(self.frame_info.radius.get())

    def __reset_button(self):
        self.frame_button.destroy()
        self.frame_button = tk.Frame(self)

    def __reset_pic(self):
        self.frame_pic.destroy()
        self.frame_pic = tk.Frame(self)
        self.frame_pic.grid(column=5, rowspan=16, sticky=tk.N+tk.E+tk.W)

    def __reset_text(self):
        self.frame_info.destroy()
        self.frame_info = tk.Frame(self)

    def __close(self):
        if hasattr(self, 'cinrad'):
            del self.cinrad
            self.__reset_button()
            self.__reset_text()
            self.ax.clear()
            self.canvas.draw()

    def __menu(self):
        menu_file = tk.Menu(self.menu, tearoff=0)
        menu_file.add_command(label='打开', command=self.__open)
        menu_file.add_separator()
        menu_file.add_command(label='关闭', command=self.__close)
        menu_config = tk.Menu(self.menu, tearoff=0)
        menu_config.add_command(label='基本反射率', command=lambda x='REF':self.__set_dtype(x))
        menu_config.add_command(label='基本速度', command=lambda x='VEL':self.__set_dtype(x))
        self.menu.add_cascade(label='文件', menu=menu_file)
        self.menu.add_cascade(label='数据', menu=menu_config)
        self.config(menu=self.menu)
    
    def __set_dtype(self, dtype):
        self.dtype = dtype
        print('set dtype complete')

    def __draw(self, tilt):
        for b in self.button_list:
            b['bg'] = 'SystemButtonFace'
        self.button_list[tilt]['bg'] = 'grey'
        print('Call: Tilt {}'.format(tilt))
        print(self.drange)
        data = self.cinrad.get_data(tilt, self.drange, self.dtype)
        if hasattr(self, "canvas"):
            self.ax.clear()
        else:
            fig = plt.figure(figsize=(7, 7), dpi=100)
            self.ax = plt.axes(projection=ccrs.PlateCarree())
            self.canvas = FigureCanvasTkAgg(fig, master=self.frame_pic)
            self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
            self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
            toolbar = NavigationToolbar2Tk(self.canvas, self.frame_pic)
            toolbar.update()
        self.ax.background_patch.set_fill(False)
        if not isinstance(data.data, (tuple, list)):
            self.ax.pcolormesh(data.lon, data.lat, data.data, cmap=cmap_plot[data.dtype], norm=norm_plot[data.dtype])
        else:
            self.ax.pcolormesh(data.lon, data.lat, data.data[0], cmap=cmap_plot[data.dtype], norm=norm_plot[data.dtype])
            self.ax.pcolormesh(data.lon, data.lat, data.data[1], cmap=cmap_plot['RF'], norm=norm_plot['RF'])
        add_shp(self.ax)
        self.canvas.draw()

    def exit(self):
        del self.cinrad
        self.quit()
        self.destroy()

app = RadarGUI()
app.mainloop()