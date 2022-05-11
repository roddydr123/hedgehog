from hedgehog import hedgehog


h = hedgehog(0.7, 4, 7, "test1", d_across_pinbase=0.5)

# h.viewDetails()
h.generateGDML(5, 2.5)
# h.gdml2f()
h.gdml2stl()
