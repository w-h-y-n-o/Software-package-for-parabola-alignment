import math
import numpy as np
from openpyxl import load_workbook
from gui import Draw
import time
from pyautocad import Autocad
from pyautocad import APoint

start_time = time.time()    # начало отсчёта времени

# Ввод данных с листа экселя
wb = load_workbook(f'./data.xlsx')
sheet = wb['Лист1']
x = []
y = []
p = 1   # значение по умолчанию, если не задано
value_x = sheet['A2'].value
value_y = sheet['B2'].value

i = 3
while type(value_x) is float:
    x.append(value_x)
    value_x = sheet[f'A{i}'].value
    y.append(value_y)
    value_y = sheet[f'B{i}'].value
    i += 1

if type(sheet['C2'].value) is float or type(sheet['C2'].value) is int:
    p = sheet['C2'].value

# исходные данные, где n - кол-во точек
n = len(x)
count_ust = 0   # для подсчёта кол-ва итераций перемещений щитов
count_search = 0    # для подсчёта кол-ва итераций поискового метода

# предварительные значения координат вершины параболы
x0 = 0
y0 = 0

# сохранение первоначальных координат для работы функции ust()
origin_x = x
origin_y = y


def count_after_decimal_point(number):  # Функция, которая возвращает кол-во цифр в числе после запятой
    number = str(number)
    point = number.find('.')
    quantity = len(number) - (point + 1)
    point_0 = number.find('.0')
    if quantity > 1 and point != -1:  # обработка варианта 0.01
        return quantity
    elif point_0 == (-1):  # обработка варианта 0.1
        return quantity
    else:
        return 0  # вариант 0.0


accuracy = count_after_decimal_point(x[0])  # вызов count_after_decimal_point() для определения точности исходных данных


# функция для вычисления значений целевой функции в каждой точке, т.е. отклонений от параболы
def delta(x0, y0, x, y):
    d = []
    for i in range(n):
        di = ((((y[i] - y0) ** 2) / (2 * p)) - (x[i] - x0))
        d.append(di)
    return d


def summa_d(x0, y0, x, y):  # функция для вычисления суммы значений целевой функции
    s = 0
    for i in range(n):
        s += ((((y[i] - y0) ** 2) / (2 * p)) - (x[i] - x0)) ** 2
    print(s)
    return s


# функция, которая возвращает половину угла между прямой, параллельной оси X и проведённой к данной точке,
# и прямой, проходящей через данную точку и фокус (направление биссектрисы этого угла)
def angle(x, y, x0, y0):
    angle = []
    # координаты фокуса
    xf = x0 + p / 2
    yf = y0

    for i in range(n):
        if x[i] != xf:
            # только для точек, которые левее фокуса
            angle.append(math.degrees(np.arctan(((y[i] - yf) / (x[i] - xf)))) / 2)
            # случай, когда точка правее фокуса
            if x[i] > xf:
                if y[i] < yf:
                    angle[i] += 90
                elif y[i] > yf:
                    angle[i] -= 90
        # критический случай xi = xf
        else:
            if y[i] < yf:
                angle[i] = 45
            elif y[i] > yf:
                angle[i] = -45
    return angle


def pgz(x0, y0, x, y):  # Решает прямую геодезическую задачу и возвращает исправленные координаты винта
    xn = []
    yn = []
    d = delta(x0, y0, x, y)  # вызов функции delta() для вычисления величин отклонений
    fi = angle(x, y, x0, y0)  # вызов функции angle() для определения угла смещения винтов
    for i in range(n):
        dx = (d[i] * math.cos(math.radians(fi[i])))
        dy = (d[i] * math.sin(math.radians(fi[i])))
        xn.append(round(x[i] + dx / 2, accuracy))
        yn.append(round(y[i] + dy / 2, accuracy))
    return xn, yn, x, y  # x и y возвращаются только для корректной работы графического интерфейса


def direction_and_step(x0, y0, x, y, step_x, step_y, a):
    # Поиск направления минимума по оси X
    while True:
        # Пробный шаг
        xn0 = x0 + step_x
        if summa_d(xn0, y0, x, y) < summa_d(x0, y0, x, y):
            x0 = xn0
            dirx = 1
            break

        xn0 = x0 - step_x
        if summa_d(xn0, y0, x, y) < summa_d(x0, y0, x, y):
            x0 = xn0
            dirx = 0
            break

        # шаг слишком большой, поэтому нужно его уменьшить и повторить цикл
        step_x = step_x * a

    # Поиск направления минимума по оси Y
    while True:
        # Пробный шаг
        yn0 = y0 + step_y
        if summa_d(x0, yn0, x, y) < summa_d(x0, y0, x, y):
            y0 = yn0
            diry = 1
            break

        yn0 = y0 - step_y
        if summa_d(x0, yn0, x, y) < summa_d(x0, y0, x, y):
            y0 = yn0
            diry = 0
            break

        # шаг слишком большой, поэтому нужно его уменьшить и повторить цикл
        step_y = step_y * a

    return dirx, diry, step_x, step_y


