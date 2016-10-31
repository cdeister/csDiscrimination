# pyDiscrim:
# This is a python program that runs sensory discrimination tasks in a state-based manner.
# It works with microcontrolors or dac boards (conceptually). 
# It can easily be modified to suit different needs.
#
# version 1.2 (Retooled to take better advantage of arm boards; version decrment)
# 10/29/2016
# questions? --> Chris Deister --> cdeister@Bbrown.edu

# todo: find alternative to isnumeric so signed variables are handeled ok and pass lists.


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

class pyDiscrim_mainGUI:

    def __init__(self, master):
        self.master = master
        self.frame = Frame(self.master)
        master.title("pyDiscrim")
        
        # Key Initialization
        self.probsSet=0 # this gets set in a new window so we need to track if it is there

        # ------> serial stuff
        self.comPortEntry_label = Label(master, text="COM Port Location")
        self.comPortEntry_label.grid(row=0, column=0)

        self.comPath=StringVar(master)
        self.comPath.set('/dev/cu.usbmodem1411')
        self.comEntry = OptionMenu(master,self.comPath, \
            '/dev/cu.usbmodem1411','/dev/cu.usbmodem1421','/dev/cu.usbmodem2299751')
        self.comEntry.grid(row=1, column=0)
        self.comEntry.config(width=20)

        self.baudEntry_label = Label(master,text="BAUD Rate")
        self.baudEntry_label.grid(row=2, column=0)

        self.baudSelected=IntVar(master)
        self.baudSelected.set(9600)
        self.baudPick = OptionMenu(master,self.baudSelected,9600,19200)
        self.baudPick.grid(row=3, column=0)
        self.baudPick.config(width=20)

        # ------>

        self.animalIDStr_label = Label(master, text="animal id").grid(row=4,sticky=W)
        self.animalIDStr=StringVar(master)
        self.animalIDStr_entry=Entry(master,textvariable=self.animalIDStr)
        self.animalIDStr_entry.grid(row=4, column=0)
        self.animalIDStr.set('cj_dX')
        self.animalIDStr_entry.config(width=10)

        self.totalTrials_label = Label(master, text="total trials").grid(row=5,sticky=W)
        self.totalTrials=StringVar(master)
        self.totalTrials_entry=Entry(master,textvariable=self.totalTrials)
        self.totalTrials_entry.grid(row=5, column=0)
        self.totalTrials.set('100')
        self.totalTrials_entry.config(width=10)

        # session variables
        self.quit_button = Button(master, text="Exit", command=self.simpleQuit, width=10)
        self.quit_button.grid(row=20, column=2)


        self.ux_adaptThresh=StringVar(master)
        self.ux_adaptThreshToggle=Checkbutton(master, \
            text="Ad Thr?",variable=self.ux_adaptThresh)
        self.ux_adaptThreshToggle.grid(row=20, column=0)
        self.ux_adaptThreshToggle.select()

        self.lickValuesOrDeltas=StringVar(master)
        self.ux_lickValuesToggle=Checkbutton(master, \
            text="Lk Val?",variable=self.lickValuesOrDeltas)
        self.ux_lickValuesToggle.grid(row=21, column=0)
        self.ux_lickValuesToggle.select()


        self.sampPlot_label = Label(master, text="samples to plot")
        self.sampPlot_label.grid(row=21, column=2)
        self.sampsToPlot=StringVar(master)
        self.sampPlot_entry=Entry(master,width=6,textvariable=self.sampsToPlot)
        self.sampPlot_entry.grid(row=22, column=2)
        self.sampsToPlot.set('1000')

        self.lickMax_label = Label(master, text="lick max")
        self.lickMax_label.grid(row=23, column=2)
        self.lickPlotMax=StringVar(master)
        self.lickMax_entry=Entry(master,width=6,textvariable=self.lickPlotMax)
        self.lickMax_entry.grid(row=24, column=2)
        self.lickPlotMax.set('1024')

        self.lickThrA=StringVar(master)
        self.lickThresholdA_label = Label(master, text="lick a threshold")
        self.lickThresholdA_label.grid(row=23, sticky=W)
        self.lickThrA_entry=Entry(master,width=6,textvariable=self.lickThrA)
        self.lickThrA_entry.grid(row=23, column=0)
        self.lickThrA.set(100)
        self.lickThrB=StringVar(master)
        self.lickThresholdB_label = Label(master, text="lick b threshold")
        self.lickThresholdB_label.grid(row=24, sticky=W)
        self.lickThrB_entry=Entry(master,width=6,textvariable=self.lickThrB)
        self.lickThrB_entry.grid(row=24, column=0)
        self.lickThrB.set(100)


        self.createCom_button = Button(master, text="Start Serial",\
         width = 10, command=self.initComObj)
        self.createCom_button.grid(row=0, column=2)   

        self.nwButton = Button(master, text = 'Task Probs',\
         width = 10, command = self.taskProb_frame)
        self.nwButton.grid(row=1, column=2)
        self.nwButton.config(state=DISABLED)

        self.stW_Button = Button(master, text = 'State Toggles',\
         width = 10, command = self.stateToggle_frame)
        self.stW_Button.grid(row=2, column=2)
        self.stW_Button.config(state=DISABLED)

        self.start_button = Button(master, text="Start Task",\
            width = 10, command=self.runTask)
        self.start_button.grid(row=3, column=2)
        self.start_button.config(state=DISABLED)

        self.close_button = Button(master, text="Close Serial",\
            width = 10, command=self.closeComObj)
        self.close_button.grid(row=4, column=2)
        self.close_button.config(state=DISABLED)

        # init counters etc
        self.dPos=float(0)
        self.currentTrial=1
        self.currentState=0
        self.lastAbsPos=0;

        self.t1_probEntries='sTask1_prob','sTask1_target_prob','sTask1_distract_prob',\
        'sTask1_target_reward_prob','sTask1_target_punish_prob',\
        'sTask1_distract_reward_prob','sTask1_distract_punish_prob'
        self.t1_probEntriesValues=[0.5,0.5,0.5,1.0,0.0,0.0,1.0]
        self.t2_probEntries='sTask2_prob','sTask2_target_prob','sTask2_distract_prob',\
        'sTask2_target_reward_prob','sTask2_target_punish_prob',\
        'sTask2_distract_reward_prob','sTask2_distract_punish_prob'
        self.t2_probEntriesValues=[0.5,0.5,0.5,0.0,1.0,1.0,0.0]

        self.lickMinMax=[-5,10]

        ## Globals
        self.movThr=500       # in position units (The minimum ammount of movement allowed)
        self.movTimeThr=2    # in seconds (The time the mouse must be still)
        # initialization
        self.stillTime=float(0)
        self.stillLatch=0
        self.stillTimeStart=float(0)
        self.distThr=1000;  

        # session variables (user won't change)
        self.currentTrial=1
        self.currentState=0
        self.lowDelta=0
        self.stateIt=0;

        self.streamNum_header=0          #todo: this is obvious jank
        self.streamNum_time=1
        self.streamNum_trialTime=2
        self.streamNum_posDelta_positive=3
        self.streamNum_posDelta_negative=4
        self.streamNum_state=5
        self.streamNum_lickSensor_left=6
        self.streamNum_lickSensor_right=7
        self.segPlot=1000


        # # # # # # # # # # # # # # # # # # # # # # # # 
        # Functions and Dynamic Variables             #
        # # # # # # # # # # # # # # # # # # # # # # # #
        self.dateStr = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M')

        self.initPltRng=2.5
        self.pltDelay=0.00000001 
        # this can be changed, but doesn't need to be. 
        #We have to have a plot delay, but it can be tiny.
        self.stateDiagX=[1,1,3,5,5,7,7,7,7,9,9,9,9,1]
        self.stateDiagY=[3,5,5,6,4,8,6,4,2,8,6,4,2,7]
        self.smMrk=10
        self.lrMrk=20
        self.postionMin=-1000
        self.positionMax=3000
        self.lickMin=0
        self.lickMax=1000
        self.timeBase=1000000

    def taskProb_frame(self):
        #self.frame = Frame(self.master)
        tb_frame = Toplevel()
        tb_frame.title('Task Probs')
        self.tb_frame=tb_frame

        #result.geometry('1600x150')
        self.makeProbEntries_t1()
        self.makeProbEntries_t2()
        self.closeTaskProbWindowButton = Button(tb_frame, text = 'Set and Close', width = 10, command = self.taskProb_frame_close)
        self.closeTaskProbWindowButton.grid(row=8, column=1)

        # update the GUI
        self.close_button.config(state=NORMAL)
        self.comEntry.config(state=DISABLED)
        self.baudPick.config(state=DISABLED)
        self.createCom_button.config(state=NORMAL)      #button 1
        self.nwButton.config(state=NORMAL)              #button 2
        self.stW_Button.config(state=NORMAL)            #button 3

    def taskProb_frame_close(self):
        self.sTask1_prob_captured=float(self.sTask1_prob.get())
        self.sTask1_prob.set(str(self.sTask1_prob_captured))
        self.probsSet=1

    def makeProbEntries_t1(self):
        for x in range(0,len(self.t1_probEntries)):
            exec('self.{}=StringVar(self.tb_frame)'.format(self.t1_probEntries[x]))
            exec('self.{}_label = Label(self.tb_frame, text="{}")'.format(self.t1_probEntries[x],self.t1_probEntries[x]))
            exec('self.{}_entry=Entry(self.tb_frame,width=6,textvariable=self.{})'.format(self.t1_probEntries[x],self.t1_probEntries[x]))
            exec('self.{}_label.grid(row=x, column=1)'.format(self.t1_probEntries[x]))
            exec('self.{}_entry.grid(row=x, column=0)'.format(self.t1_probEntries[x]))
            exec('self.{}.set({})'.format(self.t1_probEntries[x],self.t1_probEntriesValues[x]))

    def makeProbEntries_t2(self):
        for x in range(0,len(self.t2_probEntries)):
            exec('self.{}=StringVar(self.tb_frame)'.format(self.t2_probEntries[x]))
            exec('self.{}_label = Label(self.tb_frame, text="{}")'.format(self.t2_probEntries[x],self.t2_probEntries[x]))
            exec('self.{}_entry=Entry(self.tb_frame,width=6,textvariable=self.{})'.format(self.t2_probEntries[x],self.t2_probEntries[x]))
            exec('self.{}_label.grid(row=x, column=3)'.format(self.t2_probEntries[x]))
            exec('self.{}_entry.grid(row=x, column=2)'.format(self.t2_probEntries[x]))
            exec('self.{}.set({})'.format(self.t2_probEntries[x],self.t2_probEntriesValues[x]))

    def captureEntry(self,entryString="a"):  #sTask1_prob
        print(entryString)
        #eval('self.{}_captured=float(self.{}.get())'.format(entryString,entryString))

    def stateToggle_frame(self):
        st_frame = Toplevel()
        st_frame.title('States in Task')
        self.st_frame=st_frame

        #result.geometry('1600x150')
                # ------> state update stuff
        stateStartColumn=0
        stateStartRow=4
        self.stateStartColumn=stateStartColumn
        self.stateStartRow=stateStartRow

        self.s0_button = Button(st_frame, text="S0: Boot", command=lambda: self.switchState(0))
        self.s0_button.grid(row=stateStartRow-1, column=stateStartColumn)
        self.s0_button.config(state=NORMAL)

        self.s1_button = Button(st_frame, text="S1: Wait", command=lambda: self.switchState(1))
        self.s1_button.grid(row=stateStartRow, column=stateStartColumn)
        self.s1_button.config(state=DISABLED)

        self.s2_button = Button(st_frame, text="S2: Initiate", command=lambda: self.switchState(2))
        self.s2_button.grid(row=stateStartRow, column=stateStartColumn+1)
        self.s2_button.config(state=DISABLED)

        self.s3_button = Button(st_frame, text="S3: Cue 1", command=lambda: self.switchState(3))
        self.s3_button.grid(row=stateStartRow-1, column=stateStartColumn+2)
        self.s3_button.config(state=DISABLED)

        self.s4_button = Button(st_frame, text="S4: Cue 2", command=lambda: self.switchState(4))
        self.s4_button.grid(row=stateStartRow+1, column=stateStartColumn+2)
        self.s4_button.config(state=DISABLED)

        self.s5_button = Button(st_frame, text="S3a: Stim 1", command=lambda: self.switchState(5))
        self.s5_button.grid(row=stateStartRow-2, column=stateStartColumn+3)
        self.s5_button.config(state=DISABLED)

        self.s6_button = Button(st_frame, text="S3b: Stim 2",command=lambda: self.switchState(6))
        self.s6_button.grid(row=stateStartRow-1, column=stateStartColumn+3)
        self.s6_button.config(state=DISABLED)

        self.s7_button = Button(st_frame, text="SC: Catch", command=lambda: self.switchState(7))
        self.s7_button.grid(row=stateStartRow, column=stateStartColumn+3)
        self.s7_button.config(state=DISABLED)

        self.s8_button = Button(st_frame, text="S4a: Stim 2", command=lambda: self.switchState(8))
        self.s8_button.grid(row=stateStartRow+1, column=stateStartColumn+3)
        self.s8_button.config(state=DISABLED)

        self.s9_button = Button(st_frame, text="S4b: Stim 1", command=lambda: self.switchState(9))
        self.s9_button.grid(row=stateStartRow+2, column=stateStartColumn+3)
        self.s9_button.config(state=DISABLED)

        self.s10_button = Button(st_frame, text="SR: Reward", command=lambda: self.switchState(10))
        self.s10_button.grid(row=stateStartRow-1, column=stateStartColumn+4)
        self.s10_button.config(state=DISABLED)

        self.s11_button = Button(st_frame, text="SN: Neutral", command=lambda: self.switchState(11))
        self.s11_button.grid(row=stateStartRow, column=stateStartColumn+4)
        self.s11_button.config(state=DISABLED)

        self.s12_button = Button(st_frame, text="SP: Punish", command=lambda: self.switchState(12))
        self.s12_button.grid(row=stateStartRow+1, column=stateStartColumn+4)
        self.s12_button.config(state=DISABLED)

        self.s13_button = Button(st_frame, text="SS: Saving", command=lambda: self.switchState(13))
        self.s13_button.grid(row=stateStartRow+1, column=stateStartColumn)
        self.s13_button.config(state=DISABLED)

        # self.s13_button = Button(master, text="Save/Quit", bg='red', command=lambda: self.saveQuit())
        # self.s13_button.grid(row=16, column=0)
        # self.s13_button.config(state=NORMAL)

        # update the GUI
        self.close_button.config(state=NORMAL)
        self.quit_button.config(state=DISABLED)
        self.createCom_button.config(state=NORMAL)
        self.comEntry.config(state=NORMAL)
        self.baudPick.config(state=NORMAL)
        self.nwButton.config(state=NORMAL)
        self.stW_Button.config(state=NORMAL)
        self.start_button.config(state=NORMAL)        #button 4

    def toggleStateButtons(self,tS=1,tempBut=[0]):
        if tS==1:
            for tMem in range(0,len(tempBut)):
                eval('self.s{}_button.config(state=NORMAL)'.format(tempBut[tMem]))
        elif tS==0:
            for tMem in range(0,len(tempBut)):
                eval('self.s{}_button.config(state=DISABLED)'.format(tempBut[tMem]))

    def switchState(self,selectedStateNumber):
        self.selectedStateNumber=selectedStateNumber
        print(self.selectedStateNumber)
        self.currentState=self.selectedStateNumber
        self.comObj.write(struct.pack('>B', selectedStateNumber))

    def initComObj(self):
        print('Opening serial port')
        # Start serial communication
        self.comObj = serial.Serial(self.comPath.get(), self.baudSelected.get()) #Creating our serial object named arduinoData
        # just in case we left it in a weird state lets flip back to the init state 0
        self.comObj.write(struct.pack('>B', 0)) # todo: init state should be abstracted
        print(self.baudSelected.get())  #debug
        print(type(self.comObj))
        self.readData()
        print(self.sR)

        # update the GUI
        self.close_button.config(state=NORMAL)
        self.comEntry.config(state=DISABLED)
        self.baudPick.config(state=DISABLED)
        self.createCom_button.config(state=NORMAL)      #button 1
        self.nwButton.config(state=NORMAL)              #button 2
        self.stW_Button.config(state=DISABLED)          #button 3
        self.start_button.config(state=DISABLED)        #button 4

        self.nwButton.invoke()
        self.stW_Button.invoke()
        
    def closeComObj(self):
        self.saveData() 
        self.comObj.write(struct.pack('>B', 0)) #todo: abstract init state
        self.comObj.close()
        exit()

    def simpleQuit(self):  #todo: delete this
        print('audi 5k')    #debug
        exit()

    def saveQuit(self):
        self.comObj.write(struct.pack('>B', 0))
        self.saveData() 
        self.comObj.close()
        exit()

    def initTaskProbs(self):
        self.sTask1_prob.get()
        self.sTask1_target_prob.get()
        self.sTask1_distract_prob.get()
        self.sTask1_target_reward_prob.get()
        self.sTask1_target_punish_prob.get()
        self.sTask1_distract_reward_prob.get()
        self.sTask1_distract_punish_prob.get()
        self.sTask2_prob.get()
        self.sTask2_target_prob.get()
        self.sTask2_distract_prob.get()
        self.sTask2_target_reward_prob.get()
        self.sTask2_target_punish_prob.get()
        self.sTask2_distract_reward_prob.get()
        self.sTask2_distract_punish_prob.get()

    def makeContainers(self):
        self.arStates=[]          
        self.arduinoTime=[]
        self.arduinoTrialTime=[]  
        self.posSensA_vals=[]
        self.posSensB_vals=[]  
        self.absolutePosition=[]      
        self.lickValues_a=[]
        self.lickValues_b=[]
        self.detectedLicks_a=[]
        self.detectedLicks_b=[]
        self.lastAbsPos=0

    def readData(self):
        self.sR=self.comObj.readline().strip().decode()
        self.sR=self.sR.split(',')
        if self.sR[self.streamNum_header]=='data' and str.isnumeric(self.sR[1])==1 and str.isnumeric(self.sR[3])==1 and str.isnumeric(self.sR[4])==1 and str.isnumeric(self.sR[5])==1 and str.isnumeric(self.sR[6])==1:
            self.dataAvail=1
        elif self.sR[self.streamNum_header]!='data' or str.isnumeric(self.sR[1])!=1  or str.isnumeric(self.sR[3])!=1 or str.isnumeric(self.sR[4])!=1 or str.isnumeric(self.sR[5])!=1 or str.isnumeric(self.sR[6])!=1:
            self.dataAvail=0

    def readDataFlush(self):
        self.comObj.flush()
        self.readData()

    def parseData(self):
        # self.streamNum_header=0          #todo: this is obvious jank
        # self.streamNum_time=1
        # self.streamNum_trialTime=2
        # self.streamNum_posDelta_positive=3
        # self.streamNum_posDelta_negative=4
        # self.streamNum_state=5
        # self.streamNum_lickSensor_left=6
        # self.streamNum_lickSensor_right=7

        self.arduinoTime.append(float(int(self.sR[self.streamNum_time])/self.timeBase))
        self.arduinoTrialTime.append(float(int(self.sR[self.streamNum_trialTime])/self.timeBase))
        #print('parsed time vars') #debug

        self.posSensA_vals.append(int(self.sR[self.streamNum_posDelta_positive]))
        self.posSensB_vals.append(int(self.sR[self.streamNum_posDelta_negative]))
        #print('parsed pos vars') #debug

        self.currentState=int(self.sR[self.streamNum_state])
        self.arStates.append(self.currentState)  #todo: wtf?
        #print('parsed state vars') #debug

        self.lickValues_a.append(int(self.sR[self.streamNum_lickSensor_left]))
        self.lickValues_b.append(int(self.sR[self.streamNum_lickSensor_right]))
        #print('parsed lick vars') #debug

        self.absolutePosition.append(0)
        self.lastAbsPos=self.absolutePosition[-1]
        #print('computed abs pos vars') #debug
        #self.lastAbsPos+(self.posSensA_vals[-1]-self.posSensB_vals[-1])

        self.lickDetect()
        #print('did lick stuff') #debug

    def cleanContainers(self):
        self.arStates=[]          
        self.arduinoTime=[]
        self.arduinoTrialTime=[]  
        self.posSensA_vals=[]
        self.posSensB_vals=[]  
        self.absolutePosition=[]      
        self.lickValues_a=[]
        self.lickValues_b=[]
        self.detectedLicks_a=[]
        self.detectedLicks_b=[]
        self.lastAbsPos=0

    def updateLickThresholds(self):   #todo: I think the asignment conflicts now because of the graph
        if self.ux_adaptThresh.get()==1:
            print(int(self.lickThr))
            tA=np.abs(np.array(self.lickDeltas))
            print(int(np.percentile(aaa[np.where(aaa != 0)[0]],75)))
            self.lickThr.set(str(np.percentile(tA[np.where(tA != 0)[0]],75)))
            self.lickMinMax=[min(self.lickValues),max(self.lickValues)]

    def lickDetect(self):
        if self.lickValues_a[-1]>int(self.lickThrA.get()):
            self.detectedLicks_a.append(1)
        elif self.lickValues_a[-1]<=int(self.lickThrA.get()):
            self.detectedLicks_a.append(0)
        if self.lickValues_b[-1]>int(self.lickThrB.get()):
            self.detectedLicks_b.append(1)
        elif self.lickValues_b[-1]<=int(self.lickThrB.get()):
            self.detectedLicks_b.append(0)

    def updatePosPlot(self): 
        if len(self.arduinoTrialTime)>2:
            self.cTD=self.arduinoTrialTime[-1]-self.arduinoTrialTime[-2]
            self.tTP=self.segPlot*self.cTD
        self.segPlot=int(self.sampsToPlot.get())    #=int(self.sampsToPlot.get())
        int(self.sampsToPlot.get())

        plt.subplot(2,2,1)
        self.lA=plt.plot(self.arduinoTrialTime[-self.segPlot:-1],self.absolutePosition[-self.segPlot:-1],'k-')
        plt.ylim(-1024,1024)
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
        #plt.title(int(1000000*np.mean(np.diff(np.array(self.arduinoTrialTime[-self.segPlot:-1])))))

        plt.subplot(2,2,2)
        self.lC=plt.plot(self.stateDiagX,self.stateDiagY,'ro',markersize=self.smMrk)
        self.lD=plt.plot(self.stateDiagX[self.currentState],self.stateDiagY[self.currentState],'go',markersize=self.lrMrk)
        plt.ylim(0,10)
        plt.xlim(0,10)
        plt.title(self.currentTrial)

        plt.pause(self.pltDelay)
        self.lA.pop(0).remove()
        self.lC.pop(0).remove()
        self.lD.pop(0).remove()
        self.lG.pop(0).remove()

    def handShake(self):
        print('should be good; will take you to wait state (S1)')
        self.comObj.write(struct.pack('>B', 1))
        print('hands')
        self.waitForStateToUpdateOnTarget(self.currentState) #todo self.currentState right?
        print('did maint call')

    def generic_StateHeader(self):
        while self.stateIt==0:
            self.generic_InitState()
        self.readData()
        if self.dataAvail==1:
            #print('bout to parse') #debug
            self.parseData()
            #print('parsed that shit') # debug

    def generic_InitState(self):
        print('in state init {}'.format(self.currentState))
        self.cycleCount=1
        self.stateIt=1

    def updatePlotCheck(self):
        self.updateLickThresholds()
        self.updatePosPlot()
        self.cycleCount=0

    def conditionBlock_s1(self):
        if self.arduinoTime[-1]-self.entryTime>2:  #todo: make this a variable
            self.dPos=abs(self.posSensA_vals[-1]-self.posSensA_vals[-2])
            
            if self.dPos>self.movThr and self.stillLatch==1:
                self.stillLatch=0

            if self.dPos<=self.movThr and self.stillLatch==0:
                self.stillTimeStart=self.arduinoTime[-1]
                self.stillLatch=1

            if self.dPos<self.movThr and self.stillLatch==1:
                self.stillTime=self.arduinoTime[-1]-self.stillTimeStart

            if self.stillLatch==1 and self.stillTime>1:
                self.comObj.write(struct.pack('>B', 2))
                print('Still! ==> Out of wait')
                self.waitForStateToUpdateOnTarget(self.currentState)  #<--- has to be in every cond block

    def conditionBlock_s2(self):

        self.dPos=self.posSensA_vals[-1]-self.posSensA_vals[-2]
        t1P=float(self.sTask1_prob.get())
        if self.posSensA_vals[-1]>self.distThr and self.distSwitch==0:
            self.distSwitch=1
            print('moved enough')
        if abs(self.posSensA_vals[-1])<=100 and self.distSwitch==1:
            if self.task_switch<=t1P:
                print('t1')
                self.comObj.write(struct.pack('>B', 3))
                print('moving spout; cueing stim task #1')
                self.waitForStateToUpdateOnTarget(2)
            # if stimSwitch is more than task1's probablity then send to task #2
            elif self.task_switch>t1P:
                print('t2')
                self.comObj.write(struct.pack('>B', 4))
                print('moving spout; cueing stim task #2')
                self.waitForStateToUpdateOnTarget(2)

    def conditionBlock_s3(self):  #todo; mov could be a func
        trP=float(self.sTask1_target_prob.get())
        if self.arduinoTime[-1]-self.entryTime>4:
            self.dPos=abs(self.posSensA_vals[-1]-self.posSensA_vals[-2])
            if self.dPos>self.movThr and self.stillLatch==1:
                self.stillLatch=0
            if self.dPos<=self.movThr and self.stillLatch==0:
                self.stillTimeStart=self.arduinoTime[-1]
                self.stillLatch=1
            if self.dPos<=self.movThr and self.stillLatch==1:
                self.stillTime=self.arduinoTime[-1]-self.stillTimeStart
            if self.stillLatch==1 and self.stillTime>1:
                print(self.outcomeSwitch<=trP)
                print('Still!')
                if self.outcomeSwitch<=trP:
                    self.comObj.write(struct.pack('>B', 5))
                    print('will play dulcet tone')
                    self.waitForStateToUpdateOnTarget(3)
                # if stimSwitch is more than task1's probablity then send to task #2
                elif self.outcomeSwitch>trP:
                    self.comObj.write(struct.pack('>B', 6))
                    print('will play ominous tone')
                    self.waitForStateToUpdateOnTarget(3)

    def conditionBlock_s4(self):  #todo; mov could be a func
        trP=float(self.sTask2_target_prob.get())
        if self.arduinoTime[-1]-self.entryTime>4:
            self.dPos=abs(self.posSensA_vals[-1]-self.posSensA_vals[-2])
            if self.dPos>self.movThr and self.stillLatch==1:
                self.stillLatch=0
            if self.dPos<=self.movThr and self.stillLatch==0:
                self.stillTimeStart=self.arduinoTime[-1]
                self.stillLatch=1
            if self.dPos<=self.movThr and self.stillLatch==1:
                self.stillTime=self.arduinoTime[-1]-self.stillTimeStart
            if self.stillLatch==1 and self.stillTime>1:
                print('result={}'.format(self.outcomeSwitch<=trP))
                print('Still!')
                print(self.outcomeSwitch<=trP)
                if self.outcomeSwitch<=trP:
                    print('debug a')
                    self.comObj.write(struct.pack('>B', 6))
                    print('will play dulcet tone')
                    self.waitForStateToUpdateOnTarget(4)
                # if stimSwitch is more than task1's probablity then send to task #2
                elif self.outcomeSwitch>trP:
                    print('debug b')
                    self.comObj.write(struct.pack('>B', 5))
                    print('will play ominous tone')
                    self.waitForStateToUpdateOnTarget(4)
    
    def conditionBlock_tones(self):
        if self.arduinoTime[-1]-self.entryTime>6:
            print('Done With Tone.')
            self.comObj.write(struct.pack('>B', 13))
            print('off to save')
            self.waitForStateToUpdateOnTarget(self.currentState)

    def saveData(self):
        self.exportArray=np.array([self.arduinoTime,self.arduinoTrialTime,self.arStates,self.absolutePosition,\
            self.posSensA_vals,self.posSensB_vals,self.detectedLicks_a,self.detectedLicks_b])
        np.savetxt('aad_{}.csv'.format(self.currentTrial), self.exportArray, delimiter=",",fmt="%f")

        # self.arStates=[]          
        # self.arduinoTime=[]
        # self.arduinoTrialTime=[]  
        # self.posSensA_vals=[]
        # self.posSensB_vals=[]  
        # self.absolutePosition=[]      
        # self.lickValues_a=[]
        # self.lickValues_b=[]
        # self.detectedLicks_a=[]
        # self.detectedLicks_b=[]
        # self.lastAbsPos=0

    def getStateSetDiff(self):
        aa={self.currentState}
        bb={1,2,3,4,5,6,7,8,9,10,11,12,13}  #todo: this should not be hand-coded
        self.outStates=list(bb-aa)

    def updateStateButtons(self):
        self.getStateSetDiff()
        self.toggleStateButtons(tS=1,tempBut=[self.currentState])
        self.toggleStateButtons(tS=0,tempBut=self.outStates)

    def waitForStateToUpdateOnTarget(self,maintState): 
        self.maintState=maintState
        while self.currentState==self.maintState:      
            self.stateIt=0  # will go away todo
            self.readDataFlush()
            if self.dataAvail==1:
                self.parseData()
                self.currentState=int(self.sR[self.streamNum_state])

    def runTask(self):
        self.makeContainers()
        #self.initTaskProbs()

        # plotting variables
        self.uiUpdateDelta=200  # 200 is good for 1kHz; 400 is ok for 2kHz; 
        
        # Start the task (will iterate through trials)
        while self.currentTrial<=int(self.totalTrials.get()):
            self.initTime=0  # debug
            try:
                #S0 -----> hand shake (initialization state)
                if self.currentState==0:
                    td=[float(0)]  #debug #document: inset inits before the while!
                    self.updateStateButtons()
                    print('in state 0')
                    while self.currentState==0:
                        self.generic_StateHeader() # gets data
                        if self.dataAvail==1:
                            td.append(float(self.arduinoTime[-1]-self.initTime)) 
                            self.initTime=self.arduinoTime[-1]
                            if len(td)>300: #todo: bigtime jank here
                                if np.var(td[-98:-1])<0.01:
                                    print('cond fine') 
                                    self.handShake()  

                #S1 -----> trial wait state
                elif self.currentState==1:
                    print('in s1')
                    self.entryTime=self.arduinoTime[-1]
                    self.updateStateButtons()
                    while self.currentState==1:
                        self.generic_StateHeader()
                        if self.dataAvail==1:
                            if int(self.cycleCount) % int(self.uiUpdateDelta)==0:
                                self.updatePlotCheck()
                            self.conditionBlock_s1()
                            self.cycleCount=self.cycleCount+1;

                #S2 -----> trial initiation state
                elif self.currentState==2:
                    self.distSwitch=0
                    self.updateStateButtons()
                    self.task_switch=random.random()
                    print('in s2')
                    while self.currentState==2:
                        self.generic_StateHeader() 
                        if self.dataAvail==1: # todo: in all states
                            if int(self.cycleCount) % int(self.uiUpdateDelta)==0: 
                            # todo: in all states
                                self.updatePlotCheck()   # todo: in all states
                            self.conditionBlock_s2()  # condition blocks are unique (always custom)
                            self.cycleCount=self.cycleCount+1; # todo: in all states (just for ui)

                #S3 -----> stim task #1 cue
                elif self.currentState==3:
                    print('in s3')
                    self.updateStateButtons()
                    self.entryTime=self.arduinoTime[-1]
                    self.outcomeSwitch=random.random() # debug
                    while self.currentState==3:
                        self.generic_StateHeader()
                        if self.dataAvail==1:
                            if int(self.cycleCount) % int(self.uiUpdateDelta)==0:
                                self.updatePlotCheck()
                            self.conditionBlock_s3()
                            self.cycleCount=self.cycleCount+1;

                #S4 -----> stim task #2 cue
                elif self.currentState==4:
                    self.updateStateButtons()
                    self.outcomeSwitch=random.random() # debug
                    self.entryTime=self.arduinoTime[-1]
                    while self.currentState==4:
                        self.generic_StateHeader()
                        if self.dataAvail==1:
                            if int(self.cycleCount) % int(self.uiUpdateDelta)==0:
                                self.updatePlotCheck()
                            self.conditionBlock_s4()
                            self.cycleCount=self.cycleCount+1;

                #S5 -----> pos tone
                elif self.currentState==5:
                    self.updateStateButtons()
                    self.entryTime=self.arduinoTime[-1]
                    while self.currentState==5:
                        self.generic_StateHeader()
                        if self.dataAvail==1:
                            if int(self.cycleCount) % int(self.uiUpdateDelta)==0:
                                self.updatePlotCheck()
                            self.conditionBlock_tones()
                            self.cycleCount=self.cycleCount+1;

                #S6 -----> neg tone
                elif self.currentState==6:
                    self.updateStateButtons()
                    self.entryTime=self.arduinoTime[-1]
                    while self.currentState==6:
                        self.generic_StateHeader()
                        if self.dataAvail==1:
                            if int(self.cycleCount) % int(self.uiUpdateDelta)==0:
                                self.updatePlotCheck()
                            self.conditionBlock_tones()
                            self.cycleCount=self.cycleCount+1;

                # ----------------- (S13: save state)
                elif self.currentState==13:
                    print('in state 13; saving your bacon') # debug
                    self.saveData()                    # clean up plot data (memory managment)
                    self.cleanContainers()
                    self.currentTrial=self.currentTrial+1
                    print('trial done')
                    self.comObj.write(struct.pack('>B', 1)) #todo: abstract wait
                    self.waitForStateToUpdateOnTarget(13)         
            except:
                print(self.dPos)
                print('EXCEPTION: peace out bitches')
                print('last trial = {} and the last state was {}. \
                    I will try to save last trial ...'.format(self.currentTrial,self.currentState))
                self.saveData() 
                self.comObj.write(struct.pack('>B', 0))
                print('save was a success; now I will close com port and quit')
                self.comObj.close()
                exit()

        print('NORMAL: peace out')
        print('I completed {} trials.'.format(self.currentTrial-1))
        self.comObj.write(struct.pack('>B', 0))  #todo: abstract reset state
        self.comObj.close()
        exit()

def main(): 
    root = Tk()
    app = pyDiscrim_mainGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()