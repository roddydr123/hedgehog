from hedgehog import hedgehog


h = hedgehog(1, 4, 9, "full7c")

# h.viewDetails()
h.generateGDML(5, 2.5)
h.gdml2f()
#h.gdml2stl()
