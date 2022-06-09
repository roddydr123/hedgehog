from hedgehog import hedgehog


h = hedgehog(1.0, 4.0, 8, "hedgehogJ5", tolerance=1E-3)

#h.viewDetails()
#h.generateGDML(5, 2.3)
#h.gdml2f()
h.gdml2stl()
