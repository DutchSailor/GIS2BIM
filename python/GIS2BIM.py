## GIS2BIM Library

def GIS2BIM_CreateBoundingBox(CoördinateX,CoördinateY,BoxWidth,BoxHeight,DecimalNumbers):
    XLeft = round(CoördinateX-0.5*BoxWidth,DecimalNumbers)
    XRight = round(CoördinateX+0.5*BoxWidth,DecimalNumbers)
    YBottom = round(CoördinateY-0.5*BoxWidth,DecimalNumbers)
    YTop = round(CoördinateY+0.5*BoxWidth,DecimalNumbers)

    boundingBoxString1 = str(XLeft) + "," + str(YBottom) + "," + str(XRight) + "," + str(YTop)
    return boundingBoxString1

a = GIS2BIM_CreateBoundingBox(1000,1000,200,200,0)

print(a)