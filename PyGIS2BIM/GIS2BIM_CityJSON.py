from packages.GIS2BIM.GIS2BIM_NL import *
from packages.GIS2BIM.GIS2BIM import *
from project.fileformat import *
from packages.GIS2BIM.GIS2BIM_NL_helpers import *
import json
import os
import time
import ijson
import sys
import random

#SETTINGS
lst = NL_GetLocationData(NLPDOKServerURL,"Dordrecht", "werf van schouten", "501")
Bboxwidth = 250 #m
cityJSONFolder = "C:/TEMP/GIS/cityJSON/"
maximumLoD = 2.2

#BOUNDINGBOX
RdX = lst[0]
RdY = lst[1]
GISBbox = GisRectBoundingBox().Create(RdX,RdY,Bboxwidth,Bboxwidth,0)
start = time.time()
bbox = GISBbox.boundingBoxXY
projectLocation = [RdX, RdY, 0]
scaleFactor = 1000
transformedBBox = [
    (bbox[0] - projectLocation[0]) * scaleFactor,
    (bbox[1] - projectLocation[1]) * scaleFactor,
    (bbox[2] - projectLocation[0]) * scaleFactor,
    (bbox[3] - projectLocation[1]) * scaleFactor
] if len(bbox) == 4 else []

#CITYJSON FILES
filePaths = []
for file in os.listdir(cityJSONFolder):
    if file.endswith(".json"):
        filepath = os.path.join(cityJSONFolder, file)
        filePaths.append(filepath)
        print(filepath)

def translateVertex(vertices, index, transform):
    vertex = list(vertices[index])
    if len(transform.get('scale', [])) == 3 and len(transform.get('translate', [])) == 3:
        vertex[0] = round(
            ((vertex[0] * transform['scale'][0]) + transform['translate'][0] - projectLocation[0]) * scaleFactor)
        vertex[1] = round(
            ((vertex[1] * transform['scale'][1]) + transform['translate'][1] - projectLocation[1]) * scaleFactor)
        vertex[2] = round(
            ((vertex[2] * transform['scale'][2]) + transform['translate'][2] - projectLocation[2]) * scaleFactor)
    else:
        vertex[0] = round((vertex[0] - projectLocation[0]) * scaleFactor)
        vertex[1] = round((vertex[1] - projectLocation[1]) * scaleFactor)
        vertex[2] = round((vertex[2] - projectLocation[2]) * scaleFactor)
    return vertex

def sitsInsideBBox(vertex):
    if len(transformedBBox) == 4:
        return transformedBBox[0] < vertex[0] < transformedBBox[2] and transformedBBox[1] < vertex[1] < transformedBBox[
            3]
    else:
        return True

