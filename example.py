# AUTHOR:	Gyanranjan Hazarika - gyanranjanh@gmail.com
# Copyright (c) 2015-2016, All Rights Reserved.

from plot_curves import PlotGraph
import csv

if __name__ == "__main__":
    x  = []
    y1 = []
    y2 = []
    y3 = []
    y4 = []
    y5 = []
    y6 = []
    y7 = []
    count = 0
    with open("/home/Itr.csv", "r") as f:
        lines = f.readlines()
        for line in lines:
            values = line.rstrip().split(',')
            x.append(count)
            y1.append(float(values[0]))
            y2.append(float(values[1]))
            y3.append(float(values[2]))
            y4.append(float(values[3]))
            y5.append(float(values[4]))
            y6.append(float(values[5]))
            y7.append(float(values[6]))
            count += 1

    p = PlotGraph()
    p.plot(x, y1, y2, y3, y4, y5, y6, y7, title="t_vs_time_to_solve_puzzle",
    xlabel='t values', legend0='itr1(sec)', legend1='itr2(sec)',
    legend2='itr3(sec)', legend3='itr4(sec)',
    legend4='itr5(sec)', legend5='itr6(sec)',
    legend6='itr7(sec)', linestyle='-')
