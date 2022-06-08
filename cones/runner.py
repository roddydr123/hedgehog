from hedgehog import hedgehog


h = hedgehog(1, 4.0, 50, "hedgehogJ2a", usrWeights=[10, 1, 1], tolerance=1E-3)

h.viewDetails()
#h.generateGDML(5, 2.3)
#h.gdml2f()
#h.gdml2stl()
