from hedgehog import hedgehog


h = hedgehog(0.7, 4, 8, "test", d_across_pinbase=1)

# h.viewDetails()
#h.generateGDML(4)
#h.gdml2f()
h.gdml2stl()
