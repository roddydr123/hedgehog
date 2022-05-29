from hedgehog import hedgehog


h = hedgehog(1, 4, 9, "reverse", d_across_pinbase=0.7)

# h.viewDetails()
h.generateGDML(5, 1.5)
h.gdml2f()
#h.gdml2stl()
