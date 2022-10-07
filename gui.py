from tkinter import *


class Draw:
    def __init__(self, x0, y0, p, x, y, xn, yn):
        self.x0 = x0
        self.y0 = y0
        self.p = p
        self.x = x
        self.y = y
        self.xn = xn
        self.yn = yn
        self.scale = 100    # масштаб

        self.root = Tk()
        self.root.title('Выверка главного сечения отражающей поверхности антенны')

        # размеры окна
        w = 840
        h = 620
        # координаты центра экрана
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        X = (sw - w) / 2
        Y = (sh - h) / 2 - 20
        self.root.geometry('%dx%d+%d+%d' % (w, h, X, Y))  # размеры окна
        self.root.resizable(width=False, height=False)  # нельзя менять размеры окна

        self.canvas = Canvas(width=840, height=620, background="white")
        self.canvas.pack()

    # отслеживает координаты курсора мыши по нажатию ЛКМ
    def move_start(self, event):
        self.canvas.scan_mark(event.x, event.y)

    # перемещение с помощью ЛКМ
    def move_move(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=2)

    # масштабирование с помощью колёсика мыши
    def zoomer(self, event):
        if event.delta > 0:
            self.canvas.scale("all", event.x, event.y, 1.1, 1.1)
        elif event.delta < 0:
            self.canvas.scale("all", event.x, event.y, 0.9, 0.9)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    # функция для отображения параболы, её элементов и работы функций навигации в пользовательском окне
    def draw_parabola(self):
        x0 = self.x0 * self.scale
        y0 = self.y0 * self.scale
        p = self.p * self.scale
        i = min(self.y) - 1
        set_x = []
        set_y = []

        while (min(self.y) - 2) < i < (max(self.y) + 1):
            y = i * self.scale
            x = round(x0 + ((y - y0) ** 2) / (2 * p), 4)
            set_x.append(x)
            set_y.append(y)
            i += 0.1

        # отрисовывает параболу
        for n in range(len(set_x) - 1):
            self.canvas.create_line(set_x[n], set_y[n], set_x[n + 1], set_y[n + 1], width=3, activefill='purple',
                                    fill='red')

        self.canvas.create_oval(x0, y0, x0, y0, width=10, outline='grey')   # отрисовывает вершину параболы
        self.canvas.create_oval((x0 + p / 2), y0, (x0 + p / 2), y0, width=6, outline='red')    # отрисовывает т. фокуса

        # описание работы мыши
        self.canvas.bind("<ButtonPress-1>", self.move_start)  # отслеживает координаты курсора мыши по нажатию ЛКМ
        self.canvas.bind("<B1-Motion>", self.move_move)  # перемещение с помощью ЛКМ
        self.canvas.bind("<MouseWheel>", self.zoomer)  # масштабирование с помощью колёсика мыши

    # функция для отображения щитов по точкам
    def draw_points(self):
        i = 0
        x = [el * self.scale for el in self.x]
        y = [el * self.scale for el in self.y]
        xn = [el * self.scale for el in self.xn]
        yn = [el * self.scale for el in self.yn]
        while i < len(x):
            self.canvas.create_oval(x[i], y[i], x[i], y[i], width=6, outline='blue')    # отрисовывает юст. винты
            # отрисовывает величину и направление смещения для юстировки
            self.canvas.create_line(x[i], y[i], xn[i], yn[i], width=3, dash=(1, 1), activefill='purple')
            for l in range(len(x) - 1):
                if l % 2 == 0:
                    self.canvas.create_line(x[l], y[l], x[l + 1], y[l + 1], width=3, activefill='purple')   # отрисовывает щиты
            i += 1
