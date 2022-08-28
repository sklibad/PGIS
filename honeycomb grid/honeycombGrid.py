#script ulozi vystupni soubor pod nazvem sys.argv[2] do uloziste vstupniho souboru
import arcpy, math, sys, arcgisscripting, os

def get_initial_coordinates(input_file):
    scur = arcpy.da.SearchCursor(input_file, ["SHAPE@"])
    a = True
    for row in scur:
        if a:
            inGeom = row[0]
            pnt = inGeom.getPart(0)
            a = False
    del scur
    return pnt.X, pnt.Y

def add_point_to_arcpy_array(X, Y, arcpy_array):
    pnt = arcpy.Point(X, Y)
    arcpy_array.add(pnt)
    return arcpy_array

def create_col(rows, X, Y, size, arcpy_array):
    r = 1
    while r != rows/2:
        Y = Y + math.sin(math.radians(60))*size*2
        arcpy_array = add_point_to_arcpy_array(X, Y, arcpy_array)
        r += 1
    return arcpy_array

def create_list_of_centroids(size, nrows, ncols, X, Y):
    centroids = arcpy.Array()
    centroids = add_point_to_arcpy_array(X, Y, centroids)
    
    odd_rows = nrows
    if nrows % 2 != 0:
        odd_rows -= 1

    even_rows = nrows
    if nrows % 2 != 0:
        even_rows += 1    

    while True:
        X0 = X
        Y0 = Y
        if nrows > 3:
            centroids = create_col(odd_rows, X, Y, size, centroids)
        
        ncols -= 1
        if ncols == 0:
            break
        
        X = X0 + size + math.cos(math.radians(60))*size
        Y = Y0 - math.sin(math.radians(60))*size
        centroids = add_point_to_arcpy_array(X, Y, centroids)
        
        centroids = create_col(even_rows, X, Y, size, centroids)
        
        ncols -= 1
        if ncols == 0:
            break

        X = X0 + 3*size 
        Y = Y0
        centroids = add_point_to_arcpy_array(X, Y, centroids)
    
    return centroids

def get_hexagon_coordinates(X, Y, size):
    degrees = [0, 60, 120, 180, 240, 300, 0]
    outGeom = arcpy.Array()
    for d in degrees:
        pnt = arcpy.Point(X + size*math.cos(math.radians(d)), Y + size*math.sin(math.radians(d)))
        outGeom.add(pnt)
    return outGeom

def draw_honeycomb_grid(output_file, centroids, size):
    icur = arcpy.da.InsertCursor(output_file, ["SHAPE@"])
    for pnt in centroids:
        outGeom = get_hexagon_coordinates(pnt.X, pnt.Y, size)
        icur.insertRow([arcpy.Polygon(outGeom)])
    del icur


if len(sys.argv) < 6:
    exit("Error: Byl zadan nedostatecny pocet parametru: 1. nazev scriptu, 2. bodova feature class v souradnicovem systemu S-JTSK Krovak East North (EPSG:5514), 3. nazev vystupniho souboru, 4. velikost polomeru kruznice opsane sestiuhelniku, 5. pocet radku, 6. pocet sloupcu")

#vstupni soubor musi byt v souradnicovem systemu S-JTSK Krovak East North (EPSG:5514)
points = sys.argv[1]
honeycomb = sys.argv[2]
size = int(sys.argv[3])
nrows = int(sys.argv[4])
ncols = int(sys.argv[5])

if nrows == 1 and ncols == 2 or nrows == 2 and ncols == 1:
    exit("ERROR: Nelze vytvorit sestiuhelnikova sit s jednim sloupcem a dvema radky a obracene")

abs_path = os.path.abspath(points)
arcpy.env.workspace = os.path.dirname(abs_path)

if arcpy.Exists(honeycomb):
    arcpy.Delete_management(honeycomb)

sr = arcpy.Describe(points).spatialReference

try:
    arcpy.CreateFeatureclass_management(arcpy.env.workspace, honeycomb, "POLYGON", spatial_reference = sr)
except arcgisscripting.ExecuteError:
    if "ERROR 999999" in arcpy.GetMessages(2):
            exit("Error: Zadejte pouze nazev vystupniho souboru, ulozi se do uloziste vstupniho souboru")

X, Y = get_initial_coordinates(points)

centroids = create_list_of_centroids(size, nrows, ncols, X, Y)

draw_honeycomb_grid(honeycomb, centroids, size)