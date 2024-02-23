# Load the Python Standard and DesignScript Libraries
import sys
import clr

clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

clr.AddReference('MeshToolkit')
import Autodesk.Dynamo.MeshToolkit as mtk

import System
from System.Collections.Generic import List

import numpy as np

##############
# HELPERS
#############

# ==============================================================================
#
# Double linked list
#
# ==============================================================================

__author__ = 'Nils Olofsson'
__email__ = 'me@nilsolovsson.se'
__copyright__ = 'Copyright 2021, AllSystemsPhenomenal'
__license__ = 'MIT'


class Node:
    """
        Node element in a DoubleLinkedList.
        Each node in a valid list is associated with a value/data element and
        with its left and right neighbor.
        [Prev. node]<--[Node]-->[Next node]
                         |
                       [Data]
    """

    def __init__(self, data):
        self.data = data
        self.prev = None
        self.next = None


class DoubleLinkedList:
    """
        A double linked list. Each element keeps a reference to both left and
        right neighbor. This allows e.g. for easy removal of elements.
        The list is circular and is usually considered traversed when the next element
        is the same element as when when we started.
    """

    def __init__(self):
        self.first = None
        self.size = 0

    def __str__(self):
        if self.first == None:
            return '[]'
        msg = '['
        msg += str(self.first.data)
        node = self.first.next
        while node != self.first:
            msg += ', ' + str(node.data)
            node = node.next
        msg += ']'
        return msg

    def append(self, data):
        self.size += 1
        if self.first == None:
            self.first = Node(data)
            self.first.prev = self.first
            self.first.next = self.first
            return
        node = Node(data)
        last = self.first.prev
        node.prev = last
        node.next = self.first
        last.next = node
        self.first.prev = node

    def remove(self, item):
        if self.first == None:
            return
        rmv = None
        node = self.first
        if node.data == item:
            rmv = node
        node = node.next
        while not rmv and node != self.first:
            if node.data == item:
                rmv = node
            node = node.next
        if rmv:
            nxt = rmv.next
            prv = rmv.prev
            prv.next = nxt
            nxt.prev = prv
            self.size -= 1
            if rmv == self.first:
                self.first = nxt
            if rmv == self.first:
                self.first = None
        return

    def count(self):
        if self.first == None:
            return 0
        i = 1
        node = self.first.next
        while node != self.first:
            i += 1
            node = node.next
        return i

    def flatten(self):
        if self.first == None:
            return []
        l = []
        node = self.first
        l.append(node.data)
        node = self.first.next
        while node != self.first:
            l.append(node.data)
            node = node.next
        return l


# ==============================================================================
#
# Triangulation Code
# based on Tutorial at https://all-systems-phenomenal.com/articles/ear_clipping_triangulation/index.php
#
# ==============================================================================


def angleCCW(a, b):
    """
        Counter clock wise angle (radians) from normalized 2D vectors a to b
    """
    dot = a[0] * b[0] + a[1] * b[1]
    det = a[0] * b[1] - a[1] * b[0]
    angle = np.arctan2(det, dot)
    if angle < 0.0:
        angle = 2.0 * np.pi + angle
    return angle


def isConvex(vertex_prev, vertex, vertex_next):
    """
        Determine if vertex is locally convex.
    """
    a = vertex_prev - vertex
    b = vertex_next - vertex
    internal_angle = angleCCW(b, a)
    return internal_angle <= np.pi


def insideTriangle(a, b, c, p):
    """
        Determine if a vertex p is inside (or "on") a triangle made of the
        points a->b->c
        http://blackpawn.com/texts/pointinpoly/
    """

    # Compute vectors
    v0 = c - a
    v1 = b - a
    v2 = p - a

    # Compute dot products
    dot00 = np.dot(v0, v0)
    dot01 = np.dot(v0, v1)
    dot02 = np.dot(v0, v2)
    dot11 = np.dot(v1, v1)
    dot12 = np.dot(v1, v2)

    # Compute barycentric coordinates
    denom = dot00 * dot11 - dot01 * dot01
    if abs(denom) < 1e-20:
        return True
    invDenom = 1.0 / denom
    u = (dot11 * dot02 - dot01 * dot12) * invDenom
    v = (dot00 * dot12 - dot01 * dot02) * invDenom

    # Check if point is in triangle
    return (u >= 0) and (v >= 0) and (u + v < 1)


