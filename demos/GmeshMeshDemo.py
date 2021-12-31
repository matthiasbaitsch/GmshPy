from GmshMesh import GmshMesh

# Object
m = GmshMesh('demos/gmsh/rectangle-0.msh')

# List physical names
print('\nPhysical names\n', m.physicalNamesList)

# Element blocks for entities of dimension 1
g = m.elementBlocksBy(entityDim=1)
print('\nDim=1\n', g)

# Element blocks for entities of dimension 2
g = m.elementBlocksBy(entityDim=2)
print('\nDim=2\n', g)

# Element block attached to entity with physical name C1
g = m.elementBlocksBy(physicalName='C1')
print('\nC1\n', g)

# Nodes and elements
print('\nNodes and elements')
print(m.nodes)
print(m.elements)
