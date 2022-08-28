#script ulozi vystupni soubor pod nazvem sys.argv[2] do uloziste vstupniho souboru
import arcpy, math, sys, os, arcgisscripting

if len(sys.argv) < 5:
    exit("Error: Byl zadan nedostatecny pocet parametru: 1. nazev scriptu, 2. bodova feature class v souradnicovem systemu S-JTSK Krovak East North (EPSG:5514), 3. nazev vystupniho souboru, 4. sloupec s typem diagramu, 5. sloupec s velikosti diagramu")

#vstupni soubor musi byt v souradnicovem systemu S-JTSK Krovak East North (EPSG:5514)
points = sys.argv[1]
diagrams = sys.argv[2]
type_field = sys.argv[3]
size_field = sys.argv[4]

abs_path = os.path.abspath(points)
arcpy.env.workspace = os.path.dirname(abs_path)

if arcpy.Exists(diagrams):
    arcpy.Delete_management(diagrams)

sr = arcpy.Describe(points).spatialReference
try:
    arcpy.CreateFeatureclass_management(arcpy.env.workspace, diagrams, "POLYGON", points, spatial_reference = sr)
except arcgisscripting.ExecuteError:
    if "ERROR 999999" in arcpy.GetMessages(2):
            exit("Error: Zadejte pouze nazev vystupniho souboru, ulozi se do uloziste vstupniho souboru")

scur = arcpy.da.SearchCursor(points, ["SHAPE@", type_field, size_field])
icur = arcpy.da.InsertCursor(diagrams, ["SHAPE@", type_field, size_field])

for row in scur:
    inGeom = row[0]
    pnt = inGeom.getPart(0)
    X = pnt.X
    Y = pnt.Y
    diagram_type = row[1]
    size = row[2]

    outGeom = arcpy.Array()
    if diagram_type == "S":
        A = arcpy.Point(X - 0.5*size, Y - 0.5*size)
        B = arcpy.Point(X - 0.5*size, Y + 0.5*size)
        C = arcpy.Point(X + 0.5*size, Y + 0.5*size)
        D = arcpy.Point(X + 0.5*size, Y - 0.5*size)
        E = arcpy.Point(X - 0.5*size, Y - 0.5*size)
        polygon_vertexes = [A, B, C, D, E]           
   
    elif diagram_type == "T":
        A = arcpy.Point(X - 0.5*size, Y - math.tan(math.radians(60))*size*1/6)
        B = arcpy.Point(X, Y + math.tan(math.radians(60))*size*1/3)
        C = arcpy.Point(X + 0.5*size, Y - math.tan(math.radians(60))*size*1/6)
        D = arcpy.Point(X - 0.5*size, Y - math.tan(math.radians(60))*size*1/6)
        polygon_vertexes = [A, B, C, D]

    elif diagram_type == "C":
        icur.insertRow((inGeom.buffer(size), diagram_type, size))
        continue

    for vertex in polygon_vertexes:
        outGeom.add(vertex)
    
    icur.insertRow((arcpy.Polygon(outGeom), diagram_type, size))

del scur, icur