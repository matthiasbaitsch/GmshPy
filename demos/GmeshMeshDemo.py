from GmshMesh import GmshMesh

m = GmshMesh('demos/gmsh/rectangle-0.msh')

# print(m.groupNames)
# g = m.findGroup(entityDim=1)
# print(g)
g = m.findGroup(entityDim=2)
print(g)

# print(m.nodes)
# print(m.elements)