def parseGeometry(geometries, vertices, decompressionTransform, filterBBox=True, cutGeometries=False,
                  includeHoles=False):
    outVolBoundary = []
    insideBBox = False
    # Find highest lod
    targetLoD = 0;
    targetGeoIndex = -1;
    for index, geometry in enumerate(geometries):
        geoLoD = float(geometry['lod'])
        if targetLoD < geoLoD and geoLoD <= maximumLoD:
            targetLoD = geoLoD
            targetGeoIndex = index

    if targetGeoIndex > -1:
        selectedGeometry = geometries[targetGeoIndex]
        if selectedGeometry['type'] == 'Solid':
            # TODO: Only supports whole solids atm. Inner shells would be defined in following indices
            for faceBoundaries in selectedGeometry['boundaries'][0]:
                boundaryInsideBBox = False
                outSrfBoundary = []
                # If Holes are included they are returned as consecutive arrays in the surface boundary.
                if includeHoles:
                    for boundary in faceBoundaries:
                        outPolyBoundary = []
                        for vertexIndex in boundary:
                            vertex = translateVertex(vertices, vertexIndex, decompressionTransform)
                            outPolyBoundary.append(vertex)
                            if sitsInsideBBox(vertex):
                                insideBBox = True
                                boundaryInsideBBox = True
                        outSrfBoundary.append(outPolyBoundary)
                else:
                    for vertexIndex in faceBoundaries[0]:
                        vertex = translateVertex(vertices, vertexIndex, decompressionTransform)
                        outSrfBoundary.append(vertex)
                        if sitsInsideBBox(vertex):
                            insideBBox = True
                            boundaryInsideBBox = True
                if boundaryInsideBBox or not cutGeometries:
                    outVolBoundary.append(outSrfBoundary)
        if selectedGeometry['type'] == 'MultiSurface':
            for faceBoundaries in selectedGeometry['boundaries']:
                boundaryInsideBBox = False
                outSrfBoundary = []
                # If Holes are included they are returned as consecutive arrays in the surface boundary.
                if includeHoles:
                    for boundary in faceBoundaries:
                        outPolyBoundary = []
                        for vertexIndex in boundary:
                            vertex = translateVertex(vertices, vertexIndex, decompressionTransform)
                            outPolyBoundary.append(vertex)
                            if sitsInsideBBox(vertex):
                                insideBBox = True
                                boundaryInsideBBox = True
                        outSrfBoundary.append(outPolyBoundary)
                else:
                    for vertexIndex in faceBoundaries[0]:
                        vertex = translateVertex(vertices, vertexIndex, decompressionTransform)
                        outSrfBoundary.append(vertex)
                        if sitsInsideBBox(vertex):
                            insideBBox = True
                            boundaryInsideBBox = True
                if boundaryInsideBBox or not cutGeometries:
                    outVolBoundary.append(outSrfBoundary)

        if insideBBox or not filterBBox:
            return outVolBoundary
        else:
            return None
    else:
        return None

def parseAttributes(attributes, objectKey):
    availableKeys = attributes.keys()
    result = {}

    # The id might not always be the objecyKey but for the BAG files it seems to be the most reliable
    result['cadastre_id'] = objectKey

    # Attributes can be different from file to file: update/extend if-checks to adjust to new ones
    if 'bouwjaar' in availableKeys:
        result['year_of_construction'] = int(attributes['bouwjaar'])
    if 'oorspronkelijkbouwjaar' in availableKeys:
        result['year_of_construction'] = int(attributes['oorspronkelijkbouwjaar'])
    if 'status' in availableKeys:
        result['usage_status'] = attributes['status']
    if 'pandstatus' in availableKeys:
        result['usage_status'] = attributes['pandstatus']

    return result

