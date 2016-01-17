from AlgorithmRunner.algorithmInterface import Algorithm
from Rendering.utilities import GenerateRectangle
from Rendering.color import Color

UNSORTED_COLOR = Color(1.0, 1.0, 1.0, 1.0)
SORTED_COLOR = Color(0.1, 1.0, 0.1, 1.0)
COMPARE_COLOR = Color(0.7, 0.0, 0.7, 1.0)
LOWEST_VALUE_COLOR = Color(0.1, 1.0, 0.1, 0.7)

class SelectionSort(Algorithm):
    DIMENSIONS = 2
    COLORS = {
        "Unsorted": UNSORTED_COLOR,
        "Sorted": SORTED_COLOR,
        "Comparing": COMPARE_COLOR,
        "Current iteration lowest value": LOWEST_VALUE_COLOR
    }

    def __init__(self):
        Algorithm.__init__(self)
        self.width = 15
        self.padding = 10
        self.stepIndex = 0
        self.renderingData = []

    def setupRenderingData(self):
        self.renderingData = [
            (value, GenerateRectangle(self.width, value, UNSORTED_COLOR))
             for value in self.data
        ]

    def getRenderData(self):
        renderingData = [ renderingData for _, renderingData in self.renderingData ]
        dataCenter = (len(renderingData) * self.width + (len(renderingData) - 1) * self.padding) / 2.0

        # move the data along the x axis
        for i, rd in enumerate(renderingData):
            rd.SetPosition(i * (self.width + self.padding) - dataCenter, 0.0, 0.0)

        return renderingData

    def step(self):
        indexOfLowestValue = self.stepIndex
        selectedValue, selectedRenderingData = self.renderingData[indexOfLowestValue]
        selectedRenderingData.SetColor(COMPARE_COLOR)
        with self.context("Selecting lowest value"):
            lowestRenderingData = None
            for i, value, renderingData in enumerate(self.renderingData[self.stepIndex:]):
                renderingData.SetColor(COMPARE_COLOR)
                yield
                if value < lowestValue:
                    lowestValue = value
                    indexOfLowestValue = i
                    if lowestRenderingData is not None:
                        lowestRenderingData.SetColor(UNSORTED_COLOR)
                    lowestRenderingData = renderingData
                    lowestRenderingData.SetColor(LOWEST_VALUE_COLOR)
                else:
                    renderingData.SetColor(UNSORTED_COLOR)
                yield

        with self.context("Swapping"):
            tmp = self.renderingData[self.stepIndex]
            self.renderingData[self.stepIndex] = self.renderingData[indexOfLowestValue]
            self.renderingData[indexOfLowestValue] = tmp
            yield

        self.stepIndex = self.stepIndex + 1

    def endCondition(self):
        raise self.stepIndex == len(self.renderingData)
