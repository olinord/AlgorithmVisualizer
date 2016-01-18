from Queue import Queue
import sys
import time
from threading import Thread

from algorithmInterface import Algorithm


class NotAnAlgorithmException(Exception):
    def __init__(self, o):
        self.objectThatIsNotAnAlgorithm = o

    def __str__(self):
        return "%s: is not an algorithm" % type(self.objectThatIsNotAnAlgorithm)

class AlgorithmThread(Thread):
    def __init__(self, functionToRun, exceptionBucket):
        Thread.__init__(self)
        self.exceptionBucket = exceptionBucket
        self.functionToRun = functionToRun

    def run(self):
        try:
            self.functionToRun()
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.exceptionBucket.put(sys.exc_info())


class AlgorithmRunner(object):

    """
    This class should have the following features
    """
    def __init__(self, renderRefreshMethod=None):
        self.algorithm = None
        self.thread = None
        self.forcedToStop = False
        self.threadExceptionBucket = Queue()
        self.renderRefreshMethod = renderRefreshMethod
        self.sleepTime = 0.1

    def SetAlgorithm(self, algorithm):
        if not isinstance(algorithm, Algorithm):
            raise NotAnAlgorithmException(algorithm)

        self.algorithm = algorithm

    def run(self):
        self.forcedToStop = False
        self.threadExceptionBucket = Queue()
        self.thread = AlgorithmThread(self._run, self.threadExceptionBucket)
        self.thread.daemon = True
        self.thread.start()

    def _run(self):
        while not self.forcedToStop:
            self.step()
            time.sleep(self.sleepTime)

    def isRunning(self):
        return not self.thread is None and self.thread.isAlive()

    def step(self):
        if not self.algorithm.endCondition():
            for sleepMultiplier in self.algorithm.step():
                multiplier = 1.0
                if sleepMultiplier is not None:
                    multiplier = sleepMultiplier
                self.renderRefreshMethod()
                time.sleep(multiplier * self.sleepTime)

    def stop(self):
        self.forcedToStop = True

    def getThreadException(self):
        if self.threadExceptionBucket.empty():
            return None

        return self.threadExceptionBucket.get()[1]