def triangulate(vertices_raw):
    """
        Triangulation of a polygon in 2D.
        Assumption that the polygon is simple, i.e has no holes, is closed and
        has no crossings and also that its vertex order is counter clockwise.
    """

    vertices = np.array(vertices_raw)

    n, m = vertices.shape
    indices = np.zeros([n - 2, 3], dtype=int)

    vertlist = DoubleLinkedList()
    for i in range(0, n):
        vertlist.append(i)
    index_counter = 0

    # Simplest possible algorithm. Create list of indexes.
    # Find first ear vertex. Create triangle. Remove vertex from list
    # Do this while number of vertices > 2.
    node = vertlist.first
    full_loop_counter = n
    while vertlist.size > 2:
        i = node.prev.data
        j = node.data
        k = node.next.data

        vert_prev = vertices[i, :]
        vert_current = vertices[j, :]
        vert_next = vertices[k, :]

        is_convex = isConvex(vert_prev, vert_current, vert_next)
        is_ear = True
        if is_convex:
            test_node = node.next.next
            while test_node != node.prev and is_ear:
                vert_test = vertices[test_node.data, :]
                is_ear = not insideTriangle(vert_prev,
                                            vert_current,
                                            vert_next,
                                            vert_test)
                test_node = test_node.next
        else:
            is_ear = False

        if is_ear:
            indices[index_counter, :] = np.array([i, j, k], dtype=int)
            index_counter += 1
            vertlist.remove(node.data)
            full_loop_counter = n
        node = node.next
        full_loop_counter -= 1

        if full_loop_counter < 0:
            print('CANT FIND MORE EARS - ERROR - CANCELLING TRIANGULATION')
            break

    return indices


################
# ACTUAL SCRIPT
################


# The inputs to this node will be stored as a list in the IN variables.
geometries = IN[0]


# Place your code below this line

def pointInList(point, vertexList):
    for index, vertex in enumerate(vertexList):
        if point.X == vertex.X and point.Y == vertex.Y and point.Z == vertex.Z:
            return index
    return -1


def equalPoints2D(A, B):
    return A[0] == B[0] and A[1] == B[1]


def squareDistancePoints2D(A, B):
    return (B[0] - A[0]) ** 2 + (B[1] - A[1]) ** 2


def isCounterClockwise(vertices):
    edgeSum = 0
    lastVertex = vertices[-1]
    for vertex in vertices:
        edgeSum += (vertex[0] - lastVertex[0]) * (vertex[1] + lastVertex[1])
        lastVertex = vertex

    return edgeSum < 0


def getLargestCoordinate(vertexList, index):
    largest = float('-inf')
    for vertex in vertexList:
        if vertex[index] > largest:
            largest = vertex[index]
    return largest


def getLineIntersection(x1, y1, x2, y2, x3, y3, x4, y4):
    denom = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
    if denom == 0:
        return None  # Parallel.
    ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denom
    ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / denom
    if 0.0 <= ua <= 1.0 and 0.0 <= ub <= 1.0:
        return (x1 + ua * (x2 - x1)), (y1 + ua * (y2 - y1))
    return None


