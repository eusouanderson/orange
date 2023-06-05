import tkinter
from tkinter import *
from psutil import cpu_freq, cpu_count, Process, pids, process_iter
from clean import clean
from theme import *
from PIL import ImageTk, Image
import matplotlib.pyplot as plt
import numpy as np
import os

path = os.getcwd()


class Software:
    def __init__(self):
        self.ws = Tk()

        self.numero_cpu = cpu_count()
        self.frequencia_cpu = cpu_freq().current
        self.todosProcessos = pids()
        self.processos = Process()
        self.color, self.colorL, self.colorB, self.imagem = self.theme()

        'self.ws.wm_iconphoto(True)'
        self.ws.config(bg=self.colorL)
        self.ws.title('Orange')

        width = self.ws.winfo_screenwidth()
        height = self.ws.winfo_screenheight()
        self.ws.geometry('%dx%d' % (width, height))
        self.ws.overrideredirect(False)
        self.ws.wm_overrideredirect(False)
        #self.ws.attributes('-transparentcolor', 'blue', '-alpha', 5)

        """Menubar"""
        self.menubar = Menu(self.ws)
        self.ws.config(menu=self.menubar)

        file_menu = Menu(self.menubar, tearoff=False)
        help_menu = Menu(self.menubar, tearoff=False)

        file_menu.add_command(label='Novo', command='')
        file_menu.add_command(label='Abrir', command='')
        file_menu.add_command(label='Iniciar', command='')
        file_menu.add_command(label='Salvar', command='')
        file_menu.add_command(label='PrintScreen', command='')
        file_menu.add_separator()

        file_menu.add_command(
            label='Sair',
            command=self.ws.destroy,
        )

        self.menubar.add_cascade(label='Arquivo', menu=file_menu, command='')
        self.menubar.add_cascade(label='Temas', menu=help_menu, command='')
        self.img1 = Label(self.ws, bg=self.color)
        self.img1.pack()

        self.widget = Frame(self.ws)
        self.widget.pack(side='bottom')

        self.bto1 = Button(
            self.widget,
            bg=self.colorB,
            activebackground=self.color,
            bd=1,
            borderwidth=4,
            width=10,
            fg=self.colorL,
        )
        self.bto1['text'] = 'Investigate'
        self.bto1['command'] = self.scanner
        self.bto1.grid(row=6, column=0)


        self.bto2 = Button(
            self.widget,
            bg=self.colorB,
            activebackground=self.color,
            bd=1,
            borderwidth=4,
            width=10,
            fg=self.colorL,
        )
        self.bto2['text'] = 'Grafico'
        self.bto2['command'] = self.graphic
        self.bto2.grid(row=6, column=1)

        self.bto3 = Button(
            self.widget,
            bg=self.colorB,
            activebackground=self.color,
            bd=1,
            borderwidth=4,
            width=10,
            fg=self.colorL,
        )
        self.bto3['text'] = 'Otmizar'
        self.bto3['command'] = clean
        self.bto3.grid(row=6, column=2)

        self.bto4 = Button(
            self.widget,
            bg=self.colorB,
            activebackground=self.color,
            bd=1,
            borderwidth=4,
            width=10,
            fg=self.colorL,
        )
        self.bto4['text'] = 'FPS'
        self.bto4['command'] = self.fps
        self.bto4.grid(row=6, column=3)

        self.bto5 = Button(
            self.widget,
            bg=self.colorB,
            activebackground=self.color,
            bd=1,
            borderwidth=4,
            width=10,
            fg=self.colorL,
        )
        self.bto5['text'] = 'Net Control'
        self.bto5['command'] = ''
        self.bto5.grid(row=6, column=4)

        self.bto6 = Button(
            self.widget,
            bg=self.colorB,
            activebackground=self.color,
            bd=1,
            borderwidth=4,
            width=10,
            fg=self.colorL,
        )
        self.bto6['text'] = 'Ping'
        self.bto6['command'] = self.ws.update()
        self.bto6.grid(row=6, column=5)

        self.bto7 = Button(
            self.widget,

            bg=self.colorB,
            activebackground=self.color,
            bd=1,
            borderwidth=4,
            width=5,
            fg=self.colorL,
            command=self.theme,

        )
        self.bto7['text'] = 'Theme'
        self.bto7.grid(row=6, column=6)

        self.image = Image.open(self.image)
        self.image = self.image.resize((width- 1500, height-500))
        self.image_tk = ImageTk.PhotoImage(self.image)

        label_image = tkinter.Label(self.ws, image=self.image_tk)

        label_image.pack()

        self.ws.update()
        self.ws.mainloop()

    def scanner(self):
        self.msg = Label(self.ws, bg=self.color, background=self.color)
        self.msg['text'] = 'Numero de Processadores'
        self.msg['font'] = font
        self.msg.place(x=20, y=60)

        self.msg = Label(self.ws, bg=self.colorL, background=self.color)
        self.msg['text'] = 'Frequencia do Processador'
        self.msg['font'] = font
        self.msg.place(x=20, y=100)

        self.msg = Label(self.ws, bg=self.color, background=self.color)
        self.msg['text'] = 'Processos abertos'
        self.msg['font'] = font
        self.msg.place(x=20, y=140)
        self.processos.parent()
        self.processos = len(self.todosProcessos)
        self.msg = Label(self.ws, text=self.numero_cpu, bg=self.color)
        self.msg['font'] = ('BungeeSpice Regular', '10', 'italic')
        self.msg.place(x=40, y=80)
        self.msg = Label(self.ws, text=self.frequencia_cpu, bg=self.color)
        self.msg['font'] = ('BungeeSpice Regular', '10', 'italic')
        self.msg.place(x=40, y=120)
        self.msg = Label(self.ws, text=self.processos, bg=self.color)
        self.msg['font'] = ('BungeeSpice Regular', '10', 'italic')
        self.msg.place(x=40, y=160)
        self.ws.update()

    def graphic(self):
        np.random.seed(19680801)

        dt = 0.01
        t = np.arange(0, 10, dt)
        nse = np.random.randn(len(t))
        r = np.exp(-t / 0.05)

        cnse = np.convolve(nse, r) * dt
        cnse = cnse[: len(t)]
        s = 0.1 * np.sin(2 * np.pi * t) + cnse

        fig, (ax0, ax1) = plt.subplots(2, 1)
        ax0.plot(t, s)
        ax1.psd(s, 512, 1 / dt)

        plt.show()

        return self.ws

    def fps(self):
        self.ws2 = Tk()
        width = 50
        height = 50
        self.ws2.geometry('%dx%d' % (width, height))
        self.ws2.overrideredirect(False)
        self.icon = PhotoImage(master=self.ws2, file='Screenshots/orange.png')
        self.ws2.mainloop()

    def theme(self):
        color = [orcolor, vicolor, rubcolor, redcolor, brcolor]
        BG = ['../src/BG/1.jpg', '../src/BG/2.jpg', '../src/BG/3.jpg', '../src/BG/4.jpg', '../src/BG/5.jpg']
        backcolor = color[randint(0, 4)]
        print(backcolor)
        self.image = BG[randint(0, 4)]
        self.colorB = brcolor
        self.colorL = backcolor
        self.color = brcolor
        self.ws.config(bg=self.colorL)
        self.ws.update()
        return self.color, self.colorL, self.colorB, self.image


def font(model=0, value=0):
    font = dict()
    font['Model'] = (
        ['Calibri'],
        ['Arial'],
        ['Courier New'],
        ['Times New Roman'],
    )
    font['Size'] = [10], [18], [15], [25]
    for f in font:
        fmodel = font['Model'][model]
        fsize = font['Size'][value]

    return fmodel, fsize


font = font(0, 0)

if __name__ == '__main__':
    App = Software()
