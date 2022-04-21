from hedgehog import hedgehog


h = hedgehog(0.7, 4, 8, 0.05, 1E-3, "base12")

h.generateGDML(0.6)
h.gdml2f()
