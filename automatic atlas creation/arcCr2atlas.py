# -*- coding: utf-8 -*-
import arcpy, arcgisscripting

arcpy.env.overwriteOutput = 1

symbology = "C:\\PGIS\\arcCr2atlas\\okres.mxd"
arcCRAdminGdb = "C:\\PGIS\\AdministrativniCleneni_v13.gdb"
arcCR500Gdb = "C:\\PGIS\\ArcCR500_v33.gdb"
result = "C:\\PGIS\\arcCr2atlas\\atlas.pdf"
#okresy = "C:\\PGIS\\arcCr2atlas\\okresy.shp"
okresy = "C:\\PGIS\\\AdministrativniCleneni_v13.gdb\\OkresyPolygony"
obce_polygony = "C:\\PGIS\\\AdministrativniCleneni_v13.gdb\\ObcePolygony"
#obce_polygony = "C:\\PGIS\\arcCr2atlas\\obce.shp"
obce_body = "C:\\PGIS\\AdministrativniCleneni_v13.gdb\\ObceBody"
vodni_toky = "C:\\PGIS\\ArcCR500_v33.gdb\\VodniToky"
silnice = "C:\\PGIS\\ArcCR500_v33.gdb\\Silnice_2016"

pdf = "C:\\PGIS\\arcCr2atlas\\okres.pdf"
pdfDoc = arcpy.mapping.PDFDocumentCreate("C:\\PGIS\\arcCr2atlas\\atlas_pokus2.pdf")
mxd = arcpy.mapping.MapDocument(symbology)

dfs = arcpy.mapping.ListDataFrames(mxd)
layerList_okres = arcpy.mapping.ListLayers(dfs[0])
layerList_prehledka = arcpy.mapping.ListLayers(dfs[1])

kartogram_layer = layerList_okres[3]
obec_layer = layerList_okres[0]
silnice_layer = layerList_okres[1]
vodni_tok_layer = layerList_okres[2]
okres_bod_layer = layerList_prehledka[0]

obce_polygony_output = "C:\\PGIS\\arcCr2atlas\\okresy\\temp_obce_polygony.shp"
obce_body_output = "C:\\PGIS\\arcCr2atlas\\okresy\\temp_obce_body.shp"
silnice_output = "C:\\PGIS\\arcCr2atlas\\okresy\\temp_silnice.shp"
vodni_toky_output = "C:\\PGIS\\arcCr2atlas\\okresy\\temp_vodni_toky.shp"
okres_bod_output = "C:\\PGIS\\arcCr2atlas\\okresy\\temp_okres_bod.shp"

arcpy.MakeFeatureLayer_management(okresy, "okresy_lyr")
a = 1
scur = arcpy.da.SearchCursor(okresy, ["NAZ_LAU1"])
for row in scur:
    print(a)
    arcpy.SelectLayerByAttribute_management("okresy_lyr", "NEW_SELECTION", """"NAZ_LAU1" = '{}'""".format(row[0]))
    okres_output = "C:\\PGIS\\arcCr2atlas\\okresy\\temp_okres.shp"
    arcpy.CopyFeatures_management("okresy_lyr", okres_output)

    #try:
    #    arcpy.CopyFeatures_management("okresy_lyr", okres_output)
    #except arcgisscripting.ExecuteError:
    #    index = row[0].find("-")
    #    zezadu = -(len(row[0]) - index - 1)
    #    okres_output = "C:\\PGIS\\arcCr2atlas\\okresy\\" + row[0][0:index] + "_" + row[0][zezadu:] + ".shp"
    #    arcpy.CopyFeatures_management("okresy_lyr", okres_output)

    extent = arcpy.Describe(okres_output).extent
    dfs[0].extent = extent
    mxd.title = row[0]

    #if row[0].find("-") == -1:
    #    obce_polygony_output = "C:\\PGIS\\arcCr2atlas\\okresy\\" + str(row[0]) + "_obce.shp"
    #else:
    #    index = row[0].find("-")
    #    zezadu = -(len(row[0]) - index - 1)
    #    obce_polygony_output = "C:\\PGIS\\arcCr2atlas\\okresy\\" + row[0][0:index] + "_" + row[0][zezadu:] + "_obce.shp"

    arcpy.Clip_analysis(obce_polygony, okres_output, obce_polygony_output)
    arcpy.AddField_management(obce_polygony_output, "hustota", "DOUBLE", field_alias = "obyv./km^2")
    #arcpy.CalculateField_management(obce_polygony_output, "hustota", "[OB01] *100000 / [AREA]")
    arcpy.CalculateField_management(obce_polygony_output, "hustota", "[POCET_OBYV] *100000 / [SHAPE_Area]")

    kartogram_layer.replaceDataSource("C:\\PGIS\\arcCr2atlas\\okresy", "SHAPEFILE_WORKSPACE", "temp_obce_polygony", True)
    kartogram_layer.symbology.numClasses = 5
    kartogram_layer.symbology.reclassify()
    
    arcpy.Clip_analysis(obce_body, okres_output, obce_body_output)
    obec_layer.replaceDataSource("C:\\PGIS\\arcCr2atlas\\okresy", "SHAPEFILE_WORKSPACE", "temp_obce_body", True)
    arcpy.Clip_analysis(vodni_toky, okres_output, vodni_toky_output, 100)
    vodni_tok_layer.replaceDataSource("C:\\PGIS\\arcCr2atlas\\okresy", "SHAPEFILE_WORKSPACE", "temp_vodni_toky", True)
    arcpy.Clip_analysis(silnice, okres_output, silnice_output, 100)
    silnice_layer.replaceDataSource("C:\\PGIS\\arcCr2atlas\\okresy", "SHAPEFILE_WORKSPACE", "temp_silnice", True)
    
    arcpy.FeatureToPoint_management(okres_output, okres_bod_output)
    okres_bod_layer.replaceDataSource("C:\\PGIS\\arcCr2atlas\\okresy", "SHAPEFILE_WORKSPACE", "temp_okres_bod", True)

    #mxd.saveACopy("C:\\PGIS\\arcCr2atlas\\okres_" + str(a) + "pokus.mxd")
    #mxd2 = arcpy.mapping.MapDocument("C:\\PGIS\\arcCr2atlas\\okres_" + str(a) + "pokus.mxd")
    arcpy.mapping.ExportToPDF(mxd, pdf)
    pdfDoc.appendPages(pdf)
    #del mxd2
    a +=1


pdfDoc.saveAndClose()