def cityJSONParser(filePaths):
    # START PARSING

    if type(filePaths) != list:
        filePaths = [filePaths]

    print('BBOX', transformedBBox)
    print('LoD', maximumLoD)

    buildings = []
    bridges = []
    roads = []
    railways = []
    landuses = []
    plantcovers = []
    waterways = []
    waterbodies = []
    generics = []
    reliefs = []

    decompressionTransform = {}

    # Open and Parse JSON file(s)

    for filePath in filePaths:
        with open(filePath, 'rb') as f:

            # Step 1: Read Metadata and Transform (if available)

            transformParser = ijson.kvitems(f, 'transform', use_float=True)
            for k, v in transformParser:
                decompressionTransform[k] = v

            # print('Transform', decompressionTransform)

            # also possible to read out: referenceSystem/EPSG, thematicModels (occuring cityObject types), ...
            # metadataParser = ijson.kvitems(f, 'metadata')
            # f.seek(0)

            # Reset File Cursor Between parses:
            f.seek(0)

            # Step 2: Read Vertices
            vertices = list(ijson.items(f, 'vertices'))[0]

            # Reset File Cursor Between parses:
            f.seek(0)

            # Step 3: Read CityObjects and extract and decompress (transform & translate) coordinate, filter LOD and BBox
            cityObjectsParser = ijson.kvitems(f, 'CityObjects')

            waitingBuildings = {}
            waitingBuildingParts = {}

            for k, v in cityObjectsParser:
                if v['type'] == 'Building':
                    geometries = []
                    attributes = {}
                    missingChildren = []
                    if 'children' in v.keys():
                        for child in v['children']:
                            if child in waitingBuildingParts.keys():
                                part = waitingBuildingParts.pop(child)
                                geometries += part['geometry']
                                attributes = {**attributes, **parseAttributes(part['attributes'], child)}
                            else:
                                missingChildren.append(child)

                    geometries += v['geometry']
                    attributes = {**attributes, **parseAttributes(v['attributes'], k)}

                    if len(missingChildren) == 0:
                        # building complete: parse complete geometry
                        geometry = parseGeometry(geometries, vertices, decompressionTransform, True, False, True)

                        if geometry is not None:
                            buildings.append({
                                'geometry': geometry,
                                'attributes': attributes
                            })
                    else:
                        waitingBuildings[k] = {
                            'geometries': geometries,
                            'attributes': attributes,
                            'missingChildren': missingChildren
                        }

                if v['type'] == 'BuildingPart':
                    # TODO: Support multiple parents??
                    parentId = v['parents'][0]
                    if parentId in waitingBuildings.keys():
                        building = waitingBuildings[parentId]
                        building['geometries'] += v['geometry']
                        building['attributes'] = {**building['attributes'], **parseAttributes(v['attributes'], k)}

                        building['missingChildren'].remove(k)

                        if len(building['missingChildren']) == 0:
                            # building complete: parse complete geometry
                            geometry = parseGeometry(geometries, vertices, decompressionTransform, True, False, True)

                            if geometry is not None:
                                buildings.append({
                                    'geometry': geometry,
                                    'attributes': attributes
                                })

                        else:
                            waitingBuildingParts[k] = {
                                'geometry': geometry,
                                'attributes': attributes
                            }

                if v['type'] == 'Bridge':
                    geometry = parseGeometry(v['geometry'], vertices, decompressionTransform)
                    if geometry is not None:
                        bridges.append(geometry)
                if v['type'] == 'Road':
                    geometry = parseGeometry(v['geometry'], vertices, decompressionTransform, True, True)
                    if geometry is not None:
                        roads.append(geometry)
                if v['type'] == 'Railway':
                    geometry = parseGeometry(v['geometry'], vertices, decompressionTransform, True, True)
                    if geometry is not None:
                        railways.append(geometry)
                if v['type'] == 'LandUse':
                    geometry = parseGeometry(v['geometry'], vertices, decompressionTransform, True, True)
                    if geometry is not None:
                        landuses.append(geometry)
                if v['type'] == 'PlantCover':
                    geometry = parseGeometry(v['geometry'], vertices, decompressionTransform, True, True)
                    if geometry is not None:
                        plantcovers.append(geometry)
                if v['type'] == 'Waterway':
                    geometry = parseGeometry(v['geometry'], vertices, decompressionTransform, True, True)
                    if geometry is not None:
                        waterways.append(geometry)
                if v['type'] == 'WaterBody':
                    geometry = parseGeometry(v['geometry'], vertices, decompressionTransform, True, True)
                    if geometry is not None:
                        waterbodies.append(geometry)
                if v['type'] == 'GenericCityObject':
                    geometry = parseGeometry(v['geometry'], vertices, decompressionTransform)
                    if geometry is not None:
                        generics.append(geometry)
                if v['type'] == 'TINRelief':
                    geometry = parseGeometry(v['geometry'], vertices, decompressionTransform, True, True)
                    if geometry is not None:
                        reliefs.append(geometry)

    # DEBUG and TIMING
    end = time.time()
    print('Found',
        len(buildings), 'buildings,',
        len(bridges), 'bridges,',
        len(roads), 'roads,',
        len(railways), 'railways,',
        len(landuses), 'landuse items,',
        len(plantcovers), 'plant cover items,',
        len(waterways), 'waterways,',
        len(waterbodies), 'water bodies,',
        len(generics), 'other items and',
        len(reliefs), 'TIN reliefs.'
    )
    print('Execution time:', end - start, 'seconds')

    # Object Types in Example
    # Building
    # Bridge
    # Road
    # GenericCityObject
    # LandUse
    # PlantCover
    # WaterBody
    #
    # see here for full schema: https://3d.bk.tudelft.nl/schemas/cityjson/1.1.3/cityobjects.schema.json

    return buildings, bridges, roads, railways, landuses, plantcovers, waterways, waterbodies, generics, reliefs

lst = cityJSONParser(filePaths)

print(lst)