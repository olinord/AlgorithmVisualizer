from AlgorithmRunner.algorithmInterface import Algorithm
from Rendering.utilities import GenerateRectangle
from Rendering.color import Color

UNSORTED_COLOR = Color(1.0, 1.0, 1.0, 1.0)
SORTED_COLOR = Color(0.4, 1.0, 0.4, 1.0)
COMPARE_COLOR = Color(0.7, 0.7, 0.0, 1.0)
LOWEST_VALUE_COLOR = Color(1.0, 1.0, 0.0, 1.0)

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

        with self.stepContext("Selecting lowest value"):
            lowestValue, lowestRenderingData = self.renderingData[indexOfLowestValue]
            lowestRenderingData.SetColor(COMPARE_COLOR)
            for i, data in enumerate(self.renderingData[self.stepIndex:]):
                value, renderingData = data
                renderingData.SetColor(COMPARE_COLOR)
                yield 0.5
                if value < lowestValue or lowestValue is None:
                    lowestValue = value
                    indexOfLowestValue = self.stepIndex + i
                    if lowestRenderingData is not None:
                        lowestRenderingData.SetColor(UNSORTED_COLOR)
                    lowestRenderingData = renderingData
                    lowestRenderingData.SetColor(LOWEST_VALUE_COLOR)
                else:
                    renderingData.SetColor(UNSORTED_COLOR)
                yield 0.5

        with self.stepContext("Swapping"):
            tmp = self.renderingData[self.stepIndex]
            self.renderingData[self.stepIndex] = self.renderingData[indexOfLowestValue]
            self.renderingData[indexOfLowestValue] = tmp
            self.renderingData[self.stepIndex][1].SetColor(SORTED_COLOR)
            if self.stepIndex != indexOfLowestValue:
                self.renderingData[indexOfLowestValue][1].SetColor(UNSORTED_COLOR)

            yield 0.5

        self.stepIndex = self.stepIndex + 1

    def endCondition(self):
        return self.stepIndex == len(self.renderingData)
