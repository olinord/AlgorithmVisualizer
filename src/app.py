import math

from OpenGL.GL import *
from OpenGL.GL.ARB.vertex_array_object import *
from OpenGL.GL.shaders import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo
from PySide.QtCore import Qt
from PySide.QtGui import QMainWindow, QWidget, QApplication, QBoxLayout, QFontDatabase, QComboBox
from PySide.QtOpenGL import QGLWidget

from AlgorithmRunner.algorithmLoader import AlgorithmLoader
from Rendering.camera import Camera
from Rendering.utilities import UnitCube
from UI.Button import PlayButton, StopButton
from euclid import Matrix4
from fileUtils import AbsJoin, APP_ROOT, LoadYamlFromRoot


def override(interface_class):
    """
    Method to implement Java-like derived class method override annotation.
    Courtesy of mkorpela's answer at
    http://stackoverflow.com/questions/1167617/in-python-how-do-i-indicate-im-overriding-a-method
    """
    def override(method):
        assert(method.__name__ in dir(interface_class))
        return method
    
    return override

class AlgorithmVisualizerWidget(QGLWidget):
    "The widget that displays vertices, edges and faces of triangles in an algorithm"
    
    def __init__(self):
        QGLWidget.__init__(self)
        self.triangleCount = 0
        self.edgeCount = 0
        
        self.lastMouseX = 0
        self.lastMouseY = 0
        self.camera = Camera([3.0, 3.0, 3.0], [0.0, 0.0, 0.0], [0.0, 1.0, 0.0])
        self.setProperty("class", "AlgorithmVisualizerWidget")
                
    def SetVertices(self, mesh):
        self.SetRenderingDataFromMesh(mesh)        
    
    @override(QGLWidget)
    def initializeGL(self):
        "runs once, after OpenGL context is created"
        self.pointProgram = None

        glClearColor(0.3, 0.3, 0.3, 1.0)
        
        # Set up the shader.
        self.loadShaders()            
        
    @override(QGLWidget)
    def paintGL(self):
        "runs every time an image update is needed"
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.drawScene()
    
    def UpdateWVPMatrix(self):
        self.WVPMatrix = self.camera.matrix * self.perspectiveMatrix 
        
    @override(QGLWidget)
    def resizeGL(self, w, h):
        "runs every time the window changes size"
        glViewport(0, 0, w, h)
        w *= 1.0
        h *= 1.0
        
        self.perspectiveMatrix = Matrix4.new_perspective(math.pi / 2.0, max(w, 1.0) / max(h, 1.0), 0.1, 1000.0)
        self.perspectiveMatrix.transpose()
                
        self.UpdateWVPMatrix() 
        
    @override(QGLWidget)
    def mousePressEvent(self, event):
        self.lastMouseX = event.pos().x()
        self.lastMouseY = event.pos().y()
    
    @override(QGLWidget)
    def mouseMoveEvent(self, event):
        deltaX = event.pos().x() - self.lastMouseX
        deltaY = event.pos().y() - self.lastMouseY
        self.camera.MouseMotion(deltaX, deltaY)
        
        self.UpdateWVPMatrix() 
        self.update()
        self.lastMouseX += deltaX
        self.lastMouseY += deltaY     
    
    @override(QGLWidget)
    def wheelEvent(self, e):
        self.camera.Zoom(0.1 * e.delta() / abs(e.delta()))
        self.UpdateWVPMatrix() 
        self.update()

    def drawScene(self):
        if self.pointProgram:
            glUseProgram(self.pointProgram)            
            
            glUniformMatrix4fv(self.WVPUniformLocation, 1, GL_FALSE, [
                                                                        self.WVPMatrix.a, self.WVPMatrix.b, self.WVPMatrix.c, self.WVPMatrix.d,
                                                                        self.WVPMatrix.e, self.WVPMatrix.f, self.WVPMatrix.g, self.WVPMatrix.h,
                                                                        self.WVPMatrix.i, self.WVPMatrix.j, self.WVPMatrix.k, self.WVPMatrix.l,
                                                                        self.WVPMatrix.m, self.WVPMatrix.n, self.WVPMatrix.o, self.WVPMatrix.p
                                                                      ])
                
            glBindVertexArray(self.edgeVertexArrayObject)
            glDrawArrays(GL_LINES, 0, self.edgeCount * 2)
            
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glDepthMask(0)
            
            glBindVertexArray(self.triangleVertexArrayObject)
            # Modern GL makes the draw call really simple
            # All the complexity has been pushed elsewhere
            glDrawArrays(GL_TRIANGLES, 0, self.triangleCount * 3)

    def loadShaders(self):
        with open(AbsJoin(APP_ROOT, "resources/shaders/pointShader.vs")) as pointVertexShaderFile:
            with open(AbsJoin(APP_ROOT, "resources/shaders/pointShader.fs")) as pointPixelShaderFile:
                self.pointProgram = compileProgram(compileShader(pointVertexShaderFile.read(), GL_VERTEX_SHADER),
                    compileShader(pointPixelShaderFile.read(), GL_FRAGMENT_SHADER))
        self.WVPUniformLocation = glGetUniformLocation(self.pointProgram, "WVP")

    def CreateBuffers(self, vertex_data, color_data):
        vaoId = glGenVertexArrays(1)
        glBindVertexArray(vaoId)
        
        pointVertexBufferID = glGenBuffers(2)
        
        # Create the vertex array for the positions
        glBindBuffer(GL_ARRAY_BUFFER, pointVertexBufferID[0])
        glBufferData(GL_ARRAY_BUFFER, 3 * 4 * len(vertex_data), vbo.ArrayDatatype.asArray(vertex_data, GL_FLOAT), GL_STATIC_DRAW)
        glVertexAttribPointer(glGetAttribLocation(self.pointProgram, 'vin_position'), 3, GL_FLOAT, GL_FALSE, 0, None)
        
        # Enable it on the shader program
        glEnableVertexAttribArray(0)
        
        # Create the vertex array for the colors
        glBindBuffer(GL_ARRAY_BUFFER, pointVertexBufferID[1])
        glBufferData(GL_ARRAY_BUFFER, 4 * 4 * len(vertex_data), vbo.ArrayDatatype.asArray(color_data, GL_FLOAT), GL_STATIC_DRAW)
        glVertexAttribPointer(glGetAttribLocation(self.pointProgram, 'vin_color'), 4, GL_FLOAT, GL_FALSE, 0, None)
        
        # Enable it on the shader program
        glEnableVertexAttribArray(1)
        
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
        
        return vaoId
    
    def SetRenderingDataFromMesh(self, mesh):
        triangleVertices = [x for x in mesh.GetTriangleVertexGenerator()]
        triangleColors = [x for x in mesh.GetTriangleColorGenerator()]        
        
        self.triangleVertexArrayObject = self.CreateBuffers(triangleVertices, triangleColors)
        self.triangleCount = len(mesh.GetTriangles())
                
        edgeVertices = [x for x in mesh.GetEdgeVertexGenerator()]
        edgeColors = [x for x in mesh.GetEdgeColorGenerator()]
        
        self.edgeVertexArrayObject = self.CreateBuffers(edgeVertices, edgeColors)
        self.edgeCount = len(mesh.GetEdges())       
     
        
