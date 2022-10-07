from random import *
import openpyxl


class Data:
    def __init__(self):
        # координаты вершины параболы
        self.x0 = 10
        self.y0 = 20
        self.p = 15  # параметр параболы
        self.count_shield = 8  # кол-во щитов с одной стороны
        self.size_shield = 2  # размер щита в метрах

    def points_shields(self):
        set_x = []
        set_y = []

        for i in range(self.count_shield * 4):
            if i != 0 and i != 16:
                if i % 2 != 0:
                    y = round(set_y[-1] + 2, 4)    # размер щита
                else:
                    y = round(set_y[-1] + 0.01, 4)  # расстояние между щитами
            elif i == 0:
                y = round(self.y0 - 1 - self.count_shield * self.size_shield, 4)
            else:  # i = 16
                y = round(self.y0 + 1)

            x = round(self.x0 + ((y - self.y0) ** 2) / (2 * self.p), 4)
            set_x.append(x)
            set_y.append(y)
        return set_x, set_y

    def deformation(self):
        points = self.points_shields()
        x = points[0]
        y = points[1]

        # искажение с СКО 0.01 м по нормальному закону
        x = [round(normalvariate(x, 0.01), 4) for x in x]
        y = [round(normalvariate(y, 0.01), 4) for y in y]

        # Вывод искажённых данных на лист Excel в файл data
        wb = openpyxl.load_workbook('data.xlsx')
        sheet = wb['Лист1']
        sheet['A1'].value = 'X'
        sheet['B1'].value = 'Y'
        sheet['C1'].value = 'P'
        sheet['C2'].value = self.p

        i = 2
        for elx in x:
            sheet[f'A{i}'].value = elx
            i += 1

        i = 2
        for ely in y:
            sheet[f'B{i}'].value = ely
            i += 1

        wb.save('data.xlsx')
        return x, y


a = Data()
print(a.points_shields())
print(a.deformation())
print(a.p)
