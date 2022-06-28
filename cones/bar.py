import matplotlib.pyplot as plt

fig, ax = plt.subplots()

# hedgehog 1
#ax.broken_barh([(110, 30), (150, 10)], (10, 9), facecolors='tab:blue')
yextent = 2

ax.broken_barh([(3, 1)], (1, yextent), facecolors='tab:blue')
ax.broken_barh([(3.1, 0.9)], (3, yextent), facecolors='tab:orange')
ax.broken_barh([(3.191, 0.809)], (5, yextent), facecolors='tab:green')

# j1-1
ax.broken_barh([(3.5, 0.5)], (9, yextent), facecolors='tab:blue')
ax.broken_barh([(3.3, 0.7)], (11, yextent), facecolors='tab:orange')
ax.broken_barh([(3.4, 0.6)], (13, yextent), facecolors='tab:green')

#j2
ax.broken_barh([(3, 1)], (17, yextent), facecolors='tab:blue')
ax.broken_barh([(2.7, 1.3)], (19, yextent), facecolors='tab:orange')
ax.broken_barh([(3.3, 0.7)], (21, yextent), facecolors='tab:green')

ax.set_ylim(0, 100)
ax.set_xlim(0, 5)
ax.set_xlabel('Depth into water (cm)')
ax.set_yticks([3, 11, 19], labels=['1', 'J1-1', 'J2'])

plt.show()