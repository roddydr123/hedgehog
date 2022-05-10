from hedgehog import hedgehog


h = hedgehog(1, 4, 9, "reduced-5mm", d_across_pinbase=0.5)

# h.viewDetails()
h.generateGDML(3)
h.gdml2f()
#h.gdml2stl()
