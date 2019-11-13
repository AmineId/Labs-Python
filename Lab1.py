####################
###### Author ######
# ---# Amine_ID #---#
####################

import pandas as pd
import numpy as np
import csv


# Class & Fct definer
class Date:
    def __init__(self, Day='', Month='', Year='', Hour='', Minutes=''):
        self.day = Day
        self.month = Month
        self.year = Year
        self.hour = Hour
        self.min = Minutes

    # Vous permet a l'aide d'une chaine de caracteres sous format 'dd/mm/yyyy HH:MM'
    # d'instancier un objet Date
    def auto_processing(self, date_string: str):

        tmp = ''
        date_string = str(date_string)

        output = []
        for t in range(0, date_string.find('/')):
            output.append(date_string[t])

        self.day = ''.join(output)

        for t in range(date_string.find('/') + 1, len(date_string)):
            tmp = tmp + date_string[t]

        date_string = tmp
        tmp = ''

        output = []
        for t in range(0, date_string.find('/')):
            output.append(date_string[t])

        self.month = ''.join(output)

        for t in range(date_string.find('/') + 1, len(date_string)):
            tmp = tmp + date_string[t]

        date_string = tmp
        tmp = ''

        output = []

        for t in range(0, date_string.find(' ')):
            output.append(date_string[t])

        self.year = ''.join(output)

        for t in range(date_string.find(' ') + 1, len(date_string)):
            tmp = tmp + date_string[t]

        date_string = tmp
        tmp = ''

        output = []

        for t in range(0, date_string.find(':')):
            output.append(date_string[t])

        self.hour = ''.join(output)

        for t in range(date_string.find(':') + 1, len(date_string)):
            tmp = tmp + date_string[t]

        date_string = tmp
        tmp = ''

        self.min = date_string

    def reverse_processing(self):
        return str(self.day + '/' + self.month + '/' + self.year + ' ' + self.hour + ':' + self.min)


class Intersection_State:
    def __init__(self, IsIntersection=False, A1=.0, b1=.0, A2=.0, b2=.0):
        self.IsIntersection = IsIntersection
        self.A1 = A1
        self.A2 = A2
        self.b1 = b1
        self.b2 = b2


class Line_Formula:
    def __init__(self, A, b):
        self.A = A
        self.b = b


class Point:
    def __init__(self, id_=None, date=None, x_=.0, y_=.0):
        self.id = id_
        self.date = date
        self.x = x_
        self.y = y_


def Line2Formula(seg_p1: Point, seg_p2: Point):
    try:
        A = float(seg_p1.y - seg_p2.y) / float(seg_p1.x - seg_p2.x)
    except ZeroDivisionError:
        A = None

    if A is None:
        b = 0
    else:
        b = float(seg_p1.y - A * seg_p1.x)

    return Line_Formula(A, b)


