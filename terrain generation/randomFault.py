# -*- coding:utf-8 -*-
import arcpy, numpy, random, math, sys

#funkce vracející pozice dvou bodů v matici (řádek, sloupec), které určují náhodnou poruchu
def get_random_boundary_pair(row_amount, column_amount):
    n = random.randint(0, 1)
    if n == 0:
        row_coord1 = random.randint(1, row_amount)
        m = random.randint(0, 1)
        if m == 0:
            col_coord1 = 1
        else:
            col_coord1 = column_amount
    else:
        col_coord1 = random.randint(1, column_amount)
        m = random.randint(0, 1)
        if m == 0:
            row_coord1 = 1
        else:
            row_coord1 = row_amount

    o = random.randint(0, 1)
    if o == 0:
        if row_coord1 == 1:
            row_coord2 = random.randint(2, row_amount)
        elif row_coord1 == row_amount:
            row_coord2 = random.randint(1, row_amount - 1)
        else:
            row_coord2 = random.randint(1, row_amount)  
  
        if n == 0:
            if m == 0:
                col_coord2 = column_amount
            else:
                col_coord2 = 1
        else:
            if col_coord1 == 1:
                col_coord2 = column_amount
            elif col_coord1 == column_amount:
                col_coord2 = 1
            else:
                p = random.randint(0, 1)
                if p == 0:
                    col_coord2 = 1
                else:
                    col_coord2 = column_amount
    else:
        if col_coord1 == 1:
            col_coord2 = random.randint(2, column_amount)
        elif col_coord1 == column_amount:
            col_coord2 = random.randint(1, column_amount - 1)
        else:
            col_coord2 = random.randint(1, column_amount)

        if n == 1:
            if m == 0:
                row_coord2 = row_amount
            else:
                row_coord2 = 1
        else:
            if row_coord1 == 1:
                row_coord2 = row_amount
            elif row_coord1 == row_amount:
                row_coord2 = 1
            else:
                q = random.randint(0, 1)
                if q == 0:
                    row_coord2 = 1
                else:
                    row_coord2 = row_amount
    return [row_coord1, col_coord1], [row_coord2, col_coord2]

#funkce vracející matici v podobě seznamu souřadnic jednotlivých pixelů
def adjust_coordinates_to_pixels(rows, cols, width, height):
    outer_array = []
    for r in range(0, rows):
        y = rasYmax - 0.5*height - height*r
        inner_array = []
        for c in range(0, cols):
            x = rasXmin + 0.5*width + width*c
            inner_array.append([x, y])
        outer_array.append(inner_array)
    return outer_array

#funkce vracející matici po proběhnutí algoritmu náhodných poruch
def random_faults(array, outer_array, mean, std, hurst_exp, variance, iterations):
    for i in range(1, iterations):
        print(i)
        delta = round(numpy.random.normal(mean, std), 0)
        a, b = get_random_boundary_pair(rows, cols)
        a_coords = outer_array[a[0] - 1][a[1] - 1]
        b_coords = outer_array[b[0] - 1][b[1] - 1]
        condition1 = a_coords[0] == x_min or a_coords[0] == x_max
        condition2 = b_coords[0] == x_min or b_coords[0] == x_max
        if condition1 or condition2:
            axis_vector = [0, y_max - y_min]
            if condition1:
                a_is_wanted = True
                pair_vector = [b_coords[0] - a_coords[0], b_coords[1] - a_coords[1]]
            else:
                a_is_wanted = False
                pair_vector = [a_coords[0] - b_coords[0], a_coords[1] - b_coords[1]]
        elif a_coords[1] == y_min or b_coords[1] == y_min:
            if a_coords[1] == y_min:
                a_is_wanted = True
            else:
                a_is_wanted = False
            axis_vector = [x_min - x_max, 0]
            if a_is_wanted:
                pair_vector = [b_coords[0] - a_coords[0], b_coords[1] - a_coords[1]]
            else:
                pair_vector = [a_coords[0] - b_coords[0], a_coords[1] - b_coords[1]]
        else:
            print("something went wrong")
        cos_alpha = (axis_vector[0]*pair_vector[0] + axis_vector[1]*pair_vector[1])/(math.sqrt(axis_vector[0]**2 + axis_vector[1]**2)*math.sqrt(pair_vector[0]**2 + pair_vector[1]**2))
        alpha = math.acos(cos_alpha)*180/math.pi
        row_count = 0
        rand_value = random.randint(0,1)
        for r in outer_array:
            col_count = 0
            for c in r:
                if a_is_wanted:
                    vector = [c[0] - a_coords[0], c[1] - a_coords[1]]
                else:
                    vector = [c[0] - b_coords[0], c[1] - b_coords[1]]
                if vector == [0, 0]:
                    array[row_count, col_count] += delta
                    col_count += 1
                    continue
                cos_beta = (axis_vector[0]*vector[0] + axis_vector[1]*vector[1])/(math.sqrt(axis_vector[0]**2 + axis_vector[1]**2)*math.sqrt(vector[0]**2 + vector[1]**2))
                beta = math.acos(cos_beta)*180/math.pi
                if beta > alpha:
                    if rand_value == 0:
                        array[row_count, col_count] -= delta
                    else:
                        array[row_count, col_count] += delta
                else:
                    if rand_value == 0:
                        array[row_count, col_count] += delta
                    else:
                        array[row_count, col_count] -= delta 
                col_count += 1
            row_count += 1
        variance = variance/2**(2*H*(i+1))
        if math.sqrt(variance) > 0:
            std = math.sqrt(variance)
    return array

