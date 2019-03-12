from TestClass2 import Testclass2

class Testclass(object):
    def __init__(self, var1):
        self.printthis = var1

    def printthing(self):
        Testclass2().printokay()


a = Testclass("jumbo")
a.printthing()