def Date_Interpolate(Pt1: Point, Pt2: Point, Pt3: Point):
    Date1 = Date()
    Date2 = Date()
    Date3 = Date()

    Date1.auto_processing(Pt1.date)
    Date2.auto_processing(Pt2.date)

    vect1 = [Pt1.x, Pt3.x, Pt2.x]

    if Date1.year == Date2.year:
        if Date1.month == Date2.month:
            if Date1.day == Date2.day:
                if Date1.hour == Date2.hour:
                    if Date1.min == Date2.min:
                        print('Interpolation 0. similarities')
                    else:
                        sr = pd.Series([Date1.min, np.nan, Date2.min], index=vect1)
                        value = int(sr.astype('float').interpolate(method='index').values[1])
                        Date3 = Date(Day=Date1.day,
                                     Month=Date1.month,
                                     Year=Date1.year,
                                     Hour=Date1.hour,
                                     Minutes='{:02d}'.format(value))
                else:
                    sr = pd.Series([int(Date1.hour) * 60 + int(Date1.min),
                                    np.nan,
                                    int(Date2.hour) * 60 + int(Date2.min)], index=vect1)
                    value = int(sr.astype('float').interpolate(method='index').values[1])
                    Date3 = Date(Day=Date1.day,
                                 Month=Date1.month,
                                 Year=Date1.year,
                                 Hour='{:02d}'.format(int(value / 60)),
                                 Minutes='{:02d}'.format(value % 60))
            else:
                sr = pd.Series([(int(Date1.day) * 24 + int(Date1.hour)) * 60 + int(Date1.min),
                                np.nan,
                                (int(Date2.day) * 24 + int(Date2.hour)) * 60 + int(Date2.min)], index=vect1)
                value = int(sr.astype('float').interpolate(method='index').values[1])
                Date3 = Date(Month=Date1.month,
                             Year=Date1.year,
                             Day='{:02d}'.format(int(value / (60 * 24))),
                             Hour='{:02d}'.format(int((value % (60 * 24)) / 60)),
                             Minutes='{:02d}'.format(int(((value % (60 * 24)) / 60) % 60)))
        else:
            sr = pd.Series([((int(Date1.month) * 30 + int(Date1.day)) * 24 + int(Date1.hour)) * 60 + int(Date1.min),
                            np.nan,
                            ((int(Date2.month) * 30 + int(Date2.day)) * 24 + int(Date1.hour)) * 60 + int(Date2.min)],
                           index=vect1)
            value = int(sr.astype('float').interpolate(method='index').values[1])
            Date3 = Date(Month='{:02d}'.format(int(value / (30 * 60 * 24))),
                         Year=Date1.year,
                         Day='{:02d}'.format(int(((value % (30 * 60 * 24)) / (60 * 24)))),
                         Hour='{:02d}'.format(int(((value % (30 * 60 * 24)) % (60 * 24)) / 60),
                         Minutes='{:02d}'.format(((value % (30 * 60 * 24)) % (60 * 24)) % 60)))
    else:
        sr = pd.Series([
            (((int(Date1.year) * 12 + int(Date1.month)) * 30 + int(Date1.day)) * 24 + int(Date1.hour)) * 60 + int(
                Date1.min),
            np.nan,
            (((int(Date2.year) * 12 + int(Date2.month)) * 30 + int(Date2.day)) * 24 + int(Date2.hour)) * 60 + int(
                Date2.min)], index=vect1)
        value = int(sr.astype('float').interpolate(method='index').values[1])
        Date3 = Date(Month='{:02d}'.format(int((value % (12 * 30 * 60 * 24))/ (30 * 60 * 24))),
                     Year='{:02d}'.format(int(value / (12 * 30 * 60 * 24))),
                     Day='{:02d}'.format(int(((value % (12 * 30 * 60 * 24)) % (30 * 60 * 24)) / (60 * 24))),
                     Hour='{:02d}'.format(int((((value % (12 * 30 * 60 * 24)) % (30 * 60 * 24)) % (60 * 24)) / 60)),
                     Minutes='{:02d}'.format(int((((value % (12 * 30 * 60 * 24)) % (30 * 60 * 24)) % (60 * 24)) % 60)))

    Pt3.date = Date3.reverse_processing()


def getIDs(dataset):
    return dataset.id.unique()


def Filtering_Data(df_, id_, mode=False):
    x_ = []
    y_ = []
    ind = []
    IsIn = df_['id'] == int(id_)

    if not mode:
        for elt in df_[IsIn].iterrows():
            ind.append(elt[0])

        for elt in ind:
            x_.append(df_.iloc[elt].x)
            y_.append(df_.iloc[elt].y)

        return x_, y_, df_[IsIn]
    else:
        return df_[IsIn]


