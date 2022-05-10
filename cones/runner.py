from hedgehog import hedgehog


h = hedgehog(0.7, 4, 8, "test1")

# h.viewDetails()
h.generateGDML(4, 3)
#h.gdml2f()
h.gdml2stl()
