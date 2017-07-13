# pyDiscrim:
# A Python3 program that interacts with a microcontroller -
# to perform state-based behavioral tasks.
#
# Version 3.45 -- Default Choices and Shaping Variables All Implemented
# fixed a problematic plotting between trials issue
#
# questions? --> Chris Deister --> cdeister@brown.edu

# bugs: must keep a benign matplotlib fig (Figure 1) open. Can be minmized, but has to be open.
# bugs: have to keep task feedback opebn

# todos: make outcome plot frequency
# todos: make rewardState and do reward1State reward2State

from tkinter import *
from tkinter import filedialog
import serial
import numpy as np

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg 
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
# import matplotlib.animation as animation

import time
import datetime
import random
import math
import struct
import sys
import os
import pandas as pd


class pyDiscrim_mainGUI:

    #####################################
    ## **** Set Initial Variables **** ##
    #####################################

    def setStateNames(self):
        self.stateNames=\
        ['bootState','waitState','initiationState','cue1State','cue2State',\
        'stim1State','stim2State','catchState','saveState','rewardState',\
        'neutralState','punishState','endState','defaultState']

        self.stateIDs=\
        [0,1,2,3,4,\
        5,6,7,13,21,\
        22,23,25,29]
        
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

    ##############################
    ##  Custom State Callbacks  ##
    ##############################

    def callback_waitState(self):
        if self.arduinoTime[-1]-self.entryTime>2:  #todo: make this a variable
            self.dPos=abs(self.absolutePosition[-1]-self.absolutePosition[-2])
            
            if self.dPos>self.movThr and self.stillLatch==1:
                self.stillLatch=0

            if self.dPos<=self.movThr and self.stillLatch==0:
                self.stillTimeStart=self.arduinoTime[-1]
                self.stillLatch=1

            if self.dPos<self.movThr and self.stillLatch==1:
                self.stillTime=self.arduinoTime[-1]-self.stillTimeStart

            if self.stillLatch==1 and self.stillTime>1:
                print('Still! ==> Out of wait')
                print('### S1 --> S2')
                self.switchState(self.initiationState)

    def custHeader_initiationState(self):

        self.task_switch=random.random()

    def callback_initiationState(self):
        t1P=self.sTask1_prob
        if self.absolutePosition[-1]>self.distThr:
            if self.task_switch<=t1P:
                print('moving spout; cue stim task #1')
                self.switchState(self.cue1State)
            # if stimSwitch is more than task1's probablity then send to task #2
            elif self.task_switch>t1P:
                print('moving spout; cue stim task #2')
                self.switchState(self.cue2State)

    def custHeader_cue1State(self):

        self.outcomeSwitch=random.random()

    def custHeader_cue2State(self):
        
        self.outcomeSwitch=random.random()

    def callback_cue1State(self):
        #trP=float(self.sTask1_target_prob.get())
        if self.arduinoTime[-1]-self.entryTime>4:
            self.dPos=abs(self.absolutePosition[-1]-self.absolutePosition[-2])
            if self.dPos>self.movThr and self.stillLatch==1:
                self.stillLatch=0
            if self.dPos<=self.movThr and self.stillLatch==0:
                self.stillTimeStart=self.arduinoTime[-1]
                self.stillLatch=1
            if self.dPos<=self.movThr and self.stillLatch==1:
                self.stillTime=self.arduinoTime[-1]-self.stillTimeStart
            if self.stillLatch==1 and self.stillTime>1:
                print('Still!')
                if self.outcomeSwitch<=0.5:
                    print('stim 1 reward left')
                    self.switchState(self.stim1State)
                    self.rewardContingency.append(10)   # stim bit: correct spout bit --> 1 is stim 1 and 0 is left spout
                elif self.outcomeSwitch>0.5:
                    print('stim 2 reward right')
                    self.switchState(self.stim2State)
                    self.rewardContingency.append(21) # stim bit: correct spout bit --> 2 is stim 2 and 1 is reward right spout

    def callback_cue2State(self): 
        #trP=float(self.sTask2_target_prob.get())
        if self.arduinoTime[-1]-self.entryTime>4:
            self.dPos=abs(self.absolutePosition[-1]-self.absolutePosition[-2])
            if self.dPos>self.movThr and self.stillLatch==1:
                self.stillLatch=0
            if self.dPos<=self.movThr and self.stillLatch==0:
                self.stillTimeStart=self.arduinoTime[-1]
                self.stillLatch=1
            if self.dPos<=self.movThr and self.stillLatch==1:
                self.stillTime=self.arduinoTime[-1]-self.stillTimeStart
            if self.stillLatch==1 and self.stillTime>1:
                print('Still!')
                if self.outcomeSwitch<=0.5:
                    print('stim 1 reward right')
                    self.switchState(self.stim1State)
                    self.rewardContingency.append(11)
                elif self.outcomeSwitch>0.5:
                    print('stim 2 reward left')
                    self.switchState(self.stim2State)
                    self.rewardContingency.append(20)
    
    def callback_stim1State(self):
        
        # conditions < -- training vars
        self.minStim1Time=0.2
        self.minTarget1Licks=2
        self.maxOffTarget1Licks=1
        self.minOffTarget1Licks=1
        self.reportMax1Time=10

        if self.arduinoTime[-1]-self.entryTime>self.minStim1Time:
            if self.arduinoTime[-1]-self.entryTime<self.reportMax1Time:
                if self.rewardContingency[-1] == 10 and \
                self.stateLickCountA[-1]>=self.minTarget1Licks and \
                self.stateLickCountB[-1]<self.maxOffTarget1Licks: # target left; licked left
                    print('licked left: on target -> reward') #debug
                    self.trialOutcome.append(11) # 1 was the stim, and the outcome is rewarded: 1
                    self.switchState(self.rewardState)

                elif self.rewardContingency[-1] == 10 and \
                self.stateLickCountA[-1]<=self.minTarget1Licks and \
                self.stateLickCountB[-1]>self.minOffTarget1Licks: # target left; licked right
                    print('licked right: obvious off target -> punish')
                    self.trialOutcome.append(12)
                    self.switchState(self.punishState)

                elif self.rewardContingency[-1] == 10 and \
                self.stateLickCountA[-1]>self.minTarget1Licks and \
                self.stateLickCountB[-1]>self.minOffTarget1Licks:
                    print('licked both: ambiguous choice ... wrong -> punish')
                    self.trialOutcome.append(13)
                    self.switchState(self.punishState)

                elif self.rewardContingency[-1] == 11 and \
                self.stateLickCountB[-1]>=self.minTarget1Licks and \
                self.stateLickCountA[-1]<self.maxOffTarget1Licks: # target left; licked left
                    print('licked right: on target -> reward') #debug
                    self.trialOutcome.append(11) # 1 is rewarded
                    self.switchState(self.rewardState)

                elif self.rewardContingency[-1] == 11 and \
                self.stateLickCountA[-1]<=self.minTarget1Licks \
                and self.stateLickCountB[-1]>self.minOffTarget1Licks: # target left; licked right
                    print('licked left: off target -> punish')
                    self.trialOutcome.append(12)
                    self.switchState(self.punishState)

                elif self.rewardContingency[-1] == 11 and \
                self.stateLickCountA[-1]>self.minTarget1Licks \
                and self.stateLickCountB[-1]>self.minOffTarget1Licks:
                    print('licked both: ambiguous choice ... wrong -> punish')
                    self.trialOutcome.append(13)
                    self.switchState(self.punishState)
            
            elif self.arduinoTime[-1]-self.entryTime>=self.reportMax1Time:
                self.trialOutcome.append(10)
                print('timed out: did not report')
                self.switchState(self.neutralState)      #5

    def callback_stim2State(self):
        # conditions < -- training vars
        self.minStim2Time=0.2
        self.minTarget2Licks=2
        self.maxOffTarget2Licks=1
        self.minOffTarget2Licks=1
        self.reportMax2Time=10

        if self.arduinoTime[-1]-self.entryTime>self.minStim2Time:
            if self.arduinoTime[-1]-self.entryTime<self.reportMax2Time:
                if self.rewardContingency[-1] == 20 and \
                self.stateLickCountA[-1]>=self.minTarget2Licks and \
                self.stateLickCountB[-1]<self.maxOffTarget2Licks: # target left; licked left
                    print('20 licked left: on target -> reward') #debug
                    self.trialOutcome.append(11) # 1 was the stim, and the outcome is rewarded: 1
                    self.switchState(self.rewardState)

                elif self.rewardContingency[-1] == 20 and \
                self.stateLickCountA[-1]<=self.minTarget2Licks and \
                self.stateLickCountB[-1]>self.minOffTarget2Licks: # target left; licked right
                    print('20 licked right: obvious off target -> punish')
                    self.trialOutcome.append(12)
                    self.switchState(self.punishState)

                elif self.rewardContingency[-1] == 20 and \
                self.stateLickCountA[-1]>self.minTarget2Licks and \
                self.stateLickCountB[-1]>self.minOffTarget2Licks:
                    print('20 licked both: ambiguous choice ... wrong -> punish')
                    self.trialOutcome.append(13)
                    self.switchState(self.punishState)

                elif self.rewardContingency[-1] == 21 and \
                self.stateLickCountB[-1]>=self.minTarget2Licks and \
                self.stateLickCountA[-1]<self.maxOffTarget2Licks: # target left; licked left
                    print('21 licked right: on target -> reward') #debug
                    self.trialOutcome.append(11) # 1 is rewarded
                    self.switchState(self.rewardState)

                elif self.rewardContingency[-1] == 21 and\
                 self.stateLickCountB[-1]<=self.minTarget2Licks and \
                 self.stateLickCountA[-1]>self.minOffTarget2Licks: # target left; licked right
                    print('21 licked left: off target -> punish')
                    self.trialOutcome.append(12)
                    self.switchState(self.punishState)

                elif self.rewardContingency[-1] == 21 and \
                self.stateLickCountA[-1]>self.minTarget2Licks \
                and self.stateLickCountB[-1]>self.minOffTarget2Licks:
                    print('21 licked both: ambiguous choice ... wrong -> punish')
                    self.trialOutcome.append(13)
                    self.switchState(self.punishState)
            
            elif self.arduinoTime[-1]-self.entryTime>=self.reportMax2Time:
                self.trialOutcome.append(10)
                print('timed out: did not report')
                self.switchState(self.neutralState)   #6

    def callback_rewardState(self):
        self.rewardTime=1
        if self.arduinoTime[-1]-self.entryTime<self.rewardTime:
            print('rewarding')
            self.switchState(self.saveState)

    def callback_neutralState(self):
        self.neutralTime=1
        if self.absolutePosition[-1]>self.distThr:
            print('no reward')
            self.switchState(self.saveState)

    def callback_punishState(self):
        if self.arduinoTime[-1]-self.entryTime>=self.timeOutDuration:
            print('timeout of {} seconds is over'.format(self.timeOutDuration))
            self.switchState(self.saveState)
    
    ###########################
    ## ****  Main Task  **** ##
    ###########################

    def __init__(self,master):
        self.master = master
        self.frame = Frame(self.master)
        self.setSessionVars()
        self.mainWindowPopulate()
        print('starting. curTrial={}'.format(self.currentTrial))
        print('starting. curSession={}'.format(self.currentSession))
        self.setStateNames()
        self.setTaskProbs()
        self.setStateVars()
        self.data_serialInputIDs()
        self.data_makeContainers()

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

    def task(self):
        self.taskHeader()
        aa=time.time()
        while self.currentTrial <=int(self.totalTrials.get()) \
        and self.shouldRun==1:
            try:
                #S0 -----> hand shake (initialization state)
                if self.currentState==self.bootState:
                    self.serial_readDataFlush()
                    print('in state 0: boot state')
                    self.lastPos=0 
                    while self.currentState==self.bootState:
                        self.serial_readDataFlush()
                        if self.dataAvail==1:
                            self.data_parseData()
                            self.switchState(self.waitState)
                
                #S1 -----> trial wait state
                elif self.currentState==self.waitState:
                    self.stateHeader(1)
                    while self.currentState==self.waitState:
                        self.coreState()
                        if self.fireCallback:
                            self.callback_waitState()

                
                #S2 -----> trial initiation state
                elif self.currentState==self.initiationState:
                    self.stateHeader(1)
                    self.custHeader_initiationState()
                    while self.currentState==self.initiationState:
                        self.coreState()
                        if self.fireCallback:
                            self.callback_initiationState()
                
                #S3 -----> cue #1
                elif self.currentState==self.cue1State:
                    self.stateHeader(1)
                    self.custHeader_cue1State()
                    while self.currentState==self.cue1State:
                        self.coreState()
                        if self.fireCallback:
                            self.callback_cue1State()
                #S4 -----> cue #2
                elif self.currentState==self.cue2State:
                    self.stateHeader(1)
                    self.custHeader_cue2State()
                    while self.currentState==self.cue2State:    
                        self.coreState()
                        if self.fireCallback:
                            self.callback_cue2State()
                #S5 -----> stim tone #1
                elif self.currentState==self.stim1State:
                    self.stateHeader(1)
                    while self.currentState==self.stim1State:
                        self.coreState()
                        if self.fireCallback:
                            self.callback_stim1State()
                #S6 -----> stim tone #2
                elif self.currentState==self.stim2State:
                    self.stateHeader(1)
                    while self.currentState==self.stim2State:
                        self.coreState()
                        if self.fireCallback:
                            self.callback_stim2State()
                
                #S21 -----> reward state
                elif self.currentState==self.rewardState:
                    self.stateHeader(0)
                    while self.currentState==self.rewardState:
                        self.coreState()
                        if self.fireCallback:
                            self.callback_rewardState()
                #S22 -----> neutral state
                elif self.currentState==self.neutralState:
                    self.stateHeader(0)
                    while self.currentState==self.neutralState:
                        self.coreState()
                        if self.fireCallback:
                            self.callback_neutralState()
                #S23 -----> punish state
                elif self.currentState==self.punishState:
                    self.stateHeader(0)
                    while self.currentState==self.punishState:
                        self.coreState()
                        if self.fireCallback:
                            self.callback_punishState()

                #S13: save state
                elif self.currentState==self.saveState:
                    enter=1
                    while enter==1:
                        self.updatePerfPlot()
                        self.data_saveData()
                        bb=time.time()
                        self.trialTimes.append(bb-aa)
                        print('last trial took: {} seconds'.format(bb-aa))
                        # if self.pf_frame.winfo_exists():
                        self.currentTrial=self.currentTrial+1
                        self.sessionTrialCount=self.sessionTrialCount+1 # in case you run a second session
                        print('trial {} done, saved its data'.format(self.currentTrial-1))
                        aa=time.time()
                        enter=0
                        self.plot_cache(0)
                        self.data_cleanContainers()
                    while enter==0:
                        self.comObj.write(struct.pack('>B', 0))
                        self.serial_readDataFlush()
                        if self.dataAvail==1:
                            self.currentState=int(self.sR[self.stID_state])
                            print(self.currentState)
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
                    self.shouldRun=0

            except:
                self.exportAnimalMeta()
                self.exceptionCallback()
        self.currentSession=self.currentSession+1
        self.exportAnimalMeta()
        self.endBtn.config(state=DISABLED)
        self.startBtn.config(state=NORMAL)
        self.stateBindings.to_csv('{}{}_stateMap.csv'\
            .format(self.dirPath.get() + '/',self.animalIDStr.get()))
        print('I completed {} trials.'.format(self.currentTrial-1))
        print('!!!!!!! --> Session #:{} Finished'.format(self.ranTask))
        self.updateDispTime()
        self.syncSerial()

    ##################################
    ## ****  Utility Functions **** ##
    ##################################

    def syncSerial(self):
        ranHeader=0
        self.dataExists=0
        while ranHeader==0:
            gaveFeedback=0
            ranHeader=1
            loopCount=0
        while ranHeader==1:
            self.comObj.write(struct.pack('>B', self.bootState))
            self.serial_readDataFlush()
            if self.dataAvail==1:
                self.currentState=int(self.sR[self.stID_state])
                if self.currentState!=self.bootState:
                    if gaveFeedback==0:
                        print('mc state is not right, thinks it is #: {}'\
                            .format(self.currentState))
                        print('will force boot state, might take a second or so ...')
                        print('!!!! ~~> UI may become unresponsive \
                            for 1-30 seconds or so, but I havent crashed ...')
                        gaveFeedback=1
                    loopCount=loopCount+1
                    if loopCount % 5000 ==0:
                        print('still syncing: state #: {}; loop #: {}'\
                            .format(self.currentState,loopCount))

                elif self.currentState==self.bootState:
                    print('ready: mc is in state #: {}'.format(self.currentState))
                    return

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
        'uiUpdateSamps','ux_adaptThresh','lickValuesOrDeltas','lickThresholdStrValA','lickPlotMax']
        sesVarVals=[self.comPath.get(),self.dirPath.get(),self.animalIDStr.get(),\
        self.totalTrials.get(),\
        self.sampsToPlot.get(),self.uiUpdateSamps.get(),self.ux_adaptThresh.get(),\
        self.lickValuesOrDeltas.get(),\
        self.lickThresholdStrValA.get(),self.lickPlotMax.get()]
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
            print(self.sessionDF)

    ###############################
    ##  State Related Functions  ##
    ###############################
    
    def switchState(self,targetState):
        self.targetState=targetState
        if self.dataExists==1:
            self.pyStatesRS.append(self.targetState)
            self.pyStatesRT.append(self.arduinoTime[-1])
        print('pushing: s{} -> s{}'.format(self.currentState,targetState))
        self.comObj.write(struct.pack('>B', targetState))
        self.exitState(self.currentState)

    def exitState(self,cState): 
        self.cState=cState
        while self.currentState==self.cState:      
            self.serial_readDataFlush()
            if self.dataAvail==1:
                self.data_parseData()
                self.currentState=int(self.sR[self.stID_state])
        self.pyStatesTS.append(self.currentState)
        self.pyStatesTT.append(self.arduinoTime[-1])

    def stateHeader(self,upSt):
        self.upSt=upSt
        self.tp_frame.title('Task Feedback: S={}'.format(self.currentState))
        ranHeader=0 # set the latch, the header runs once per entry.
        while ranHeader==0:
            self.cycleCount=1
            self.lastPos=0 # reset where we think the animal is
            self.lastLickCountA=0
            self.lastLickCountB=0
            self.entryTime=self.arduinoTime[-1] # log state entry time
            print('in state # {}'.format(self.currentState))
            ranHeader=1 # fire the latch
        
    def coreState(self):
        uiUp=int(self.uiUpdateSamps.get())
        self.fireCallback=0
        self.serial_readDataFlush()
        if self.dataAvail==1:
            self.data_parseData()
            if self.cycleCount % uiUp == 0:
                self.updatePlotCheck()
            self.fireCallback=1
            self.cycleCount=self.cycleCount+1;

    ####################
    ##  Window: Main  ##
    ####################

    def addMainBlock(self,startRow):
        self.startRow = startRow
        self.blankLine(self.master,startRow)

        self.mainCntrlLabel = Label(self.master, text="Main Controls:")\
        .grid(row=startRow,column=0,sticky=W)

        self.quitBtn = Button(self.master,text="Exit Program",command=self.mwQuitBtn, width=self.col2BW)
        self.quitBtn.grid(row=startRow+1, column=2)

        self.startBtn = Button(self.master, text="Start Task",\
            width=10, command=self.task,state=DISABLED)
        self.startBtn.grid(row=startRow+1, column=0,sticky=W,padx=10)

        self.endBtn = Button(self.master, text="End Task",width=self.col2BW, \
            command=lambda: self.switchState(self.endState),state=DISABLED)
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
        self.baudSelected.set(9600)
        self.baudPick = OptionMenu(self.master,self.baudSelected,9600,19200)
        self.baudPick.grid(row=startRow+2, column=0,sticky=E)
        self.baudPick.config(width=14)

        self.createCom_button = Button(self.master,text="Start Serial",width=self.col2BW, \
            command=self.serial_initComObj)
        self.createCom_button.grid(row=startRow+0, column=2)
        self.createCom_button.config(state=NORMAL)

        self.syncComObj_button = Button(self.master,text="Sync Serial",width=self.col2BW, \
            command=self.syncSerial)
        self.syncComObj_button.grid(row=startRow+1, column=2)
        self.syncComObj_button.config(state=DISABLED)  

        self.closeComObj_button = Button(self.master,text="Close Serial",width=self.col2BW, \
            command=self.serial_closeComObj)
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

        self.setPath_button = Button(self.master,text="<- Set Path",command=self.mwPathBtn,width=self.col2BW)
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
        self.curSession_entry=Entry(self.master,textvariable=self.totalTrials)
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
            width = self.col2BW, command = self.mwLoadMetaBtn)
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
            command=self.taskPlotWindow)
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


        self.lickMinMax=[-5,10]
        self.initPltRng=2.5
        self.pltDelay=0.0000001 
        self.segPlot=10000
        self.lastPos=0

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
        self.bThrEntry=Entry(self.master,width=6,textvariable=self.lickThresholdStrValA)
        self.bThrEntry.grid(row=startRow+3, column=0,sticky=E,padx=5)
        
        self.lickThresholdStrValA.set(12)
        self.lickThresholdStrValB.set(12)

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

        self.addSerialBlock(serStart)
        self.addSessionBlock(sesStart)
        self.addPlotBlock(plotStart)
        self.addLickDetectionBlock(lickStart)
        self.addMainBlock(mainStart)

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
                self.syncSerial()
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
        print(tempStates)
        
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

    #######################
    ###  Window: Debug  ###
    #######################

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
            self.lastPos=self.lastPos+delta
        elif len(self.absolutePosition)==0:
            self.lastPos=delta

    def dbLick(self,val,spout):
        if len(self.lickValsA)>0 and spout == 0:
            self.lickValsA[-1]=self.lickValsA[-1]+val
            self.analysisDebugLickDetection()

        if len(self.lickValsB)>0 and spout == 1:
            self.lickValsB[-1]=self.lickValsB[-1]+val
            self.analysisDebugLickDetection()

    #####################################
    ###  Window: Basic Task Feedback  ###
    #####################################
  
    def taskPlotWindow(self):
        tp_frame = Toplevel()
        tp_frame.title('Task Feedback: S={}'.format(self.currentState))
        self.tp_frame=tp_frame

        self.fig2 = Figure()
        splt=int(self.sampsToPlot.get())
        sbIDs=[221,222,223,224]
        
        for x in range(0,4):
            exec('self.initX{}=np.arange(0,{},1)'.format(x,splt))
            exec('self.initY{}=np.zeros({})'.format(x,splt))
            exec('self.ax{}=self.fig2.add_subplot({})'.format(x,sbIDs[x]))
            exec('self.line{},=self.ax{}.plot(self.initX{},self.initY{})'.format(x,x,x,x))

        self.canvas = FigureCanvasTkAgg(self.fig2, master=tp_frame)
        self.canvas.get_tk_widget().grid(row=0,column=0)

        self.figButton=Button(master=tp_frame,text="Stuff",width=10, command=self.updatePlot)
        self.figButton.grid(row=1, column=0)
        self.figButton.config(state=NORMAL)
    
    def updatePlot(self):
        splt=int(self.sampsToPlot.get())
        if len(self.arduinoTrialTime)<(splt+1) and self.currentTrial>1:
            x0=self.cache_arduinoTrialTime[-splt:-1]
            y0=self.cache_arStates[-splt:-1]
            y1=self.cache_absolutePosition[-splt:-1]
            y2=self.cache_lickValsA[-splt:-1]
            y3=self.cache_lickValsB[-splt:-1]
            y4=self.cache_thrLicksA[-splt:-1]
            y5=self.cache_thrLicksB[-splt:-1]
            for x in range(0,4):
                exec('self.line{}.set_data(x0,y{})'.format(x,x,x))
                exec('self.ax{}.relim()'.format(x))
                exec('self.ax{}.autoscale_view()'.format(x))
            self.plot_cache(1)

        elif len(self.arduinoTrialTime)>(splt+10):
            x0=self.arduinoTrialTime[-splt:-1]
            y0=self.arStates[-splt:-1]
            y1=self.absolutePosition[-splt:-1]
            y2=self.lickValsA[-splt:-1]
            y3=self.lickValsB[-splt:-1]
            y4=self.thrLicksA[-splt:-1]
            y5=self.thrLicksB[-splt:-1]
            for x in range(0,4):
                exec('self.line{}.set_data(x0,y{})'.format(x,x,x))
                exec('self.ax{}.relim()'.format(x))
                exec('self.ax{}.autoscale_view()'.format(x))

        self.canvas.draw()

    def updatePlotCheck(self):
        self.analysis_updateLickThresholds()
        self.updatePosPlot()
        if self.tp_frame.winfo_exists():
            self.updatePlot()
            self.tp_frame
        self.cycleCount=0

    def updatePosPlot(self):
        plt.subplot(2,2,1)
        self.lA=plt.plot([],[],'k-')

        plt.pause(self.pltDelay)
        self.lA.pop(0).remove()

    def setPlotVariables(self):

        self.plotVarIDs=['arStates','arduinoTime','lickValsA','lickValsB']

    #####################################
    ###  Window: Basic Task Feedback  ###
    #####################################
  
    def performanceWindow(self):
        pf_frame = Toplevel()
        pf_frame.title('Last Trial# {}'.format(self.currentTrial-1))
        self.pf_frame=pf_frame

        self.fig3 = Figure()
        self.axP1=self.fig3.add_subplot(111)
        self.lineP1,=self.axP1.plot(0,0,'ro')

        self.canvas2 = FigureCanvasTkAgg(self.fig3, master=pf_frame)
        self.canvas2.get_tk_widget().grid(row=0,column=0)

        self.figButton1=Button(master=pf_frame,text="Stuff",width=10, \
        command=self.updatePerfPlot) #ver notes added perf
        self.figButton1.grid(row=1, column=0) #todo: clean up this hacky var crap
        self.figButton1.config(state=NORMAL)

    def updatePerfPlot(self):
        print('yup')
        self.rcCol.append(self.rewardContingency[-1])
        print(self.rcCol)
        print(type(self.rcCol))
        self.toCol.append(self.trialOutcome[-1])
        print(self.toCol)
        print(type(self.rcCol))
        self.lineP1.set_data(self.rcCol,self.toCol)
        self.axP1.relim()
        self.axP1.autoscale_view()
        self.canvas2.draw()

    #############################
    ##  Window: State Toggles  ##
    #############################

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
            command=lambda: self.switchState(self.saveState),width=btWdth)
        self.sBtn_save.grid(row=sRw+1, column=sCl)
        self.sBtn_save.config(state=NORMAL)

        self.sBtn_endSession = Button(st_frame, text="End Session", \
            command=lambda: self.switchState(self.endState),width=btWdth)
        self.sBtn_endSession.grid(row=sRw-2, column=sCl+1)
        self.sBtn_endSession.config(state=NORMAL)

        self.sBtn_boot = Button(st_frame, text="S0: Boot", \
            command=lambda: self.switchState(self.bootState),width=btWdth)
        self.sBtn_boot.grid(row=sRw-1, column=sCl)
        self.sBtn_boot.config(state=NORMAL)

        self.sBtn_wait = Button(st_frame, text="S1: Wait", \
            command=lambda: self.switchState(self.waitState),width=btWdth)
        self.sBtn_wait.grid(row=sRw, column=sCl)
        self.sBtn_wait.config(state=NORMAL)

        self.sBtn_initiate = Button(st_frame, text="S2: Initiate", \
            command=lambda: self.switchState(self.initiationState),width=btWdth)
        self.sBtn_initiate.grid(row=sRw, column=sCl+1)
        self.sBtn_initiate.config(state=NORMAL)

        self.sBtn_cue1 = Button(st_frame, text="S3: Cue 1", \
            command=lambda: self.switchState(self.cue1State),width=btWdth)
        self.sBtn_cue1.grid(row=sRw-1, column=sCl+2)
        self.sBtn_cue1.config(state=NORMAL)

        self.sBtn_cue2 = Button(st_frame, text="S4: Cue 2", \
            command=lambda: self.switchState(self.cue2State),width=btWdth)
        self.sBtn_cue2.grid(row=sRw+1, column=sCl+2)
        self.sBtn_cue2.config(state=NORMAL)

        self.sBtn_stim1 = Button(st_frame, text="SS1: Stim 1", \
            command=lambda: self.switchState(self.stim1State),width=btWdth)
        self.sBtn_stim1.grid(row=sRw-2, column=sCl+3)
        self.sBtn_stim1.config(state=NORMAL)

        self.sBtn_stim2 = Button(st_frame, text="SS1: Stim 2",\
            command=lambda: self.switchState(self.stim2State),width=btWdth)
        self.sBtn_stim2.grid(row=sRw+2, column=sCl+3)
        self.sBtn_stim2.config(state=NORMAL)


        self.sBtn_catch = Button(st_frame, text="SC: Catch", \
            command=lambda: self.switchState(self.catchState),width=btWdth)
        self.sBtn_catch.grid(row=sRw, column=sCl+3)
        self.sBtn_catch.config(state=NORMAL)

        self.sBtn_reward = Button(st_frame, text="SR: Reward", \
            command=lambda: self.switchState(self.rewardState),width=btWdth)
        self.sBtn_reward.grid(row=sRw-1, column=sCl+4)
        self.sBtn_reward.config(state=NORMAL)

        self.sBtn_neutral = Button(st_frame, text="SN: Neutral", \
            command=lambda: self.switchState(self.neutralState),width=btWdth)
        self.sBtn_neutral.grid(row=sRw, column=sCl+4)
        self.sBtn_neutral.config(state=NORMAL)

        self.sBtn_punish = Button(st_frame, text="SP: Punish", \
            command=lambda: self.switchState(self.punishState),width=btWdth)
        self.sBtn_punish.grid(row=sRw+1, column=sCl+4)
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

    #######################
    ##  State Variables  ##
    #######################

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

    ################################
    ##  Serial Related Functions  ##
    ################################

    def serial_initComObj(self):
        if self.comObjectExists==0:
            print('Opening serial port: {}'.format(self.comPath.get()))
            self.comObj = serial.Serial(self.comPath.get(),self.baudSelected.get()) 
            self.syncSerial()
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
            self.syncSerial()
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
        self.serial_readData()

    def serial_readData(self):
        # position is 8-bit, hence the 256
        self.sR=self.comObj.readline().strip().decode()
        self.sR=self.sR.split(',')
        if len(self.sR)==7 and \
        self.sR[self.stID_header]=='data' and \
        str.isnumeric(self.sR[1])==1 and \
        str.isnumeric(self.sR[2])==1 and \
        str.isnumeric(self.sR[self.stID_pos])==1 and \
        int(self.sR[self.stID_pos]) < 256 and \
        str.isnumeric(self.sR[4])==1 and \
        str.isnumeric(self.sR[5])==1 and \
        str.isnumeric(self.sR[6])==1 :
            self.dataAvail=1

        elif len(self.sR)!=7 or \
        self.sR[self.stID_header] != 'data' or \
        str.isnumeric(self.sR[1])!=1 or \
        str.isnumeric(self.sR[2])!=1 or \
        str.isnumeric(self.sR[self.stID_pos])!=1 or \
        int(self.sR[self.stID_pos]) >= 256 or \
        str.isnumeric(self.sR[4])!=1 or \
        str.isnumeric(self.sR[5])!=1 or \
        str.isnumeric(self.sR[6])!=1 :
            self.dataAvail=0


    ###############################
    ##  Data Handling Functions  ##
    ###############################

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
        self.arduinoTime=[]
        self.arduinoTrialTime=[]  
        self.absolutePosition=[]
        self.posDelta=[]        
        self.lickValsA=[]
        self.lickValsB=[]
        self.thrLicksA=[]
        self.thrLicksB=[]
        self.stateLickCountA=[]
        self.stateLickCountB=[]
        self.pyStatesRS = []
        self.pyStatesRT = []
        self.pyStatesTT = []
        self.pyStatesTS = []
        self.lastLickCountA=0
        self.lastLickCountB=0
        self.rewardContingency=[] 
        self.trialOutcome=[]   

    def data_cleanContainers(self):
        self.arStates=[]          
        self.arduinoTime=[]
        self.arduinoTrialTime=[]  
        self.absolutePosition=[]
        self.posDelta=[]        
        self.lickValsA=[]
        self.lickValsB=[]
        self.thrLicksA=[]
        self.thrLicksB=[]
        self.stateLickCountA=[]
        self.stateLickCountB=[]
        self.pyStatesRS = []
        self.pyStatesRT = []
        self.pyStatesTT = []
        self.pyStatesTS = []
        self.lastLickCountA=0
        self.lastLickCountB=0
        self.rewardContingency=[]
        self.trialOutcome=[]    

    def plot_cache(self,newOrUpdate):
        splt=int(self.sampsToPlot.get())
        if newOrUpdate==0:
            self.cache_arStates=self.arStates[-splt:-1]         
            self.cache_arduinoTime=self.arduinoTime[-splt:-1]
            self.cache_arduinoTrialTime=self.arduinoTrialTime[-splt:-1]  
            self.cache_absolutePosition=self.absolutePosition[-splt:-1]
            self.cache_posDelta=self.posDelta[-splt:-1]       
            self.cache_lickValsA=self.lickValsA[-splt:-1]
            self.cache_lickValsB=self.lickValsB[-splt:-1]
            self.cache_thrLicksA=self.thrLicksA[-splt:-1]
            self.cache_thrLicksB=self.thrLicksB[-splt:-1]
            self.cache_stateLickCountA=self.stateLickCountA[-splt:-1]
            self.cache_stateLickCountB=self.stateLickCountB[-splt:-1]
        elif newOrUpdate==1 and len(self.arduinoTime)>=1:
            self.cache_arStates.append(self.arStates[-1])         
            self.cache_arduinoTime.append(self.arduinoTime[-1])
            self.cache_arduinoTrialTime.append(self.arduinoTrialTime[-1])  
            self.cache_absolutePosition.append(self.absolutePosition[-1])
            self.cache_posDelta.append(self.posDelta[-1])     
            self.cache_lickValsA.append(self.lickValsA[-1])
            self.cache_lickValsB.append(self.lickValsB[-1])
            self.cache_thrLicksA.append(self.thrLicksA[-1])
            self.cache_thrLicksB.append(self.thrLicksB[-1])
            self.cache_stateLickCountA.append(self.stateLickCountA[-1])
            self.cache_stateLickCountB.append(self.stateLickCountB[-1])


        splt=int(self.sampsToPlot.get())
        if len(self.arduinoTrialTime)>(splt+10):
            x0=self.arduinoTrialTime[-splt:-1]   

    def data_parseData(self):
        self.arduinoTime.append(float(int(self.sR[self.stID_time])/self.timeBase))
        self.arduinoTrialTime.append(float(int(self.sR[self.stID_trialTime])/\
            self.timeBase))
        self.posDelta.append(int(self.sR[self.stID_pos])-128)
        self.absolutePosition.append(int(self.lastPos+self.posDelta[-1]))
        self.lastPos=int(self.absolutePosition[-1])
        self.currentState=int(self.sR[self.stID_state])
        self.arStates.append(self.currentState)
        self.lickValsA.append(int(self.sR[self.stID_lickSensor_a]))
        self.lickValsB.append(int(self.sR[self.stID_lickSensor_b]))
        self.analysisLickDetection()
        self.dataExists=1

    def data_saveData(self):
        self.dateSvStr = datetime.datetime.fromtimestamp(time.time()).strftime('%H%M_%m%d%Y')

        saveStreams='arduinoTime','arduinoTrialTime','absolutePosition','arStates',\
        'lickValsA','lickValsB','thrLicksA','thrLicksB','stateLickCountA','stateLickCountB','pyStatesRS',\
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
            format(self.dirPath.get() + '/', self.animalIDStr.get(), self.currentSession, self.dateSvStr, self.currentTrial))
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

    #########################
    ##  Analysis Function  ##
    #########################

    def analysis_updateLickThresholds(self):
        if self.ux_adaptThresh.get()==1:
            print(int(self.lickThresholdStrValA))
            tA=np.abs(np.array(self.lickValsA))
            print(int(np.percentile\
                (aaa[np.where(aaa != 0)[0]],75)))
            self.lickThresholdStrValA.set(\
                str(np.percentile(tA[np.where(tA != 0)[0]],75)))
            self.lickMinMax=[min(self.lickValsA),\
            max(self.lickValsA)]

    def analysisDebugLickDetection(self):
        if self.lickValsA[-1]>int(self.lickThresholdStrValA.get()):
            self.thrLicksA[-1]=1
            
            self.lastLickCountA=self.lastLickCountA+1
            self.stateLickCountA[-1]=self.lastLickCountA+1


        if self.lickValsB[-1]>int(self.lickThresholdStrValB.get()):
            self.thrLicksB[-1]=1
            
            self.lastLickCountB=self.lastLickCountB+1
            self.stateLickCountB[-1]=self.lastLickCountB+1

    def analysisLickDetection(self):
        if self.lickValsA[-1]>int(self.lickThresholdStrValA.get()):
            self.thrLicksA.append(1)
            
            self.lastLickCountA+1
            self.stateLickCountA.append(self.lastLickCountA)

        elif self.lickValsA[-1]<=int(self.lickThresholdStrValA.get()):
            self.thrLicksA.append(0)
            self.stateLickCountA.append(self.lastLickCountA)

        if self.lickValsB[-1]>int(self.lickThresholdStrValB.get()):
            self.thrLicksB.append(1)
            self.lastLickCountB+1
            self.stateLickCountB.append(self.lastLickCountB)
        elif self.lickValsB[-1]<=int(self.lickThresholdStrValB.get()):
            self.thrLicksB.append(0)
            self.stateLickCountB.append(self.lastLickCountB)

root = Tk()
app = pyDiscrim_mainGUI(root)
root.mainloop()