class Segment:
    def __init__(self, Pt1: Point = None, Pt2: Point = None):
        self.Pt1 = Pt1
        self.Pt2 = Pt2

    def setPoints(self, Pt1: Point, Pt2: Point):
        self.Pt1 = Pt1
        self.Pt2 = Pt2

    def Intersect(self, Seg):
        f1 = Line2Formula(self.Pt1, self.Pt2)
        f2 = Line2Formula(Seg.Pt1, Seg.Pt2)

        if (f1.A is None) or (f2.A is None):
            return Intersection_State()
        elif f1.A == f2.A:
            return Intersection_State()
        else:
            return Intersection_State(True, float(f1.A), float(f1.b), float(f2.A), float(f2.b))

    def Pt_Intersect(self, Seg):
        Int = self.Intersect(Seg)
        if Int.IsIntersection:
            Xa = float(float(Int.b2 - Int.b1) / float(Int.A1 - Int.A2))
            Ya = float(Int.A2 * Xa + Int.b2)
        else:
            Xa = 0
            Ya = 0

        return Point(id_=self.Pt1.id, x_=Xa, y_=Ya)

    def IsInBoth(self, Seg, P):
        """

        :type P: list
        :type Seg: Segment
        """
        Self_Int = [min(self.Pt2.x, self.Pt1.x), max(self.Pt1.x, self.Pt2.x)]
        Seg_Int = [min(Seg.Pt1.x, Seg.Pt2.x), max(Seg.Pt1.x, Seg.Pt2.x)]
        I = [max(Self_Int[0], Seg_Int[0]), min(Self_Int[1], Seg_Int[1])]

        Intersection_Point = self.Pt_Intersect(Seg)
        if (Intersection_Point.x == 0) and (Intersection_Point.y == 0):
            return False
        elif I[0] <= Intersection_Point.x <= I[1]:
            # plt.plot(Intersection_Point.x, Intersection_Point.y, 'ro')
            Date_Interpolate(self.Pt1, self.Pt2, Intersection_Point)
            P.append(Intersection_Point)
            return Intersection_Point


if __name__ == '__main__':

    import matplotlib.pyplot as plt

    # Global Vars
    ids = []
    df_filtered = []
    Points_of_intersect = []
    s = 1

    Gate_X = [51.60333, 51.6015]
    Gate_Y = [-8.529166, -8.5292]

    plt.axis(
        [min(Gate_X[0], Gate_X[1]), max(Gate_X[0], Gate_X[1]), min(Gate_Y[0], Gate_Y[1]), max(Gate_Y[0], Gate_Y[1])])
    plt.plot(Gate_X, Gate_Y)

    Gate_P1 = Point('Gate', None, Gate_X[0], Gate_Y[0])
    Gate_P2 = Point('Gate', None, Gate_X[1], Gate_Y[1])

    Gate_P1_np = np.array([Gate_P1.x, Gate_P1.y])
    Gate_P2_np = np.array([Gate_P2.x, Gate_P2.y])

    Gate = Segment(Gate_P1, Gate_P2)

    # Main
    csv.register_dialect('StdCSV', delimiter=';', quoting=csv.QUOTE_NONE, skipinitialspace=True)

    plt.plot(Gate_X, Gate_Y, label='Gate')

    df = pd.read_csv("data.csv", sep=";")
    ids = df.id.unique()

    for val in ids:
        # Clearing
        indexes = []
        x = []
        y = []

        is_in = df['id'] == val
        df_filtered = df[is_in]

        for i in df_filtered.iterrows():
            indexes.append(i[0])

        for i in indexes:
            x.append(df.iloc[i].x)
            y.append(df.iloc[i].y)

        plt.plot(x, y, label=val)

        index = 0
        while index < len(indexes) - 1:
            Pt1 = Point(df.iloc[indexes[index]].id, df.iloc[indexes[index]].date, df.iloc[indexes[index]].x,
                        df.iloc[indexes[index]].y)
            Pt2 = Point(df.iloc[indexes[index + 1]].id, df.iloc[indexes[index + 1]].date, df.iloc[indexes[index + 1]].x,
                        df.iloc[indexes[index + 1]].y)

            Seg1 = Segment(Pt1, Pt2)
            Seg1.IsInBoth(Gate, Points_of_intersect)

            index = index + 1

    # plt.legend()
    plt.show()
    print(Points_of_intersect)

    with open('intersection.csv', 'a') as writefile:
        writer = csv.writer(writefile, dialect='StdCSV')
        for i in range(0, len(Points_of_intersect)):
            writer.writerow([Points_of_intersect[i].id, Points_of_intersect[i].date, Points_of_intersect[i].x,
                             Points_of_intersect[i].y])
