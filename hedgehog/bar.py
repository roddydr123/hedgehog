import matplotlib.pyplot as plt
from SOBPwidth import getwidth
from loader import loader
import sys
"""
fig, ax = plt.subplots()

labels = []
yextent = 2

#ax.broken_barh([(3, 1)], (1, yextent), facecolors='tab:blue')
#ax.broken_barh([(3.1, 0.9)], (3, yextent), facecolors='tab:orange')
#ax.broken_barh([(3.191, 0.809)], (5, yextent), facecolors='tab:green')
#labels.append("1")

# j1-1
ax.broken_barh([(3.5, 0.5)], (9, yextent), facecolors='tab:blue')
ax.broken_barh([(3.3, 0.7)], (11, yextent), facecolors='tab:orange')
ax.broken_barh([(3.4, 0.6)], (13, yextent), facecolors='tab:green')
labels.append("J1-1")

#j2
ax.broken_barh([(3, 1)], (17, yextent), facecolors='tab:blue')
ax.broken_barh([(2.7, 1.3)], (19, yextent), facecolors='tab:orange')
ax.broken_barh([(3.3, 0.7)], (21, yextent), facecolors='tab:green')
labels.append("J2")

ax.set_ylim(8, 100)
ax.set_xlim(0, 5)
ax.set_xlabel('Depth into water (cm)')
ax.set_yticks([11, 19], labels=labels)

plt.show()
"""

plt.style.use('/mnt/c/users/david/documents/triumf/thesis/thesis.mplstyle')

files = ["nohedgehog.txt", "film34cg6.csv",
         "hedgehogJ1-1-gen.npz", "hedgehogJ1-1.txt", "film33cg6.csv", 
         "hedgehogJ2-gen.npz", "hedgehogJ2.txt", "film35cg6.csv",
         "hedgehogJ3-gen.npz", "hedgehogJ3.txt", "film30cg6.csv",
         "hedgehogJ4-gen.npz", "hedgehogJ4.txt", "film31cg6.csv",
         "hedgehogJ5-gen.npz", "hedgehogJ5.txt", "film32cg6.csv"]

labelsl = ['Optimized', 'Simulated', 'Measured']

def repbar(data):

    labels = ["None", "J1-1", "J2", "J3", "J4", "J5"]
    ticklocs = []
    fcs = ['C0', 'C1', 'C2']
    fcs1 = ['#194d72', '#ba671f', '#237723']

    yextent = 2
    ystart = int(yextent / 2)

    fig, ax = plt.subplots()

    ax.broken_barh([(0, 0)], (ystart, yextent), facecolors="w")

    for i, bar in enumerate(data):
        i += 1

        startpeak = bar[0]
        peakwidth = bar[1]
        dropoff = bar[2]

        wheel = int(i % 3)

        start_drop = startpeak + peakwidth

        if i == 2:
            ax.broken_barh([(startpeak, peakwidth), (start_drop, dropoff)], (ystart, yextent), facecolors=[fcs[wheel], fcs1[wheel]], label=labelsl[2])
        elif i == 4:
            ax.broken_barh([(startpeak, peakwidth), (start_drop, dropoff)], (ystart, yextent), facecolors=[fcs[wheel], fcs1[wheel]], label=labelsl[1])
        elif i == 6:
            ax.broken_barh([(startpeak, peakwidth), (start_drop, dropoff)], (ystart, yextent), facecolors=[fcs[wheel], fcs1[wheel]], label=labelsl[0])
        else:
            ax.broken_barh([(startpeak, peakwidth), (start_drop, dropoff)], (ystart, yextent), facecolors=[fcs[wheel], fcs1[wheel]])

        if wheel == 1:
            ticklocs.append(ystart + yextent/2)

        if wheel == 2:
            ystart += yextent * 2
        else:
            ystart += yextent

    ax.set_ylim(0, 46)
    ax.set_xlim(0, 5)
    ax.set_xlabel('Depth into water (cm)')
    ax.set_ylabel('HEDGEHOG name')
    ax.set_yticks(ticklocs, labels=labels)
    ax.legend(frameon=False, loc=3)

    plt.show()


def main():
    data = []
    for file in files:
        dat = loader(file)
        start, width, dropoff = getwidth(dat[0], dat[1])
        data.append([start, width, dropoff])
    repbar(data)


if __name__ == "__main__":
    main()