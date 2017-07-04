# pyDiscrim:
# A Python3 program that interacts with a microcontroller -
# to perform state-based behavioral tasks.
#
# Version 2.99
# Changes: logs and loads metadata, can specify a path will load some info
# Laying the groundwork for the concept of 
# a per animal profile that lives with that animal.
# questions? --> Chris Deister --> cdeister@brown.edu


from tkinter import *
from tkinter import filedialog
import serial
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt
import time
import datetime
import random
import math
import struct
import sys
import os
# check out pathlib as pythonic? os replacement
import pandas as pd

class pyDiscrim_mainGUI:

    def __init__(self,master):
        
        # Make the main GUI window
        # Tkinter requires a parent named master.
        self.master = master
        self.frame = Frame(self.master)
        self.populate_MainWindow_Primary()
        self.sessionVars_init()
        self.stateNames_init()
        self.populate_MainWindow_SerialBits()
        self.metadata_sessionFlow()
        self.metadata_lickDetection()
        self.metadata_plotting()
        self.initialize_TaskProbs()
        self.initialize_StateVars()
        self.stateVars_init()
        self.data_serialInputIDs()

    def runTask(self):
        self.exportAnimalMeta()
        self.shouldRun=1
        initTrials=self.sessionTrialCount 
        # baseline requested trials, by what's been done before.
        self.runTask_header()
        while self.currentTrial-initTrials <=int(self.totalTrials.get()) \
        and self.shouldRun==1:
            self.initTime=0
            try:
                #S0 -----> hand shake (initialization state)
                if self.currentState==self.bootState:
                    self.updateStateMap=1
                    print('in state 0: boot state')
                    self.lastPos=0 
                    while self.currentState==self.bootState:
                        self.serial_readDataFlush()
                        if self.dataAvail==1:
                            self.data_parseData()
                            self.state_util_switchToNewState(self.initiationState)

                #S1 -----> trial wait state
                elif self.currentState==self.waitState:
                    self.state_flow_stateHeader(1)
                    while self.currentState==self.waitState:
                        self.state_flow_coreState()
                        if self.fireCallback:
                            self.callback_waitState()

                #S2 -----> trial initiation state
                elif self.currentState==self.initiationState:
                    self.task_switch=random.random()
                    self.state_flow_stateHeader(1)
                    while self.currentState==self.initiationState:
                        self.state_flow_coreState()
                        if self.fireCallback:
                            self.callback_initiationState()

                #S3 -----> cue #1
                elif self.currentState==self.cue1State:
                    self.state_flow_stateHeader(1)
                    self.outcomeSwitch=random.random()
                    while self.currentState==self.cue1State:
                        self.state_flow_coreState()
                        if self.fireCallback:
                            self.callback_cue1State()

                #S4 -----> cue #2
                elif self.currentState==self.cue2State:
                    self.state_flow_stateHeader(1)
                    self.outcomeSwitch=random.random() # debug
                    while self.currentState==self.cue2State:    
                        self.state_flow_coreState()
                        if self.fireCallback:
                            self.callback_cue2State()

                #S5 -----> stim tone #1
                elif self.currentState==self.stim1State:
                    self.state_flow_stateHeader(1)
                    while self.currentState==self.stim1State:
                        self.state_flow_coreState()
                        if self.fireCallback:
                            self.callback_stim1State()

                #S6 -----> stim tone #2
                elif self.currentState==self.stim2State:
                    self.state_flow_stateHeader(1)
                    while self.currentState==self.stim2State:
                        self.state_flow_coreState()
                        if self.fireCallback:
                            self.callback_stim2State()

                #S21 -----> reward state
                elif self.currentState==self.rewardState:
                    self.state_flow_stateHeader(0)
                    while self.currentState==self.rewardState:
                        self.state_flow_coreState()
                        if self.fireCallback:
                            self.callback_rewardState()

                #S23 -----> punish state
                elif self.currentState==self.punishState:
                    self.state_flow_stateHeader(0)
                    while self.currentState==self.punishState:
                        self.state_flow_coreState()
                        if self.fireCallback:
                            self.callback_punishState()

                #S13: save state
                elif self.currentState==self.saveState:
                    self.data_saveData()
                    self.data_cleanContainers()
                    self.currentTrial=self.currentTrial+1
                    self.sessionTrialCount=self.sessionTrialCount+1 # in case you run a second session
                    print('trial {} done, saved its data'.format(self.currentTrial-1))
                    self.comObj.write(struct.pack('>B', self.waitState))
                    self.state_flow_exitCurState(self.saveState)
                
                #S25: end session state
                elif self.currentState==self.endState:
                    print('About to end the session ...')
                    if self.dataExists==1:
                        self.data_saveData()
                        print('saved data')
                    self.shouldRun=0

            except:
                self.exceptionCallback()

        self.mw_button_endSession.config(state=DISABLED)
        self.mw_button_startSession.config(state=NORMAL)
        print('I completed {} trials.'.format(self.currentTrial-1))
        print('!!!!!!! --> Session #:{} Finished'.format(self.ranTask))
        self.utilState_syncSerial()

    def runTask_header(self):
        self.mw_button_endSession.config(state=NORMAL)
        self.mw_button_startSession.config(state=DISABLED)
        print('started at state #: {}'.format(self.currentState))
        self.data_makeContainers()
        self.uiUpdateDelta=300
        self.ranTask=self.ranTask+1

    #########################################################
    ## **** These Functions Set All Initial Variables **** ##
    ######################################################### 

    # these do not need editing
    def sessionVars_init(self):
        
        self.ranTask=0  # This increments every time you run a task        
        self.dataExists=0 
        self.comObjectExists=0
        self.taskProbsRefreshed=0
        self.stateVarsRefreshed=0 

        self.currentTrial=0
        self.currentState=0
        self.currentSession=0
        self.sessionTrialCount=0

    def exportAnimalMeta(self):
        self.fixPath()
        self.metaNames=['comPath','dirPath']
        sesVarVals=[self.comPath.get(),self.dirPath]
        self.animalMetaDF=pd.DataFrame([sesVarVals],columns=self.metaNames)
        self.animalMetaDF.to_csv('{}{}_animalMeta.csv'.\
            format(self.sdir,self.animalIDStr.get()))

    def stateNames_init(self):
        # All state have a name (string) and a numerical ID (int).
        # The stateName is up to you. T
        # The stateIDs should line up with your microcontroller however. 
        self.stateNames=['bootState','waitState','initiationState',\
        'cue1State','cue2State','stim1State','stim2State','catchState',\
        'saveState','rewardState','neutralState','punishState',\
        'endState','defaultState']

        self.stateIDs=[0,1,2,3,4,5,6,7,13,21,22,23,25,29]
        self.stateBindings=pd.Series(self.stateIDs,index=self.stateNames)
        # This links the names and IDs together.
        for x in range(0,len(self.stateIDs)):
            exec('self.{}={}'.format(self.stateNames[x],self.stateIDs[x]))
        print(self.stateBindings)

    def stateVars_init(self):
        self.dPos=float(0)
        self.movThr=40       
        self.movTimeThr=2    
        self.stillTime=float(0)
        self.stillLatch=0
        self.stillTimeStart=float(0)
        self.distThr=1000  
        self.timeOutDuration=2;

    ####
    # Check For User Imports
    ####

    def makeMetaFrame(self):
        sesVarVals=[]
        self.saveVars_session_ids=['sessionTrialCount','currentTrial','timeOutDuration']
        for x in range(0,len(self.saveVars_session_ids)):
            exec('sesVarVals.append(self.{})'.format(self.saveVars_session_ids[x]))

        self.sessionDF=pd.DataFrame([sesVarVals],columns=self.saveVars_session_ids)
        # print(self.sessionDF)

    def updateMetaFrame(self):
        # updates are series
            sesVarVals=[]
            for x in range(0,len(self.saveVars_session_ids)):
                exec('sesVarVals.append(self.{})'.format(self.saveVars_session_ids[x]))
            ds=pd.Series(sesVarVals,index=self.saveVars_session_ids)
            self.sessionDF=self.sessionDF.append(ds,ignore_index=True)
            print(self.sessionDF)


    #########################################
    ## ****  Utility Functions **** ##
    ########################################

    def utilState_syncSerial(self):
        ranHeader=0
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

    def getFilePath(self):
        self.dirPath =  filedialog.askdirectory(title = "what what?")
        print (self.dirPath)


    #########################################
    ## **** State Switching Functions **** ##
    ######################################### 
    
    def state_util_switchToNewState(self,targetState):
        self.targetState=targetState
        if self.dataExists==1:
            self.pyStatesRS.append(self.targetState)
            self.pyStatesRT.append(self.arduinoTime[-1])
        print('pushing: s{} -> s{}'.format(self.currentState,targetState))
        self.comObj.write(struct.pack('>B', targetState))
        self.state_flow_exitCurState(self.currentState)

    def state_flow_exitCurState(self,cState): 
        self.cState=cState
        while self.currentState==self.cState:      
            self.serial_readDataFlush()
            if self.dataAvail==1:
                self.data_parseData()
                self.currentState=int(self.sR[self.stID_state])
        self.pyStatesTS.append(self.currentState)
        self.pyStatesTT.append(self.arduinoTime[-1])

    def state_flow_stateHeader(self,upSt):
        self.upSt=upSt
        ranHeader=0 # set the latch, the header runs once per entry.
        self.updateStateMap=upSt
        while ranHeader==0:
            self.cycleCount=1
            self.lastPos=0 # reset where we think the animal is
            self.entryTime=self.arduinoTime[-1] # log state entry time
            print('in state # {}'.format(self.currentState))
            ranHeader=1 # fire the latch
        
    def state_flow_coreState(self):
        self.fireCallback=0
        self.serial_readDataFlush()
        if self.dataAvail==1:
            self.data_parseData()
            if int(self.cycleCount) % int(self.uiUpdateDelta)==0:
                self.updatePlotCheck()
            self.fireCallback=1
            self.cycleCount=self.cycleCount+1;

    ################################
    ## **** main window etc. **** ##
    ################################     
    
    def populate_MainWindow_Primary(self):
        self.master.title("pyDiscrim")  

        comStrt=0
        self.comPathLabel = Label(self.master, text="COM Port Location:")
        self.comPathLabel.grid(row=comStrt, column=0,sticky=W,padx=7)

        self.comPath=StringVar(self.master)
        self.comPathEntry=Entry(self.master,\
            textvariable=self.comPath)
        self.comPathEntry.grid(row=1, column=0)
        if sys.platform == 'darwin':
            self.comPath.set('/dev/cu.usbmodem2762721')
        elif sys.platform == 'win':
            self.comPath.set('COM11')
        self.comPathEntry.config(width=20)

        pthStrt=12
        self.pathLabel = Label(self.master, text="data path:").grid(row=pthStrt,column=0,sticky=W)
        self.sesPath=StringVar(self.master)
        self.sesPathEntry=Entry(self.master,textvariable=self.sesPath)
        self.sesPathEntry.grid(row=pthStrt+1,column=0,sticky=W)
        self.sesPathEntry.config(width=20)
        # guess that the right path is current directory
        self.sesPath.set(os.getcwd())

        self.setPath_button = Button(self.master, text="<- Set Path", \
            command=self.btnCB_setPath, width=10)
        self.setPath_button.grid(row=pthStrt+1,column=2,stick=E)

        quitStrt=14
        self.quitBtn = Button(self.master, text="Exit", command=self.quitBtnCB, width=10)
        self.quitBtn.grid(row=14, column=2)

    def populate_MainWindow_SerialBits(self):
        # Entries and Selections Left
        fRow=0
        fCol=0
        txtPad=7


        self.baudEntry_label = Label(self.master,text="BAUD Rate:")
        self.baudEntry_label.grid(row=fRow+2, column=fCol,sticky=W,padx=txtPad)

        self.baudSelected=IntVar(self.master)
        self.baudSelected.set(9600)
        self.baudPick = OptionMenu(self.master,self.baudSelected,9600,19200)
        self.baudPick.grid(row=fRow+3, column=fCol)
        self.baudPick.config(width=20)

        # Buttons Right
        fRow=1
        self.createCom_button = Button(self.master, text="Start Serial",\
         width = 10, command=self.serial_initComObj)
        self.createCom_button.grid(row=fRow, column=2)
        self.createCom_button.config(state=NORMAL) 
        
        self.syncComObj_button = Button(self.master, text="Sync Serial",\
            width = 10, command=self.utilState_syncSerial)
        self.syncComObj_button.grid(row=fRow+1, column=2)
        self.syncComObj_button.config(state=DISABLED)  

        self.closeComObj_button = Button(self.master, text="Close Serial",\
            width = 10, command=self.serial_closeComObj)
        self.closeComObj_button.grid(row=fRow+2, column=2)
        self.closeComObj_button.config(state=DISABLED) 
    
    def metadata_sessionFlow(self):
        self.guiPad = Label(self.master, text="")
        self.guiPad.grid(row=6, column=0)

        self.sessionStuffLabel = Label(self.master, text="Session Stuff:")
        self.sessionStuffLabel.grid(row=7, column=0,sticky=W,padx=5)

        self.animalIDStr_label = \
        Label(self.master, text="animal id:").grid(row=8,column=0,sticky=W)
        self.animalIDStr=StringVar(self.master)
        self.animalIDStr_entry=Entry(self.master,\
            textvariable=self.animalIDStr)
        self.animalIDStr_entry.grid(row=8,column=0,sticky=E)
        self.animalIDStr.set('cj_dX')
        self.animalIDStr_entry.config(width=12)

        self.totalTrials_label = \
        Label(self.master, text="total trials").grid(row=9,column=0,sticky=W)
        self.totalTrials=StringVar(self.master)
        self.totalTrials_entry=Entry(self.master,textvariable=self.totalTrials)
        self.totalTrials_entry.grid(row=9, column=0,sticky=E)
        self.totalTrials.set('100')
        self.totalTrials_entry.config(width=12)
        self.dateStr = datetime.datetime.\
        fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M')

        self.mw_button_startSession = Button(self.master, text="Start Task",\
            width = 7, command=self.runTask)
        self.mw_button_startSession.grid(row=10, column=0,sticky=W,padx=6)
        self.mw_button_startSession.config(state=DISABLED)

        self.mw_button_endSession = Button(self.master, text="End Task",\
            width = 7, command=lambda: self.state_util_switchToNewState(self.endState))
        self.mw_button_endSession.grid(row=10, column=0,sticky=E,padx=6)
        self.mw_button_endSession.config(state=DISABLED)



        self.taskProbs_Button = Button(self.master, text = 'Task Probs',\
         width = 10, command = self.make_taskProbFrame)
        self.taskProbs_Button.grid(row=8, column=2)
        self.taskProbs_Button.config(state=NORMAL)

        self.stateToggles_Button = Button(self.master, text = 'State Toggles',\
         width = 10, command = self.make_stateToggleFrame)
        self.stateToggles_Button.grid(row=9, column=2)
        self.stateToggles_Button.config(state=NORMAL)
        
        self.stateVars_Button = Button(self.master, text = 'State Vars',\
         width = 10, command = self.make_stateVarFrame)
        self.stateVars_Button.grid(row=10, column=2)
        self.stateVars_Button.config(state=NORMAL)

    def metadata_lickDetection(self):
        sRow=12
        self.guiPad = Label(self.master, text="")
        self.guiPad.grid(row=sRow, column=0)

        self.guiPad = Label(self.master, text="Lick Detection:")
        self.guiPad.grid(row=sRow+2, column=0,sticky=W,padx=7)

        self.ux_adaptThresh=StringVar(self.master)
        self.ux_adaptThreshToggle=Checkbutton(self.master, \
            text="Ad Thr?",variable=self.ux_adaptThresh)
        self.ux_adaptThreshToggle.grid(row=sRow+3, column=0,sticky=W,padx=20)
        self.ux_adaptThreshToggle.select()

        self.lickValuesOrDeltas=StringVar(self.master)
        self.ux_lickValuesToggle=Checkbutton(self.master, \
            text="Lk Val?",variable=self.lickValuesOrDeltas)
        self.ux_lickValuesToggle.grid(row=sRow+3, column=0,sticky=E,padx=20)
        self.ux_lickValuesToggle.select()

        self.lickThreshold_label = Label(self.master, text="lick threshold:")
        self.lickThreshold_label.grid(row=sRow+4,column=0,sticky=W,padx=12)
        self.lickThr_a=StringVar(self.master)
        self.lickMax_entry=Entry(self.master,width=6,textvariable=self.lickThr_a)
        self.lickMax_entry.grid(row=sRow+4, column=0,sticky=E,padx=12)
        self.lickThr_a.set(12)

        # plot stuff
        self.lickMax_label = Label(self.master, text="        lick max:")
        self.lickMax_label.grid(row=sRow+5, column=0,sticky=W,padx=12)
        self.lickPlotMax=StringVar(self.master)
        self.lickMax_entry=Entry(self.master,width=6,textvariable=self.lickPlotMax)
        self.lickMax_entry.grid(row=sRow+5, column=0,sticky=E,padx=12)
        self.lickPlotMax.set('2000')

    def metadata_plotting(self):
        sRow=17
        self.guiPad = Label(self.master, text="")
        self.guiPad.grid(row=sRow, column=0)

        # TODO: organize by plot types
        self.sampPlot_label = Label(self.master, text="samples to plot")
        self.sampPlot_label.grid(row=sRow+1, column=0,sticky=W)
        self.sampsToPlot=StringVar(self.master)
        self.sampPlot_entry=Entry(self.master,width=6,textvariable=self.sampsToPlot)
        self.sampPlot_entry.grid(row=sRow+1, column=0,sticky=E)
        self.sampsToPlot.set('1000')
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

    def quitBtnCB(self):
        if self.ranTask==0 or self.comObjectExists==0:  
            print('*** bye: closed without saving ***')
            exit()
        elif self.ranTask>=1 and self.comObjectExists==1:
            self.data_saveData() 
            self.utilState_syncSerial()
            self.comObj.close()
            print('bye: closed com port, resyncd its state, and saved some data')
            exit()

    def btnCB_setPath(self):
        self.getFilePath()
        self.sesPath.set(self.dirPath)
        self.fixPath()
        self.animalIDStr.set(os.path.basename(self.dirPath))
        metaString='{}{}_animalMeta.csv'.format(self.sdir,self.animalIDStr.get())
        stateString='{}{}_stateMap.csv'.format(self.sdir,self.animalIDStr.get())
        self.loadedMeta=os.path.isfile(metaString)
        self.loadedStates=os.path.isfile(stateString)
        if self.loadedMeta is True:
            tempMeta=pd.read_csv(metaString,index_col=0)
        if self.loadedStates is True:
            tempStates=pd.Series.from_csv(stateString)
        print(tempStates)
        tempMeta.to_csv('.lastMeta.csv')
        tempStates.to_csv('.lastStates.csv')

    ################################
    ## **** Auxilary Windows **** ##
    ################################

    def make_taskProbFrame(self):
        tb_frame = Toplevel()
        tb_frame.title('Task Probs')
        self.tb_frame=tb_frame

        self.taskLimbs=2  
        # How many choice splits in your task

        self.populate_taskProbFrame()
        self.setTaskProbs = Button(tb_frame, \
            text = 'Set Probs.', width = 10, \
            command = self.refresh_TaskProbs)
        self.setTaskProbs.grid(row=8, column=1)    

    def make_stateToggleFrame(self):
        st_frame = Toplevel()
        st_frame.title('States in Task')
        self.st_frame=st_frame

        stateStartColumn=0
        stateStartRow=4
        self.stateStartColumn=stateStartColumn
        self.stateStartRow=stateStartRow

        self.sBtn_boot = Button(st_frame, text="S0: Boot", \
            command=lambda: self.state_util_switchToNewState(self.bootState))
        self.sBtn_boot.grid(row=stateStartRow-1, column=stateStartColumn)
        self.sBtn_boot.config(state=NORMAL)

        self.sBtn_wait = Button(st_frame, text="S1: Wait", \
            command=lambda: self.state_util_switchToNewState(self.waitState))
        self.sBtn_wait.grid(row=stateStartRow, column=stateStartColumn)
        self.sBtn_wait.config(state=NORMAL)

        self.sBtn_initiate = Button(st_frame, text="S2: Initiate", \
            command=lambda: self.state_util_switchToNewState(self.initiationState))
        self.sBtn_initiate.grid(row=stateStartRow, column=stateStartColumn+1)
        self.sBtn_initiate.config(state=NORMAL)

        self.sBtn_cue1 = Button(st_frame, text="S3: Cue 1", \
            command=lambda: self.state_util_switchToNewState(self.cue1State))
        self.sBtn_cue1.grid(row=stateStartRow-1, column=stateStartColumn+2)
        self.sBtn_cue1.config(state=NORMAL)

        self.sBtn_cue2 = Button(st_frame, text="S4: Cue 2", \
            command=lambda: self.state_util_switchToNewState(self.cue2State))
        self.sBtn_cue2.grid(row=stateStartRow+1, column=stateStartColumn+2)
        self.sBtn_cue2.config(state=NORMAL)

        self.sBtn_stim1 = Button(st_frame, text="SS1: Stim 1", \
            command=lambda: self.state_util_switchToNewState(self.stim1State))
        self.sBtn_stim1.grid(row=stateStartRow-2, column=stateStartColumn+3)
        self.sBtn_stim1.config(state=NORMAL)

        self.sBtn_stim2 = Button(st_frame, text="SS2: Stim 2",\
            command=lambda: self.state_util_switchToNewState(self.stim2State))
        self.sBtn_stim2.grid(row=stateStartRow-1, column=stateStartColumn+3)
        self.sBtn_stim2.config(state=NORMAL)

        self.sBtn_catch = Button(st_frame, text="SC: Catch", \
            command=lambda: self.state_util_switchToNewState(self.catchState))
        self.sBtn_catch.grid(row=stateStartRow, column=stateStartColumn+3)
        self.sBtn_catch.config(state=NORMAL)

        self.sBtn_reward = Button(st_frame, text="Reward State", \
            command=lambda: self.state_util_switchToNewState(self.rewardState))
        self.sBtn_reward.grid(row=stateStartRow-1, column=stateStartColumn+4)
        self.sBtn_reward.config(state=NORMAL)

        self.sBtn_neutral = Button(st_frame, text="SN: Neutral", \
            command=lambda: self.state_util_switchToNewState(self.neutralState))
        self.sBtn_neutral.grid(row=stateStartRow, column=stateStartColumn+4)
        self.sBtn_neutral.config(state=NORMAL)

        self.sBtn_punish = Button(st_frame, text="SP: Punish", \
            command=lambda: self.state_util_switchToNewState(self.punishState))
        self.sBtn_punish.grid(row=stateStartRow+1, column=stateStartColumn+4)
        self.sBtn_punish.config(state=NORMAL)

        self.sBtn_save = Button(st_frame, text="Save State", \
            command=lambda: self.state_util_switchToNewState(self.saveState))
        self.sBtn_save.grid(row=stateStartRow+1, column=stateStartColumn)
        self.sBtn_save.config(state=NORMAL)

        self.sBtn_endSession = Button(st_frame, text="End Session", \
            command=lambda: self.state_util_switchToNewState(self.endState))
        self.sBtn_endSession.grid(row=stateStartRow-2, column=stateStartColumn)
        self.sBtn_endSession.config(state=NORMAL)
    
    def make_stateVarFrame(self):
        frame_sv = Toplevel()
        frame_sv.title('Task Probs')
        self.frame_sv=frame_sv

        self.populate_stateVarFrame()
        self.setStateVars = Button(frame_sv, \
            text = 'Set Variables.', width = 10, \
            command = self.refresh_stateVars)
        self.setStateVars.grid(row=8, column=1)
    
    def initialize_TaskProbs(self):
        self.t1_probEntries='sTask1_prob','sTask1_target_prob',\
        'sTask1_distract_prob','sTask1_target_reward_prob',\
        'sTask1_target_punish_prob','sTask1_distract_reward_prob',\
        'sTask1_distract_punish_prob'
        if self.taskProbsRefreshed==0:
            self.t1_probEntriesValues=[0.5,0.5,0.5,1.0,0.0,0.0,1.0]

        self.t2_probEntries='sTask2_prob','sTask2_target_prob',\
        'sTask2_distract_prob','sTask2_target_reward_prob',\
        'sTask2_target_punish_prob','sTask2_distract_reward_prob',\
        'sTask2_distract_punish_prob'
        if self.taskProbsRefreshed==0:
            self.t2_probEntriesValues=[0.5,0.5,0.5,0.0,1.0,1.0,0.0]
    
    def populate_taskProbFrame(self):
        for x in range(0,len(self.t1_probEntries)):
            exec('self.{}=StringVar(self.tb_frame)'.format(self.t1_probEntries[x]))
            exec('self.{}_label = Label(self.tb_frame, text="{}")'.\
                format(self.t1_probEntries[x],self.t1_probEntries[x]))
            exec('self.{}_entry=Entry(self.tb_frame,width=6,textvariable=self.{})'.\
                format(self.t1_probEntries[x],self.t1_probEntries[x]))
            exec('self.{}_label.grid(row=x, column=1)'.format(self.t1_probEntries[x]))
            exec('self.{}_entry.grid(row=x, column=0)'.format(self.t1_probEntries[x]))
            exec('self.{}.set({})'\
                .format(self.t1_probEntries[x],self.t1_probEntriesValues[x]))

        for x in range(0,len(self.t2_probEntries)):
            exec('self.{}=StringVar(self.tb_frame)'.format(self.t2_probEntries[x]))
            exec('self.{}_label = Label(self.tb_frame, text="{}")'.\
                format(self.t2_probEntries[x],self.t2_probEntries[x]))
            exec('self.{}_entry=Entry(self.tb_frame,width=6,textvariable=self.{})'.\
                format(self.t2_probEntries[x],self.t2_probEntries[x]))
            exec('self.{}_label.grid(row=x, column=3)'.format(self.t2_probEntries[x]))
            exec('self.{}_entry.grid(row=x, column=2)'.format(self.t2_probEntries[x]))
            exec('self.{}.set({})'\
                .format(self.t2_probEntries[x],self.t2_probEntriesValues[x]))

    def refresh_TaskProbs(self):
        
        for x in range(0,len(self.t1_probEntries)):
            exec('self.t1_probEntriesValues[x]=(float(self.{}.get()))'\
                .format(self.t1_probEntries[x]))
            exec('self.{}.set(str(self.t1_probEntriesValues[x]))'\
                .format(self.t1_probEntries[x]))
        
        for x in range(0,len(self.t2_probEntries)):
            exec('self.t2_probEntriesValues[x]=(float(self.{}.get()))'\
                .format(self.t2_probEntries[x]))
            exec('self.{}.set(str(self.t2_probEntriesValues[x]))'\
                .format(self.t2_probEntries[x]))

        self.taskProbsRefreshed=1

    def initialize_StateVars(self):
        self.t1_stateVarsEntries='self.movThr','self.movTimeThr'
        if self.stateVarsRefreshed==0:
            self.t1_stateVarsValues=[40,2]

    def populate_stateVarFrame(self):
        for x in range(0,len(self.t1_stateVarsEntries)):
            exec('self.{}=StringVar(self.self.frame_sv)'\
                .format(self.t1_stateVarsEntries[x]))
            exec('self.{}_label = Label(self.self.frame_sv, text="{}")'.\
                format(self.t1_stateVarsEntries[x],self.t1_stateVarsEntries[x]))
            exec('self.{}_entry=Entry(self.self.frame_sv,width=6,textvariable=self.{})'.\
                format(self.t1_stateVarsEntries[x],self.t1_stateVarsEntries[x]))
            exec('self.{}_label.grid(row=x, column=1)'\
                .format(self.t1_stateVarsEntries[x]))
            exec('self.{}_entry.grid(row=x, column=0)'\
                .format(self.t1_stateVarsEntries[x]))
            exec('self.{}.set({})'\
                .format(self.t1_stateVarsEntries[x],self.t1_stateVarsValues[x]))

    def refresh_stateVars(self):
        
        for x in range(0,len(self.t1_stateVarsEntries)):
            exec('self.t1_stateVarsValues[x]=(float(self.{}.get()))'\
                .format(self.t1_stateVarsEntries[x]))
            exec('self.{}.set(str(self.t1_stateVarsValues[x]))'\
                .format(self.t1_stateVarsEntries[x]))
        
        self.stateVarsRefreshed=1

    ########################################
    ## **** Serial Related Functions **** ##
    ########################################

    def serial_initComObj(self):
        if self.comObjectExists==0:
            print('Opening serial port: {}'.\
                format(self.comPath.get()))
            self.comObj = serial.Serial(self.comPath.get(),\
                self.baudSelected.get()) 
            self.utilState_syncSerial()
            self.comObjectExists=1

            # update the GUI
            self.comPathEntry.config(state=DISABLED)
            self.baudPick.config(state=DISABLED)
            self.createCom_button.config(state=DISABLED)
            self.mw_button_startSession.config(state=NORMAL)
            self.closeComObj_button.config(state=NORMAL)
            self.syncComObj_button.config(state=NORMAL)
            # self.taskProbs_Button.invoke()
            # self.stateToggles_Button.invoke()
        
    def serial_closeComObj(self):
        if self.comObjectExists==1:
            if self.dataExists==1:
                self.data_saveData()
            self.utilState_syncSerial()
            self.comObj.close()
            self.comObjectExists=0
            print('> i closed the COM object')
            
            # update the GUI
            self.comPathEntry.config(state=NORMAL)
            self.baudPick.config(state=NORMAL)
            self.createCom_button.config(state=NORMAL)
            self.mw_button_startSession.config(state=DISABLED)
            self.closeComObj_button.config(state=DISABLED)
            self.syncComObj_button.config(state=DISABLED)
            # self.taskProbs_Button.invoke()
            # self.stateToggles_Button.invoke()

    def serial_readDataFlush(self):
        self.comObj.flush()
        self.serial_readData()

    def serial_readData(self):
        # position is 8-bit, hence the 256
        self.sR=self.comObj.readline().strip().decode()
        self.sR=self.sR.split(',')
        if len(self.sR)==7 and self.sR[self.stID_header]=='data' and \
        str.isnumeric(self.sR[1])==1 and \
        str.isnumeric(self.sR[2])==1 and \
        str.isnumeric(self.sR[self.stID_pos])==1 and \
        int(self.sR[self.stID_pos]) < 256 and \
        str.isnumeric(self.sR[4])==1 and \
        str.isnumeric(self.sR[5])==1 and \
        str.isnumeric(self.sR[6])==1 :
            self.dataAvail=1

        elif len(self.sR)!=7 or self.sR[self.stID_header]!='data' or \
        str.isnumeric(self.sR[1])!=1 or \
        str.isnumeric(self.sR[2])!=1 or \
        str.isnumeric(self.sR[self.stID_pos])!=1 or \
        int(self.sR[self.stID_pos]) >= 256 or \
        str.isnumeric(self.sR[4])!=1 or \
        str.isnumeric(self.sR[5])!=1 or \
        str.isnumeric(self.sR[6])!=1 :
            self.dataAvail=0

        #print(self.sR)

    #################################################
    ## **** These Are Data Handling Functions **** ##
    #################################################

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
        self.lickValues_a=[]
        self.lickValues_b=[]
        self.detectedLicks_a=[]
        self.detectedLicks_b=[]
        self.pyStatesRS = []
        self.pyStatesRT = []
        self.pyStatesTT = []
        self.pyStatesTS = []

    def data_cleanContainers(self):
        self.arStates=[]          
        self.arduinoTime=[]
        self.arduinoTrialTime=[]  
        self.absolutePosition=[]
        self.posDelta=[]        
        self.lickValues_a=[]
        self.lickValues_b=[]
        self.detectedLicks_a=[]
        self.detectedLicks_b=[]
        self.detectedTrialLicks = []
        self.pyStatesRS = []
        self.pyStatesRT = []
        self.pyStatesTT = []
        self.pyStatesTS = []

    def data_parseData(self):
        self.arduinoTime.append(float(int(self.sR[self.stID_time])/self.timeBase))
        self.arduinoTrialTime.append(float(int(self.sR[self.stID_trialTime])/\
            self.timeBase))
        self.posDelta.append(int(self.sR[self.stID_pos])-128)
        self.absolutePosition.append(int(self.lastPos+self.posDelta[-1]))
        self.lastPos=int(self.absolutePosition[-1])
        self.currentState=int(self.sR[self.stID_state])
        self.arStates.append(self.currentState)
        self.lickValues_a.append(int(self.sR[self.stID_lickSensor_a]))
        self.lickValues_b.append(int(self.sR[self.stID_lickSensor_b]))
        self.analysis_lickDetect()
        self.dataExists=1

    def fixPath(self):
        self.sdir=os.path.isdir(self.sesPath.get())
        if self.sdir==False:
            os.mkdir(self.sesPath.get())
        self.sdir=self.sesPath.get()
        if self.sdir[-1] != '/' :
            self.sdir=self.sdir + '/' 

    def data_saveData(self):

        self.fixPath()

        saveStreams='arduinoTime','arduinoTrialTime','absolutePosition','arStates',\
        'lickValues_a','lickValues_b','pyStatesRS','pyStatesRT','pyStatesTS','pyStatesTT'

        self.tCo=[]
        for x in range(0,len(saveStreams)):
            exec('self.tCo=self.{}'.format(saveStreams[x]))
            if x==0:
                self.rf=pd.DataFrame({'{}'.format(saveStreams[x]):self.tCo})
            elif x != 0:
                self.tf=pd.DataFrame({'{}'.format(saveStreams[x]):self.tCo})
                self.rf=pd.concat([self.rf,self.tf],axis=1)

        self.rf.to_csv('{}{}_{}_trial_{}.csv'.format(self.sdir,self.animalIDStr.get(),\
            self.dateStr,self.currentTrial))
        self.stateBindings.to_csv('{}{}_stateMap.csv'.\
            format(self.sdir,self.animalIDStr.get()))

        self.dataExists=0

    def exceptionCallback(self):
        print('EXCEPTION thrown: I am going down')
        print('last trial = {} and the last state was {}. \
            I will try to save last trial ...'\
            .format(self.currentTrial,self.currentState))
        self.dataExists=0
        self.data_saveData()
        print('save was a success; now I will close com port and quit')
        print('I will try to reset the mc state before closing the port ...')
        self.comObj.close()
        #todo: add a timeout for the resync
        print('closed the com port cleanly')
        exit()

    #################################################
    ## **** These Are Data Handling Functions **** ##
    #################################################

    def analysis_updateLickThresholds(self):   
        #todo: I think the asignment conflicts now because of the graph
        if self.ux_adaptThresh.get()==1:
            print(int(self.lickThr_a))
            tA=np.abs(np.array(self.lickValues_a))
            print(int(np.percentile(aaa[np.where(aaa != 0)[0]],75)))
            self.lickThr_a.set(str(np.percentile(tA[np.where(tA != 0)[0]],75)))
            self.lickMinMax=[min(self.lickValues_a),max(self.lickValues_a)]

    def analysis_lickDetect(self):
        if self.lickValues_a[-1]>int(self.lickThr_a.get()):
            self.detectedLicks_a.append(int(self.lickPlotMax.get())/2)
        elif self.lickValues_a[-1]<=int(self.lickThr_a.get()):
            self.detectedLicks_a.append(0)

    #################################################
    ## **** These Are Plotting  Functions **** ##
    #################################################

    def updatePosPlot(self):
        if len(self.arduinoTime)>2: 
            self.cTD=self.arduinoTrialTime[-1]-self.arduinoTrialTime[-2]
            self.tTP=self.segPlot*self.cTD
        self.segPlot=int(self.sampsToPlot.get())    #=int(self.sampsToPlot.get())
        int(self.sampsToPlot.get())
        
        plt.subplot(2,2,1)
        self.lA=plt.plot(self.arduinoTrialTime[-self.segPlot:-1],\
            self.absolutePosition[-self.segPlot:-1],'k-')
        plt.ylim(-6000,6000)
        
        if len(self.arduinoTrialTime)>self.segPlot+1:
            plt.xlim(self.arduinoTrialTime[-self.segPlot],self.arduinoTrialTime[-1])
        elif len(self.arduinoTrialTime)<=self.segPlot+1:
            plt.xlim(0,self.tTP)

        
        plt.ylabel('position')
        plt.xlabel('time since trial start (sec)')

        plt.subplot(2,2,3)
        self.lG=plt.plot(self.arduinoTrialTime[-self.segPlot:-1],\
            self.lickValues_a[-self.segPlot:-1],'k-')
        plt.ylim(0,int(self.lickPlotMax.get()))
        if len(self.arduinoTrialTime)>self.segPlot+1:
            plt.xlim(self.arduinoTrialTime[-self.segPlot],self.arduinoTrialTime[-1])
        elif len(self.arduinoTrialTime)<=self.segPlot+1:
            plt.xlim(0,self.tTP)
        plt.ylabel('licks (binary)')
        plt.xlabel('time since trial start (sec)')

        plt.subplot(2,2,2)
        if self.updateStateMap==1:
            self.lC=plt.plot(self.stateDiagX,self.stateDiagY,'ro',markersize=self.smMrk)
            self.lD=plt.plot(self.stateDiagX[self.currentState],\
                self.stateDiagY[self.currentState],'go',markersize=self.lrMrk)
            plt.ylim(0,10)
            plt.xlim(0,10)
            plt.title('trial = {} ; state = {}'.format(self.currentTrial,self.currentState))

        plt.pause(self.pltDelay)
        self.lA.pop(0).remove()
        self.lG.pop(0).remove()
        if self.updateStateMap==1:
            self.lC.pop(0).remove()
            self.lD.pop(0).remove()

    def updatePlotCheck(self):
        self.analysis_updateLickThresholds()
        self.updatePosPlot()
        self.cycleCount=0

    #######################################
    ## **** Custom State Callbacks **** ##
    ######################################

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
                self.state_util_switchToNewState(self.initiationState)

    def callback_initiationState(self):
        t1P=0.5
        if self.absolutePosition[-1]>self.distThr:
            if self.task_switch<=t1P:
                print('moving spout; cue stim task #1')
                self.state_util_switchToNewState(self.cue1State)
            # if stimSwitch is more than task1's probablity then send to task #2
            elif self.task_switch>t1P:
                print('moving spout; cue stim task #2')
                self.state_util_switchToNewState(self.cue2State)

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
                    print('will play dulcet tone')
                    self.state_util_switchToNewState(self.stim1State)
                elif self.outcomeSwitch>0.5:
                    print('will play ominous tone')
                    self.state_util_switchToNewState(self.stim2State)

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
                #print('result={}'.format(self.outcomeSwitch<=trP))
                print('Still!')
                if self.outcomeSwitch<=0.5:
                    print('will play dulcet tone')
                    self.state_util_switchToNewState(self.stim2State)
                # if stimSwitch is more than task1's probablity then send to task #2
                elif self.outcomeSwitch>0.5:
                    print('will play ominous tone')
                    self.state_util_switchToNewState(self.stim1State)
    
    def callback_stim1State(self):
        if self.arduinoTime[-1]-self.entryTime>2:
            print('time cond met') #debug
            self.dPos=abs(self.absolutePosition[-1]-self.absolutePosition[-2])
            print(self.dPos)
            if self.dPos>self.movThr and self.stillLatch==1:
                print('moving')
                self.stillLatch=0
            if self.dPos<=self.movThr and self.stillLatch==0:
                print('still')
                self.stillTimeStart=self.arduinoTime[-1]
                self.stillLatch=1
            if self.dPos<=self.movThr and self.stillLatch==1:
                self.stillTime=self.arduinoTime[-1]-self.stillTimeStart
            if self.stillLatch==1 and self.stillTime>1:
                print('Still!: off to save')
                self.state_util_switchToNewState(self.saveState)

    def callback_stim2State(self):
        if self.arduinoTime[-1]-self.entryTime>2:
            print('time cond met') #debug
            self.dPos=abs(self.absolutePosition[-1]-self.absolutePosition[-2])
            print(self.dPos)
            if self.dPos>self.movThr and self.stillLatch==1:
                print('moving')
                self.stillLatch=0
            if self.dPos<=self.movThr and self.stillLatch==0:
                print('still')
                self.stillTimeStart=self.arduinoTime[-1]
                self.stillLatch=1
            if self.dPos<=self.movThr and self.stillLatch==1:
                self.stillTime=self.arduinoTime[-1]-self.stillTimeStart
            if self.stillLatch==1 and self.stillTime>1:
                print('Still!: off to save')
                self.state_util_switchToNewState(self.saveState)

    def callback_rewardState(self): #21
        #t1P=float(self.sTask1_prob.get())
        if self.absolutePosition[-1]>self.distThr:
            print('rewarding')
            self.state_util_switchToNewState(self.saveState)

    def callback_punishState(self): #23
        if self.arduinoTime[-1]-self.entryTime>=self.timeOutDuration:
            print('timeout of {} seconds is over'.format(self.timeOutDuration))
            self.state_util_switchToNewState(self.saveState)

def main(): 
    root = Tk()
    app = pyDiscrim_mainGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()