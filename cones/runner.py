from hedgehog import hedgehog


h = hedgehog(1, 4, 9, "full7")

# h.viewDetails()
h.generateGDML(5, 1.7)
h.gdml2f()
#h.gdml2stl()
