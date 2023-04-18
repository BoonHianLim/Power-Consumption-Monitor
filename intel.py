import os
import subprocess
import asyncio
import re
from concurrent.futures import ThreadPoolExecutor
from utility import reverse_readline, split, diffBetweenArr

_executor = ThreadPoolExecutor(1)
import qasync


class Intel():
  def __init__(self, intelDIR, appDIR, statusLabel):
    self.intelDIR = intelDIR
    self.appDIR = appDIR
    self.statusLabel = statusLabel
    self.idleSavePath = "results1.txt"
    self.runningSavePath = "results2.txt"

  def setIntelDIR(self, newPath):
    self.intelDIR = newPath
  def setAppDIR(self, newPath):
    self.appDIR = newPath
  def setIdleSavePath(self, newPath):
    self.idleSavePath = newPath
  def setRunningSavePath(self, newPath):
    self.runningSavePath = newPath
  def dirValid(self, path):
    return os.path.exists(path)

  def intelValid(self, path):
    return 'PowerLog' in path

  def pathValid(self):
    if not self.dirValid(self.intelDIR) or not self.intelValid(self.intelDIR):
      self.statusLabel.setText("Invalid Intel Power Gadget Directory!")
      return False
    elif not self.dirValid(self.appDIR):
      self.statusLabel.setText("Invalid App Directory!")
      return False
    return True

  async def startTest(self, monitorTime = 60, startUpWait = 0):
    self.statusLabel.setText("Start Measuring Power Consume in Idle State...")
    await self.monitor(monitorTime, savePath = self.idleSavePath)
    self.statusLabel.setText("Starting Test Application...")
    try:
      subprocess.call(self.appDIR)
    except Exception as e:
      print(e)
      self.statusLabel.setText("Start Test Application Fail. Terminating Test...")
      return False

    if (startUpWait != 0):
      await asyncio.sleep(startUpWait)

    self.statusLabel.setText("Start Measuring Power Consume in Running State...")
    await self.monitor(monitorTime, savePath = self.runningSavePath)

    # buffer time for the file to be generated
    await asyncio.sleep(3)

    generatedFile1Exist = await self.checkFileExist(self.idleSavePath)
    generatedFile2Exist = await self.checkFileExist(self.runningSavePath)
    if not generatedFile1Exist or not generatedFile2Exist:
      self.statusLabel.setText("Log file is not found, analysis cannot be done!")
      return False


    return True
  async def checkFileExist(self, filePath, attempt = 3):
    while attempt > 0:
      if self.dirValid(filePath):
        return True
      await asyncio.sleep(2)
      attempt -= 1
    return False
  async def monitor(self, time, savePath = "results.txt"):
    subprocess.Popen(self.intelDIR + ' -duration ' + str(time) + ' -file ' + savePath)
    await asyncio.sleep(time)

  def readAllData(self):
    return [self.readData(self.idleSavePath),self.readData(self.runningSavePath)]
  def readData(self, savePath = "results.txt"):
    result = ""
    for qline in reverse_readline(savePath):
      result += (qline + "\n")
      found = re.search("Total Elapsed Time", qline)
      if found != None:
        break
    return result

  def processData(self, idleText, runningText):
    listOfIdleFloat = re.findall("\d+\.\d+", idleText)
    listOfRunningFloat = re.findall("\d+\.\d+", runningText)

    splittedList = split(idleText, listOfIdleFloat)

    listofDiffFloat = diffBetweenArr(listOfRunningFloat,listOfIdleFloat)
    listofDiffFloat = ['{:.2f}'.format(x) for x in listofDiffFloat]

    headerString = '\n'.join(splittedList).strip()
    idleFloatString = '\n'.join(listOfIdleFloat).strip()
    runningFloatString = '\n'.join(listOfRunningFloat).strip()
    diffFloatString = '\n'.join(listofDiffFloat).strip()

    return [headerString,idleFloatString,runningFloatString,diffFloatString]

  def printData(self, printFn):
    self.statusLabel.setText("Generating Report...")
    idleText, runningText = self.readAllData()
    resultsList = self.processData(idleText,runningText)
    printFn(resultsList)