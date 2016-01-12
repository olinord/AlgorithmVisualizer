from Queue import Queue
import sys
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
        except Exception:
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
        self.renderRefreshMethod = renderRefreshMethod or lambda: pass

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
        while not self.algorithm.endCondition() and not self.forcedToStop:
            for s in self.algorithm.step():
                self.renderRefreshMethod()

    def isRunning(self):
        return not self.thread is None and self.thread.isAlive()

    def step(self):
        if not self.algorithm.endCondition():
            for s in self.algorithm.step():
                self.renderRefreshMethod()

    def stop(self):
        self.forcedToStop = True

    def getThreadException(self):
        if self.threadExceptionBucket.empty():
            return None

        return self.threadExceptionBucket.get()[1]