#funkce vracející matici s přeškálovanými hodnotami vzhledem k maximální nadmořské výšce
def rescale_data_by_max_height(array, max_height):
    a_min = abs(numpy.amin(array))
    a_max = abs(numpy.amax(array))
    row_count = 0
    for row in array:
        col_count = 0
        for v in row:
            new_value = float(v + a_min)
            new_value = new_value/(a_min + a_max)
            new_value = new_value*max_height
            if new_value == 0:
                new_value = 1
            array[row_count, col_count] = round(new_value, 0)
            col_count += 1
        row_count += 1
    return array

if len(sys.argv) < 10:
    exit("Zadali jste nedostatečný počet vstupních argumentů: sys.argv[1] = počet řádků výsledného rastru, sys.argv[2] = počet sloupců výsledného rastru, sys.argv[3] = úložiště, sys.argv[4] = název výstupního rastru, sys.argv[5] = průměrná nadmořská výška odpovídající počátečnímu rozptylu, sys.argv[6] = směrodatná odchylka dat odpovídající počátečnímu rozptylu, sys.argv[7] = Hurstův exponent, sys.argv[8] = počet náhodných poruch (iterací), sys.argv[9] = maximální výška terénu")

rows = sys.argv[1]
cols = sys.argv[2]

path = sys.argv[3]
name = "empty_raster.tif"
size = 1
field_type = "16_BIT_UNSIGNED"
sr = "5514"
bands = 1

arcpy.env.workspace = path
arcpy.env.overwriteOutput = 1
arcpy.CreateRasterDataset_management(path, name, size, field_type, sr, bands)

in_raster = path + "\\" + name

array = numpy.zeros((cols, rows), dtype = int)

desc = arcpy.Describe(in_raster)

rasXmin = desc.Extent.XMin
rasYmax = desc.Extent.YMax
height = desc.MeanCellHeight
width = desc.MeanCellWidth

raster = arcpy.Raster(in_raster)
mx = raster.extent.XMin + raster.meanCellWidth * 0.5
my = raster.extent.YMin - raster.meanCellHeight * 0.5

x_min = rasXmin + 0.5*width
x_max = rasXmin + 0.5*width + width*(cols - 1)
y_min = rasYmax - 0.5*height - height*(rows - 1)
y_max = rasYmax - 0.5*height

outer_array = adjust_coordinates_to_pixels(rows, cols, width, height)

mean = sys.argv[5]
std = sys.argv[6]
variance = std**2
H = sys.argv[7]
iterations = sys.argv[8]

array = random_faults(array, outer_array, mean, std, H, variance, iterations)

max_height = sys.argv[9]

array = rescale_data_by_max_height(array, max_height)

raster = arcpy.NumPyArrayToRaster(array, arcpy.Point(mx, my), width, height, 0)
raster.save(sys.argv[4])

arcpy.Delete_management(path + "\\empty_raster.tif")