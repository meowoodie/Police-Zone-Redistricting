import numpy as ny

with open("data/sim-output.txt", "r") as f:
    Xs = []
    Ys = []
    for line in f:
        d, Y        = line.strip("\n").split("\t")
        year, beats = d.split(",")[0], d.split(",")[1:]
        Xs.append([year, beats])
        Ys.append(Y)

