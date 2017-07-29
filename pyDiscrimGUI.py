# pyDiscrim:
# A Python3 program that interacts with a microcontroller -
# to perform state-based behavioral tasks.
#
# Version 3.79 -- Corrects 9DOF rollover.
#
# questions? --> Chris Deister --> cdeister@brown.edu

# bugs: must keep a benign matplotlib fig (Figure 1) open. Can be minmized, but has to be open.
# bugs: have to keep task feedback opebn

# todos: make outcome plot frequency
# todos: make rewardState and do reward1State reward2State

from tkinter import *
from tkinter import filedialog
from threading import Thread
import serial
import numpy as np

import matplotlib 
matplotlib.use("TkAgg")
from matplotlib.lines import Line2D
from matplotlib import pyplot as plt
from matplotlib.figure import Figure


import time
import datetime
import random
import math
import struct
import sys
import os
import pandas as pd
import threading
import queue

class serialFunctions:

    def syncSerial(self):
        ranHeader=0
        self.dataExists=0
        while ranHeader==0:
            gaveFeedback=0
            ranHeader=1
            loopCount=0
        while ranHeader==1:
            self.comObj.write(struct.pack('>B', self.bootState))
            serialFunctions.serial_readDataFlush(self)
            if self.dataAvail==1:
                self.currentState=int(self.sR[self.stID_state])
                if self.currentState!=self.bootState:
                    if gaveFeedback==0:
                        print('mc state is not right, thinks it is #: {}'.format(self.currentState))
                        print('will force boot state, might take a second or so ...')
                        print('!!!! ~~> UI may become unresponsive for 1-30 seconds or so, but I havent crashed ...')
                        gaveFeedback=1
                    loopCount=loopCount+1
                    if loopCount % 5000 ==0:
                        print('still syncing: state #: {}; loop #: {}'.format(self.currentState,loopCount))
                elif self.currentState==self.bootState:
                    print('ready: mc is in state #: {}'.format(self.currentState))
                    return

    def serial_initComObj(self):
        if self.comObjectExists==0:
            print('Opening serial port: {}'.format(self.comPath.get()))
            self.comObj = serial.Serial(self.comPath.get(),self.baudSelected.get()) 
            serialFunctions.syncSerial(self)
            self.comObjectExists=1



            # update the GUI
            self.comPathLabel.config(text="COM Object Connected ***",justify=LEFT,fg="green",bg="black") 
            self.comPathEntry.config(state=DISABLED)
            self.baudPick.config(state=DISABLED)
            self.createCom_button.config(state=DISABLED)
            self.startBtn.config(state=NORMAL)
            self.closeComObj_button.config(state=NORMAL)
            self.syncComObj_button.config(state=NORMAL)
            # self.taskProbsBtn.invoke()
            # self.stateTogglesBtn.invoke()
        
    def serial_closeComObj(self):
        if self.comObjectExists==1:
            if self.dataExists==1:
                self.data_saveData()
            serialFunctions.syncSerial(self)
            self.comObj.close()
            self.comObjectExists=0
            print('> i closed the COM object')
            
            # update the GUI
            self.comPathLabel.config(text="COM Port Location:",justify=LEFT,fg="black",bg="white")
            self.comPathEntry.config(state=NORMAL)
            self.baudPick.config(state=NORMAL)
            self.createCom_button.config(state=NORMAL)
            self.startBtn.config(state=DISABLED)
            self.closeComObj_button.config(state=DISABLED)
            self.syncComObj_button.config(state=DISABLED)
            # self.taskProbsBtn.invoke()
            # self.stateTogglesBtn.invoke()

    def serial_readDataFlush(self):

        self.comObj.flush()
        serialFunctions.serial_readData(self,'data')

    def serial_readData(self,header):
        self.sR=self.comObj.readline().strip().decode()
        self.sR=self.sR.split(',')
        #todo: abstract length below:
        if len(self.sR)==7 and self.sR[self.stID_header]==header and str.isnumeric(self.sR[1])==1 and str.isnumeric(self.sR[2])==1 :
            self.dataAvail=1
        elif len(self.sR)!=7 or self.sR[self.stID_header] != header or str.isnumeric(self.sR[1])!=1 or str.isnumeric(self.sR[2])!=1:
            self.dataAvail=0

class taskFeedbackFigure:

    def taskPlotWindow(self):
        self.fig1 = plt.figure(100)
        self.fig1.suptitle('state 0', fontsize=10)
        subIds=[221,222,223,224]
    
        for x in range(0,4):
            # exec('self.fig{}=Figure(figsize=(1, 1), dpi=100)'.format(x))
            exec('self.initX{}=[]'.format(x))
            exec('self.initY{}=[]'.format(x))
            exec('self.ax{}=self.fig1.add_subplot({})'.format(x,subIds[x]))
            exec('self.line{}=Line2D(self.initX{},self.initY{})'.format(x,x,x))
            exec('self.ax{}.add_line(self.line{})'.format(x,x))

        self.ax0.set_ylim([0,25])
        self.ax1.set_ylim([-500,2000])
        self.ax2.set_ylim([0,1100])
        self.ax3.set_ylim([0,1100])
        plt.tight_layout()
        plt.show()
    
    def updateTaskPlot(self):
        splt=int(self.sampsToPlot.get())
        y0=self.arStates[-splt:]
        x0=self.mcTrialTime[-splt:]
        y1=self.absolutePosition[-splt:]
        y2=self.lickValsA[-splt:]
        y3=self.lickValsB[-splt:]

        for x in range(0,4):
            exec('self.line{}.set_xdata(x0)'.format(x))
            exec('self.line{}.set_ydata(y{})'.format(x,x))
            exec('self.ax{}.relim()'.format(x))
            exec('self.ax{}.autoscale_view()'.format(x))
        plt.draw()
        plt.pause(self.pltDelay)

class setUserVars:

    def setStateNames(self):
        self.stateNames=\
        ['bootState','waitState','initiationState','cue1State','cue2State',\
        'stim1State','stim2State','catchState','saveState','rewardState','rewardState2',\
        'neutralState','punishState','endState','defaultState']

        self.stateIDs=\
        [0,1,2,3,4,\
        5,6,7,13,21,22,\
        23,24,25,29]
        
        self.mapAssign(self.stateNames,self.stateIDs)
        
        self.stateBindings=pd.Series(self.stateIDs,index=self.stateNames)    

    def setSessionVars(self):
        # session vars
        self.sessionVarIDs=['ranTask','dataExists','comObjectExists',\
        'taskProbsRefreshed','stateVarsRefreshed','currentTrial',\
        'currentState','currentSession','sessionTrialCount']
        self.sessionVarVals=\
        [0,0,0,\
         0,0,1,\
         0,1,1]
        self.mapAssign(self.sessionVarIDs,self.sessionVarVals)

    def setStateVars(self):
        self.stateVarLabels=\
        ['dPos','movThr','movTimeThr','stillTime','stillLatch',\
        'stillTimeStart','distThr','timeOutDuration']
        self.stateVarValues=\
        [0,40,2,0,0,\
        0,1000,2]
        
        self.mapAssign(self.stateVarLabels,self.stateVarValues)

    def setTaskProbs(self):

        self.t1ProbLabels='sTask1_prob','sTask1_target_prob',\
            'sTask1_distract_prob','sTask1_target_reward_prob',\
            'sTask1_target_punish_prob','sTask1_distract_reward_prob',\
            'sTask1_distract_punish_prob'
        self.t1ProbValues=[0.5,0.5,0.5,1.0,0.0,0.0,1.0]
        self.mapAssign(self.t1ProbLabels,self.t1ProbValues)

        self.t2ProbLabels='sTask2_prob','sTask2_target_prob',\
                'sTask2_distract_prob','sTask2_target_reward_prob',\
                'sTask2_target_punish_prob','sTask2_distract_reward_prob',\
                'sTask2_distract_punish_prob'
        self.t2ProbValues=[0.5,0.5,0.5,1.0,0.0,0.0,1.0]
        self.mapAssign(self.t2ProbLabels,self.t2ProbValues)

