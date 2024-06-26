# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DronePath
                                 A QGIS plugin
 This plugin draws a drone flight path based on certain required inputs. The paths must be fed into drone mission planning softwares for adding further attributes.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2022-05-24
        git sha              : $Format:%H$
        copyright            : (C) 2022 by Technology for Wildlife Foundation
        email                : sravanthi@techforwildlife.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsProject
from PyQt5.QtWidgets import QAction,QMessageBox,QTableWidgetItem,QApplication,QFileDialog
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt,QPoint, QRegExp,QPointF
from PyQt5.QtGui import QIcon,QRegExpValidator,QPolygonF
from qgis.core import *
from qgis.PyQt.QtCore import *
# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .drone_path_dialog import DronePathDialog
from qgis.utils import iface
import os.path
import math, processing, ntpath
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from PyQt5.QtWidgets import *


class DronePath:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):                     
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """ 
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'DronePath_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Drone Path')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None
        self.dlg = None
        self.dlg = DronePathDialog()
        
        
    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('DronePath', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/drone_path/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Draw grid lines'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&Drone Path'),
                action)
            self.iface.removeToolBarIcon(action)

    def calD(self):
        #This function checks if all the camera parameters exist and based on that other parameters are calculated
        if ((self.dlg.lineEdit_3.text()=='') or (self.dlg.lineEdit.text()=='') or (self.dlg.lineEdit_6.text()=='')
        or (self.dlg.lineEdit_9.text()=='') or (self.dlg.lineEdit_10.text()=='')):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Camera Field Paramaeters Error")
            msg.setText("Please enter all Camera Field Parameters and calculate again.")
            msg.setStandardButtons(QMessageBox.Ok )
            return msg.exec_()
        self.alt = self.dlg.lineEdit.text()
        fov = self.dlg.lineEdit_3.text()                #Enter in degrees 
        fov = math.radians(float(fov))                  #Convert to radians
        print(int(self.alt))
        D = 2*int(self.alt)*math.tan((float(fov))/2)    #Diagonal of the drone image
        D  = round(D,2)
        self.dlg.lineEdit_4.setText(str(D))
        r = float(self.dlg.lineEdit_6.text())
        sideA = float(D)/(1+(r**2))                     #side A of the drone image
        sideA = round(sideA,2)
        sideB = r*float(sideA)                          #side B of the drone image
        sideB = round(sideB,2)
        area = round((sideA*sideB),2)                   #area of the drone image
        gsd = round(math.sqrt(area/(int(self.dlg.lineEdit_9.text())*int(self.dlg.lineEdit_10.text()))),4) #ground sampling distance
        
        x = float(self.dlg.lineEdit_2.text())/100
        
        self.dist = round(((1-x)*int(self.dlg.lineEdit_10.text())*gsd),3) #distance between gridlines to maintain overlap percentage
        
        self.dlg.lineEdit_7.setText(str(sideA))
        self.dlg.lineEdit_8.setText(str(sideB))
        self.dlg.lineEdit_11.setText(str(area))
        self.dlg.lineEdit_12.setText(str(gsd))
        self.dlg.lineEdit_13.setText(str(self.dist))
        return sideA,sideB, gsd, self.dist, area, D, fov, self.alt,r
    def linePathBrowse(self):
        self.save_dir_name = QFileDialog.getExistingDirectory(self,"Select Save Directory","/")
        print(self.save_dir_name)
        self.savePathEdit.setText(self.save_dir_name)
    
    def drawALine(self):
        #create a vector of line geometry type
        vectorDraftLyr = QgsVectorLayer('LineString?crs=epsg:4326', #epsg needs to be checked and made common for anywhere in the world
                                        'Input_Line' , 
                                        "memory")
        QgsProject().instance().addMapLayer(vectorDraftLyr)
        # set layer active 
        self.dlg.hide()
        iface.setActiveLayer(vectorDraftLyr)
        # start edit
        iface.actionToggleEditing().trigger()
        # enable tool
        iface.actionAddFeature().trigger() 
        #self.show()
        iface.actionToggleEditing().triggered.connect(self.endDrawLine)
    
    def endDrawLine(self):
        iface.actionToggleEditing().triggered.disconnect(self.endDrawLine)
        self.dlg.show()
        vlayer = iface.activeLayer()
    
        selection = vlayer.getFeatures()
        count = vlayer.featureCount()
        # to copy the co-ordinates of the input line in the plugin dialogue box
        for feature in selection:
            geom = feature.geometry()
            geomSingleType = QgsWkbTypes.isSingleType(geom.wkbType())
            if geom.type() == QgsWkbTypes.LineGeometry:
                if geomSingleType:
                    x = geom.asPolyline()
                    #print("Line: ", x, "length: ", geom.length())
                    pstr_list = []
                    for index in range(len(x) - 1):
                        resStr = "{},{},{},{}".format(x[index].x(),x[index].y()
                                                    ,x[index+1].x(), x[index+1].y())
                        pstr_list.append(resStr)
                    
                    print(pstr_list)
                    self.dlg.stEndPoint.setText(';'.join(pstr_list))
    
    def selectLineRB_clicked(self):
        #Populate the combobox at the Select Line Option with all the layers in the iface
        if self.dlg.radioButton.isChecked() == True:
            self.dlg.stackedWidget.show()
            self.dlg.stackedWidget.setCurrentIndex(0)
            layers = [layer for layer in QgsProject.instance().mapLayers().values()]
            layer_list = []        
            for layer in layers:
                layer_list.append(layer.name())
            self.dlg.comboBox.clear()
            self.dlg.comboBox.addItems(layer_list)
    
    def drawLineRB_clicked(self):
        #if 'Draw a line' option is chosen then open the corresponding page in the stack widget attached to radio button 
        if self.dlg.radioButton_2.isChecked() == True:
            self.dlg.stackedWidget.show()
            self.dlg.stackedWidget.setCurrentIndex(1)
        
    def calculateLine(self):
        if (self.dlg.comboBox.currentText() == "") and (self.dlg.stEndPoint.text()==""):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Input Line Error")
            msg.setText("No line drawn or selected.")
            msg.setStandardButtons(QMessageBox.Ok )
            return msg.exec_()
        if self.dlg.radioButton.isChecked() == True:
            if (self.dlg.comboBox.currentText() != "") and (self.dlg.stEndPoint.text()==""):
                for layer in QgsProject.instance().mapLayers().values():
                    if layer.name() == self.dlg.comboBox.currentText():
                        line = layer
        elif self.dlg.radioButton_2.isChecked() == True:
            if (self.dlg.comboBox.currentText() == "") and (self.dlg.stEndPoint.text()!=""):
                for layer in QgsProject.instance().mapLayers().values():
                    if layer.name() == 'Input_Line':
                        line = layer
        #print(line)
        #sideA, sideB, fov, alt, D,gsd, area, dist, r = calD()
        if line.crs() != QgsCoordinateReferenceSystem(4326):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Line Error")
            msg.setText("Change the input line projection to EPSG: 4326 and try again")
            msg.setStandardButtons(QMessageBox.Ok)
            return msg.exec_()
        if line.crs() == QgsCoordinateReferenceSystem(4326):
            R = 6371000 #earth radius in meters
            pi = math.pi
            griddist = (180*self.dist)/(R*pi)
            print(griddist)
           
            #Using arrayoffsetlines tool to create parallel lines tothe input line
            parameters = {'INPUT': line, 'COUNT':int(self.dlg.rightLines.text()), 'OFFSET': griddist, 'OUTPUT': 'memory:parallel_lines'} 
            plines=processing.run('native:arrayoffsetlines',parameters)
        plinesLayer = plines['OUTPUT']
        QgsProject.instance().addMapLayer(plinesLayer)
        #Clipping those line with the AOI input layer
        parameters_clip = {'INPUT':plinesLayer, 'OVERLAY':self.aoi_layer, 'OUTPUT':'memory:clipped_lines'}
        clip_lines=processing.run('native:clip',parameters_clip)
        clip_linesLayer = clip_lines['OUTPUT']
        QgsProject.instance().addMapLayer(clip_linesLayer)
        #Extracting the vertices of the lines
        wayPts = processing.run('native:extractvertices',{'INPUT':clip_linesLayer,'OUTPUT':'memory:way_points'})
        wayPtsLayerNoGeom = wayPts['OUTPUT']
        wayPtsGeom = processing.run('qgis:exportaddgeometrycolumns',{'INPUT': wayPtsLayerNoGeom, 'CALC_METHOD':0,'OUTPUT':'memory:Way_Points'})
        wayPtsGeomLayer = wayPtsGeom['OUTPUT']
        
        #adding lat long columns 
        fields = wayPtsGeomLayer.fields()
        wayPtsGeomLayer.startEditing()
        for field in fields:    
            if (field.name() != 'xcoord') and (field.name() !='ycoord'):
                print(field.name())
                wayPtsGeomLayer.deleteAttribute(wayPtsGeomLayer.fields().indexFromName(field.name()))
        #layer = iface.activeLayer()
        for field in wayPtsGeomLayer.fields():
            if field.name() == 'xcoord':
                idx = wayPtsGeomLayer.fields().indexFromName(field.name())
                wayPtsGeomLayer.renameAttribute(idx, 'longitude')
        for field in wayPtsGeomLayer.fields():
            if field.name() == 'ycoord':
                idx = wayPtsGeomLayer.fields().indexFromName(field.name())
                wayPtsGeomLayer.renameAttribute(idx, 'latitude')
        wayPtsGeomLayer.commitChanges()
        refactor = processing.run('native:refactorfields',{'INPUT': wayPtsGeomLayer,'FIELDS_MAPPING':[
        {'expression': '"latitude"','length': 0,'name': 'latitude','precision': 0,'type': 6},
        {'expression': '"longitude"','length': 0,'name': 'longitude','precision': 0,'type': 6}], 'OUTPUT':'memory:Points'})
        refactorLayer = refactor['OUTPUT']
        
        refactorLayer.dataProvider().addAttributes([QgsField( 'Sr.no', QVariant.Int,"integer",10 )])
        refactorLayer.updateFields()
        refactorLayer.dataProvider().addAttributes([QgsField( 'Sr.no2', QVariant.Int,"integer",10 )])
        refactorLayer.updateFields()
        
        # adding other mandatory columns to make it Fly Litchi compatible
        refactorLayer.dataProvider().addAttributes([QgsField( 'altitude(m)', QVariant.Double,"double",10,2 )])
        refactorLayer.dataProvider().addAttributes([QgsField( 'heading(deg)', QVariant.Double,"double",10,2 )])
        refactorLayer.dataProvider().addAttributes([QgsField( 'curvesize(m)', QVariant.Double,"double",10,2 )])
        refactorLayer.dataProvider().addAttributes([QgsField( 'rotationdir', QVariant.Double,"double",10,2 )])
        refactorLayer.dataProvider().addAttributes([QgsField( 'gimbalmode', QVariant.Double,"double",10,2 )])
        refactorLayer.dataProvider().addAttributes([QgsField( 'gimbalpitchangle', QVariant.Double,"double",10,2 )])
        refactorLayer.dataProvider().addAttributes([QgsField( 'actiontype1', QVariant.Double,"double",10,2 )])
        refactorLayer.dataProvider().addAttributes([QgsField( 'actionparam1', QVariant.Double,"double",10,2 )])
        refactorLayer.dataProvider().addAttributes([QgsField( 'actiontype2', QVariant.Double,"double",10,2 )])
        refactorLayer.dataProvider().addAttributes([QgsField( 'actionparam2', QVariant.Double,"double",10,2 )])
        refactorLayer.dataProvider().addAttributes([QgsField( 'altitudemode', QVariant.Double,"double",10,2 )])
        refactorLayer.dataProvider().addAttributes([QgsField( 'speed(m/s)', QVariant.Double,"double",10,2 )])
        refactorLayer.dataProvider().addAttributes([QgsField( 'poi_latitude', QVariant.Double,"double",10,2 )])
        refactorLayer.dataProvider().addAttributes([QgsField( 'poi_longitude', QVariant.Double,"double",10,2 )])
        refactorLayer.dataProvider().addAttributes([QgsField( 'poi_altitude(m)', QVariant.Double,"double",10,2 )])
        refactorLayer.dataProvider().addAttributes([QgsField( 'poi_altitudemode', QVariant.Double,"double",10,2 )])
        refactorLayer.dataProvider().addAttributes([QgsField( 'photo_timeinterval', QVariant.Double,"double",10,2 )])
        refactorLayer.dataProvider().addAttributes([QgsField( 'photo_distinterval', QVariant.Double,"double",10,2 )])
        refactorLayer.updateFields()
        refactorLayer.startEditing()
        
        #Populating the columns with default values
        for feat in refactorLayer.getFeatures():
            feat['altitude(m)'] = self.alt
            feat['heading(deg)'] = 45
            feat['curvesize(m)']=0.2
            feat['rotationdir']=0
            feat['gimbalmode'] = 2
            feat['actiontype1']= -1
            feat['gimbalpitchangle']= 0
            feat['actionparam1']= 0
            feat['actiontype2']= -1
            feat['actionparam2']= 0
            feat['altitudemode'] = 0
            feat['speed(m/s)'] =0
            feat['poi_latitude'] =0
            feat['poi_longitude'] =0
            feat['poi_altitude(m)'] =0
            feat['poi_altitudemode'] =0
            feat['photo_timeinterval'] =-1
            feat['photo_distinterval'] =-1
            refactorLayer.updateFeature(feat)
        refactorLayer.commitChanges()
        refactorLayer.updateFields()
        x=1
        refactorLayer.startEditing()
        for feat in refactorLayer.getFeatures():
            feat['Sr.no'] = x
            refactorLayer.updateFeature(feat)
            x+=1
            
        refactorLayer.commitChanges()
        refactorLayer.updateFields()
        
        y=0
        refactorLayer.startEditing()
        for feat in refactorLayer.getFeatures():
            if feat['Sr.no'] == y+3:
                feat['Sr.no2'] = y+3+1
                refactorLayer.updateFeature(feat)
            if feat['Sr.no'] == y+4:
                feat['Sr.no2'] = y+3
                refactorLayer.updateFeature(feat)
                y+=4    
        refactorLayer.commitChanges()
        refactorLayer.updateFields()
        
        refactorLayer.startEditing()
        for feat in refactorLayer.getFeatures():
            if feat['Sr.no2'] == NULL:
                feat['Sr.no2'] = feat['Sr.no']
                refactorLayer.updateFeature(feat)
        refactorLayer.commitChanges()
        refactorLayer.updateFields()
        
        refactorLayer.startEditing()
        if refactorLayer.fields().exists(refactorLayer.fields().indexFromName("Sr.no")):
            refactorLayer.dataProvider().deleteAttributes([refactorLayer.fields().indexFromName("Sr.no")])
            refactorLayer.updateFields()
        refactorLayer.commitChanges()
        
        c = refactorLayer.featureCount()
        
        vl = QgsVectorLayer("Point", "WayPoints", "memory")
        
        vl.dataProvider().addAttributes([QgsField( 'latitude', QVariant.Double,"double",10,6 )])
        vl.dataProvider().addAttributes([QgsField( 'longitude', QVariant.Double,"double",10,6 )])
        vl.dataProvider().addAttributes([QgsField( 'Sr.no2', QVariant.Int,"integer",10 )])
        vl.dataProvider().addAttributes([QgsField( 'altitude(m)', QVariant.Double,"double",10,2 )])
        vl.dataProvider().addAttributes([QgsField( 'heading(deg)', QVariant.Double,"double",10,2 )])
        vl.dataProvider().addAttributes([QgsField( 'curvesize(m)', QVariant.Double,"double",10,2 )])
        vl.dataProvider().addAttributes([QgsField( 'rotationdir', QVariant.Double,"double",10,2 )])
        vl.dataProvider().addAttributes([QgsField( 'gimbalmode', QVariant.Double,"double",10,2 )])
        vl.dataProvider().addAttributes([QgsField( 'gimbalpitchangle', QVariant.Double,"double",10,2 )])
        vl.dataProvider().addAttributes([QgsField( 'actiontype1', QVariant.Double,"double",10,2 )])
        vl.dataProvider().addAttributes([QgsField( 'actionparam1', QVariant.Double,"double",10,2 )])
        vl.dataProvider().addAttributes([QgsField( 'actiontype2', QVariant.Double,"double",10,2 )])
        vl.dataProvider().addAttributes([QgsField( 'actionparam2', QVariant.Double,"double",10,2 )])
        vl.dataProvider().addAttributes([QgsField( 'altitudemode', QVariant.Double,"double",10,2 )])
        vl.dataProvider().addAttributes([QgsField( 'speed(m/s)', QVariant.Double,"double",10,2 )])
        vl.dataProvider().addAttributes([QgsField( 'poi_latitude', QVariant.Double,"double",10,2 )])
        vl.dataProvider().addAttributes([QgsField( 'poi_longitude', QVariant.Double,"double",10,2 )])
        vl.dataProvider().addAttributes([QgsField( 'poi_altitude(m)', QVariant.Double,"double",10,2 )])
        vl.dataProvider().addAttributes([QgsField( 'poi_altitudemode', QVariant.Double,"double",10,2 )])
        vl.dataProvider().addAttributes([QgsField( 'photo_timeinterval', QVariant.Double,"double",10,2 )])
        vl.dataProvider().addAttributes([QgsField( 'photo_distinterval', QVariant.Double,"double",10,2 )])
        vl.updateFields()
        refactorLayer.startEditing()
        for feature in refactorLayer.getFeatures():
            count = refactorLayer.featureCount()
            geom = feature.geometry()
            attr = feature.attributes()

        vl.startEditing
        features = sorted(refactorLayer.getFeatures(),key = lambda feature: feature["Sr.no2"])
        layer_provider = vl.dataProvider()
        layer_provider.addFeatures(features)
        vl.commitChanges()
        refactorLayer.commitChanges()
        
        vl.startEditing()
        if vl.fields().exists(vl.fields().indexFromName("Sr.no2")):
            vl.dataProvider().deleteAttributes([vl.fields().indexFromName("Sr.no2")])
            vl.updateFields()
        vl.commitChanges()
        QgsProject.instance().addMapLayer(vl)
        
        #Converting the shapefile to csv file
        QgsVectorFileWriter.writeAsVectorFormat(vl,
            self.dlg.output.text(),
            "utf-8",driverName = "CSV" , layerOptions = ['GEOMETRY=AS_latlng']) #add this to this line if you want XY to be calculated on the 
            #go = (, layerOptions = ['GEOMETRY=AS_XY']).As we are running addgeometry column tool we are not adding this.
        self.dlg.radioButton.setChecked(False)
        self.dlg.radioButton_2.setChecked(False)
        self.dlg.stackedWidget.hide()
        self.dlg.stEndPoint.clear()
        
    def browse_csv(self):
        final_file = QFileDialog.getSaveFileName(self.dlg, "Save output file ","", '*.csv')
        self.dlg.output.setText(final_file[0])
    def BrowseAOI(self):
        aoi = QFileDialog.getOpenFileName(self.dlg, "Select AOI file ","", '*.shp')
        self.dlg.lineEdit_5.setText(aoi[0])
        
    def loadAOI(self):
        msg = QMessageBox()
        if self.dlg.lineEdit_5.text() == '':
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Unable to load layer")
            msg.setText("No shapefile selected to load.")
            msg.setStandardButtons(QMessageBox.Ok )
            return msg.exec_()
        elif self.dlg.lineEdit_5.text() != '':    
            aoi_name = ntpath.basename(self.dlg.lineEdit_5.text()).split('.')[0]
            self.aoi_layer = QgsVectorLayer(self.dlg.lineEdit_5.text(),aoi_name,"ogr")
            
            if (((self.aoi_layer).wkbType()!= QgsWkbTypes.MultiPolygon) and ((self.aoi_layer).wkbType()!= QgsWkbTypes.MultiPolygonZ) and 
                ((self.aoi_layer).wkbType()!= QgsWkbTypes.Polygon) and ((self.aoi_layer).wkbType()!= QgsWkbTypes.MultiPolygonZM) and  
                ((self.aoi_layer).wkbType()!= QgsWkbTypes.MultiPolygonM)and ((self.aoi_layer).wkbType()!= QgsWkbTypes.PolygonZ) and 
                ((self.aoi_layer).wkbType()!= QgsWkbTypes.PolygonM) and ((self.aoi_layer).wkbType()!= QgsWkbTypes.PolygonZM)):
            
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Unable to load layer")
                msg.setText("AOI shapefile should be of Polygon Geometry Type only.")
                msg.setStandardButtons(QMessageBox.Ok )
                return msg.exec_()
            if ((self.aoi_layer).crs() != QgsCoordinateReferenceSystem(4326)): 
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Projection Error")
                msg.setText("Change the polygon projection to EPSG: 4326 and try again.")
                msg.setStandardButtons(QMessageBox.Ok)
                return msg.exec_()
        layers =[]        
        for layer in QgsProject.instance().mapLayers().values():
                layers.append(layer.name())
        if aoi_name in layers:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Layer Loaded")
            msg.setText("Layer already loaded in QGIS instance.")
            msg.setStandardButtons(QMessageBox.Ok)
            return msg.exec_()    
        QgsProject.instance().addMapLayer(self.aoi_layer)
        
    
    
    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = DronePathDialog()
            
        self.dlg.pushButton.clicked.connect(self.calD)
        self.dlg.pushButton_2.clicked.connect(self.BrowseAOI)  
        self.dlg.pushButton_4.clicked.connect(self.drawALine)
        self.dlg.pushButton_3.clicked.connect(self.loadAOI)
        self.dlg.lineEdit_4.clear()
        self.dlg.lineEdit_7.clear()
        self.dlg.lineEdit_8.clear()
        self.dlg.lineEdit_11.clear()
        self.dlg.lineEdit_12.clear()
        self.dlg.lineEdit_13.clear()
        self.dlg.lineEdit_4.setReadOnly(True)
        self.dlg.lineEdit_7.setReadOnly(True)
        self.dlg.lineEdit_8.setReadOnly(True)
        self.dlg.lineEdit_11.setReadOnly(True)
        self.dlg.lineEdit_12.setReadOnly(True)
        self.dlg.lineEdit_13.setReadOnly(True)
        self.dlg.lineEdit_5.clear()
        self.dlg.rightLines.clear()
        self.dlg.output.clear()
        self.dlg.radioButton.setChecked(False)
        self.dlg.radioButton_2.setChecked(False)
        self.dlg.lineEdit.clear()
        reg_ex = QRegExp("^[0-9]{2,3}") #2 or 3 digits and no decimals  #(\d\d\d\.[0-9]{,2})
        input_validator = QRegExpValidator(reg_ex)
        self.dlg.lineEdit.setValidator(input_validator)
        self.dlg.lineEdit_3.clear()
        reg_ex = QRegExp("\d{0,3}(\.\d{1,2})") #two digit with two decimals
        input_validator = QRegExpValidator(reg_ex)
        self.dlg.lineEdit_3.setValidator(input_validator)
        self.dlg.lineEdit_2.clear()
        reg_ex = QRegExp("(\d{2})") # upto two digits only
        input_validator = QRegExpValidator(reg_ex)
        self.dlg.lineEdit_2.setValidator(input_validator)  
        self.dlg.lineEdit_6.clear()
        reg_ex = QRegExp("(\d\.[0-9]{,2})") #one digit with two decimals
        input_validator = QRegExpValidator(reg_ex)
        self.dlg.lineEdit_6.setValidator(input_validator)
        
        self.dlg.lineEdit_9.clear()
        reg_ex = QRegExp("^[0-9]{4,5}") #four or five digits
        input_validator = QRegExpValidator(reg_ex)
        self.dlg.lineEdit_9.setValidator(input_validator) 
        
        self.dlg.lineEdit_10.clear()
        reg_ex = QRegExp("^[0-9]{4,5}") #four or five digits
        input_validator = QRegExpValidator(reg_ex)
        self.dlg.lineEdit_10.setValidator(input_validator) 
        
        self.dlg.lineEdit.setText('80')
        self.dlg.lineEdit_2.setText('50')
        self.dlg.lineEdit_3.setText('83')
        self.dlg.lineEdit_6.setText('1.55')
        self.dlg.lineEdit_9.setText('3648')
        self.dlg.lineEdit_10.setText('5672')
        self.dlg.pushButton_5.clicked.connect(self.calculateLine)
        self.dlg.pushButton_6.clicked.connect(self.browse_csv)
        self.dlg.radioButton.clicked.connect(self.selectLineRB_clicked)
        self.dlg.radioButton_2.clicked.connect(self.drawLineRB_clicked)
        #self.dlg.comboBox.activated.connect(self.layerlist)
        self.dlg.stackedWidget.hide()
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
