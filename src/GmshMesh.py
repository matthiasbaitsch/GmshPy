import numpy as np
from objdict import ObjDict


class GmshMesh(ObjDict):

    def __init__(self, filename) -> None:

        f = open(filename, 'r')
        line = f.readline().strip()

        while line:
            if line == '$MeshFormat':
                self.meshFormat = readMeshFormat(f)
            elif line == '$PhysicalNames':
                self.physicalNames = readPhysicalNames(f)
            elif line == '$Entities':
                self.entities = readEntities(f)
            elif line == '$Nodes':
                self.nodeBlocks, self.nodes = readNodes(f)
            elif line == '$Elements':
                self.elementBlocks, self.elements = readElements(f)
            else:
                print('Warning: Unknown entry', line)
                readsection(f, line)
            nexttoken(f)
            line = f.readline().strip()

    def findGroup(self, entityDim=None):
        g = ObjDict()
        g.nodeIDs = []
        g.elementIDs = []

        # TODO: Recursively find attached nodes, find by name

        if entityDim is not None:
            g.dimension = entityDim
            for nb in self.nodeBlocks:
                if nb.entityDim == entityDim:
                    g.nodeIDs += nb.tags
            for eb in self.elementBlocks:
                if eb.entityDim == entityDim:
                    g.elementIDs += eb.tags

        return g

    @property
    def groupNames(self):
        names = []
        for pn in self.physicalNames:
            names.append(pn.name)
        return names


def readElements(f):

    # Description of all element blocks
    nBlocks, nElements, minElementTag, maxElementTag = textscan(f, '%d %d %d %d')

    # Check numbering
    if maxElementTag - minElementTag + 1 != nElements:
        raise Exception('Elements not continously numbered') 

    # Return values
    blocks = []
    elements = nElements * [None]

    # Loop over element blocks
    for i in range(0, nBlocks):

        # Block object
        eb = ObjDict()
        eb.tags = []

        # Description of element block
        eb.entityDim, eb.entityTag, eb.elementType = textscan(f, '%d %d %d')

        # Number of elements in block
        nElementsIB = textscan(f, '%d')[0]

        # Read elements
        for j in range(0, nElementsIB):
            tag = textscan(f, '%d')[0]
            eb.tags.append(tag - 1)
            elements[tag - 1] = list(map(int, f.readline().split()))

        # Append block
        blocks.append(eb)

    # Python uses zero-based indexing
    for e in elements:
        for j in range(0, len(e)):
            e[j] -= 1

    # Return
    return blocks, elements


def readNodes(f):

    # Description of all node blocks
    nBlocks, nNodes, minNodeTag, maxNodeTag = textscan(f, '%d %d %d %d')

    # Check numbering
    if maxNodeTag - minNodeTag + 1 != nNodes:
        raise Exception('Nodes not continously numbered') 

    # Return values
    blocks = []
    nodes = nNodes * [None]

    # Loop over node blocks
    for i in range(0, nBlocks):

        # Block object
        nb = ObjDict()

        # Description of node block
        nb.entityDim, nb.entityTag, parametric = textscan(f, '%d %d %d')

        # Number, tags and coordinates
        nNodesIB = textscan(f, '%d')[0]
        tags = textscan(f, nNodesIB * '%d ')
        coordinates = textscan(f, '%f %f %f', nNodesIB)

        # Work around overly 'clever' textscan
        if nNodesIB == 1:
            coordinates = [coordinates]

        # Checks
        assert len(tags) > 0
        if parametric != 0:
            raise Exception('Parametric geometry not supported yet')
        if tags[-1] - tags[0] + 1 != nNodesIB:
            raise Exception('Nodes in block not continously numbered') 

        # Save values
        nb.tags = []
        for j in range(0, nNodesIB):
            nb.tags.append(tags[j] - 1)
            nodes[tags[j] - 1] = coordinates[j]

        # Append to list
        blocks.append(nb)

    # Return
    return blocks, np.array(nodes)


def readEntities(f):
    e = ObjDict()
    np, nc, ns, nv = textscan(f, '%d %d %d %d', 1)
    e.points = readPoints(f, np)
    e.curves = readPointSets(f, nc, 1)
    e.surfaces = readPointSets(f, ns, 2)
    e.volumes = readPointSets(f, nv, 3)
    return e


def readPointSets(f, n, dim):
    ptss = []
    for i in range(0, n):
        p = ObjDict()
        p.dim = dim
        p.tag = textscan(f, '%d')[0]
        p.boundingBox = textscan(f, '%f %f %f %f %f %f')
        npt = textscan(f, '%d')[0]
        p.physicalTags = textscan(f, npt * '%d ')
        npt = textscan(f, '%d')[0]
        p.boundingTags = textscan(f, npt * '%d ')
        ptss.append(p)
    return ptss


def readPoints(f, n):
    pts = []
    for i in range(0, n):
        p = ObjDict()
        p.tag, p.x, p.y, p.z = textscan(f, '%d %f %f %f')
        npt = textscan(f, '%d')[0]
        p.physicalTags = textscan(f, npt * '%d ')
        pts.append(p)
    return pts


def readPhysicalNames(f):
    pns = []
    n = textscan(f, '%d')[0]
    d = textscan(f, '%d %d %q', n)
    for di in d:
        o = ObjDict()
        o.dimension = di[0]
        o.tag = di[1]
        o.name = di[2]
        pns.append(o)
    return pns


def readMeshFormat(f):
    mf = ObjDict()
    mf.version, mf.fileType, mf.dataSize = textscan(f, '%f %d %d')
    return mf


def readsection(f, s):
    line = f.readline().strip()
    while line and line != '$End' + s[1:]:
        line = f.readline().strip()


def textscan(f, format, n=1):
    """Poor man's version of Matlab textscan"""

    # Converters
    c = []
    for s in format.split():
        if s == '%d':
            c.append(lambda s: int(s))
        elif s == '%f':
            c.append(lambda s: float(s))
        elif s == '%q':
            c.append(lambda s: s[1:-1])
        else:
            raise Exception('Illegal format: ' + s)
    nt = len(c)

    # Result
    result = []
    for i in range(0, n):
        row = []
        for j in range(0, nt):
            convert = c[j]
            token = nexttoken(f)
            row.append(convert(token))
        result.append(row)

    # Return
    if n == 1:
        return result[0]
    else:
        return result


def nexttoken(f):
    c = ''

    # find beginning
    cc = f.read(1)
    while cc and cc.isspace():
        cc = f.read(1)

    # read until next whitespace
    while cc and not cc.isspace():
        c += cc
        cc = f.read(1)

    # return
    return c
