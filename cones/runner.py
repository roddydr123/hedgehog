from hedgehog import hedgehog


h = hedgehog(0.7, 4, 8, "test")

# h.viewDetails()
h.generateGDML(4, 2)
#h.gdml2f()
h.gdml2stl()