class analysis:

    def getQunat(self,pyList,quantileCut):
        tA=np.abs(np.array(pyList))

    def updateLickThresholdA(self,dataSpan):  #todo: should be one function for all

        if self.ux_adaptThresh.get()==1:
            # print(int(self.lickThresholdStrValA))
            tA=np.abs(np.array(dataSpan))
            # print(int(np.percentile(aaa[np.where(aaa != 0)[0]],75)))
            self.lickThresholdStrValA.set(str(np.percentile(tA[np.where(tA != 0)[0]],75)))
            self.lickMinMaxA=[min(dataSpan),max(dataSpan)]

    def updateLickThresholdB(self,dataSpan,quantileCut):

        if self.ux_adaptThresh.get()==1:
            # print(int(self.lickThresholdStrValB))
            tA=np.abs(np.array(dataSpan))
            # print(int(np.percentile(aaa[np.where(aaa != 0)[0]],quantileCut)))
            self.lickThresholdStrValB.set(str(np.percentile(tA[np.where(tA != 0)[0]],quantileCut)))
            self.lickMinMaxB=[min(dataSpan),max(dataSpan)]

    def lickDetection(self):
    
        if self.lickValsA[-1]>int(self.lickThresholdStrValA.get()) and self.lickThresholdLatchA==0:
            self.thrLicksA.append(1)
            self.lastLickCountA=self.lastLickCountA+1
            self.stateLickCount0.append(self.lastLickCountA)
            
            self.lickThresholdLatchA=1
            self.lastLickA=self.mcTrialTime[-1]
            

        elif self.lickValsA[-1]<=int(self.lickThresholdStrValA.get()) or self.lickThresholdLatchA==1:
            self.thrLicksA.append(0)
            self.stateLickCount0.append(self.lastLickCountA)
            self.lickThresholdLatchA=1;
            

        if self.lickValsB[-1]>int(self.lickThresholdStrValB.get()) and self.lickThresholdLatchB==0:
            self.thrLicksB.append(1)
            self.lastLickCountB=self.lastLickCountB+1
            self.stateLickCount1.append(self.lastLickCountB)
            
            self.lickThresholdLatchA=1
            self.lastLickA=self.mcTrialTime[-1]

        elif self.lickValsB[-1]<=int(self.lickThresholdStrValB.get()) or self.lickThresholdLatchA==1:
            self.thrLicksB.append(0)
            self.stateLickCount1.append(self.lastLickCountB)

        if self.mcTrialTime[-1]-self.lastLickA>0.01:
            self.lickThresholdLatchA=0;

        if self.mcTrialTime[-1]-self.lastLickB>0.01:
            self.lickThresholdLatchB=0;


    def lickDetectionDebug(self):

        if self.lickValsA[-1]>int(self.lickThresholdStrValA.get()):
            self.thrLicksA[-1]=1
            self.lastLickCountA=self.lastLickCountA+1
            self.stateLickCount0[-1]=self.lastLickCountA+1


        if self.lickValsB[-1]>int(self.lickThresholdStrValB.get()):
            self.thrLicksB[-1]=1
            self.lastLickCountB=self.lastLickCountB+1
            self.stateLickCount1[-1]=self.lastLickCountB+1

class stateCallbacks:

    def checkMotion(self,acelThr,sampThr):
        # pt=2+2
        if len(self.posDelta)>sampThr:
            runAcel=np.mean(np.array(self.posDelta[-sampThr:]))
            if runAcel<acelThr:
                lastLatch=self.stillLatch
                self.stillLatch=1
                latchDelta=self.stillLatch-lastLatch
                if latchDelta!=0:
                    self.stillTimeStart=self.mcTrialTime[-1]
                self.stillTime=self.mcTrialTime[-1]-self.stillTimeStart
            elif runAcel>=acelThr:
                self.stillLatch=0
                self.stillTime=0

    def defineOutcome(self,rwCnt):
        tRCnt=str(self.rewardContingency[-1])
        sPres=int(tRCnt[0])
        rwdSpout=int(tRCnt[1])
        offSpout=abs(int(tRCnt[1])-1)

        targetMinLicked=eval('self.stateLickCount{}[-1]>=self.minTarget{}Licks'.format(rwdSpout,sPres))
        targetMaxLicked=eval('self.stateLickCount{}[-1]>=self.maxTarget{}Licks'.format(rwdSpout,sPres))
        distractMinLicked=eval('self.stateLickCount{}[-1]>=self.minOffTarget{}Licks'.format(offSpout,sPres))
        distractMaxLicked=eval('self.stateLickCount{}[-1]>=self.maxTarget{}Licks'.format(offSpout,sPres))

        if targetMinLicked==1 and targetMaxLicked == 0 and distractMinLicked == 0:

            print('licked spout {}: on target -> reward'.format(rwdSpout))
            exec('self.trialOutcome.append({}1)'.format(sPres))
            if rwdSpout==0:
                stateFunctions.switchState(self,self.rewardState)
            elif rwdSpout==1:
                stateFunctions.switchState(self,self.rewardState2)
        
            print(self.trialOutcome[-1])

        elif targetMinLicked==0 and distractMinLicked == 1:
            print('licked spout {}: off target -> punish'.format(offSpout))
            exec('self.trialOutcome.append({}2)'.format(sPres))
            stateFunctions.switchState(self,self.punishState)
            print(self.trialOutcome[-1])

        elif targetMinLicked==1 and distractMinLicked == 1:
            print('licked both spouts: ambiguous -> punish')
            exec('self.trialOutcome.append({}3)'.format(sPres))
            stateFunctions.switchState(self,self.neutralState)
            print(self.trialOutcome[-1])

    def waitStateCB(self):       
        stateCallbacks.checkMotion(self,1,10)
        if self.stillLatch==1 and self.stillTime>0.75:  #var todo minStill
            print('Still! ==> S1 --> S2')
            stateFunctions.switchState(self,self.initiationState)

    def initiationStateHead(self):
        t1P=self.sTask1_prob
        self.task_switch=random.random()
        if self.task_switch<=t1P:
            self.cueSelected=1
        elif self.task_switch>t1P:
            self.cueSelected=2

    def initiationStateCB(self):
        if self.absolutePosition[-1]>self.distThr:
            print('moving spout; cue stim task #{}'.format(self.cueSelected))
            eval('stateFunctions.switchState(self,self.cue{}State)'.format(self.cueSelected))

    def cue1StateHead(self):
        self.outcomeSwitch=random.random()
        o1P=self.sTask1_target_prob
        if self.outcomeSwitch<=o1P:
            self.stimSelected=1
        elif self.outcomeSwitch>o1P:
            self.stimSelected=2

    def cue1StateCB(self):
        trP=0.5
        stateCallbacks.checkMotion(self,1,10)
        if self.stillLatch==1 and self.stillTime>1.5:
            self.cuePresented=1;
            print('Still: Task 1 --> Stim {}: Rwd On Spout {}'.format(self.stimSelected,self.stimSelected-1))
            eval('stateFunctions.switchState(self,self.stim{}State)'.format(self.stimSelected))
            exec('self.rewardContingency.append({}{})'.format(self.stimSelected,self.stimSelected-1))
            print(self.rewardContingency[-1])

    def cue2StateHead(self):
        self.outcomeSwitch=random.random()
        o2P=self.sTask2_target_prob
        if self.outcomeSwitch<=o2P:
            self.stimSelected=2
        elif self.outcomeSwitch>o2P:
            self.stimSelected=1

    def cue2StateCB(self): 
        stateCallbacks.checkMotion(self,1,10)
        if self.stillLatch==1 and self.stillTime>1.5:
            self.cuePresented=2;
            print('Still: Task 2 --> Stim {}: Rwd On Spout {}'.format(self.stimSelected,self.stimSelected-1))
            eval('stateFunctions.switchState(self,self.stim{}State)'.format(self.stimSelected))
            exec('self.rewardContingency.append({}{})'.format(self.stimSelected,self.stimSelected-1))
            print(self.rewardContingency[-1])
    
    def stim1StateCB(self):
        self.minStim1Time=0
        self.minTarget1Licks=1
        self.maxTarget1Licks=100
        self.maxOffTarget1Licks=1
        self.minOffTarget1Licks=1
        self.reportMax1Time=20

        if self.mcStateTime[-1]>self.minStim1Time:
            if self.mcStateTime[-1]<self.reportMax1Time:
                stateCallbacks.defineOutcome(self,self.rewardContingency)

            elif self.mcStateTime[-1]>=self.reportMax1Time:
                self.trialOutcome.append(10)
                print('timed out: did not report')
                stateFunctions.switchState(self,self.neutralState)      #5

    def stim2StateCB(self):
        self.minStim2Time=0
        self.minTarget2Licks=1
        self.maxTarget2Licks=100
        self.maxOffTarget2Licks=1
        self.minOffTarget2Licks=1
        self.reportMax2Time=10

        if self.mcStateTime[-1]>self.minStim2Time:
            if self.mcStateTime[-1]<self.reportMax2Time:
                stateCallbacks.defineOutcome(self,self.rewardContingency)
            elif self.mcStateTime[-1]>=self.reportMax2Time:
                self.trialOutcome.append(20)
                print('timed out: did not report')
                stateFunctions.switchState(self,self.neutralState) 

    def rewardStateCB(self):
        self.rewardTime=1
        if self.mcStateTime[-1]<self.rewardTime:
            print('rewarding')
            stateFunctions.switchState(self,self.saveState)

    def rewardState2CB(self):
        self.rewardTime2=1
        if self.mcStateTime[-1]<self.rewardTime2:
            print('rewarding')
            stateFunctions.switchState(self,self.saveState)

    def neutralStateCB(self):
        self.neutralTime=1
        if self.mcStateTime[-1]<0.1:
            print('no reward')
            stateFunctions.switchState(self,self.saveState)

    def punishStateCB(self):
        if self.mcTrialTime[-1]-self.entryTime>=self.timeOutDuration:
            print('timeout of {} seconds is over'.format(self.timeOutDuration))
            stateFunctions.switchState(self,self.saveState)

