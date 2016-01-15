import math

from OpenGL.GL import *
from OpenGL.GL.ARB.vertex_array_object import *
from OpenGL.GL.shaders import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo

from qtpy.QtCore import Qt
from qtpy.QtGui import QMainWindow, QWidget, QApplication, QBoxLayout, QFontDatabase, QComboBox
from PySide.QtOpenGL import QGLWidget

from AlgorithmRunner.algorithmLoader import AlgorithmLoader
from Rendering.camera import Camera
from Rendering.utilities import UnitCube, GenerateRectangle
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
        self.triangleVertexArrayObject = None
        self.edgeVertexArrayObject = None

        self.lastMouseX = 0
        self.lastMouseY = 0
        self.camera = Camera([0.0, 0.0, 1.0], [0.0, 0.0, 0.0], [0.0, 1.0, 0.0])
        self.WVPMatrix = None
        self.setProperty("class", "AlgorithmVisualizerWidget")
        self.UpdateWVPMatrix()

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
        self.WVPMatrix = self.camera.matrix * self.camera.projectionMatrix

    @override(QGLWidget)
    def resizeGL(self, w, h):
        "runs every time the window changes size"
        glViewport(0, 0, w, h)
        w *= 1.0
        h *= 1.0

        self.camera.SetProjectionInfo(w, h)

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
            glDrawArrays(GL_LINES, 0, self.edgeCount)

            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glDepthMask(0)

            glBindVertexArray(self.triangleVertexArrayObject)
            # Modern GL makes the draw call really simple
            # All the complexity has been pushed elsewhere
            glDrawArrays(GL_TRIANGLES, 0, self.triangleCount)

    def loadShaders(self):
        with open(AbsJoin(APP_ROOT, "resources/shaders/pointShader.vs")) as pointVertexShaderFile:
            with open(AbsJoin(APP_ROOT, "resources/shaders/pointShader.fs")) as pointPixelShaderFile:
                self.pointProgram = compileProgram(compileShader(pointVertexShaderFile.read(), GL_VERTEX_SHADER),
                    compileShader(pointPixelShaderFile.read(), GL_FRAGMENT_SHADER))
        self.WVPUniformLocation = glGetUniformLocation(self.pointProgram, "WVP")

    def CreateBuffers(self, vertex_data, color_data, vaoId=None):
        if vaoId is not None:
            glDeleteVertexArray(1, [vaoID])
        vaoId = glGenVertexArrays(1)
        glBindVertexArray(vaoId)

        pointVertexBufferID = glGenBuffers(2)

        # Create the vertex array for the positions
        glBindBuffer(GL_ARRAY_BUFFER, pointVertexBufferID[0])
        glBufferData(GL_ARRAY_BUFFER, 4 * len(vertex_data), vbo.ArrayDatatype.asArray(vertex_data, GL_FLOAT), GL_STATIC_DRAW)
        glVertexAttribPointer(glGetAttribLocation(self.pointProgram, 'vin_position'), 3, GL_FLOAT, GL_FALSE, 0, None)

        # Enable it on the shader program
        glEnableVertexAttribArray(0)

        # Create the vertex array for the colors
        glBindBuffer(GL_ARRAY_BUFFER, pointVertexBufferID[1])
        glBufferData(GL_ARRAY_BUFFER, 4 * len(color_data), vbo.ArrayDatatype.asArray(color_data, GL_FLOAT), GL_STATIC_DRAW)
        glVertexAttribPointer(glGetAttribLocation(self.pointProgram, 'vin_color'), 4, GL_FLOAT, GL_FALSE, 0, None)

        # Enable it on the shader program
        glEnableVertexAttribArray(1)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
        return vaoId


    def SetRenderingDataFromMesh(self, mesh, reFocusCamera=False):
        if not isinstance(mesh, list):
            mesh = [mesh]

        triangleVertices = []
        triangleColors = []
        edgeVertices = []
        edgeColors = []

        for m in mesh:
            triangleVertices.extend([x for x in m.GetTriangleVertexGenerator()])
            triangleColors.extend([x for x in m.GetTriangleColorGenerator()])

            edgeVertices.extend([x for x in m.GetEdgeVertexGenerator()])
            edgeColors.extend([x for x in m.GetEdgeColorGenerator()])

        if reFocusCamera:
            minX, maxX, minY, maxY = None, None, None, None
            it = iter(triangleVertices)
            for vertex in it:
                x, y, _ = vertex, next(it), next(it)
                if minX is None or x < minX:
                    minX = x
                elif maxX is None or x > maxX:
                    maxX = x
                if minY is None or y < minY:
                    minY = y
                if maxY is None or y > maxY:
                    maxY = y
            padding = 10
            self.camera.Focus(minX - padding, maxX + padding, minY - padding, maxY + padding)
            self.UpdateWVPMatrix()

        self.triangleCount = int(len(triangleVertices)/3.0)
        self.edgeCount = int(len(edgeVertices)/3.0)
        self.triangleVertexArrayObject = self.CreateBuffers(triangleVertices, triangleColors)
        self.edgeVertexArrayObject = self.CreateBuffers(edgeVertices, edgeColors)


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

        self.algorithms = QComboBox(self)
        algorithmNamesAndIDs = self.algorithmLoader.GetAllAlgorithmNameAndIDs()

        for name, _ in algorithmNamesAndIDs:
            self.algorithms.addItem(name[0].upper() + name[1:])

        self.algorithms.currentIndexChanged['QString'].connect(self.handleAlgorithmChanged)
        horizontalLayout.addWidget(self.algorithms)

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
        import random
        algorithm = self.algorithmLoader.GetAlgorithmInstance("selectionSort.SelectionSort")
        algorithm.setData([ random.random() * 100 for _ in range(50) ])

        self.gl_widget.SetRenderingDataFromMesh(algorithm.getRenderData(), reFocusCamera=True)
        # modify the orhtogonal perspective based of the width and height of the data
        # self.gl_widget.SetRenderingDataFromMesh(GenerateRectangle(10, 10))

    def setupLayout(self):

        buttonLayout = QBoxLayout(QBoxLayout.LeftToRight)
        playButton = PlayButton()
        stopButton = StopButton()
        buttonLayout.addWidget(playButton)
        buttonLayout.addWidget(stopButton)

        self.verticalBoxLayout.addStretch(1)
        self.verticalBoxLayout.addStretch(1)
        self.verticalBoxLayout.addLayout(buttonLayout)

    def handleAlgorithmChanged(self, text):
        print 'algorithmChanged: %s' %  text


class MainWindow(QApplication):
    "Simple application for the algorithm visualizer"

    def __init__(self):
        QApplication.__init__(self, sys.argv)

        # Enable High DPI display with PyQt5
        if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
            self.setAttribute(Qt.AA_UseHighDpiPixmaps)

        self.setApplicationName("Algorithm Visualizer")

        # QFontDatabase.addApplicationFont(AbsJoin(APP_ROOT, "resources/fontawesome-webfont.tff"))

        with open(AbsJoin(APP_ROOT, "resources/stylesheet.qss")) as styleSheetFile:
            self.setStyleSheet(styleSheetFile.read())

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