def getIntersectionEdge(outerPolygon, innerVertex):
    lastVertex = outerPolygon[-1]
    infiniteLineEnd = getLargestCoordinate(outerPolygon, 0) + 100
    for index, vertex in enumerate(outerPolygon):
        if lastVertex[0] >= innerVertex[0] or vertex[0] >= innerVertex[0]:
            vertexInt = getLineIntersection(innerVertex[0], innerVertex[1], infiniteLineEnd, innerVertex[1],
                                            lastVertex[0], lastVertex[1], vertex[0], vertex[1])
            if vertexInt is not None:
                return lastVertex, vertex, vertexInt, index
        lastVertex = vertex
    raise Exception('No intersection found... This should not happen - check the code')


meshGeometries = []
for geometry in geometries:
    vertexList = []
    indexList = []

    holesArePossible = type(geometry[0][0]) == list

    for surface in geometry:

        withHoles = False

        if holesArePossible and len(surface) > 1:
            srfOuterBoundVertices = surface[0]
            holes = surface[1:]
            withHoles = True
        elif holesArePossible and len(surface) == 1:
            srfOuterBoundVertices = surface[0]
        else:
            srfOuterBoundVertices = surface

        if not withHoles and len(srfOuterBoundVertices) < 3:
            print('Invadlid Surface - only', len(srfOuterBoundVertices), 'Vertexes')
            continue
        elif not withHoles and len(srfOuterBoundVertices) == 3:
            for point in srfOuterBoundVertices:
                geoPoint = Point.ByCoordinates(point[0], point[1], point[2])
                pointIndex = pointInList(geoPoint, vertexList)
                if pointIndex > -1:
                    indexList.append(pointIndex)
                else:
                    vertexList.append(geoPoint)
                    indexList.append(len(vertexList) - 1)
        else:
            # Create Geometry Points
            points = []
            for point in srfOuterBoundVertices:
                points.append(Point.ByCoordinates(point[0], point[1], point[2]))

            if withHoles:
                holesPoints = []
                for hole in holes:
                    holePoints = []
                    for point in hole:
                        holePoints.append(Point.ByCoordinates(point[0], point[1], point[2]))
                    holesPoints.append(holePoints)

            # Get plane/coord system of surface
            surfacePlane = Plane.ByBestFitThroughPoints(points)

            # Transform points into it
            fromCS = CoordinateSystem.ByOrigin(0, 0, 0)
            toCS = CoordinateSystem.ByPlane(surfacePlane)
            transformedPoints = []
            for point in points:
                transformedPoint = point.Transform(toCS, fromCS)
                transformedPoints.append([transformedPoint.X, transformedPoint.Y])

            if isCounterClockwise(transformedPoints):
                polyPoints = transformedPoints
            else:
                polyPoints = np.flip(transformedPoints, 0)
                points = np.flip(points, 0)

            if withHoles:
                transformedHolesPoints = []
                for index, hole in enumerate(holesPoints):
                    transformedHolePoints = []
                    for point in hole:
                        transformedPoint = point.Transform(toCS, fromCS)
                        transformedHolePoints.append([transformedPoint.X, transformedPoint.Y])

                    # Make sure the transforme hole vertices are clockwise and the original points are ordered the same
                    if not isCounterClockwise(transformedHolePoints):
                        transformedHolesPoints.append(transformedHolePoints)
                    else:
                        transformedHolesPoints.append(np.flip(transformedHolePoints, 0))
                        holesPoints[index] = np.flip(holesPoints[index], 0)

                # Combine outer (polyPoints) and inner (transformedHolesPoints) boundaries
                largestXs = []
                largestXIndices = []
                for hole in transformedHolesPoints:
                    largestX = float('-inf')
                    largestXIndex = 0
                    for index, point in enumerate(hole):
                        if point[0] > largestX:
                            largestX = point[0]
                            largestXIndex = index
                    largestXs.append(largestX)
                    largestXIndices.append(largestXIndex)

                holeOrder = np.flip(np.argsort(largestXs))

                for holeIndex in holeOrder:
                    nextHole = transformedHolesPoints[holeIndex]

                    startVertex = nextHole[largestXIndices[holeIndex]]
                    shiftedHole = np.roll(nextHole, -1 * largestXIndices[holeIndex], 0)
                    shiftedHolePoints = np.roll(holesPoints[holeIndex], -largestXIndices[holeIndex])

                    try:
                        edgeA, edgeB, edgeInt, edgeBIndex = getIntersectionEdge(polyPoints, startVertex)
                    except:
                        print('ERROR connecting hole', polyPoints, startVertex, nextHole)
                        continue

                    if equalPoints2D(edgeInt, edgeA):
                        # Point A is already mutually visible
                        edgeAIndex = edgeBIndex - 1
                        if edgeAIndex < 0:
                            edgeAIndex = len(transformedPoints) - 1

                        polyPoints = np.concatenate(
                            (polyPoints[:edgeAIndex + 1], shiftedHole, [shiftedHole[0]], polyPoints[edgeAIndex:]))
                        points = np.concatenate(
                            (points[:edgeAIndex + 1], shiftedHolePoints, [shiftedHolePoints[0]], points[edgeAIndex:]))
                        continue
                    elif equalPoints2D(edgeInt, edgeB):
                        polyPoints = np.concatenate(
                            (polyPoints[:edgeBIndex + 1], shiftedHole, [shiftedHole[0]], polyPoints[edgeBIndex:]))
                        points = np.concatenate(
                            (points[:edgeBIndex + 1], shiftedHolePoints, [shiftedHolePoints[0]], points[edgeBIndex:]))
                        continue
                    else:
                        candidatePoint = edgeA if edgeA[0] >= edgeB[0] else edgeB
                        candidateIndex = edgeBIndex - 1 if edgeA[0] >= edgeB[0] else edgeBIndex
                        otherCandidateIndices = []
                        for index, point in enumerate(polyPoints):
                            prevIndex = index - 1
                            nextIndex = index + 1 if index + 1 < len(polyPoints) else 0
                            if not isConvex(polyPoints[prevIndex], point, polyPoints[nextIndex]) and insideTriangle(
                                    startVertex, edgeInt, candidatePoint, point):
                                otherCandidateIndices.append(index)

                        distance = 0
                        for index in otherCandidateIndices:
                            point = transformedPoints[index]
                            nextDistance = squareDistancePoints2D(startVertex, point)
                            if nextDistance > distance:
                                distance = nextDistance
                                candidateIndex = index

                        polyPoints = np.concatenate((polyPoints[:candidateIndex + 1], shiftedHole, [shiftedHole[0]],
                                                     polyPoints[candidateIndex:]))
                        points = np.concatenate((points[:candidateIndex + 1], shiftedHolePoints, [shiftedHolePoints[0]],
                                                 points[candidateIndex:]))

            # print('TRANSFORM', polyPoints)

            # Triangulate
            triangulation = triangulate(polyPoints)
            # Load the Python Standard and DesignScript Libraries
            import sys
            import clr

            clr.AddReference('ProtoGeometry')
            from Autodesk.DesignScript.Geometry import *

            clr.AddReference('MeshToolkit')
            import Autodesk.Dynamo.MeshToolkit as mtk

            import System
            from System.Collections.Generic import List

            import numpy as np

            ##############
            # HELPERS
            #############

            # ==============================================================================
            #
            # Double linked list
            #
            # ==============================================================================

            __author__ = 'Nils Olofsson'
            __email__ = 'me@nilsolovsson.se'
            __copyright__ = 'Copyright 2021, AllSystemsPhenomenal'
            __license__ = 'MIT'


            class Node:
                """
                    Node element in a DoubleLinkedList.
                    Each node in a valid list is associated with a value/data element and
                    with its left and right neighbor.
                    [Prev. node]<--[Node]-->[Next node]
                                     |
                                   [Data]
                """

                def __init__(self, data):
                    self.data = data
                    self.prev = None
                    self.next = None


            class DoubleLinkedList:
                """
                    A double linked list. Each element keeps a reference to both left and
                    right neighbor. This allows e.g. for easy removal of elements.
                    The list is circular and is usually considered traversed when the next element
                    is the same element as when when we started.
                """

                def __init__(self):
                    self.first = None
                    self.size = 0

                def __str__(self):
                    if self.first == None:
                        return '[]'
                    msg = '['
                    msg += str(self.first.data)
                    node = self.first.next
                    while node != self.first:
                        msg += ', ' + str(node.data)
                        node = node.next
                    msg += ']'
                    return msg

                def append(self, data):
                    self.size += 1
                    if self.first == None:
                        self.first = Node(data)
                        self.first.prev = self.first
                        self.first.next = self.first
                        return
                    node = Node(data)
                    last = self.first.prev
                    node.prev = last
                    node.next = self.first
                    last.next = node
                    self.first.prev = node

                def remove(self, item):
                    if self.first == None:
                        return
                    rmv = None
                    node = self.first
                    if node.data == item:
                        rmv = node
                    node = node.next
                    while not rmv and node != self.first:
                        if node.data == item:
                            rmv = node
                        node = node.next
                    if rmv:
                        nxt = rmv.next
                        prv = rmv.prev
                        prv.next = nxt
                        nxt.prev = prv
                        self.size -= 1
                        if rmv == self.first:
                            self.first = nxt
                        if rmv == self.first:
                            self.first = None
                    return

                def count(self):
                    if self.first == None:
                        return 0
                    i = 1
                    node = self.first.next
                    while node != self.first:
                        i += 1
                        node = node.next
                    return i

                def flatten(self):
                    if self.first == None:
                        return []
                    l = []
                    node = self.first
                    l.append(node.data)
                    node = self.first.next
                    while node != self.first:
                        l.append(node.data)
                        node = node.next
                    return l


            # ==============================================================================
            #
            # Triangulation Code
            # based on Tutorial at https://all-systems-phenomenal.com/articles/ear_clipping_triangulation/index.php
            #
            # ==============================================================================

            def angleCCW(a, b):
                """
                    Counter clock wise angle (radians) from normalized 2D vectors a to b
                """
                dot = a[0] * b[0] + a[1] * b[1]
                det = a[0] * b[1] - a[1] * b[0]
                angle = np.arctan2(det, dot)
                if angle < 0.0:
                    angle = 2.0 * np.pi + angle
                return angle


            def isConvex(vertex_prev, vertex, vertex_next):
                """
                    Determine if vertex is locally convex.
                """
                a = vertex_prev - vertex
                b = vertex_next - vertex
                internal_angle = angleCCW(b, a)
                return internal_angle <= np.pi


            def insideTriangle(a, b, c, p):
                """
                    Determine if a vertex p is inside (or "on") a triangle made of the
                    points a->b->c
                    http://blackpawn.com/texts/pointinpoly/
                """

                # Compute vectors
                v0 = c - a
                v1 = b - a
                v2 = p - a

                # Compute dot products
                dot00 = np.dot(v0, v0)
                dot01 = np.dot(v0, v1)
                dot02 = np.dot(v0, v2)
                dot11 = np.dot(v1, v1)
                dot12 = np.dot(v1, v2)

                # Compute barycentric coordinates
                denom = dot00 * dot11 - dot01 * dot01
                if abs(denom) < 1e-20:
                    return True
                invDenom = 1.0 / denom
                u = (dot11 * dot02 - dot01 * dot12) * invDenom
                v = (dot00 * dot12 - dot01 * dot02) * invDenom

                # Check if point is in triangle
                return (u >= 0) and (v >= 0) and (u + v < 1)


            def triangulate(vertices_raw):
                """
                    Triangulation of a polygon in 2D.
                    Assumption that the polygon is simple, i.e has no holes, is closed and
                    has no crossings and also that its vertex order is counter clockwise.
                """

                vertices = np.array(vertices_raw)

                n, m = vertices.shape
                indices = np.zeros([n - 2, 3], dtype=int)

                vertlist = DoubleLinkedList()
                for i in range(0, n):
                    vertlist.append(i)
                index_counter = 0

                # Simplest possible algorithm. Create list of indexes.
                # Find first ear vertex. Create triangle. Remove vertex from list
                # Do this while number of vertices > 2.
                node = vertlist.first
                full_loop_counter = n
                while vertlist.size > 2:
                    i = node.prev.data
                    j = node.data
                    k = node.next.data

                    vert_prev = vertices[i, :]
                    vert_current = vertices[j, :]
                    vert_next = vertices[k, :]

                    is_convex = isConvex(vert_prev, vert_current, vert_next)
                    is_ear = True
                    if is_convex:
                        test_node = node.next.next
                        while test_node != node.prev and is_ear:
                            vert_test = vertices[test_node.data, :]
                            is_ear = not insideTriangle(vert_prev,
                                                        vert_current,
                                                        vert_next,
                                                        vert_test)
                            test_node = test_node.next
                    else:
                        is_ear = False

                    if is_ear:
                        indices[index_counter, :] = np.array([i, j, k], dtype=int)
                        index_counter += 1
                        vertlist.remove(node.data)
                        full_loop_counter = n
                    node = node.next
                    full_loop_counter -= 1

                    if full_loop_counter < 0:
                        print('CANT FIND MORE EARS - ERROR - CANCELLING TRIANGULATION')
                        break

                return indices


            ################
            # ACTUAL SCRIPT
            ################

            # The inputs to this node will be stored as a list in the IN variables.
            geometries = IN[0]


            # Place your code below this line

            def pointInList(point, vertexList):
                for index, vertex in enumerate(vertexList):
                    if point.X == vertex.X and point.Y == vertex.Y and point.Z == vertex.Z:
                        return index
                return -1


            def equalPoints2D(A, B):
                return A[0] == B[0] and A[1] == B[1]


            def squareDistancePoints2D(A, B):
                return (B[0] - A[0]) ** 2 + (B[1] - A[1]) ** 2


            def isCounterClockwise(vertices):
                edgeSum = 0
                lastVertex = vertices[-1]
                for vertex in vertices:
                    edgeSum += (vertex[0] - lastVertex[0]) * (vertex[1] + lastVertex[1])
                    lastVertex = vertex

                return edgeSum < 0


            def getLargestCoordinate(vertexList, index):
                largest = float('-inf')
                for vertex in vertexList:
                    if vertex[index] > largest:
                        largest = vertex[index]
                return largest


            def getLineIntersection(x1, y1, x2, y2, x3, y3, x4, y4):
                denom = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
                if denom == 0:
                    return None  # Parallel.
                ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denom
                ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / denom
                if 0.0 <= ua <= 1.0 and 0.0 <= ub <= 1.0:
                    return (x1 + ua * (x2 - x1)), (y1 + ua * (y2 - y1))
                return None


            def getIntersectionEdge(outerPolygon, innerVertex):
                lastVertex = outerPolygon[-1]
                infiniteLineEnd = getLargestCoordinate(outerPolygon, 0) + 100
                for index, vertex in enumerate(outerPolygon):
                    if lastVertex[0] >= innerVertex[0] or vertex[0] >= innerVertex[0]:
                        vertexInt = getLineIntersection(innerVertex[0], innerVertex[1], infiniteLineEnd, innerVertex[1],
                                                        lastVertex[0], lastVertex[1], vertex[0], vertex[1])
                        if vertexInt is not None:
                            return lastVertex, vertex, vertexInt, index
                    lastVertex = vertex
                raise Exception('No intersection found... This should not happen - check the code')


            meshGeometries = []
            for geometry in geometries:
                vertexList = []
                indexList = []

                holesArePossible = type(geometry[0][0]) == list

                for surface in geometry:

                    withHoles = False

                    if holesArePossible and len(surface) > 1:
                        srfOuterBoundVertices = surface[0]
                        holes = surface[1:]
                        withHoles = True
                    elif holesArePossible and len(surface) == 1:
                        srfOuterBoundVertices = surface[0]
                    else:
                        srfOuterBoundVertices = surface

                    if not withHoles and len(srfOuterBoundVertices) < 3:
                        print('Invadlid Surface - only', len(srfOuterBoundVertices), 'Vertexes')
                        continue
                    elif not withHoles and len(srfOuterBoundVertices) == 3:
                        for point in srfOuterBoundVertices:
                            geoPoint = Point.ByCoordinates(point[0], point[1], point[2])
                            pointIndex = pointInList(geoPoint, vertexList)
                            if pointIndex > -1:
                                indexList.append(pointIndex)
                            else:
                                vertexList.append(geoPoint)
                                indexList.append(len(vertexList) - 1)
                    else:
                        # Create Geometry Points
                        points = []
                        for point in srfOuterBoundVertices:
                            points.append(Point.ByCoordinates(point[0], point[1], point[2]))

                        if withHoles:
                            holesPoints = []
                            for hole in holes:
                                holePoints = []
                                for point in hole:
                                    holePoints.append(Point.ByCoordinates(point[0], point[1], point[2]))
                                holesPoints.append(holePoints)

                        # Get plane/coord system of surface
                        surfacePlane = Plane.ByBestFitThroughPoints(points)

                        # Transform points into it
                        fromCS = CoordinateSystem.ByOrigin(0, 0, 0)
                        toCS = CoordinateSystem.ByPlane(surfacePlane)
                        transformedPoints = []
                        for point in points:
                            transformedPoint = point.Transform(toCS, fromCS)
                            transformedPoints.append([transformedPoint.X, transformedPoint.Y])

                        if isCounterClockwise(transformedPoints):
                            polyPoints = transformedPoints
                        else:
                            polyPoints = np.flip(transformedPoints, 0)
                            points = np.flip(points, 0)

                        if withHoles:
                            transformedHolesPoints = []
                            for index, hole in enumerate(holesPoints):
                                transformedHolePoints = []
                                for point in hole:
                                    transformedPoint = point.Transform(toCS, fromCS)
                                    transformedHolePoints.append([transformedPoint.X, transformedPoint.Y])

                                # Make sure the transforme hole vertices are clockwise and the original points are ordered the same
                                if not isCounterClockwise(transformedHolePoints):
                                    transformedHolesPoints.append(transformedHolePoints)
                                else:
                                    transformedHolesPoints.append(np.flip(transformedHolePoints, 0))
                                    holesPoints[index] = np.flip(holesPoints[index], 0)

                            # Combine outer (polyPoints) and inner (transformedHolesPoints) boundaries
                            largestXs = []
                            largestXIndices = []
                            for hole in transformedHolesPoints:
                                largestX = float('-inf')
                                largestXIndex = 0
                                for index, point in enumerate(hole):
                                    if point[0] > largestX:
                                        largestX = point[0]
                                        largestXIndex = index
                                largestXs.append(largestX)
                                largestXIndices.append(largestXIndex)

                            holeOrder = np.flip(np.argsort(largestXs))

                            for holeIndex in holeOrder:
                                nextHole = transformedHolesPoints[holeIndex]

                                startVertex = nextHole[largestXIndices[holeIndex]]
                                shiftedHole = np.roll(nextHole, -1 * largestXIndices[holeIndex], 0)
                                shiftedHolePoints = np.roll(holesPoints[holeIndex], -largestXIndices[holeIndex])

                                try:
                                    edgeA, edgeB, edgeInt, edgeBIndex = getIntersectionEdge(polyPoints, startVertex)
                                except:
                                    print('ERROR connecting hole', polyPoints, startVertex, nextHole)
                                    continue

                                if equalPoints2D(edgeInt, edgeA):
                                    # Point A is already mutually visible
                                    edgeAIndex = edgeBIndex - 1
                                    if edgeAIndex < 0:
                                        edgeAIndex = len(transformedPoints) - 1

                                    polyPoints = np.concatenate((polyPoints[:edgeAIndex + 1], shiftedHole,
                                                                 [shiftedHole[0]], polyPoints[edgeAIndex:]))
                                    points = np.concatenate((points[:edgeAIndex + 1], shiftedHolePoints,
                                                             [shiftedHolePoints[0]], points[edgeAIndex:]))
                                    continue
                                elif equalPoints2D(edgeInt, edgeB):
                                    polyPoints = np.concatenate((polyPoints[:edgeBIndex + 1], shiftedHole,
                                                                 [shiftedHole[0]], polyPoints[edgeBIndex:]))
                                    points = np.concatenate((points[:edgeBIndex + 1], shiftedHolePoints,
                                                             [shiftedHolePoints[0]], points[edgeBIndex:]))
                                    continue
                                else:
                                    candidatePoint = edgeA if edgeA[0] >= edgeB[0] else edgeB
                                    candidateIndex = edgeBIndex - 1 if edgeA[0] >= edgeB[0] else edgeBIndex
                                    otherCandidateIndices = []
                                    for index, point in enumerate(polyPoints):
                                        prevIndex = index - 1
                                        nextIndex = index + 1 if index + 1 < len(polyPoints) else 0
                                        if not isConvex(polyPoints[prevIndex], point,
                                                        polyPoints[nextIndex]) and insideTriangle(startVertex, edgeInt,
                                                                                                  candidatePoint,
                                                                                                  point):
                                            otherCandidateIndices.append(index)

                                    distance = 0
                                    for index in otherCandidateIndices:
                                        point = transformedPoints[index]
                                        nextDistance = squareDistancePoints2D(startVertex, point)
                                        if nextDistance > distance:
                                            distance = nextDistance
                                            candidateIndex = index

                                    polyPoints = np.concatenate((polyPoints[:candidateIndex + 1], shiftedHole,
                                                                 [shiftedHole[0]], polyPoints[candidateIndex:]))
                                    points = np.concatenate((points[:candidateIndex + 1], shiftedHolePoints,
                                                             [shiftedHolePoints[0]], points[candidateIndex:]))

                        # print('TRANSFORM', polyPoints)

                        # Triangulate
                        triangulation = triangulate(polyPoints)

                        # print('TRIANGULATE', triangulation)

                        # Piece the mesh together
                        for triangle in triangulation:
                            for vertex in triangle:
                                threeDPoint = points[vertex]
                                pointIndex = pointInList(threeDPoint, vertexList)
                                if pointIndex > -1:
                                    indexList.append(pointIndex)
                                else:
                                    vertexList.append(threeDPoint)
                                    indexList.append(len(vertexList) - 1)

                meshIndices = List[int](indexList)  # would fail when using 'indices' directly
                simpleMesh = mtk.Mesh.ByVerticesAndIndices(vertexList, meshIndices)
                improvedMesh = mtk.Mesh.Repair(simpleMesh)
                meshGeometries.append(improvedMesh)

            # Assign your output to the OUT variable.
            OUT = meshGeometries

            # print('TRIANGULATE', triangulation)

            # Piece the mesh together
            for triangle in triangulation:
                for vertex in triangle:
                    threeDPoint = points[vertex]
                    pointIndex = pointInList(threeDPoint, vertexList)
                    if pointIndex > -1:
                        indexList.append(pointIndex)
                    else:
                        vertexList.append(threeDPoint)
                        indexList.append(len(vertexList) - 1)

    meshIndices = List[int](indexList)  # would fail when using 'indices' directly
    simpleMesh = mtk.Mesh.ByVerticesAndIndices(vertexList, meshIndices)
    improvedMesh = mtk.Mesh.Repair(simpleMesh)
    meshGeometries.append(improvedMesh)

# Assign your output to the OUT variable.
OUT = meshGeometries