# Функция, реализующая поисковый метод оптимизации и находящая вершину параболы
def search(x0, y0, x, y):
    # подсчёт кол-ва итераций перемещения щитов
    global count_ust
    count_ust += 1

    # начальные значения
    xn0 = x0
    yn0 = y0

    # начальный шаг
    if count_ust == 1:  # большой шаг для первой итерации
        step_x = 0.1
        step_y = 0.1
        a = 0.5  # коэффициент для переменного шага
    else:
        step_x = 0.0001
        step_y = 0.0001
        a = 0.5

    while True:
        # критерий остановки итерационного процесса
        if (abs(summa_d(xn0, yn0, x, y) - summa_d(x0, y0, x, y)) < (10 ** (-4))) and (
                summa_d(xn0, yn0, x, y) - summa_d(x0, y0, x, y) != 0):
            break

        global count_search    # подсчёт кол-ва итераций поискового метода
        count_search += 1

        for_search = direction_and_step(xn0, yn0, x, y, step_x, step_y, a)
        dirx = for_search[0]    # направление по оси Х
        diry = for_search[1]    # направление по оси Y
        step_x = for_search[2]  # шаг по оси Х
        step_y = for_search[3]  # шаг по оси Y

        # перемещение по оси X
        if dirx == 0:
            xn0 = x0 - step_x
            if summa_d(xn0, y0, x, y) < summa_d(x0, y0, x, y):
                x0 = xn0
                xn0 -= step_x
            else:
                continue
        elif dirx == 1:
            xn0 = x0 + step_x
            if summa_d(xn0, y0, x, y) < summa_d(x0, y0, x, y):
                x0 = xn0
                xn0 += step_x
            else:
                continue

        # перемещение по оси Y
        if diry == 0:
            yn0 = y0 - step_y
            if summa_d(x0, yn0, x, y) < summa_d(x0, y0, x, y):
                y0 = yn0
                yn0 -= step_y
            else:
                continue
        elif diry == 1:
            yn0 = y0 + step_y
            if summa_d(x0, yn0, x, y) < summa_d(x0, y0, x, y):
                y0 = yn0
                yn0 += step_y
            else:
                continue

    # округление новых координат вершины параболы до нужной точности
    x0 = round(x0, accuracy)
    y0 = round(y0, accuracy)
    return x0, y0


# определение первоначального СКО для запуска итерационного процесса
m = round(((summa_d(x0, y0, x, y) / (n - 2)) ** (1 / 2)), accuracy)  # (n - 2) - кол-во избыточных измерений

# цикл для итерационного процесс оптимизации
while m > 0.0005:
    # вызов функции search() для нахождения координат вершины параболы поисковым методом
    center_search = search(x0, y0, x, y)
    x0 = center_search[0]
    y0 = center_search[1]

    # вызов функции pgz() для определения исправленных координат винтов
    corr_coord = pgz(x0, y0, x, y)
    x = corr_coord[0]
    y = corr_coord[1]

    # определение общей СКО аппроксимации параболы
    m = round(((summa_d(x0, y0, x, y) / (n - 2)) ** (1 / 2)), accuracy)

    # запуск графического интерфейса на каждой итерации
    parabola = Draw(x0, y0, p, corr_coord[2], corr_coord[3], x, y)
    parabola.draw_parabola()
    parabola.draw_points()
    parabola.root.mainloop()

# запуск графического интерфейса для отображения параболы после юстировки
parabola = Draw(x0, y0, p, x, y, x, y)
parabola.draw_parabola()
parabola.draw_points()
parabola.root.mainloop()


# функция для определения величины юстировки каждого винта, "+" - в сторону фокуса (выкручивать),
# "-" - от фокуса (закручивать)
def ust(origin_x, origin_y, x, y):
    set_move = []
    dir_move = delta(x0, y0, origin_x, origin_y)  # для определения направления юстировки
    for i in range(n):
        move = (round(((x[i] - origin_x[i]) ** 2 + (y[i] - origin_y[i]) ** 2) ** (1 / 2), accuracy))
        if dir_move[i] < 0:
            set_move.append(move * (-1))
        else:
            set_move.append(move)
    return set_move


# функция для вывода координат винтов и вершины параболы в AutoCAD
def autocad(x0, y0, x, y):
    acad = Autocad()

    # отрисовка вершины параболы
    point_0 = APoint(x0, y0)
    acad.model.AddCircle(point_0, 0.2)

    # отрисовка координат винтов
    for i in range(n):
        point = APoint(x[i], y[i])
        acad.model.AddCircle(point, 0.1)

    # сохранение файла .dwg
    acad.doc.SaveAs("{0}".format("F:/Python/py/Парабола.dwg"), 64)


autocad(x0, y0, x, y)
move = ust(origin_x, origin_y, x, y)    # запуск функции ust() для определения величин юстировки

print('Координаты вершины параболы:', 'x0 =', f'{x0}', 'м,', 'y0 =', f'{y0}', 'м')
for i in range(n):
    if move[i] < 0:
        print(f'Исправленные координаты винта {i + 1}:', 'x =', f'{x[i]}', 'м,', 'y =', f'{y[i]}', 'м',
              "| Величина юстировки: -", move[i] * (-1), 'м')
    else:
        print(f'Исправленные координаты винта {i + 1}:', 'x =', f'{x[i]}', 'м,', 'y =', f'{y[i]}', 'м',
              '| Величина юстировки: +', move[i], 'м')
print('Общее СКО =', m, 'м')
print('Кол-во итераций перемещения винтов =', count_ust)
print('Кол-во итераций поискового метода =', count_search)
print('Время выполнения программы:', round(time.time() - start_time, 0), 'с')
