# pyDiscrim:
# This is a python program that executes a defined sensory discrimination task
# in a state-based manner.
# It works with microcontrolors or dac boards (conceptually). 
# It can be modified for different tasks.
#
# Version 2.54
# 6/28/2017
# questions? --> Chris Deister --> cdeister@brown.edu

# ver changes: most debug prints out, MUCH more reliable serial


from tkinter import *
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

class pyDiscrim_mainGUI:

    def __init__(self,master):
        
        # Make the main GUI window
        # Tkinter requires a parent named master.
        self.master = master
        self.frame = Frame(self.master)

        self.populate_MainWindow_Primary()
        self.initialize_SessionVariables()
        self.initialize_StateVariables()
        self.populate_MainWindow_SerialBits()
        self.metadata_animalID()
        self.metadata_sessionFlow()
        self.metadata_lickDetection()
        self.metadata_plotting()
        self.initialize_TaskProbs()
        self.initialize_CallbackVariables()
        self.data_serialInputIDs()

    ##################################
    # ******* Task Block ************#
    ##################################

    def runTask(self):
        print('started at state:')
        print(self.currentState)
        self.shouldRun=1
        self.data_makeContainers()
        self.uiUpdateDelta=300
        self.ranTask=1
        # while the current trial is less than the total trials, python script decides what to do based on what the current state is
        while self.currentTrial<=int(self.totalTrials.get()) and self.shouldRun==1:
            self.initTime=0  
            try:

                #S0 -----> hand shake (initialization state)
                # if the current trial is 0...
                if self.currentState==self.bootState:
                    self.updateStateMap=1
                    # the td list will be used to ensure that teensy-python communication is running smoothly
                    #as you will see, we observe the variance of 300 time samples and make sure that it is extremely
                    #small to ensure that our clocking is precise before we begin the trial
                    td=[float(0)]
                    # self.updateStateButtons()
                    print('in state 0')
                    #resetting the absolute position every time that we enter a new state 
                    self.lastPos=0 
                    while self.currentState==0:
                        #this method examines data that is currently available in the serial buffer. If the data that is present is
                        # valid (discussed in parse data), GSH sets dataAvailable = 1
                        print('past 0')
                        self.generic_StateHeader() #(GSH)
                        print('past 1')
                        if self.dataAvail==1:
                            print('past 2')
                            #his gets the total time in he state 

                            td.append(float(self.arduinoTime[-1]-self.initTime))


                            #self.initTime is the time that the script entered the current state
                            # the syntax "arduinoTime[]" is used to access a value in a list
                            #to get the most recent value, -1 is used
                            # Therefore, the variable initTime is set to the most recent value added to the list arduinoTime
                            self.initTime=self.arduinoTime[-1]
                            print("doing state 0 stuff")
                            # this uses the length of the list that is storing the time points of each iteration of the task loop where
                            # data was available
                            # if we have had data available for more than 300 loops
                            if len(td)>300:
                                #get the variance of all of the values in the time list
                                print(np.var(td[-98:-1]))
                                #make sure that the variance is less than .01 and if it is, do the serial_handShake to send the teensy into state 1
                                if np.var(td[-98:-1])<0.01: 
                                    print('cond fine')
                                    #rather than running a condition block like the other states, state 0 is the initialization state that ensures
                                    # that proper communication is established between the teensy and the python script
                                    self.serial_handShake()  

                #S1 -----> trial wait state
                elif self.currentState==self.waitState:
                    self.updateStateMap=1
                    self.lastPos=0
                    # self.updateStateButtons()
                    self.entryTime=self.arduinoTime[-1]
                    print('in s1')
                    while self.currentState==1:
                        self.generic_StateHeader()
                        if self.dataAvail==1:
                            if int(self.cycleCount) % int(self.uiUpdateDelta)==0:
                                self.updatePlotCheck()
                            self.callback_waitState()
                            self.cycleCount=self.cycleCount+1;

                #S2 -----> trial initiation state
                elif self.currentState==self.initiateState:
                    self.lastPos=0
                    self.entryTime=self.arduinoTime[-1]
                    self.task_switch=random.random()
                    while self.currentState==self.initiateState:
                        self.generic_StateHeader() 
                        if self.dataAvail==1:
                            if int(self.cycleCount) % int(self.uiUpdateDelta)==0:
                                self.updatePlotCheck()
                            self.callback_initiationState()
                            self.cycleCount=self.cycleCount+1;

                #S3 -----> cue #1
                elif self.currentState==self.cue1State:
                    self.lastPos=0
                    # self.updateStateButtons()
                    self.entryTime=self.arduinoTime[-1]
                    self.outcomeSwitch=random.random() # debug
                    while self.currentState==self.cue1State:
                        self.generic_StateHeader()
                        if self.dataAvail==1:
                            if int(self.cycleCount) % int(self.uiUpdateDelta)==0:
                                self.updatePlotCheck()
                            self.callback_cue1State()
                            self.cycleCount=self.cycleCount+1;

                #S4 -----> cue #2
                elif self.currentState==self.cue2State:
                    self.lastPos=0
                    # self.updateStateButtons()
                    self.entryTime=self.arduinoTime[-1]
                    self.outcomeSwitch=random.random() # debug
                    while self.currentState==self.cue2State:    
                        self.generic_StateHeader()
                        if self.dataAvail==1:
                            if int(self.cycleCount) % int(self.uiUpdateDelta)==0:
                                self.updatePlotCheck()
                            self.callback_cue2State()
                            self.cycleCount=self.cycleCount+1;

                #S5 -----> stim tone #1
                elif self.currentState==self.stim1State:
                    self.lastPos=0
                    # self.updateStateButtons()
                    self.entryTime=self.arduinoTime[-1]
                    while self.currentState==5:
                        self.generic_StateHeader()
                        if self.dataAvail==1:
                            if int(self.cycleCount) % int(self.uiUpdateDelta)==0:
                                self.updatePlotCheck()
                            self.callback_toneStates1()
                            self.cycleCount=self.cycleCount+1;

                #S6 -----> stim tone #2
                elif self.currentState==self.stim2State:
                    self.lastPos=0
                    # self.updateStateButtons()
                    self.entryTime=self.arduinoTime[-1]
                    while self.currentState==6:
                        self.generic_StateHeader()
                        if self.dataAvail==1:
                            if int(self.cycleCount) % int(self.uiUpdateDelta)==0:
                                self.updatePlotCheck()
                            self.callback_toneStates2()
                            self.cycleCount=self.cycleCount+1;


                #S21 -----> reward state
                elif self.currentState==self.rewardState:
                    self.updateStateMap=0
                    self.lastPos=0
                    self.entryTime=self.arduinoTime[-1]
                    self.pyStatesCT.append(self.entryTime)
                    while self.currentState==self.rewardState:
                        self.generic_StateHeader()
                        if self.dataAvail==1: # todo: in all states
                            if int(self.cycleCount) % int(self.uiUpdateDelta)==0:
                                self.updatePlotCheck()   # todo: in all states
                            self.callback_rewardState()  # condition blocks are unique (always custom)
                            self.cycleCount=self.cycleCount+1; # todo: in all states (just for ui)

                #S23 -----> punish state
                elif self.currentState==self.punishState:
                    self.updateStateMap=0
                    self.lastPos=0 # resets positions baseline
                    self.entryTime=self.arduinoTime[-1]
                    self.pyStatesCT.append(self.entryTime)
                    while self.currentState==self.punishState:
                        self.generic_StateHeader()
                        if self.dataAvail==1: # todo: in all states
                            if int(self.cycleCount) % int(self.uiUpdateDelta)==0:
                                self.updatePlotCheck()   # todo: in all states
                            self.callback_punishState()  # condition blocks are unique (always custom)
                            print
                            self.cycleCount=self.cycleCount+1; # todo: in all states (just for ui)

                #S13: save state
                elif self.currentState==self.saveState:
                    print(self.arduinoTrialTime[-1])
                    print(self.arduinoTrialTime[0])

                    print('in save state; saving your bacon') # debug
                    self.data_saveData()                    # clean up plot data (memory managment)
                    self.data_cleanContainers()
                    self.currentTrial=self.currentTrial+1
                    print('trial done')
                    self.comObj.write(struct.pack('>B', self.waitState)) #todo: abstract wait
                    self.state_waitForStateToUpdateOnTarget(self.saveState)
                
                #S25: end session state
                elif self.currentState==self.endState:
                    print('About to end the session ...')
                    print('last trial = {} and the last state was {}'\
                        .format(self.currentTrial,self.currentState))
                    if self.dataExists==1:
                        self.data_saveData()
                        print('save was a success; now I will close com port')
                    return



            except:
                print(self.dPos)
                print('EXCEPTION: peace out bitches')
                print('last trial = {} and the last state was {}. \
                    I will try to save last trial ...'\
                    .format(self.currentTrial,self.currentState))
                self.data_saveData() 
                self.comObj.write(struct.pack('>B', self.bootState))
                print('save was a success; now I will close com port and quit')
                self.comObj.close()
                exit()
        if self.shouldRun==1:
            print('NORMAL: peace out')
            print('I completed {} trials.'.format(self.currentTrial-1))
            self.serial_closeComObj()
        
        elif self.shouldRun==0:     
            print('I completed {} trials.'.format(self.currentTrial-1))


    #########################################################
    ## **** These Functions Set All Initial Variables **** ##
    #########################################################    

    def initialize_SessionVariables(self):
        self.ranTask=0
        self.dataExists=0
        self.comObjectExists=0
        self.probsRefreshed=0 
        self.fakeComObj=0
        self.updateStateMap=1

        self.dPos=float(0)
        self.currentTrial=1
        self.currentState=0

        self.currentTrial=1
        self.currentState=0
        self.lowDelta=0
        self.stateIt=0;

    def initialize_StateVariables(self):
        self.bootState=0
        self.waitState=1
        self.initiateState=2
        self.cue1State=3
        self.cue2State=4

        self.stim1State=5
        self.stim2State=6
        self.catchState=7

        self.saveState=13

        self.rewardState=21
        self.neutralState=22
        self.punishState=23
        self.endState=25
        self.defaultState=29

    def initialize_CallbackVariables(self):
        ## Globals
        self.movThr=40       
        # in position units (The minimum ammount of movement allowed)
        self.movTimeThr=2    
        # in seconds (The time the mouse must be still)
        # initialization
        self.stillTime=float(0)
        self.stillLatch=0
        self.stillTimeStart=float(0)
        self.distThr=1000  
        self.timeOutDuration=5;
        # This is the distance the mouse needs 
        #to move to initiate a stimulus trial.

    #############################################################
    ## **** These Are Key Common State Handling Functions **** ##
    #############################################################
    
    def state_switchState(self,selectedStateNumber):
        self.selectedStateNumber=selectedStateNumber
        if self.dataExists==1:
            self.pyStatesRS.append(self.selectedStateNumber)
            self.pyStatesRT.append(self.arduinoTime[-1])
        print('state change to {}'.format(self.selectedStateNumber))
        self.currentState=self.selectedStateNumber
        self.comObj.write(struct.pack('>B', selectedStateNumber))

    def state_waitForStateToUpdateOnTarget(self,maintState): 
        self.maintState=maintState
        while self.currentState==self.maintState:      
            self.stateIt=0  # will go away todo
            self.serial_readDataFlush()
            if self.dataAvail==1:
                self.data_parseData()
                self.currentState=int(self.sR[self.stID_state])

    ###########################################################
    ## **** These Functions Augment The Main GUI Window **** ##
    ###########################################################
        
    def populate_MainWindow_Primary(self):
        self.master.title("pyDiscrim")

        self.createCom_button = Button(self.master, text="Start Serial",\
         width = 10, command=self.serial_initComObj)
        self.createCom_button.grid(row=0, column=2)

        self.closeComObj_button = Button(self.master, text="Close Serial",\
            width = 10, command=self.serial_closeComObj)
        self.closeComObj_button.grid(row=4, column=2)
        self.closeComObj_button.config(state=DISABLED)   

        self.taskProbs_Button = Button(self.master, text = 'Task Probs',\
         width = 10, command = self.make_taskProbFrame)
        self.taskProbs_Button.grid(row=1, column=2)
        self.taskProbs_Button.config(state=NORMAL)

        self.stateToggles_Button = Button(self.master, text = 'State Toggles',\
         width = 10, command = self.make_stateToggleFrame)
        self.stateToggles_Button.grid(row=2, column=2)
        self.stateToggles_Button.config(state=NORMAL)

        self.start_button = Button(self.master, text="Start Task",\
            width = 10, command=self.runTask)
        self.start_button.grid(row=3, column=2)
        self.start_button.config(state=DISABLED)

        self.quit_button = Button(self.master, text="Exit", \
            command=self.simpleQuit, width=10)
        self.quit_button.grid(row=20, column=2)

    def populate_MainWindow_SerialBits(self):
        self.comPortEntry_label = Label(self.master, text="COM Port Location")
        self.comPortEntry_label.grid(row=0, column=0)

        self.comPath=StringVar(self.master)
        if sys.platform == 'darwin':
            self.mainPort='/dev/cu.usbmodem2762721';
            self.comPath.set(self.mainPort)
        elif sys.platform == 'win':
            self.mainPort='COM11';
            self.comPath.set(self.mainPort)
        else:
            self.mainPort = 'COM12'
            self.comPath.set(self.mainPort)
        self.comEntry = OptionMenu(self.master,self.comPath,self.mainPort)
        self.comEntry.grid(row=1, column=0)
        self.comEntry.config(width=20)
        if self.comEntry == 'Debug':
            self.fakeComObj=1


        self.baudEntry_label = Label(self.master,text="BAUD Rate")
        self.baudEntry_label.grid(row=2, column=0)

        self.baudSelected=IntVar(self.master)
        self.baudSelected.set(9600)
        self.baudPick = OptionMenu(self.master,self.baudSelected,9600,19200)
        self.baudPick.grid(row=3, column=0)
        self.baudPick.config(width=20)
    
    def metadata_animalID(self):
        self.animalIDStr_label = \
        Label(self.master, text="animal id").grid(row=4,sticky=W)
        self.animalIDStr=StringVar(self.master)
        self.animalIDStr_entry=Entry(self.master,\
            textvariable=self.animalIDStr)
        self.animalIDStr_entry.grid(row=4, column=0)
        self.animalIDStr.set('cj_dX')
        self.animalIDStr_entry.config(width=10)

    def metadata_sessionFlow(self):
        self.totalTrials_label = \
        Label(self.master, text="total trials").grid(row=5,sticky=W)
        self.totalTrials=StringVar(self.master)
        self.totalTrials_entry=Entry(self.master,textvariable=self.totalTrials)
        self.totalTrials_entry.grid(row=5, column=0)
        self.totalTrials.set('100')
        self.totalTrials_entry.config(width=10)
        self.dateStr = datetime.datetime.\
        fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M')

    def metadata_lickDetection(self):
        self.ux_adaptThresh=StringVar(self.master)
        self.ux_adaptThreshToggle=Checkbutton(self.master, \
            text="Ad Thr?",variable=self.ux_adaptThresh)
        self.ux_adaptThreshToggle.grid(row=20, column=0)
        self.ux_adaptThreshToggle.select()

        self.lickValuesOrDeltas=StringVar(self.master)
        self.ux_lickValuesToggle=Checkbutton(self.master, \
            text="Lk Val?",variable=self.lickValuesOrDeltas)
        self.ux_lickValuesToggle.grid(row=21, column=0)
        self.ux_lickValuesToggle.select()

        # plot stuff
        self.lickMax_label = Label(self.master, text="lick max")
        self.lickMax_label.grid(row=23, column=2)
        self.lickPlotMax=StringVar(self.master)
        self.lickMax_entry=Entry(self.master,width=6,textvariable=self.lickPlotMax)
        self.lickMax_entry.grid(row=24, column=2)
        self.lickPlotMax.set('2000')

        self.lickThreshold_label = Label(self.master, text="lick threshold")
        self.lickThreshold_label.grid(row=23, sticky=W)
        self.lickThr_a=StringVar(self.master)
        self.lickMax_entry=Entry(self.master,width=6,textvariable=self.lickThr_a)
        self.lickMax_entry.grid(row=23, column=0)
        self.lickThr_a.set(12)
    
    def metadata_plotting(self):
        # TODO: organize by plot types
        self.sampPlot_label = Label(self.master, text="samples to plot")
        self.sampPlot_label.grid(row=21, column=2)
        self.sampsToPlot=StringVar(self.master)
        self.sampPlot_entry=Entry(self.master,width=6,textvariable=self.sampsToPlot)
        self.sampPlot_entry.grid(row=22, column=2)
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

    def simpleQuit(self):
        if self.ranTask==0 or self.comObjectExists==0:  
            print('audi 5k')
            exit()
        elif self.ranTask==1 and self.comObjectExists==1:
            self.data_saveData() 
            self.comObj.write(struct.pack('>B', 0))
            self.comObj.close()
            exit()

    def saveQuit(self):
        self.data_saveData() 
        self.comObj.write(struct.pack('>B', 0))
        self.comObj.close()
        exit()

    ##############################################################
    ## **** Creates And Populates A Task Probablity Window **** ##
    ##############################################################

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

    def initialize_TaskProbs(self):
        self.t1_probEntries='sTask1_prob','sTask1_target_prob',\
        'sTask1_distract_prob','sTask1_target_reward_prob',\
        'sTask1_target_punish_prob','sTask1_distract_reward_prob',\
        'sTask1_distract_punish_prob'
        if self.probsRefreshed==0:
            self.t1_probEntriesValues=[0.5,0.5,0.5,1.0,0.0,0.0,1.0]

        self.t2_probEntries='sTask2_prob','sTask2_target_prob',\
        'sTask2_distract_prob','sTask2_target_reward_prob',\
        'sTask2_target_punish_prob','sTask2_distract_reward_prob',\
        'sTask2_distract_punish_prob'
        if self.probsRefreshed==0:
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
            exec('self.{}.set({})'.format(self.t1_probEntries[x],self.t1_probEntriesValues[x]))

        for x in range(0,len(self.t2_probEntries)):
            exec('self.{}=StringVar(self.tb_frame)'.format(self.t2_probEntries[x]))
            exec('self.{}_label = Label(self.tb_frame, text="{}")'.\
                format(self.t2_probEntries[x],self.t2_probEntries[x]))
            exec('self.{}_entry=Entry(self.tb_frame,width=6,textvariable=self.{})'.\
                format(self.t2_probEntries[x],self.t2_probEntries[x]))
            exec('self.{}_label.grid(row=x, column=3)'.format(self.t2_probEntries[x]))
            exec('self.{}_entry.grid(row=x, column=2)'.format(self.t2_probEntries[x]))
            exec('self.{}.set({})'.format(self.t2_probEntries[x],self.t2_probEntriesValues[x]))

    def refresh_TaskProbs(self):
        
        for x in range(0,len(self.t1_probEntries)):
            exec('self.t1_probEntriesValues[x]=(float(self.{}.get()))'.format(self.t1_probEntries[x]))
            exec('self.{}.set(str(self.t1_probEntriesValues[x]))'.format(self.t1_probEntries[x]))
        
        for x in range(0,len(self.t2_probEntries)):
            exec('self.t2_probEntriesValues[x]=(float(self.{}.get()))'.format(self.t2_probEntries[x]))
            exec('self.{}.set(str(self.t2_probEntriesValues[x]))'.format(self.t2_probEntries[x]))

        self.probsRefreshed=1

    ###########################################################
    ## **** Creates And Populates A State Toggle Window **** ##
    ###########################################################
    
    def make_stateToggleFrame(self):
        st_frame = Toplevel()
        st_frame.title('States in Task')
        self.st_frame=st_frame

        stateStartColumn=0
        stateStartRow=4
        self.stateStartColumn=stateStartColumn
        self.stateStartRow=stateStartRow

        self.sBtn_boot = Button(st_frame, text="S0: Boot", \
            command=lambda: self.state_switchState(self.bootState))
        self.sBtn_boot.grid(row=stateStartRow-1, column=stateStartColumn)
        self.sBtn_boot.config(state=NORMAL)

        self.sBtn_wait = Button(st_frame, text="S1: Wait", \
            command=lambda: self.state_switchState(self.waitState))
        self.sBtn_wait.grid(row=stateStartRow, column=stateStartColumn)
        self.sBtn_wait.config(state=NORMAL)

        self.sBtn_initiate = Button(st_frame, text="S2: Initiate", \
            command=lambda: self.state_switchState(self.initiateState))
        self.sBtn_initiate.grid(row=stateStartRow, column=stateStartColumn+1)
        self.sBtn_initiate.config(state=NORMAL)

        self.sBtn_cue1 = Button(st_frame, text="S3: Cue 1", \
            command=lambda: self.state_switchState(self.cue1State))
        self.sBtn_cue1.grid(row=stateStartRow-1, column=stateStartColumn+2)
        self.sBtn_cue1.config(state=NORMAL)

        self.sBtn_cue2 = Button(st_frame, text="S4: Cue 2", \
            command=lambda: self.state_switchState(self.cue2State))
        self.sBtn_cue2.grid(row=stateStartRow+1, column=stateStartColumn+2)
        self.sBtn_cue2.config(state=NORMAL)

        self.sBtn_stim1 = Button(st_frame, text="SS1: Stim 1", \
            command=lambda: self.state_switchState(self.stim1State))
        self.sBtn_stim1.grid(row=stateStartRow-2, column=stateStartColumn+3)
        self.sBtn_stim1.config(state=NORMAL)

        self.sBtn_stim2 = Button(st_frame, text="SS2: Stim 2",\
            command=lambda: self.state_switchState(self.stim2State))
        self.sBtn_stim2.grid(row=stateStartRow-1, column=stateStartColumn+3)
        self.sBtn_stim2.config(state=NORMAL)

        self.sBtn_catch = Button(st_frame, text="SC: Catch", \
            command=lambda: self.state_switchState(self.catchState))
        self.sBtn_catch.grid(row=stateStartRow, column=stateStartColumn+3)
        self.sBtn_catch.config(state=NORMAL)

        self.sBtn_reward = Button(st_frame, text="Reward State", \
            command=lambda: self.state_switchState(self.rewardState))
        self.sBtn_reward.grid(row=stateStartRow-1, column=stateStartColumn+4)
        self.sBtn_reward.config(state=NORMAL)

        self.sBtn_neutral = Button(st_frame, text="SN: Neutral", \
            command=lambda: self.state_switchState(self.neutralState))
        self.sBtn_neutral.grid(row=stateStartRow, column=stateStartColumn+4)
        self.sBtn_neutral.config(state=NORMAL)

        self.sBtn_punish = Button(st_frame, text="SP: Punish", \
            command=lambda: self.state_switchState(self.punishState))
        self.sBtn_punish.grid(row=stateStartRow+1, column=stateStartColumn+4)
        self.sBtn_punish.config(state=NORMAL)

        self.sBtn_save = Button(st_frame, text="Save State", \
            command=lambda: self.state_switchState(self.saveState))
        self.sBtn_save.grid(row=stateStartRow+1, column=stateStartColumn)
        self.sBtn_save.config(state=NORMAL)

        self.sBtn_save = Button(st_frame, text="End Session", \
            command=lambda: self.state_switchState(self.endState))
        self.sBtn_save.grid(row=stateStartRow-2, column=stateStartColumn)
        self.sBtn_save.config(state=NORMAL)

        self.sBtn_save = Button(st_frame, text="Debug", \
            command=lambda: self.debugState())
        self.sBtn_save.grid(row=stateStartRow-2, column=stateStartColumn+1)
        self.sBtn_save.config(state=NORMAL)

    def toggleStateButtons(self,tS=1,tempBut=[0]):
        if tS==1:
            for tMem in range(0,len(tempBut)):
                eval('self.s{}_button.config(state=NORMAL)'.format(tempBut[tMem]))
        elif tS==0:
            for tMem in range(0,len(tempBut)):
                eval('self.s{}_button.config(state=DISABLED)'.format(tempBut[tMem]))

    def getStateSetDiff(self):  
        aa={self.currentState}
        bb={1,2,3,4,5,6,7,8,9,10,11,12,13,14}  #todo: this should not be hand-coded
        self.outStates=list(bb-aa)

    def updateStateButtons(self):
        self.getStateSetDiff()
        self.toggleStateButtons(tS=1,tempBut=[self.currentState])
        self.toggleStateButtons(tS=0,tempBut=self.outStates)

    ##############################################################################
    ## **** These Functions Handle Creation and Deletion Of Serial Objects **** ##
    ##############################################################################

    def serial_initComObj(self):
        if self.comObjectExists==0:
            print('Opening serial port')
            # Start serial communication
            self.comObj = serial.Serial(self.comPath.get(),self.baudSelected.get()) 
            # Creating our serial object named arduinoData
            # just in case we left it in a weird state 
            # lets flip back to the init state 0
            self.comObj.write(struct.pack('>B', self.bootState))
            self.comObj.write(struct.pack('>B', self.bootState))
            self.comObj.write(struct.pack('>B', self.bootState))
            self.comObj.write(struct.pack('>B', self.bootState))
            print('connected, will read a line')
            self.serial_readData()
            print(self.sR)
            self.comObjectExists=1
            self.shouldRun=1

            # update the GUI
            self.comEntry.config(state=DISABLED)
            self.baudPick.config(state=DISABLED)
            self.createCom_button.config(state=DISABLED)
            self.start_button.config(state=NORMAL)
            self.closeComObj_button.config(state=NORMAL)
            self.debugState()
            # self.taskProbs_Button.invoke()
            # self.stateToggles_Button.invoke()
        
    def serial_closeComObj(self):
        if self.comObjectExists==1:
            if self.dataExists==1:
                self.data_saveData()
            self.comObj.write(struct.pack('>B', self.bootState))
            self.comObj.close()
            self.comObjectExists=0
            self.createCom_button.config(state=NORMAL)
            self.closeComObj_button.config(state=DISABLED)
            self.start_button.config(state=DISABLED)

    def serial_handShake(self):
        print('should be good; will take you to wait state (S1)')
        self.comObj.write(struct.pack('>B', 1))
        print('hands')
        self.state_waitForStateToUpdateOnTarget(self.currentState) #todo self.currentState right?
        print('did maint call')

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
        self.pyStatesCT = []

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
        self.pyStatesCT = []

    def data_parseData(self):

        self.arduinoTime.append(float(int(self.sR[self.stID_time])/self.timeBase))
        self.arduinoTrialTime.append(float(int(self.sR[self.stID_trialTime])/self.timeBase))

        self.posDelta.append(int(self.sR[self.stID_pos])-128)
        self.absolutePosition.append(int(self.lastPos+self.posDelta[-1]))
        self.lastPos=int(self.absolutePosition[-1])
        self.currentState=int(self.sR[self.stID_state])
        self.arStates.append(self.currentState)
        self.lickValues_a.append(int(self.sR[self.stID_lickSensor_a]))
        self.lickValues_b.append(int(self.sR[self.stID_lickSensor_b]))
        self.analysis_lickDetect()
        self.dataExists=1

    def data_saveData(self):
        self.exportArray=np.array([self.arduinoTime,self.arduinoTrialTime,self.absolutePosition,self.arStates])
        np.savetxt('{}_{}_trial_{}.csv'.\
            format(self.animalIDStr.get(),self.dateStr,self.currentTrial), self.exportArray, delimiter=",",fmt="%g")
        self.dataExists=0

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
        self.lG=plt.plot(self.arduinoTrialTime[-self.segPlot:-1],self.lickValues_a[-self.segPlot:-1],'k-')
        # self.lH=plt.plot(self.arduinoTrialTime[-self.segPlot:-1],self.detected_licks[-self.segPlot:-1],'ro')
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
            self.lD=plt.plot(self.stateDiagX[self.currentState],self.stateDiagY[self.currentState],'go',markersize=self.lrMrk)
            plt.ylim(0,10)
            plt.xlim(0,10)
            plt.title(self.currentTrial)

        plt.pause(self.pltDelay)
        self.lA.pop(0).remove()
        self.lG.pop(0).remove()
        if self.updateStateMap==1:
            self.lC.pop(0).remove()
            self.lD.pop(0).remove()
    
    def generic_InitState(self):
        print('in state init {}'.format(self.currentState))
        self.cycleCount=1
        self.stateIt=1

    def generic_StateHeader(self):
        while self.stateIt==0:
            self.generic_InitState()
        self.serial_readDataFlush()
        if self.dataAvail==1:
            self.data_parseData()

    def updatePlotCheck(self):
        self.analysis_updateLickThresholds()
        self.updatePosPlot()
        self.cycleCount=0

    ################################################################################
    ## **** User Writes Custom Callbacks That Extend Their State's Functions **** ##
    ################################################################################

    def callback_waitState(self): #1
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
                self.comObj.write(struct.pack('<B', 2))
                print('Still! ==> Out of wait')
                self.state_waitForStateToUpdateOnTarget(self.waitState)  #<--- has to be in every cond block

    def callback_initiationState(self): #2
        # if stimSwitch is less than task1's probablity then send to task #1
        t1P=0.5
        # print(float(self.sTask1_prob))
        if self.absolutePosition[-1]>self.distThr:
            if self.task_switch<=t1P:
                print('cue 1')
                self.comObj.write(struct.pack('>B', self.cue1State))
                print('moving spout; cueing stim task #1')
                self.state_waitForStateToUpdateOnTarget(self.initiateState)
            # if stimSwitch is more than task1's probablity then send to task #2
            elif self.task_switch>t1P:
                print('cue 2')
                self.comObj.write(struct.pack('>B', self.cue2State))
                print('moving spout; cueing stim task #2')
                self.state_waitForStateToUpdateOnTarget(self.initiateState)

    def callback_cue1State(self):  #todo; mov could be a func #3
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
               # print(self.outcomeSwitch<=trP)
                print('Still!')
                if self.outcomeSwitch<=0.5:
                    self.comObj.write(struct.pack('>B', 5))
                    print('will play dulcet tone')
                    self.state_waitForStateToUpdateOnTarget(3)
                # if stimSwitch is more than task1's probablity then send to task #2
                elif self.outcomeSwitch>0.5:
                    self.comObj.write(struct.pack('>B', 6))
                    print('will play ominous tone')
                    self.state_waitForStateToUpdateOnTarget(3)

    def callback_cue2State(self):  #todo; mov could be a func #4
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
                #print(self.outcomeSwitch<=trP)
                if self.outcomeSwitch<=0.5:
                    print('debug a')
                    self.comObj.write(struct.pack('>B', 6))
                    print('will play dulcet tone')
                    self.state_waitForStateToUpdateOnTarget(4)
                # if stimSwitch is more than task1's probablity then send to task #2
                elif self.outcomeSwitch>0.5:
                    print('debug b')
                    self.comObj.write(struct.pack('>B', 5))
                    print('will play ominous tone')
                    self.state_waitForStateToUpdateOnTarget(4)
    
    def callback_toneStates1(self):
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
                print('Still!')
                self.comObj.write(struct.pack('>B', 13))
                print('off to save')
                self.state_waitForStateToUpdateOnTarget(self.currentState)

    def callback_toneStates2(self):
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
                print('Still!')
                self.comObj.write(struct.pack('>B', 13))
                print('off to save')
                self.state_waitForStateToUpdateOnTarget(self.currentState)


    def callback_rewardState(self): #21
        #t1P=float(self.sTask1_prob.get())
        if self.absolutePosition[-1]>self.distThr:
            self.comObj.write(struct.pack('<B', 13))
            print('rewarding')
            self.state_waitForStateToUpdateOnTarget(self.rewardState)

    def callback_punishState(self): #23
        if self.arduinoTime[-1]-self.entryTime<self.timeOutDuration:  #todo: make this a variable
            print('TIMEOUT')
        elif self.arduinoTime[-1]-self.entryTime>=self.timeOutDuration:
            self.comObj.write(struct.pack('<B', self.saveState))
            self.state_waitForStateToUpdateOnTarget(self.punishState)

    def debugState(self):
        self.shouldRun=1
        self.currentTrial=1
        if self.currentState==self.bootState:
            self.serial_readDataFlush()
            print('should be good')
            return
        while self.currentState!=self.bootState:   
            self.serial_readDataFlush()
            if self.dataAvail==1:
                self.data_parseData()
                self.currentState=int(self.sR[self.stID_state])
                self.comObj.write(struct.pack('>B', 0))
        print('should be good')

def main(): 
    root = Tk()
    app = pyDiscrim_mainGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()