import random
from tkinter import *
from psutil import cpu_freq, cpu_count, Process, pids, process_iter
import matplotlib.pyplot as plt
import numpy as np
from clean import clean
from theme import theme, brcolor, darkcolor


class Software:
    def __init__(self):
        self.numero_cpu = cpu_count()
        self.frequencia_cpu = cpu_freq().current
        self.todosProcessos = pids()
        self.processos = Process()
        self.colorL = brcolor
        self.colorB = darkcolor

        self.color = theme()
        self.ws = Tk()
        self.ws.title('Orange')

        width = self.ws.winfo_screenwidth() - 500
        height = self.ws.winfo_screenheight() - 100
        self.ws.geometry('%dx%d' % (width, height))
        self.ws.overrideredirect(False)
        "self.ws.attributes('-transparentcolor', 'blue', '-alpha', 5)"

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

        'self.ws.wm_iconphoto(True)'
        self.ws.config(bg=self.color)
        self.ws.update()

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
        self.bto1.grid(row=0, column=0)

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
        self.bto2.grid(row=0, column=1)

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
        self.bto3.grid(row=0, column=2)

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
        self.bto4.grid(row=0, column=3)

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
        self.bto5.grid(row=0, column=4)

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
        self.bto6.grid(row=0, column=5)

        self.bto7 = Button(
            self.widget,
            bg=self.colorB,
            activebackground=self.color,
            bd=1,
            borderwidth=4,
            width=10,
            fg=self.colorL,
        )
        self.bto7['text'] = 'Theme'
        self.bto7['command'] = theme

        self.bto7.grid(row=0, column=6)

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