class stateFunctions:
    def switchState(self,targetState):
        
        self.targetState=targetState
        
        if self.dataExists==1:
            self.pyStatesRS.append(self.targetState)
            self.pyStatesRT.append(self.mcTrialTime[-1])
        print('pushing: s{} -> s{}'.format(self.currentState,targetState))
        self.comObj.write(struct.pack('>B', targetState))
        stateFunctions.exitState(self,self.currentState)

    def exitState(self,cState): 
        self.cState=cState
        while self.currentState==self.cState:      
            serialFunctions.serial_readDataFlush(self)
            if self.dataAvail==1:
                pyDiscrim_mainGUI.data_parseData(self)
                self.currentState=int(self.sR[self.stID_state])
        self.pyStatesTS.append(self.currentState)
        self.pyStatesTT.append(self.mcTrialTime[-1])

    def stateHeader(self,upSt):
        self.upSt=upSt
        # self.tp_frame.title('Task Feedback: S={}'.format(self.currentState))
        ranHeader=0 # set the latch, the header runs once per entry.
        while ranHeader==0:
            self.cycleCount=1
            self.lastPos=0 # reset where we think the animal is
            self.lastLickCountA=0
            self.lastLickCountB=0
            self.entryTime=self.mcTrialTime[-1] # log state entry time
            self.stillLatch=0
            self.stillTime=0
            self.stillTimeStart=0
            print('in state # {}'.format(self.currentState))
            ranHeader=1 # fire the latch
        
    def coreState(self):
        uiUp=int(self.uiUpdateSamps.get())
        self.fireCallback=0
        serialFunctions.serial_readDataFlush(self)
        if self.dataAvail==1:
            pyDiscrim_mainGUI.data_parseData(self)
            if self.cycleCount % uiUp == 0:
                self.updatePlotCheck()
            self.fireCallback=1
            self.cycleCount=self.cycleCount+1;

