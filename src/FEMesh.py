import numpy as np
import matplotlib.pyplot as plt

from objdict import ObjDict
from GmshMesh import GmshMesh


def readmsh(filename):
    return FEMesh(GmshMesh(filename))


class FEMesh(ObjDict):

    def __init__(self, m: GmshMesh) -> None:
        self.nodes = m.nodes.T
        self.defaultGroup = PhysicalGroup('faces', m, m.findGroup(entityDim=2))

        # Add groups
        self.groups = []
        self.groups.append(self.defaultGroup)
        self.groups.append(PhysicalGroup('edges', m, m.findGroup(entityDim=1)))

    @property
    def Ng(self):
        return len(self.groups)

    def group(self, n):
        return self.groups[n]

    @property
    def Nn(self):
        return self.nodes.shape[1]

    @property
    def Ne(self):
        return self.elements.shape[1]

    @property
    def elements(self):
        return self.defaultGroup.elements

    @property
    def p(self):
        return self.defaultGroup.p

    def plot(self):
        plt.triplot(self.nodes[0, :], self.nodes[1, :], self.elements.T)

    def print(self):
        np.set_printoptions(linewidth=np.nan)
        print('Nodes')
        print(self.nodes)
        print('Elements')
        print(self.elements)
        print('Groups')
        for g in self.groups:
            g.print()


class PhysicalGroup(ObjDict):

    def __init__(self, name, m, g) -> None:

        # Properties
        self.p = ObjDict()
        self.name = name
        self.dimension = g.dimension

        # Elements, index-vector seems not to work here
        self.elements = []
        for eid in g.elementIDs:
            self.elements.append(m.elements[eid])
        self.elements = np.array(self.elements).T

        # Node IDs from elements
        self.nodesIDs = np.unique(self.elements)

    @property
    def Nn(self):
        return len(self.nodesIDs)

    @property
    def Ne(self):
        return self.elements.shape[1]

    def print(self):
        print('name: ', self.name)
        print('elements:\n', self.elements)
        print('nodeIDs:\n', self.nodesIDs)