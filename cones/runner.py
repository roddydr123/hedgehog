from hedgehog import hedgehog


h = hedgehog(0.5, 4.0, 40, "hedgehogJ1e", usrWeights=[30, 1, 1], tolerance=1E-3)

h.viewDetails()
#h.generateGDML(5, 2.3)
#h.gdml2f()
#h.gdml2stl()
