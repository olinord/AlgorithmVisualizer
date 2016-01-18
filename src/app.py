import math

from OpenGL.GL import *
from OpenGL.GL.ARB.vertex_array_object import *
from OpenGL.GL.shaders import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo

from qtpy.QtCore import Qt, QObject, Signal
from qtpy.QtGui import QMainWindow, QWidget, QApplication, QBoxLayout, QFontDatabase, QComboBox, QPushButton
from PySide.QtOpenGL import QGLWidget

from AlgorithmRunner.algorithmLoader import AlgorithmLoader
from Rendering.camera import Camera
from Rendering.utilities import UnitCube, GenerateRectangle
from UI.Button import PlayButton, StopButton
from euclid import Matrix4
from fileUtils import AbsJoin, APP_ROOT, LoadYamlFromRoot
from AlgorithmRunner.algorithmConst import ALGORITHM_VALUE_INTEGER, ALGORITHM_VALUE_2D_POINT, ALGORITHM_VALUE_3D_POINT, ALGORITHM_RENDER_TRIANGLES, ALGORITHM_RENDER_LINES, ALGORITHM_RENDER_POINTS
from AlgorithmRunner.algorithmRunner import AlgorithmRunner


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
        self.pointCount = 0
        self.triangleVertexArrayObject = None
        self.edgeVertexArrayObject = None
        self.pointVertexArrayObject = None

        self.drawTriangles = False
        self.drawLines = False
        self.drawPoints = False

        self.lastMouseX = 0
        self.lastMouseY = 0
        self.camera = Camera([0.0, 0.0, -1.0], [0.0, 0.0, 0.0], [0.0, 1.0, 0.0])
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
            if self.drawPoints:
                glBindVertexArray(self.pointVertexArrayObject)
                glDrawArrays(GL_POINTS, 0, self.pointCount)

            if self.drawLines:
                glBindVertexArray(self.edgeVertexArrayObject)
                glDrawArrays(GL_LINES, 0, self.edgeCount)

            if self.drawTriangles:
                glEnable(GL_BLEND)
                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                glDepthMask(0)

                glBindVertexArray(self.triangleVertexArrayObject)
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


    def SetRenderingDataFromMesh(self, mesh, renderTypes=None, reFocusCamera=False):
        if not isinstance(mesh, list):
            mesh = [mesh]

        triangleVertices = []
        triangleColors = []
        edgeVertices = []
        edgeColors = []
        pointVertices = []
        pointColors = []

        if renderTypes is not None:
            self.drawTriangles = ALGORITHM_RENDER_TRIANGLES in renderTypes
            self.drawLines = ALGORITHM_RENDER_LINES in renderTypes
            self.drawPoints = ALGORITHM_RENDER_POINTS in renderTypes

        for m in mesh:
            if self.drawTriangles:
                triangleVertices.extend([x for x in m.GetTriangleVertexGenerator()])
                triangleColors.extend([x for x in m.GetTriangleColorGenerator()])
            if self.drawLines:
                edgeVertices.extend([x for x in m.GetEdgeVertexGenerator()])
                edgeColors.extend([x for x in m.GetEdgeColorGenerator()])
            if self.drawPoints:
                pointVertices.extend([x for x in m.GetPointVertexGenerator()])
                pointColors.extend([x for x in m.GetPointColorGenerator()])

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
        self.pointCount = int(len(pointVertices)/3.0)
        if self.drawTriangles:
            self.triangleVertexArrayObject = self.CreateBuffers(triangleVertices, triangleColors)
        if self.drawLines:
            self.edgeVertexArrayObject = self.CreateBuffers(edgeVertices, edgeColors)
        if self.drawPoints:
            self.pointVertexArrayObject = self.CreateBuffers(pointVertices, pointColors)
        self.update()


class Communicate(QObject):
    # create a new signal on the fly and name it 'speak'
    updateRenderInfo = Signal(list)


