from hedgehog import hedgehog


h = hedgehog(0.7, 4, 8, 0.7, 1E-3, 15, "test")

# h.viewDetails()
h.generateGDML(0.6)
h.gdml2f()
