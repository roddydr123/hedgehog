from hedgehog import hedgehog


h = hedgehog(0.7, 4, 8, 0.1, 1E-3, "comp01")

h.generateGDML(0.6)
h.gdml2f()
