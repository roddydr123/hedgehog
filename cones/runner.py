from hedgehog import hedgehog


h = hedgehog(1, 4, 9, "full3", d_across_pinbase=0.3)

# h.viewDetails()
h.generateGDML(5, 1.5)
h.gdml2f()
#h.gdml2stl()
