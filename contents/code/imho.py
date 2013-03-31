# -*- coding: utf-8 -*-
import json
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
from PyKDE4 import plasmascript
from PyKDE4.plasma import Plasma
from PyKDE4.plasmascript import Applet
from PyKDE4.kdecore import *
from PyKDE4.kdeui import *
from PyKDE4.kio import KIO



class ImhoApplet(plasmascript.Applet):
    def __init__(self, parent, args=None):
        plasmascript.Applet.__init__(self, parent)


        
    def init(self):
        # TODO: add configuration interface
        self.setHasConfigurationInterface(False)
        self.setAspectRatioMode(Plasma.IgnoreAspectRatio)
        
        self.layout = QGraphicsLinearLayout(Qt.Vertical, self.applet)
        self.layout.setSpacing(0)
        self.layout.setItemSpacing(0,0)
        
        image = QIcon( "contents/images/imho.png" );
        self.imageDisplay = Plasma.IconWidget(self.applet)
        self.imageDisplay.setMaximumSize( QSizeF(800,800) )
        self.imageDisplay.setMinimumSize( QSizeF(8,8) )
        self.imageDisplay.setPreferredIconSize( QSizeF(24,24) )
        self.imageDisplay.setIcon(image)
        self.imageDisplay.clicked.connect(self.onClickHandler)
        self.layout.addItem(self.imageDisplay)
        
        self.toolTip = Plasma.ToolTipContent( QString("IMHO - Is My Hackerspace O   pen?"), QString("loading..."), KIcon( image ) );
        Plasma.ToolTipManager.self().setContent(self.applet, self.toolTip);
        
        self.connectToEngine()
    
    
    
    def connectToEngine(self):
        self.timeEngine = self.dataEngine("time")
        self.timeEngine.connectSource("local", self, int(1000*60*5) )


            
    @pyqtSignature("dataUpdated(const QString &, const Plasma::DataEngine::Data &)")
    def dataUpdated(self, sourceName, data):
        # slot called from timer
        self.fetchHackerspaceStatus()
        
        
        
    def fetchHackerspaceStatus(self):
        # TODO: configurable hackerspace url
        data_url = KUrl("http://it-syndikat.org/status.php")
        retrieve_job = KIO.storedGet(data_url, KIO.Reload, KIO.HideProgressInfo)
        retrieve_job.result.connect(self.handleDownloadedJson)
        


    def handleDownloadedJson(self, job):
        #Slot called from the retrieval job.
        if job.error():
            self.displayErrorMessage("failed to get hackerspace status")
            return
        data = job.data()
        self.updateStatus(str(data))
        
        
    
    def updateStatus(self,jsonString):
        self.jsonData = json.loads(jsonString)
        oldstatus = self.status;
        self.status = self.jsonData["open"]
        if (oldstatus != self.status): 
            self.statusChanged()
            
    
    
    def statusChanged(self):
        data_url = KUrl( self.getImageUrl() )
        retrieve_job = KIO.storedGet(data_url, KIO.NoReload, KIO.HideProgressInfo)
        retrieve_job.result.connect(self.handleDownloadedImage)
        
        
        
    def handleDownloadedImage(self, job):
        # slot called from image retrieval
        if job.error():
            self.displayErrorMessage("failed to download image")
            return
        data = job.data()
        image = QPixmap()
        # TODO: check image type
        image.loadFromData( data, "PNG" )
        self.setDisplay(image, self.getInfoMessage() )
        
        
        
    def setDisplay(self, image, message):
        self.imageDisplay.setIcon( QIcon( image.scaled(800,800, Qt.KeepAspectRatio, Qt.SmoothTransformation) ) )
        
        Plasma.ToolTipManager.self().clearContent(self.applet)
        self.toolTip.setImage( KIcon( QIcon(image) ) )
        self.toolTip.setMainText( QString( message ) )
        self.toolTip.setSubText( QString( self.getHackerspaceUrl() ) )
        Plasma.ToolTipManager.self().setContent(self.applet, self.toolTip)
        
    
    def onClickHandler(self):
        QDesktopServices.openUrl( QUrl(self.getHackerspaceUrl()) )
        
        
    
    def getInfoMessage(self):
        if (self.status):
            return self.jsonData["space"] + " is open!"
        else:
            return self.jsonData["space"] + " is closed!"
        
        
        
    def getImageUrl(self):
        if (self.status):
            return self.jsonData["icon"]["open"]
        else:
            return self.jsonData["icon"]["closed"]
    
        
        
    def getHackerspaceUrl(self):
        return self.jsonData["url"]
    
    

    def displayErrorMessage(self, message):
        image = QIcon("contents/images/imho.png")
        self.imageDisplay.setIcon(image)
        
        Plasma.ToolTipManager.self().clearContent(self.applet)
        self.toolTip.setImage( KIcon( image ) )
        self.toolTip.setMainText( QString( "Error!" ) )
        self.toolTip.setSubText( QString( message ) )
        Plasma.ToolTipManager.self().setContent(self.applet, self.toolTip)
    
    

def CreateApplet(parent):
    return ImhoApplet(parent)
    