class mainWindow:

    def addMainBlock(self,startRow):
        self.startRow = startRow
        self.blankLine(self.master,startRow)

        self.mainCntrlLabel = Label(self.master, text="Main Controls:")\
        .grid(row=startRow,column=0,sticky=W)

        self.quitBtn = Button(self.master,text="Exit Program",command = lambda: mainWindow.mwQuitBtn(self), width=self.col2BW)
        self.quitBtn.grid(row=startRow+1, column=2)

        self.startBtn = Button(self.master, text="Start Task",\
            width=10, command=lambda: mainTask.runSession(self) ,state=DISABLED)
        self.startBtn.grid(row=startRow+1, column=0,sticky=W,padx=10)

        self.endBtn = Button(self.master, text="End Task",width=self.col2BW, \
            command=lambda: stateFunctions.switchState(self,self.endState),state=DISABLED)
        self.endBtn.grid(row=startRow+2, column=0,sticky=W,padx=10)

        self.stateEditBtn = Button(self.master, text="State Editor",width=self.col2BW, \
            command=self.stateEditWindow,state=NORMAL)
        self.stateEditBtn.grid(row=startRow+2,column=2,sticky=W,padx=10)

    def addSerialBlock(self,startRow):
        self.startRow = startRow

        # @@@@@ --> Serial Block
        self.comPathLabel = Label(self.master,text="COM Port Location:",justify=LEFT)
        self.comPathLabel.grid(row=startRow,column=0,sticky=W)

        self.comPath=StringVar(self.master)
        self.comPathEntry=Entry(self.master,textvariable=self.comPath)
        self.comPathEntry.grid(row=startRow+1, column=0)
        self.comPathEntry.config(width=24)
        
        if sys.platform == 'darwin':
            self.comPath.set('/dev/cu.usbmodem2762721')
        elif sys.platform == 'win':
            self.comPath.set('COM11')

        self.baudEntry_label = Label(self.master,text="BAUD Rate:",justify=LEFT)
        self.baudEntry_label.grid(row=startRow+2, column=0,sticky=W)

        self.baudSelected=IntVar(self.master)
        self.baudSelected.set(115200)
        self.baudPick = OptionMenu(self.master,self.baudSelected,115200,19200,9600)
        self.baudPick.grid(row=startRow+2, column=0,sticky=E)
        self.baudPick.config(width=14)

        self.createCom_button = Button(self.master,text="Start Serial",width=self.col2BW, \
            command=lambda: serialFunctions.serial_initComObj(self))
        self.createCom_button.grid(row=startRow+0, column=2)
        self.createCom_button.config(state=NORMAL)

        self.syncComObj_button = Button(self.master,text="Sync Serial",width=self.col2BW, \
            command=lambda: serialFunctions.syncSerial(self))
        self.syncComObj_button.grid(row=startRow+1, column=2)
        self.syncComObj_button.config(state=DISABLED)  

        self.closeComObj_button = Button(self.master,text="Close Serial",width=self.col2BW, \
            command=lambda: serialFunctions.serial_closeComObj(self))
        self.closeComObj_button.grid(row=startRow+2, column=2)
        self.closeComObj_button.config(state=DISABLED)

    def addSessionBlock(self,startRow):
        # @@@@@ --> Session Block
        self.sesPathFuzzy=1 # This variable is set when we guess the path.

        self.animalID='yourID'
        self.dateStr = datetime.datetime.\
        fromtimestamp(time.time()).strftime('%H:%M (%m/%d/%Y)')

        self.blankLine(self.master,startRow)
        self.sessionStuffLabel = Label(self.master, text="Session Stuff: ",justify=LEFT)\
        .grid(row=startRow+1, column=0,sticky=W)

        self.timeDisp = Label(self.master, text=' #{} started: '\
            .format(self.currentSession) + self.dateStr,justify=LEFT)
        self.timeDisp.grid(row=startRow+2,column=0,sticky=W)

        self.dirPath=StringVar(self.master)
        self.pathEntry=Entry(self.master,textvariable=self.dirPath,width=24,bg='grey')
        self.pathEntry.grid(row=startRow+3,column=0,sticky=W)
        self.dirPath.set(os.path.join(os.getcwd(),self.animalID))

        self.setPath_button = Button(self.master,text="<- Set Path",command=lambda: mainWindow.mwPathBtn(self),width=self.col2BW)
        self.setPath_button.grid(row=startRow+3,column=2)

        self.aIDLabel=Label(self.master, text="animal id:").grid(row=startRow+4,column=0,sticky=W)
        self.animalIDStr=StringVar(self.master)
        self.animalIDEntry=Entry(self.master,textvariable=self.animalIDStr,width=14,bg='grey')
        self.animalIDEntry.grid(row=startRow+4,column=0,sticky=E)
        self.animalIDStr.set(self.animalID)

        self.totalTrials_label = Label(self.master,text="total trials:")\
        .grid(row=startRow+5,column=0,sticky=W)
        self.totalTrials=StringVar(self.master)
        self.totalTrials_entry=Entry(self.master,textvariable=self.totalTrials)
        self.totalTrials_entry.grid(row=startRow+5,column=0,sticky=E)
        self.totalTrials.set('100')
        self.totalTrials_entry.config(width=10)


        self.curSession_label = Label(self.master,text="current session:")\
        .grid(row=startRow+6,column=0,sticky=W)
        self.curSession=StringVar(self.master)
        self.curSession_entry=Entry(self.master,textvariable=self.currentSession)
        self.curSession_entry.grid(row=startRow+6,column=0,sticky=E)
        self.curSession.set('1')
        self.curSession_entry.config(width=10)

        self.taskProbsBtn = Button(self.master,text='Task Probs',width=self.col2BW,\
            command=self.taskProbWindow)
        self.taskProbsBtn.grid(row=startRow+4, column=2)
        self.taskProbsBtn.config(state=NORMAL)

        self.stateTogglesBtn = Button(self.master,text = 'State Toggles',width=self.col2BW,\
            command=self.stateToggleWindow)
        self.stateTogglesBtn.grid(row=startRow+5, column=2)
        self.stateTogglesBtn.config(state=NORMAL)
        
        self.stateVarsBtn = Button(self.master,text = 'State Vars',width=self.col2BW,\
            command = self.stateVarWindow)
        self.stateVarsBtn.grid(row=startRow+6, column=2)
        self.stateVarsBtn.config(state=NORMAL)

        self.loadAnimalMetaBtn = Button(self.master,text = 'Load Metadata',\
            width = self.col2BW, command = lambda: mainWindow.mwLoadMetaBtn(self))
        self.loadAnimalMetaBtn.grid(row=startRow+1, column=2)
        self.loadAnimalMetaBtn.config(state=NORMAL)

        self.saveCurrentMetaBtn=Button(self.master,text="Save Cur. Meta",\
            command=self.exportAnimalMeta, width=self.col2BW)
        self.saveCurrentMetaBtn.grid(row=startRow+2,column=2)

    def addPlotBlock(self,startRow):
        self.blankLine(self.master,startRow)
        self.plotBlock_label = Label(self.master,text="Plotting:")
        self.plotBlock_label.grid(row=startRow+1, column=0,sticky=W)
        
        self.sampPlot_label = Label(self.master,text="samples / plot:")
        self.sampPlot_label.grid(row=startRow+2,column=0,sticky=W)
        self.sampsToPlot=StringVar(self.master)
        self.sampPlot_entry=Entry(self.master,width=5,textvariable=self.sampsToPlot)
        self.sampPlot_entry.grid(row=startRow+2, column=0,sticky=E)
        self.sampsToPlot.set('1000')

        self.uiUpdateSamps_label = Label(self.master, text="samples / UI update:")
        self.uiUpdateSamps_label.grid(row=startRow+3, column=0,sticky=W)
        self.uiUpdateSamps=StringVar(self.master)
        self.uiUpdateSamps_entry=Entry(self.master,width=5,textvariable=self.uiUpdateSamps)
        self.uiUpdateSamps_entry.grid(row=startRow+3, column=0,sticky=E)
        self.uiUpdateSamps.set('500')


        self.togglePlotWinBtn=Button(self.master,text = 'Toggle Plot',width=self.col2BW,\
            command=lambda:taskFeedbackFigure.taskPlotWindow(self))
        self.togglePlotWinBtn.grid(row=startRow+2, column=2)
        self.togglePlotWinBtn.config(state=NORMAL)

        self.debugWindowBtn=Button(self.master,text = 'Debug Toggles',width=self.col2BW,\
            command=self.debugWindow)
        self.debugWindowBtn.grid(row=startRow+3, column=2)
        self.debugWindowBtn.config(state=NORMAL)

        self.perfWindowBtn=Button(self.master,text = 'Perf Window',width=self.col2BW,\
            command=self.performanceWindow)
        self.perfWindowBtn.grid(row=startRow+4, column=2)
        self.perfWindowBtn.config(state=NORMAL)


        self.xVarsToPlot=StringVar(self.master)
        self.yVarsToPlot=StringVar(self.master)


        self.lickMinMaxA=[-5,10]
        self.initPltRng=2.5
        self.pltDelay=0.000001 
        self.segPlot=10000
        self.lastPos=0
        self.lastOrientation=0

        # this can be changed, but doesn't need to be. 
        #We have to have a plot delay, but it can be tiny.
        self.stateDiagX=[1,1,3,5,5,7,7,7,7,9,9,9,9,1]
        self.stateDiagY=[3,5,5,6,4,8,6,4,2,8,6,4,2,7]
        self.smMrk=10
        self.lrMrk=20
        self.postionMin=-10000;
        self.positionMax=30000;
        self.lickMin=0
        self.lickMax=1000
        self.timeBase=1000000

    def addLickDetectionBlock(self,startRow):
        self.blankLine(self.master,startRow)
        self.lickDetectionLabel = Label(self.master, text="Lick Detection:")
        self.lickDetectionLabel.grid(row=startRow+1, column=0,sticky=W)

        self.ux_adaptThresh=StringVar(self.master)
        self.ux_adaptThreshToggle=Checkbutton(self.master, \
            text="Ad Thr?  |",variable=self.ux_adaptThresh)
        self.ux_adaptThreshToggle.grid(row=startRow+2, column=0,sticky=W,padx=5)
        self.ux_adaptThreshToggle.select()

        self.lickValuesOrDeltas=StringVar(self.master)
        self.ux_lickValuesToggle=Checkbutton(self.master, \
            text="Lk Val?   |",variable=self.lickValuesOrDeltas)
        self.ux_lickValuesToggle.grid(row=startRow+3, column=0,sticky=W,padx=5)
        self.ux_lickValuesToggle.select()

        self.lickThresholdA_label = Label(self.master, text="Thr A:")
        self.lickThresholdA_label.grid(row=startRow+2,column=0,padx=84,sticky=E)
        self.lickThresholdStrValA=StringVar(self.master)
        
        self.lickThresholdB_label = Label(self.master,text="Thr B:")
        self.lickThresholdB_label.grid(row=startRow+3,column=0,padx=84,sticky=E)
        self.lickThresholdStrValB=StringVar(self.master)

        self.aThrEntry=Entry(self.master,width=6,textvariable=self.lickThresholdStrValA)
        self.aThrEntry.grid(row=startRow+2, column=0,sticky=E,padx=5)
        self.bThrEntry=Entry(self.master,width=6,textvariable=self.lickThresholdStrValB)
        self.bThrEntry.grid(row=startRow+3, column=0,sticky=E,padx=5)
        
        self.lickThresholdStrValA.set(400)
        self.lickThresholdStrValB.set(400)
        self.lickThresholdLatchA=0;
        self.lickThresholdLatchB=0;
        self.lastLickA=0;
        self.lastLickB=0;

        # plot stuff
        self.lickMax_label = Label(self.master, text="Lick Max:")
        self.lickMax_label.grid(row=startRow+4,column=0,sticky=W,padx=76)
        self.lickPlotMax=StringVar(self.master)
        self.lickMax_entry=Entry(self.master,width=6,textvariable=self.lickPlotMax)
        self.lickMax_entry.grid(row=startRow+4, column=0,sticky=E,padx=5)
        self.lickPlotMax.set('2000')

    def mainWindowPopulate(self):
        # The main window is organized as logical blocks.
        # You define a block as a function that takes a Tkinter Grid start row as an argument.
        # example: self.addSerialBlock(serStart)

        self.master.title("pyDiscrim")
        self.col2BW=10
        pStart=0
    
        serStart=pStart+3
        sesStart=serStart+8
        plotStart=sesStart+7
        lickStart=plotStart+7
        mainStart=lickStart+7

        mainWindow.addSerialBlock(self,serStart)
        mainWindow.addSessionBlock(self,sesStart)
        mainWindow.addPlotBlock(self,plotStart)
        mainWindow.addLickDetectionBlock(self,lickStart)
        mainWindow.addMainBlock(self,mainStart)

        # look in whatever it thinks the working dir is and look for metadata to populate
        self.dirAnimalMetaExists=os.path.isfile(self.dirPath.get() + '.lastMeta.csv')

    def mwQuitBtn(self):
        if self.ranTask==0 or self.comObjectExists==0:  
            print('*** bye: closed without saving ***')
            exit()
        else: 
            print('!!!! going down')
            if self.dataExists==1:
                self.data_saveData()
                print('... saved some remaining data')
            if self.comObjectExists==1:
                serialFunctions.syncSerial(self)
                print('... resyncd serial state')
                self.comObj.close()
                print('... closed the com obj')
            exit()

    def mwPathBtn(self):
        self.getPath()
        self.dirPath.set(self.selectPath)

        self.pathEntry.config(bg='white')
        self.animalIDStr.set(os.path.basename(self.selectPath))
        self.animalIDEntry.config(bg='white')
        self.sesPathFuzzy=0
        metaString='{}{}_animalMeta.csv'.format(self.selectPath + '/',self.animalIDStr.get())
        stateString='{}{}_stateMap.csv'.format(self.selectPath + '/',self.animalIDStr.get())
        self.loadedMeta=os.path.isfile(metaString)
        self.loadedStates=os.path.isfile(stateString)
        if self.loadedMeta is True:
            tempMeta=pd.read_csv(metaString,index_col=0)
            self.parseMetaDataStrings(tempMeta)
            print("loaded {}'s previous settings".format(self.animalIDStr.get()))
        if self.loadedStates is True:
            tempStates=pd.Series.from_csv(stateString)
            print("loaded {}'s previous state assignments, but didn't parse them".\
                format(self.animalIDStr.get()))

    def mwSaveMetaBtn(self):
        metaString='{}{}_animalMeta.csv'.format(self.pathSet,self.animalIDStr.get())
        stateString='{}{}_stateMap.csv'.format(self.pathSet,self.animalIDStr.get())
        self.loadedMeta=os.path.isfile(metaString)
        self.loadedStates=os.path.isfile(stateString)
        if self.loadedMeta is True:
            tempMeta=pd.read_csv(metaString,index_col=0)
        if self.loadedStates is True:
            tempStates=pd.Series.from_csv(stateString)
        
        tempMeta.to_csv('.lastMeta.csv')
        tempStates.to_csv('.lastStates.csv')

    def mwLoadMetaBtn(self):
        aa=filedialog.askopenfilename(title = "what what?",defaultextension='.csv')
        tempMeta=pd.read_csv(aa,index_col=0)
        aa=tempMeta.dtypes.index
        varNames=[]
        varVals=[]
        for x in range(0,len(tempMeta.columns)):
            varNames.append(aa[x])
            varVals.append(tempMeta.iloc[0][x])
        self.mapAssignStringEntries(varNames,varVals)

