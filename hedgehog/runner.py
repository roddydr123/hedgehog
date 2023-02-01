import hedgehog as hog

thicklist = [0.1, 0.19, 0.29, 0.38, 0.47, 0.57, 0.66, 0.75, 0.85, 0.94, 1.03,
             1.13, 1.22, 1.31, 1.41, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2,
             2.3, 2.4, 2.5, 2.6, 2.7, 2.8]

us = hog.undersim(thicklist, "./usims")

sobp = hog.SOBPeak(2.5, 4.0, 10)

h = hog.hedgehog(sobp, us, "bigbase", tolerance=1E-3)
# h.viewDetails()
h.generateGDML(5, 1.5, 13.6)
# h.gdml2f("template.inp")
h.gdml2stl()