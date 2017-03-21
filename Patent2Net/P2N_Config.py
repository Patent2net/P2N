import os
import sys

class P2NConfig:
    def __init__(self):

        #opening request file, reading parameters
        if len(sys.argv) > 1:
            content = open(sys.argv[1], "r").readlines()
        else:
            content = open("..//requete.cql", "r").readlines()

        for line in content:
            if line.count('request:')>0:
                self.requete = self.getStr(line)
            if line.count('DataDirectory:')>0:
                self.ndf = self.getStr(line)
            if line.count('GatherContent')>0:
                self.GatherContent = self.getBoolean(line)
            if line.count('GatherBiblio')>0:
                self.GatherBiblio = self.getBoolean(line)
            if line.count('GatherPatent')>0:
                self.GatherPatent = self.getBoolean(line)
            if line.count('GatherFamilly')>0:
                self.GatherFamilly = self.getBoolean(line)
            if line.count('OPSGatherContentsv2-Iramuteq')>0:
                self.GatherIramuteq = self.getBoolean(line)

        self.generatePaths()

    def generatePaths(self):
        self.ListPatentPath = '..//DATA//'+self.ndf+'//PatentLists'
        self.ResultPathBiblio = '..//DATA//'+self.ndf+'//PatentBiblios'
        self.ResultContents = '..//DATA//'+self.ndf+'//PatentContents'
        self.temporPath = '..//DATA//'+self.ndf+'//tempo'
        self.ResultAbstractPath = self.ResultContents+'//Abstract'

        for path in [
            self.ListPatentPath,
            self.ResultPathBiblio,
            self.ResultContents,
            self.temporPath,
            self.ResultAbstractPath
        ]:
            if not os.path.isdir(path):
                os.makedirs(path)

    def getStr(self, line):
        return line.split(':')[1].strip()

    def getBoolean(self, line):
        s = self.getStr(line)
        if s.count('True')>0 or s.count('true')>0:
            return True # to gather contents
        else:
            return False

def LoadConfig():
    return P2NConfig()
