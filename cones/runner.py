from hedgehog import hedgehog


h = hedgehog(1.8, 4, 16, "dataset4-test", usrWeights=[800, 15E2, 15E2])

#h.viewDetails()
#h.generateGDML(5, 2.3)
h.gdml2f()
#h.gdml2stl()