class mainTask:

    def taskHeader(self):
        self.endBtn.config(state=NORMAL)
        self.startBtn.config(state=DISABLED)
        print('started at state #: {}'.format(self.currentState))
        self.data_makeContainers()
        self.uiUpdateDelta=int(self.uiUpdateSamps.get())
        self.ranTask=self.ranTask+1
        self.shouldRun=1
        self.trialTimes=[]
        self.rcCol=[]
        self.toCol=[]
        self.t1RCPairs=[10,21] # stim 1, reward left; stim 2 reward right
        self.t2RCPairs=[11,20]

    def runSession(self):
        mainTask.taskHeader(self)
        self.sessionStartTime=time.time()
        while self.currentTrial <=int(self.totalTrials.get()) and self.shouldRun==1:
            self.trialStartTime=time.time()
            mainTask.trial(self)
        self.currentSession=self.currentSession+1
        self.exportAnimalMeta()
        self.endBtn.config(state=DISABLED)
        self.startBtn.config(state=NORMAL)
        self.stateBindings.to_csv('{}{}_stateMap.csv'.format(self.dirPath.get() + '/',self.animalIDStr.get()))
        print('I completed {} trials.'.format(self.currentTrial-1))
        print('!!!!!!! --> Session #:{} Finished'.format(self.ranTask))
        self.updateDispTime()
        serialFunctions.syncSerial(self)
    
    def trial(self):
        try:
            #S0 -----> hand shake (initialization state)
            if self.currentState==self.bootState:
                serialFunctions.serial_readDataFlush(self)
                print('in state 0: boot state')
                self.lastPos=0
                self.lastOrientation=0

                while self.currentState==self.bootState:
                    serialFunctions.serial_readDataFlush(self)
                    if self.dataAvail==1:
                        pyDiscrim_mainGUI.data_parseData(self)
                        stateFunctions.switchState(self,self.waitState)
            
            #S1 -----> trial wait state
            elif self.currentState==self.waitState:
                stateFunctions.stateHeader(self,1)
                while self.currentState==self.waitState:
                    stateFunctions.coreState(self)
                    if self.fireCallback:
                        stateCallbacks.waitStateCB(self)

            
            #S2 -----> trial initiation state
            elif self.currentState==self.initiationState:
                stateFunctions.stateHeader(self,1)
                stateCallbacks.initiationStateHead(self)
                while self.currentState==self.initiationState:
                    stateFunctions.coreState(self)
                    if self.fireCallback:
                        stateCallbacks.initiationStateCB(self)
            
            #S3 -----> cue #1
            elif self.currentState==self.cue1State:
                stateFunctions.stateHeader(self,1)
                stateCallbacks.cue1StateHead(self)
                while self.currentState==self.cue1State:
                    stateFunctions.coreState(self)
                    if self.fireCallback:
                        stateCallbacks.cue1StateCB(self)

            #S4 -----> cue #2
            elif self.currentState==self.cue2State:
                stateFunctions.stateHeader(self,1)
                stateCallbacks.cue2StateHead(self)
                while self.currentState==self.cue2State:    
                    stateFunctions.coreState(self)
                    if self.fireCallback:
                        stateCallbacks.cue2StateCB(self)

            #S5 -----> stim tone #1
            elif self.currentState==self.stim1State:
                stateFunctions.stateHeader(self,1)
                while self.currentState==self.stim1State:
                    stateFunctions.coreState(self)
                    if self.fireCallback:
                        stateCallbacks.stim1StateCB(self)

            #S6 -----> stim tone #2
            elif self.currentState==self.stim2State:
                stateFunctions.stateHeader(self,1)
                while self.currentState==self.stim2State:
                    stateFunctions.coreState(self)
                    if self.fireCallback:
                        stateCallbacks.stim2StateCB(self)
            
            #S21 -----> reward state
            elif self.currentState==self.rewardState:
                stateFunctions.stateHeader(self,0)
                while self.currentState==self.rewardState:
                    stateFunctions.coreState(self)
                    if self.fireCallback:
                        stateCallbacks.rewardStateCB(self)
            #S22 -----> reward state
            elif self.currentState==self.rewardState2:
                stateFunctions.stateHeader(self,0)
                while self.currentState==self.rewardState2:
                    stateFunctions.coreState(self)
                    if self.fireCallback:
                        stateCallbacks.rewardStateCB(self)

            #S23 -----> neutral state
            elif self.currentState==self.neutralState:
                stateFunctions.stateHeader(self,0)
                while self.currentState==self.neutralState:
                    stateFunctions.coreState(self)
                    if self.fireCallback:
                        stateCallbacks.neutralStateCB(self)

            #S24 -----> punish state
            elif self.currentState==self.punishState:
                stateFunctions.stateHeader(self,0)
                while self.currentState==self.punishState:
                    stateFunctions.coreState(self)
                    if self.fireCallback:
                        stateCallbacks.punishStateCB(self)

            #S13: save state
            elif self.currentState==self.saveState:
                print('debug: made it to 13')
                enter=1
                print('debug: ran header')
                while enter==1:
                    print('debug: entered main loop')
                    self.updatePerfPlot()
                    print('debug: updated performance')
                    self.data_saveData()
                    print('debug: saved data')
                    self.trialEndTime=time.time()
                    trialTime=self.trialEndTime-self.trialStartTime
                    self.trialTimes.append(trialTime)
                    print('debug: calculated trial time')
                    print('last trial took: {} seconds'.format(trialTime))
                    # if self.pf_frame.winfo_exists():
                    self.currentTrial=self.currentTrial+1
                    self.sessionTrialCount=self.sessionTrialCount+1 # in case you run a second session
                    print('trial {} done, saved its data'.format(self.currentTrial-1))
                    aa=time.time()
                    enter=0
                    self.data_cleanContainers()


                while enter==0:
                    self.comObj.write(struct.pack('>B', 0))
                    serialFunctions.serial_readDataFlush(self)
                    if self.dataAvail==1:
                        self.currentState=int(self.sR[self.stID_state])
                        if self.currentState == 0:
                            self.data_cleanContainers()
                            enter=3

            #S25: end session state
            elif self.currentState==self.endState:
                print('About to end the session ...')
                if self.dataExists==1:
                    self.data_saveData()
                    self.data_cleanContainers()
                    self.currentTrial=self.currentTrial+1
                    self.sessionTrialCount=self.sessionTrialCount+1 # in case you run a second session
                self.shouldRun=0  # session interput

        except:
            self.exportAnimalMeta()
            self.exceptionCallback()