class MainWidget(QWidget):
    "The main widget containing the rendering window and all of the controls"

    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent)
        self.setProperty("class", "MainWidget")
        self.algorithmLoader = AlgorithmLoader(LoadYamlFromRoot("algorithms/algorithms.yaml"))
        self.algorithmRunner = AlgorithmRunner(self.updateAlgorithmRenderingData)

        self.communicator = Communicate()

        # UI stuff
        self.algorithms = None
        self.gl_widget = None
        self.rightHandLayout = None
        self.layout = QBoxLayout(QBoxLayout.LeftToRight)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.layout)

        self.SetupView()

    def SetupView(self):
        verticalLayout= QBoxLayout(QBoxLayout.LeftToRight)

        leftLayout = self.SetupLeftSide()
        rightLayout = self.SetupRightSide()

        verticalLayout.addLayout(leftLayout, 1)
        verticalLayout.addLayout(rightLayout, 0)
        self.layout.addLayout(verticalLayout, 1)

    def SetupRightSide(self):
        rightLayout = QBoxLayout(QBoxLayout.TopToBottom)
        rightLayout.setContentsMargins(0, 0, 0, 0)

        generateButton = QPushButton("generate")
        rightLayout.addWidget(generateButton)

        return rightLayout

    def SetupLeftSide(self):
        leftLayout = QBoxLayout(QBoxLayout.TopToBottom)
        leftLayout.setContentsMargins(0, 0, 0, 0)

        self.SetupTop(leftLayout)
        self.SetupCenter(leftLayout)
        self.SetupBottom(leftLayout)

        return leftLayout

    def SetupTop(self, layout):
        self.algorithms = QComboBox(self)
        algorithmNames = self.algorithmLoader.GetAllAlgorithmNames()

        for name in algorithmNames:
            self.algorithms.addItem(name[0].upper() + name[1:])

        self.algorithms.currentIndexChanged['QString'].connect(self.handleAlgorithmChanged)
        layout.addWidget(self.algorithms)

    def SetupCenter(self, layout):
        self.gl_widget = AlgorithmVisualizerWidget()
        layout.addWidget(self.gl_widget)
        self.communicator.updateRenderInfo.connect(self.gl_widget.SetRenderingDataFromMesh)

    def SetupBottom(self, layout):
        buttonLayout = QBoxLayout(QBoxLayout.LeftToRight)
        playButton = PlayButton()
        playButton.clicked.connect(self.startAlgorithm)
        stopButton = StopButton()
        stopButton.clicked.connect(self.stopAlgorithm)
        buttonLayout.addWidget(playButton)
        buttonLayout.addWidget(stopButton)
        buttonLayout.setAlignment(Qt.AlignHCenter)

        layout.addLayout(buttonLayout)

    def showTopAlgorithm(self):
        # send out a fake algorithmChanged for the first algorithm in the list
        self.handleAlgorithmChanged(self.algorithms.currentText())

    def handleAlgorithmChanged(self, algorithmName):
        import random
        self.algorithm = self.algorithmLoader.GetAlgorithmInstance(algorithmName)
        self.algorithm.setData([ random.random() * 100 for _ in range(50) ])
        renderTypes = self.algorithmLoader.GetAlgorithmRenderTypes(algorithmName)
        self.gl_widget.SetRenderingDataFromMesh(self.algorithm.getRenderData(), renderTypes, reFocusCamera=True)
        self.algorithmRunner.SetAlgorithm(self.algorithm)

    def startAlgorithm(self):
        self.algorithmRunner.run()

    def stopAlgorithm(self):
        self.algorithmRunner.stop()

    def updateAlgorithmRenderingData(self):
        self.communicator.updateRenderInfo.emit(self.algorithm.getRenderData())


class MainWindow(QApplication):
    "Simple application for the algorithm visualizer"

    def __init__(self):
        QApplication.__init__(self, sys.argv)

        # Enable High DPI display with PyQt5
        if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
            self.setAttribute(Qt.AA_UseHighDpiPixmaps)

        self.setApplicationName("Algorithm Visualizer")

        with open(AbsJoin(APP_ROOT, "resources/stylesheet.qss")) as styleSheetFile:
            self.setStyleSheet(styleSheetFile.read())

        self.mainWindow = QMainWindow()
        self.mainWindow.setProperty("class", "MainWindow")

        self.mainWindow.resize(1024, 768)
        self.mainWidget = MainWidget()
        self.mainWindow.setCentralWidget(self.mainWidget)

        self.mainWindow.show()

        # this needs to happen after the main window is shown
        self.mainWidget.showTopAlgorithm()

        sys.exit(self.exec_())



if __name__ == "__main__":
    MainWindow()
