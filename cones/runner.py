from hedgehog import hedgehog


h = hedgehog(1.5, 4.0, 15, "hedgehogJ3", tolerance=1E-6)

#h.viewDetails()
h.generateGDML(5, 2.3)
h.gdml2f()
#h.gdml2stl()