class MainWidget(QWidget):
    "The main widget containing the rendering window and all of the controls"
    
    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent)
        self.setProperty("class", "MainWidget")
        self.algorithmLoader = AlgorithmLoader(LoadYamlFromRoot("algorithms/algorithms.yaml"))
        
        self.layout = QBoxLayout(QBoxLayout.LeftToRight)
        self.layout.setContentsMargins(0, 0, 0, 0)     
        
        self.setLayout(self.layout)  
        
        self.SetLeftWidgets()
        
    
    def SetLeftWidgets(self):
        horizontalLayout = QBoxLayout(QBoxLayout.TopToBottom)
        horizontalLayout.setContentsMargins(0, 0, 0, 0)
        
        algorithms = QComboBox(self)
        algorithmNames = sorted([algorithm["name"].lower() for algorithm in self.algorithmLoader.algorithmDefinitions.itervalues()])
        
        for name in algorithmNames:
            algorithms.addItem(name[0].upper() + name[1:])

        horizontalLayout.addWidget(algorithms)
        
        self.gl_widget = AlgorithmVisualizerWidget()
        horizontalLayout.addWidget(self.gl_widget)
        
        buttonLayout = QBoxLayout(QBoxLayout.LeftToRight)        
        playButton = PlayButton()
        stopButton = StopButton()        
        buttonLayout.addWidget(playButton)
        buttonLayout.addWidget(stopButton)
        buttonLayout.setAlignment(Qt.AlignHCenter)
        
        horizontalLayout.addLayout(buttonLayout)
        
        self.layout.addLayout(horizontalLayout, 1)
    
    def SetDefaultVertexSelection(self):
        self.gl_widget.SetVertices(UnitCube())
            
    def setupLayout(self):

        buttonLayout = QBoxLayout(QBoxLayout.LeftToRight)        
        playButton = PlayButton()
        stopButton = StopButton()        
        buttonLayout.addWidget(playButton)
        buttonLayout.addWidget(stopButton)
        
        self.verticalBoxLayout.addStretch(1)
        self.verticalBoxLayout.addStretch(1)             
        self.verticalBoxLayout.addLayout(buttonLayout)
        

class MainWindow(QApplication):
    "Simple application for the algorithm visualizer"
    
    def __init__(self):
        QApplication.__init__(self, sys.argv)
        self.setApplicationName("Algorithm Visualizer")
        self.fontID = QFontDatabase.addApplicationFont("../resources/fontawesome-webfont.ttf")
        
        with open(AbsJoin(APP_ROOT, "resources/stylesheet.qss")) as styleSheetFile:
            self.setStyleSheet(styleSheetFile.read())
                    
        self.setFont("FontAwesome")
        self.mainWindow = QMainWindow()     
        self.mainWindow.setProperty("class", "MainWindow") 
                        
        self.mainWindow.resize(1024, 768)
        self.mainWidget = MainWidget()  
        self.mainWindow.setCentralWidget(self.mainWidget)    
                            
        self.mainWindow.show()
        
        # this needs to happen after the main window is shown
        self.mainWidget.SetDefaultVertexSelection()
        
        sys.exit(self.exec_()) 
        
        

if __name__ == "__main__":
    MainWindow()
