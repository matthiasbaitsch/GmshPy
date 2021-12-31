from FEMesh import readmsh

m = readmsh('demos/gmsh/rectangle-0.msh')

# Print nodes and elements
print('\nNodes\n', m.nodes)
print('\nElements\n', m._elements)

# Print groups
for g in m.groups.values():
    g.print()

m.plot()
