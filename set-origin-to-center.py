import xml.etree.ElementTree as ET
import string
import sys
import math
import uuid

# generate new uuid
def get_id():
    return uuid.uuid4().hex

# get the vertex points from the bline
def get_vertex_points(item):
    x_points = []
    y_points = []
    for vertex in list(list(item)[0]):
        x = list(list(list(list(vertex)[0])[0])[0])[0].text
        x_points.append(float(x))
        y = list(list(list(list(vertex)[0])[0])[0])[1].text
        y_points.append(float(y))
    return [x_points, y_points]

# get the true center of the object
def get_true_center(x_points, y_points):
    RectVertices = []
    RectVertices.append([max(y_points), min(x_points)])
    RectVertices.append([min(y_points), max(x_points)])
    return [ (RectVertices[0][0] + RectVertices[1][0]) / 2, (RectVertices[0][1] + RectVertices[1][1]) / 2 ]

def get_distance(point1, point2 = [0, 0]):
    return math.sqrt(math.pow(point1[0] - point2[1], 2) + math.pow(point1[0] - point2[1], 2))

# get x value from a vertex
def get_x(vertex):
    return list(list(list(list(vertex)[0])[0])[0])[0]

# get y value from a vertex
def get_y(vertex):
    return list(list(list(list(vertex)[0])[0])[0])[1]

# update the vertex data
def update_vertex_data(parent, solution):
    for child in parent:
        if(child.attrib['name'] == "bline"):
            for vertex in list(list(child)[0]):
                get_x(vertex).text = str(float(get_x(vertex).text) - solution[1])
                get_y(vertex).text = str(float(get_y(vertex).text) - solution[0])
        if(child.attrib['name'] == "origin"):
            list(list(child)[0])[0].text = str(solution[1])
            list(list(child)[0])[1].text = str(solution[0])


tree = ET.parse(sys.argv[1])
root = tree.getroot()
rootChildren = list(root.iter('layer'))

def centerOriginForBline(bline):
    if(child.attrib['name'] == "bline" ):
            vertex_points= get_vertex_points(child)
            x_points = vertex_points[0]
            y_points = vertex_points[1]
            solution = get_true_center(x_points, y_points)
            if(solution[0] != 0):
                slopeOfLine = solution[1] / solution[0]
                distance = get_distance(solution)
                update_vertex_data(layer, solution)

def centerOriginForGroup(group):
    if(group.attrib['type'] == "group"):
        layerList = group.findall('.//layer')
        x_points= []
        y_points= []
        for layer in layerList:
            bline = layer.findall('.//bline')
            if(len(list(bline))):
                originX = float(layer.find("./param[@name='origin']")[0][0].text)
                originY = float(layer.find("./param[@name='origin']")[0][1].text)
                temp_x_points = []
                temp_y_points = []
                for entry in list(bline):
                    temp_x_points.extend(list(entry.iter('x')))
                    temp_y_points.extend(list(entry.iter('y')))
                for i, x in enumerate(temp_x_points):
                    temp_x_points[i] = float(x.text) + originX
                for i, y in enumerate(temp_y_points):
                    temp_y_points[i] = float(y.text) + originY
                x_points.extend(temp_x_points)
                y_points.extend(temp_y_points)
        solution = get_true_center(x_points, y_points)

        # print solution and group name
        print(solution)
        print(group.attrib.get('desc', "unnamed group"))

        for param in list(group):
            if(param.attrib['name'] == "origin"):
                origin = param 
                origin[0][0].text = str(solution[1])
                origin[0][1].text = str(solution[0])
            if(param.attrib['name'] == "transformation"):
                try:
                    vector = param[0][0][0][0][0]
                except:
                    vector = param[0][0][0]
                if(float(vector[0].text) == 0):
                    vector[0].text = str(solution[1])
                if(float(vector[1].text) == 0):
                    vector[1].text = str(solution[0])
                    pass
        pass

for layer in rootChildren:
    for child in layer:
        centerOriginForBline(child)
        

rootChildren = root.findall("layer")

def findChildGroup(parent):
    for child in parent:
        if('type' in child.attrib):
            if(child.attrib['type'] == "group"):
                findChildGroup(child[5][0].findall("layer"))
                centerOriginForGroup(child)
            elif(child.attrib['type'] == "bline"):
                centerOriginForBline(child)     
        else:
            print(child)   
    

findChildGroup(rootChildren)

if((len(sys.argv) > 2 )):
    output = sys.argv[2]
else:
    output = sys.argv[1]

tr2ee = ET.ElementTree(root)
with open(output, "wb") as fh:
    tr2ee.write(fh)