class pyDiscrim_mainGUI:

    def __init__(self,master):
        self.master = master
        self.frame = Frame(self.master)
        setUserVars.setSessionVars(self)
        mainWindow.mainWindowPopulate(self)
        print('curTrial={}'.format(self.currentTrial))
        print('curSession={}'.format(self.currentSession))
        setUserVars.setStateNames(self)
        setUserVars.setTaskProbs(self)
        setUserVars.setStateVars(self)
        self.data_serialInputIDs()
        self.data_makeContainers()


    def getPath(self):

        self.selectPath = filedialog.askdirectory(title = "what what?")

    def getFilePath(self):

        self.selectPath = filedialog.askopenfilename(title = "what what?",defaultextension='.csv')

    def setSessionPath(self):
        dirPathFlg=os.path.isdir(self.dirPath.get())
        if dirPathFlg==False:
            os.mkdir(self.dirPath)
        self.dirPath.set(self.dirPath)
        self.setSesPath=1 

    def mapAssign(self,l1,l2):
        for x in range(0,len(l1)):
            exec('self.{}={}'.format(l1[x],l2[x])) 

    def mapAssignStringEntries(self,l1,l2):
        for x in range(0,len(l1)):
            a=[l2[x]]
            exec('self.{}.set(a[0])'.format(l1[x]))

    def refreshVars(self,varLabels,varValues,refreshType):
        
        if refreshType==0: #reset
            self.mapAssign(varLabels,varValues)

        if refreshType==1: #refresh from entries
            for x in range(0,len(varLabels)):
                a=eval('float(self.{}_tv.get())'.format(varLabels[x]))
                eval('self.{}_tv.set("{}")'.format(varLabels[x],str(a)))
                varValues[x]=a
            self.mapAssign(varLabels,varValues)

        
        if refreshType==2: #write only
            for x in range(0,len(varLabels)):
                eval('self.{}_tv.set({})'.format(varLabels[x],varValues[x]))

    def parseMetaDataStrings(self,tmpDataFrame):
        aa=tmpDataFrame.dtypes.index
        varNames=[]
        varVals=[]
        for x in range(0,len(tmpDataFrame.columns)):
            varNames.append(aa[x])
            varVals.append(tmpDataFrame.iloc[0][x])
        self.mapAssignStringEntries(varNames,varVals)

    def blankLine(self,targ,startRow):
        self.guiBuf=Label(targ, text="")
        self.guiBuf.grid(row=startRow,column=0,sticky=W)

    def updateDispTime(self):
        self.dateStr = datetime.datetime.\
        fromtimestamp(time.time()).strftime('%H:%M (%m/%d/%Y)')
        self.timeDisp.config(text=' #{} started: '.format(self.currentSession) + self.dateStr)  

    ############################### 
    ##  Check For User Imports.  ## 
    ###############################

    def exportAnimalMeta(self):
        self.metaNames=['comPath','dirPath','animalIDStr','totalTrials','sampsToPlot',\
        'uiUpdateSamps','ux_adaptThresh','lickValuesOrDeltas','lickThresholdStrValA','lickThresholdStrValB','lickPlotMax']
        sesVarVals=[self.comPath.get(),self.dirPath.get(),self.animalIDStr.get(),\
        self.totalTrials.get(),\
        self.sampsToPlot.get(),self.uiUpdateSamps.get(),self.ux_adaptThresh.get(),\
        self.lickValuesOrDeltas.get(),\
        self.lickThresholdStrValA.get(),self.lickThresholdStrValB.get(),self.lickPlotMax.get()]
        self.animalMetaDF=pd.DataFrame([sesVarVals],columns=self.metaNames)
        self.animalMetaDF.to_csv('{}{}_animalMeta.csv'.format(self.dirPath.get() + '/',\
            self.animalIDStr.get()))
    
    def makeMetaFrame(self):
        sesVarVals=[]
        self.saveVars_session_ids=['sessionTrialCount','currentTrial','timeOutDuration']
        for x in range(0,len(self.saveVars_session_ids)):
            exec('sesVarVals.append(self.{})'.format(self.saveVars_session_ids[x]))

        self.sessionDF=pd.DataFrame([sesVarVals],columns=self.saveVars_session_ids)

    def updateMetaFrame(self):
        # updates are series
            sesVarVals=[]
            for x in range(0,len(self.saveVars_session_ids)):
                exec('sesVarVals.append(self.{})'.format(self.saveVars_session_ids[x]))
            ds=pd.Series(sesVarVals,index=self.saveVars_session_ids)
            self.sessionDF=self.sessionDF.append(ds,ignore_index=True)

    def debugWindow(self):
        dbgFrame = Toplevel()
        dbgFrame.title('Debug Toggles')
        self.dbgFrame=dbgFrame

        self.mFwdBtn=Button(master=dbgFrame,text="Move +",width=10,command=lambda:self.dbMv(100))
        self.mFwdBtn.grid(row=0, column=0)
        self.mFwdBtn.config(state=NORMAL)

        self.mBwdBtn=Button(master=dbgFrame,text="Move -",width=10,command=lambda:self.dbMv(-100))
        self.mBwdBtn.grid(row=1, column=0)
        self.mBwdBtn.config(state=NORMAL)

        self.lickABtn=Button(master=dbgFrame,text="Lick Left",width=10, command=lambda:self.dbLick(2000,0))
        self.lickABtn.grid(row=0, column=1)
        self.lickABtn.config(state=NORMAL)

        self.lickBBtn=Button(master=dbgFrame,text="Lick Right",width=10, command=lambda:self.dbLick(2000,1))
        self.lickBBtn.grid(row=1, column=1)
        self.lickBBtn.config(state=NORMAL)

    def dbMv(self,delta):
        if len(self.absolutePosition)>0:
            self.absolutePosition[-1]=self.absolutePosition[-1]+delta
            self.posDelta[-1]=delta
            self.lastPos=self.lastPos+delta
        elif len(self.absolutePosition)==0:
            self.lastPos=delta

    def dbLick(self,val,spout):
        if len(self.lickValsA)>0 and spout == 0:
            self.lickValsA[-1]=self.lickValsA[-1]+val
            analysis.lickDetectionDebug(self)

        if len(self.lickValsB)>0 and spout == 1:
            self.lickValsB[-1]=self.lickValsB[-1]+val
            analysis.lickDetectionDebug(self)


    def updatePlotCheck(self):
        # analysis.updateLickThresholds(self)
        Tk.Update()
        if plt.fignum_exists(100):
            taskFeedbackFigure.updateTaskPlot(self)
        self.cycleCount=0

    def setPlotVariables(self):

        self.plotVarIDs=['arStates','mcTrialTime','lickValsA','lickValsB']

 
  
    def performanceWindow(self):

        self.fig3 = plt.figure(103)
        self.axP1=self.fig3.add_subplot(111)
        self.lineP1,=self.axP1.plot(0,0,'ro')
        plt.draw()

    def updatePerfPlot(self):
        tRC=self.rewardContingency[-1]
        tTO=self.trialOutcome[-1]

        self.rcCol.append(tRC)
        self.toCol.append(tTO)

        
        if tRC ==10 or tRC ==21 :
            tTskType=1
        elif tRC ==11 or tRC ==20 :
            tTskType=2

        self.PooledTasks.append(tTskType)

        if plt.fignum_exists(103): #todo: make variable
            self.lineP1.set_data(self.rcCol,self.toCol)
            self.axP1.relim()
            self.axP1.autoscale_view()
        plt.draw()
        plt.pause(self.pltDelay)


    def stateToggleWindow(self):
        st_frame = Toplevel()
        st_frame.title('States in Task')
        self.st_frame=st_frame

        sCl=0
        sRw=4
        btWdth=8
        
        self.stateStartColumn=sCl
        self.stateStartRow=sRw

        # self.blankLine(self.st_frame,sRw)

        self.sBtn_save = Button(st_frame, text="Save State", \
            command=lambda: stateFunctions.switchState(self,self.saveState),width=btWdth)
        self.sBtn_save.grid(row=sRw+1, column=sCl)
        self.sBtn_save.config(state=NORMAL)

        self.sBtn_endSession = Button(st_frame, text="End Session", \
            command=lambda: stateFunctions.switchState(self,self.endState),width=btWdth)
        self.sBtn_endSession.grid(row=sRw-2, column=sCl+1)
        self.sBtn_endSession.config(state=NORMAL)

        self.sBtn_boot = Button(st_frame, text="S0: Boot", \
            command=lambda: stateFunctions.switchState(self,self.bootState),width=btWdth)
        self.sBtn_boot.grid(row=sRw-1, column=sCl)
        self.sBtn_boot.config(state=NORMAL)

        self.sBtn_wait = Button(st_frame, text="S1: Wait", \
            command=lambda: stateFunctions.switchState(self,self.waitState),width=btWdth)
        self.sBtn_wait.grid(row=sRw, column=sCl)
        self.sBtn_wait.config(state=NORMAL)

        self.sBtn_initiate = Button(st_frame, text="S2: Initiate", \
            command=lambda: stateFunctions.switchState(self,self.initiationState),width=btWdth)
        self.sBtn_initiate.grid(row=sRw, column=sCl+1)
        self.sBtn_initiate.config(state=NORMAL)

        self.sBtn_cue1 = Button(st_frame, text="S3: Cue 1", \
            command=lambda: stateFunctions.switchState(self,self.cue1State),width=btWdth)
        self.sBtn_cue1.grid(row=sRw-1, column=sCl+2)
        self.sBtn_cue1.config(state=NORMAL)

        self.sBtn_cue2 = Button(st_frame, text="S4: Cue 2", \
            command=lambda: stateFunctions.switchState(self,self.cue2State),width=btWdth)
        self.sBtn_cue2.grid(row=sRw+1, column=sCl+2)
        self.sBtn_cue2.config(state=NORMAL)

        self.sBtn_stim1 = Button(st_frame, text="SS1: Stim 1", \
            command=lambda: stateFunctions.switchState(self,self.stim1State),width=btWdth)
        self.sBtn_stim1.grid(row=sRw-2, column=sCl+3)
        self.sBtn_stim1.config(state=NORMAL)

        self.sBtn_stim2 = Button(st_frame, text="SS1: Stim 2",\
            command=lambda: stateFunctions.switchState(self,self.stim2State),width=btWdth)
        self.sBtn_stim2.grid(row=sRw+2, column=sCl+3)
        self.sBtn_stim2.config(state=NORMAL)


        self.sBtn_catch = Button(st_frame, text="SC: Catch", \
            command=lambda: stateFunctions.switchState(self,self.catchState),width=btWdth)
        self.sBtn_catch.grid(row=sRw, column=sCl+3)
        self.sBtn_catch.config(state=NORMAL)

        self.sBtn_reward = Button(st_frame, text="SR1: Reward1", \
            command=lambda: stateFunctions.switchState(self,21),width=btWdth)
        self.sBtn_reward.grid(row=sRw-1, column=sCl+4)
        self.sBtn_reward.config(state=NORMAL)

        self.sBtn_reward2 = Button(st_frame, text="SR2: Reward 2", \
            command=lambda: stateFunctions.switchState(self,22),width=btWdth)
        self.sBtn_reward2.grid(row=sRw+1, column=sCl+4)
        self.sBtn_reward2.config(state=NORMAL)

        self.sBtn_neutral = Button(st_frame, text="SN: Neutral", \
            command=lambda: stateFunctions.switchState(self,self.neutralState),width=btWdth)
        self.sBtn_neutral.grid(row=sRw, column=sCl+5)
        self.sBtn_neutral.config(state=NORMAL)

        self.sBtn_punish = Button(st_frame, text="SP: Punish", \
            command=lambda: stateFunctions.switchState(self,self.punishState),width=btWdth)
        self.sBtn_punish.grid(row=sRw+0, column=sCl+4)
        self.sBtn_punish.config(state=NORMAL)

    def stateEditWindow(self):
        se_frame = Toplevel()
        se_frame.title('Set States')
        self.se_frame=se_frame

        self.populateVarFrames(self.stateNames,self.stateIDs,0,'se_frame')
        
        self.setStatesBtn = Button(se_frame, text = 'Set State IDs', \
            width = 15, command = lambda: self.stateNumsRefreshBtnCB())
        self.setStatesBtn.grid(row=len(self.stateNames)+1, column=0)

    #########################
    ##  Task Prob Windows  ##
    #########################

    def taskProbWindow(self):
        tb_frame = Toplevel()
        tb_frame.title('Task Probs')
        self.tb_frame=tb_frame
        self.populateVarFrames(self.t1ProbLabels,self.t1ProbValues,0,'tb_frame')
        self.populateVarFrames(self.t2ProbLabels,self.t2ProbValues,2,'tb_frame')
        
        self.setTaskProbsBtn = Button(tb_frame,text='Set Probs.',width = 10,\
            command = lambda: self.taskProbRefreshBtnCB())
        self.setTaskProbsBtn.grid(row=8, column=0,sticky=E)

    def taskProbRefreshBtnCB(self):
        self.refreshVars(self.t1ProbLabels,self.t1ProbValues,1)
        self.refreshVars(self.t2ProbLabels,self.t2ProbValues,1)


    def stateVarWindow(self):
        frame_sv = Toplevel()
        frame_sv.title('Task Probs')
        self.frame_sv=frame_sv

        self.populateVarFrames(self.stateVarLabels,self.stateVarValues,0,'frame_sv')
        self.setStateVars = Button(frame_sv,text = 'Set Variables.', width = 10, \
            command = self.stateVarRefreshBtnCB)
        self.setStateVars.grid(row=8, column=0)  

    def stateVarRefreshBtnCB(self):

        self.refreshVars(self.stateVarLabels,self.stateVarValues,1)

    def stateNumsRefreshBtnCB(self):

        self.refreshVars(self.stateNames,self.stateIDs,1)

    def populateVarFrames(self,varLabels,varValues,stCol,frameName):
        for x in range(0,len(varLabels)):
            exec('self.{}_tv=StringVar(self.{})'.format(varLabels[x],frameName))
            exec('self.{}_label = Label(self.{}, text="{}")'\
                .format(varLabels[x],frameName,varLabels[x]))
            exec('self.{}_entries=Entry(self.{},width=6,textvariable=self.{}_tv)'\
                .format(varLabels[x],frameName,varLabels[x]))
            exec('self.{}_label.grid(row=x, column=stCol+1)'.format(varLabels[x]))
            exec('self.{}_entries.grid(row=x, column=stCol)'.format(varLabels[x]))
            exec('self.{}_tv.set({})'.format(varLabels[x],varValues[x]))



    def data_serialInputIDs(self):
        # we name each stream from the main 
        # teensey's serial data packet
        self.stID_header=0          
        self.stID_time=1
        self.stID_trialTime=2
        self.stID_pos=3
        self.stID_state=4
        self.stID_lickSensor_a=5
        self.stID_lickSensor_b=6




    def data_makeContainers(self):
        self.arStates=[]          
        self.mcTrialTime=[]
        self.mcStateTime=[]  
        self.absolutePosition=[]
        self.posDelta=[]        
        self.lickValsA=[]
        self.lickValsB=[]
        self.thrLicksA=[]
        self.thrLicksB=[]
        self.stateLickCount0=[]
        self.stateLickCount1=[]
        self.pyStatesRS = []
        self.pyStatesRT = []
        self.pyStatesTT = []
        self.pyStatesTS = []
        self.lastLickCountA=0
        self.lastLickCountB=0
        self.rewardContingency=[] 
        self.trialOutcome=[]
        self.PooledTasks=[]
        self.stillLatch=1
        self.stillTime=0
        self.sCues=[];
        self.sStims=[];
        self.sRewardTarget=[];
        self.sPunishTarget=[];
        self.sOutcome=[];   
        self.lastPos=0
        self.lastOrientation=0
        self.orientation=[]
         

    def data_cleanContainers(self):
        self.arStates=[]          
        self.mcTrialTime=[]
        self.mcStateTime=[]  
        self.absolutePosition=[]
        self.posDelta=[]        
        self.lickValsA=[]
        self.lickValsB=[]
        self.thrLicksA=[]
        self.thrLicksB=[]
        self.stateLickCount0=[]
        self.stateLickCount1=[]
        self.pyStatesRS = []
        self.pyStatesRT = []
        self.pyStatesTT = []
        self.pyStatesTS = []
        self.lastLickCountA=0
        self.lastLickCountB=0
        self.rewardContingency=[]
        self.trialOutcome=[] 
        self.PooledTasks=[]
        self.stillLatch=1
        self.stillTime=0 
        self.lastOrientation=0
        self.lastPos=0
        self.orientation=[]
            

    def data_parseData(self):
        self.mcTrialTime.append(float(int(self.sR[self.stID_time])/self.timeBase))
        self.mcStateTime.append(float(int(self.sR[self.stID_trialTime])/self.timeBase))

        
        cOr=int(self.sR[self.stID_pos])

        cTheta=cOr-self.lastOrientation
        
        rollCorrectTheta=cTheta
        
        if cTheta>250: # rolled from 180 to -180 (pos to neg)
            
            rollCorrectTheta=(cTheta-180)*-1
        elif cTheta<-250: # rolled -180 over to positive
            
            rollCorrectTheta=(cTheta+180)*-1
        
        self.orientation.append(cOr)
        
        self.lastOrientation=self.orientation[-1]
        
        self.posDelta.append(rollCorrectTheta)
        
        self.absolutePosition.append(self.lastPos+rollCorrectTheta)
        self.lastPos=self.absolutePosition[-1]


        self.currentState=int(self.sR[self.stID_state])
        self.arStates.append(self.currentState)
        self.lickValsA.append(int(self.sR[self.stID_lickSensor_a]))
        self.lickValsB.append(int(self.sR[self.stID_lickSensor_b]))
        analysis.lickDetection(self)
        self.dataExists=1


    def data_saveData(self):
        self.dateSvStr = datetime.datetime.fromtimestamp(time.time()).strftime('%H%M_%m%d%Y')

        saveStreams='mcTrialTime','mcStateTime','absolutePosition','posDelta','orientation','arStates',\
        'lickValsA','lickValsB','thrLicksA','thrLicksB','stateLickCount0','stateLickCount1','pyStatesRS',\
        'pyStatesRT','pyStatesTS','pyStatesTT'

        self.tCo=[]
        for x in range(0,len(saveStreams)):
            exec('self.tCo=self.{}'.format(saveStreams[x]))
            if x==0:
                self.rf=pd.DataFrame({'{}'.format(saveStreams[x]):self.tCo})
            elif x != 0:
                self.tf=pd.DataFrame({'{}'.format(saveStreams[x]):self.tCo})
                self.rf=pd.concat([self.rf,self.tf],axis=1)

        self.rf.to_csv('{}{}_trial_{}_{}_s{}.csv'.\
            format(self.dirPath.get() + '/', self.animalIDStr.get(),\
             self.currentTrial, self.dateSvStr, self.currentSession))
        self.dataExists=0

    def exceptionCallback(self):
        print('EXCEPTION thrown: I am going down')
        print('last trial = {} and the last state was {}. \
            I will try to save last trial ...'\
            .format(self.currentTrial,self.currentState))
        self.dataExists=0
        self.data_saveData()
        print('save was a success; now \
            I will close com port and quit')
        print('I will try to reset the mc state \
            before closing the port ...')
        self.comObj.close()
        #todo: add a timeout for the resync
        print('closed the com port cleanly')
        exit()


root = Tk()
app = pyDiscrim_mainGUI(root)
root.mainloop()