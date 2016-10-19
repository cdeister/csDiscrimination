# pyDiscrim:
# This is a python program that runs sensory discrimination tasks in a state-based manner.
# It works with microcontrolors or dac boards (conceptually). It can easily be modified to suit different needs.
#
# version 3.0 (1st GUI; Start Object Oriented Reorg)
# 10/18/2016
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
        master.title("pyDiscrim")

        self.label = Label(master, text="set pyDiscrim params")
        self.label.grid(row=0, column=0)

        self.baudSelected=IntVar(master)
        self.baudSelected.set(9600)
        self.baudPick = OptionMenu(master, self.baudSelected, 9600,987)
        self.baudPick.grid(row=1, column=0)

        self.comPath=StringVar(master)
        self.comEntry = Entry(master,width=20,textvariable=self.comPath)
        self.comEntry.grid(row=2, column=0)
        self.comPath.set('/dev/cu.usbmodem1411')

        self.createCom_button = Button(master, text="Start Serial", command=self.initComObj)
        self.createCom_button.grid(row=3, column=0)

        self.close_button = Button(master, text="Close Serial", command=self.closeComObj)
        self.close_button.grid(row=4, column=0)
        self.close_button.config(state=DISABLED)

        self.s0_button = Button(master, text="S0: Boot", command=lambda: self.switchState(0))
        self.s0_button.grid(row=0, column=1)
        self.s0_button.config(state=DISABLED)

        self.s1_button = Button(master, text="S1: Wait", command=lambda: self.switchState(1))
        self.s1_button.grid(row=1, column=1)
        self.s1_button.config(state=DISABLED)

        self.s2_button = Button(master, text="S2: Initiate", command=lambda: self.switchState(2))
        self.s2_button.grid(row=2, column=1)
        self.s2_button.config(state=DISABLED)

        self.s3_button = Button(master, text="S3: Cue", command=lambda: self.switchState(3))
        self.s3_button.grid(row=3, column=1)
        self.s3_button.config(state=DISABLED)

        self.s4_button = Button(master, text="S4", command=lambda: self.switchState(4))
        self.s4_button.grid(row=0, column=2)
        self.s4_button.config(state=DISABLED)

        self.s5_button = Button(master, text="S5", command=lambda: self.switchState(5))
        self.s5_button.grid(row=1, column=2)
        self.s5_button.config(state=DISABLED)

        self.s6_button = Button(master, text="S6", command=lambda: self.switchState(6))
        self.s6_button.grid(row=2, column=2)
        self.s6_button.config(state=DISABLED)

        self.s7_button = Button(master, text="S7", bg='red', command=lambda: self.switchState(7))
        self.s7_button.grid(row=3, column=2)
        self.s7_button.config(state=DISABLED)

        self.quit_button = Button(master, text="Exit", command=self.simpleQuit)
        self.quit_button.grid(row=5, column=0)

        self.start_button = Button(master, text="Start", command=self.runTask)
        self.start_button.grid(row=5, column=0)

        self.ttlabel = Label(master, text="total trials")
        self.ttlabel.grid(row=4, column=2)
        self.totalTrials=StringVar(master)
        self.totalTrialsEntry=Entry(master,width=6,textvariable=self.totalTrials)
        self.totalTrialsEntry.grid(row=4, column=1)
        self.totalTrials.set('100')

        self.aString_label = Label(master, text="animal id")
        self.aString_label.grid(row=5, column=2)
        self.aString=StringVar(master)
        self.aStringEntry=Entry(master,width=6,textvariable=self.aString)
        self.aStringEntry.grid(row=5, column=1)
        self.aString.set('cj_dX')

        taskStartRow=8
        taskStartCol=2
        # define task 1 params
        self.sTask1_prob_label = Label(master, text="sensory task 1 prob.")
        self.sTask1_prob_label.grid(row=taskStartRow, column=taskStartCol)
        self.sTask1_prob=StringVar(master)
        self.sTask1_prob_entry=Entry(master,width=6,textvariable=self.sTask1_prob)
        self.sTask1_prob_entry.grid(row=taskStartRow, column=taskStartCol-1)
        self.sTask1_prob.set('0.5')

        self.sTask1_target_prob_label = Label(master, text="task 1: target prob.")
        self.sTask1_target_prob_label.grid(row=taskStartRow+1, column=taskStartCol)
        self.sTask1_target_prob=StringVar(master)
        self.sTask1_target_prob_entry=Entry(master,width=6,textvariable=self.sTask1_target_prob)
        self.sTask1_target_prob_entry.grid(row=taskStartRow+1, column=taskStartCol-1)
        self.sTask1_target_prob.set('0.5')

        self.sTask1_distract_prob_label = Label(master, text="task 1: distract prob.")
        self.sTask1_distract_prob_label.grid(row=taskStartRow+2, column=taskStartCol)
        self.sTask1_distract_prob=StringVar(master)
        self.sTask1_distract_prob_entry=Entry(master,width=6,textvariable=self.sTask1_distract_prob)
        self.sTask1_distract_prob_entry.grid(row=taskStartRow+2, column=taskStartCol-1)
        self.sTask1_distract_prob.set('0.5')

        self.sTask1_target_reward_prob_label = Label(master, text="task 1: target reward prob.")
        self.sTask1_target_reward_prob_label.grid(row=taskStartRow+3, column=taskStartCol)
        self.sTask1_target_reward_prob=StringVar(master)
        self.sTask1_target_reward_prob_entry=Entry(master,width=6,textvariable=self.sTask1_target_reward_prob)
        self.sTask1_target_reward_prob_entry.grid(row=taskStartRow+3, column=taskStartCol-1)
        self.sTask1_target_reward_prob.set('1.0')

        self.sTask1_target_punish_prob_label = Label(master, text="task 1: target punish prob.")
        self.sTask1_target_punish_prob_label.grid(row=taskStartRow+4, column=taskStartCol)
        self.sTask1_target_punish_prob=StringVar(master)
        self.sTask1_target_punish_prob_entry=Entry(master,width=6,textvariable=self.sTask1_target_punish_prob)
        self.sTask1_target_punish_prob_entry.grid(row=taskStartRow+4, column=taskStartCol-1)
        self.sTask1_target_punish_prob.set('0.0')

        self.sTask1_distract_reward_prob_label = Label(master, text="task 1: distract reward prob.")
        self.sTask1_distract_reward_prob_label.grid(row=taskStartRow+5, column=taskStartCol)
        self.sTask1_distract_reward_prob=StringVar(master)
        self.sTask1_distract_reward_prob_entry=Entry(master,width=6,textvariable=self.sTask1_distract_reward_prob)
        self.sTask1_distract_reward_prob_entry.grid(row=taskStartRow+5, column=taskStartCol-1)
        self.sTask1_distract_reward_prob.set('0.0')


        self.sTask1_distract_punish_prob_label = Label(master, text="task 1: target punish prob.")
        self.sTask1_distract_punish_prob_label.grid(row=taskStartRow+6, column=taskStartCol)
        self.sTask1_distract_punish_prob=StringVar(master)
        self.sTask1_distract_punish_prob_entry=Entry(master,width=6,textvariable=self.sTask1_distract_punish_prob)
        self.sTask1_distract_punish_prob_entry.grid(row=taskStartRow+6, column=taskStartCol-1)
        self.sTask1_distract_punish_prob.set('1.0')


        # define task 2 params
        self.sTask2_prob_label = Label(master, text="sensory task 1 prob.")
        self.sTask2_prob_label.grid(row=taskStartRow, column=taskStartCol+2)
        self.sTask2_prob=StringVar(master)
        self.sTask2_prob_entry=Entry(master,width=6,textvariable=self.sTask2_prob)
        self.sTask2_prob_entry.grid(row=taskStartRow, column=taskStartCol+1)
        self.sTask2_prob.set('0.5')

        self.sTask2_target_prob_label = Label(master, text="task 1: target prob.")
        self.sTask2_target_prob_label.grid(row=taskStartRow+1, column=taskStartCol+2)
        self.sTask2_target_prob=StringVar(master)
        self.sTask2_target_prob_entry=Entry(master,width=6,textvariable=self.sTask2_target_prob)
        self.sTask2_target_prob_entry.grid(row=taskStartRow+1, column=taskStartCol+1)
        self.sTask2_target_prob.set('0.5')

        self.sTask2_distract_prob_label = Label(master, text="task 1: distract prob.")
        self.sTask2_distract_prob_label.grid(row=taskStartRow+2, column=taskStartCol+2)
        self.sTask2_distract_prob=StringVar(master)
        self.sTask2_distract_prob_entry=Entry(master,width=6,textvariable=self.sTask2_distract_prob)
        self.sTask2_distract_prob_entry.grid(row=taskStartRow+2, column=taskStartCol+1)
        self.sTask2_distract_prob.set('0.5')

        self.sTask2_target_reward_prob_label = Label(master, text="task 1: target reward prob.")
        self.sTask2_target_reward_prob_label.grid(row=taskStartRow+3, column=taskStartCol+2)
        self.sTask2_target_reward_prob=StringVar(master)
        self.sTask2_target_reward_prob_entry=Entry(master,width=6,textvariable=self.sTask2_target_reward_prob)
        self.sTask2_target_reward_prob_entry.grid(row=taskStartRow+3, column=taskStartCol+1)
        self.sTask2_target_reward_prob.set('1.0')

        self.sTask2_target_punish_prob_label = Label(master, text="task 1: target punish prob.")
        self.sTask2_target_punish_prob_label.grid(row=taskStartRow+4, column=taskStartCol+2)
        self.sTask2_target_punish_prob=StringVar(master)
        self.sTask2_target_punish_prob_entry=Entry(master,width=6,textvariable=self.sTask2_target_punish_prob)
        self.sTask2_target_punish_prob_entry.grid(row=taskStartRow+4, column=taskStartCol+1)
        self.sTask2_target_punish_prob.set('0.0')

        self.sTask2_distract_reward_prob_label = Label(master, text="task 1: distract reward prob.")
        self.sTask2_distract_reward_prob_label.grid(row=taskStartRow+5, column=taskStartCol+2)
        self.sTask2_distract_reward_prob=StringVar(master)
        self.sTask2_distract_reward_prob_entry=Entry(master,width=6,textvariable=self.sTask2_distract_reward_prob)
        self.sTask2_distract_reward_prob_entry.grid(row=taskStartRow+5, column=taskStartCol+1)
        self.sTask2_distract_reward_prob.set('0.0')


        self.sTask2_distract_punish_prob_label = Label(master, text="task 1: target punish prob.")
        self.sTask2_distract_punish_prob_label.grid(row=taskStartRow+6, column=taskStartCol+2)
        self.sTask2_distract_punish_prob=StringVar(master)
        self.sTask2_distract_punish_prob_entry=Entry(master,width=6,textvariable=self.sTask2_distract_punish_prob)
        self.sTask2_distract_punish_prob_entry.grid(row=taskStartRow+6, column=taskStartCol+1)
        self.sTask2_distract_punish_prob.set('1.0')

        self.s13_button = Button(master, text="Save/Quit", bg='red', command=self.saveQuit)
        self.s13_button.grid(row=7, column=0)
        self.s13_button.config(state=DISABLED)

        # init counters etc
        self.dPos=float(0)
        self.currentTrial=1
        self.currentState=0

        self.lickThr=[12,12]            #todo: ugh look away
        self.lickMinMax=[-5,10]

        ## Globals
        self.movThr=40       # in position units (The minimum ammount of movement allowed)
        self.movTimeThr=2    # in seconds (The time the mouse must be still)
        # initialization
        self.stillTime=float(0)
        self.stillLatch=0
        self.stillTimeStart=float(0)
        self.distThr=1000;  # This is the distance the mouse needs to move to initiate a stimulus trial.



        # session variables (user won't change)
        self.currentTrial=1
        self.currentState=0
        self.lowDelta=0
        self.stateIt=0;

        self.streamNum_header=0          #todo: this is obvious jank
        self.streamNum_time=1
        self.streamNum_position=2
        self.streamNum_state=3
        self.streamNum_lickSensor=4
        self.streamNum_lickDeriv=5
        self.streamNum_trialTime=6


        self.tt1=[float(1),float(2)]

        # # # # # # # # # # # # # # # # # # # # # # # # 
        # Functions and Dynamic Variables             #
        # # # # # # # # # # # # # # # # # # # # # # # #
        self.dateStr = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M')

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
        self.quit_button.config(state=DISABLED)
        self.createCom_button.config(state=NORMAL)
        self.comEntry.config(state=NORMAL)
        self.baudPick.config(state=NORMAL)
        self.s0_button.config(state=NORMAL)
        self.s1_button.config(state=NORMAL)
        self.s2_button.config(state=NORMAL)
        self.s3_button.config(state=NORMAL)
        self.s4_button.config(state=NORMAL)
        self.s5_button.config(state=NORMAL)
        self.s6_button.config(state=NORMAL)
        self.s7_button.config(state=NORMAL)
        self.s13_button.config(state=NORMAL)

    def switchState(self,selectedStateNumber):
        self.selectedStateNumber=selectedStateNumber
        print(self.selectedStateNumber)
        self.currentState=self.selectedStateNumber
        self.comObj.write(struct.pack('>B', selectedStateNumber))

    def closeComObj(self):
        self.comObj.write(struct.pack('>B', 0)) #todo: abstract init state
        self.comObj.close()
        exit()

    def simpleQuit(self):  #todo: finish this
        print('audi 5k')    #debug
        exit()

    def saveQuit(self):
        self.comObj.write(struct.pack('>B', 0))
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

        self.sTask2_prob=1-self.sTask1_prob.get()
        
        self.sTask2_target_prob.get()
        self.sTask2_distract_prob.get()
        
        self.sTask2_target_reward_prob.get()
        self.sTask2_target_punish_prob.get()
        
        self.sTask2_distract_reward_prob.get()
        self.sTask2_distract_punish_prob.get()


    def makeContainers(self):           #todo: this should be part of data class
        self.positions=[]            # This is the x-position of an optical mouse attached to a USB host shield
        self.arStates=[]             # Store the state the arduino thinks it is in.
        self.arduinoTime=[]          # This is the time as reported by the arduino, which resets every trial. 
        self.lickValues=[]
        self.lickDeltas=[]
        self.arduinoTrialTime=[]
        self.detected_licks=[]

    def cleanContainers(self):           #todo: this should be part of data class
        self.positions=[]            # This is the x-position of an optical mouse attached to a USB host shield
        self.arStates=[]             # Store the state the arduino thinks it is in.
        self.arduinoTime=[]          # This is the time as reported by the arduino, which resets every trial. 
        self.lickValues=[]
        self.lickDeltas=[]
        self.arduinoTrialTime=[]
        self.detected_licks=[]

    def updateLickThresholds(self):
        tA=np.abs(np.array(self.lickDeltas))
        self.lickThr = np.percentile(tA[np.where(tA != 0)[0]],[75,95])
        self.lickMinMax=[min(self.lickDeltas),max(self.lickDeltas)]

    def lickDetect(self):
        if self.lickDeltas[-1]>self.lickThr[0]:
            self.detected_licks.append(2)
        elif self.lickDeltas[-1]<=self.lickThr[0]:
            self.detected_licks.append(0)

    def updatePosPlot(self): # todo: organize this better (should be its own class I think)
        self.segPlot=100
        self.initPltRng=2.5
        self.pltDelay=0.0000001 # this can be changed, but doesn't need to be. We have to have a plot delay, but it can be tiny.
        self.stateDiagX=[1,1,3,5,5,7,7,7,7,9,9,9,9,1]
        self.stateDiagY=[3,5,5,6,4,8,6,4,2,8,6,4,2,7]
        self.smMrk=10
        self.lrMrk=20
        self.postionMin=-1000;
        self.positionMax=3000;
        self.lickMin=0
        self.lickMax=30

        plt.subplot(2,2,1)
        self.lA=plt.plot(self.arduinoTrialTime[-self.segPlot:-1],self.positions[-self.segPlot:-1],'k-')
        plt.ylim(-500,2000)
        if len(self.arduinoTrialTime)>self.segPlot:
            plt.xlim(self.arduinoTrialTime[-self.segPlot],self.arduinoTrialTime[-1])
        elif len(self.arduinoTrialTime)<=self.segPlot+1:
            plt.xlim(0,self.initPltRng)
        plt.ylabel('position')
        plt.xlabel('time since trial start (sec)')


        # plt.subplot(2,2,3)
        # print('want to make lg')
        # self.lG=plt.plot(self.arduinoTrialTime[-self.segPlot:-1],self.detected_licks[-self.segPlot:-1],'b-')
        # print('made lg')
        # plt.ylim(-1,3)
        # if len(self.arduinoTrialTime)>self.segPlot:
        #     plt.xlim(self.arduinoTrialTime[-self.segPlot],self.arduinoTrialTime[-1])
        # elif len(self.arduinoTrialTime)<=self.segPlot+1:
        #     plt.xlim(0,self.initPltRng)
        # plt.ylabel('licks (binary)')
        # plt.xlabel('time since trial start (sec)')

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
        # self.lG.pop(0).remove()


    def readData(self):
        self.sR=self.comObj.readline().strip().decode()
        self.sR=self.sR.split(',')
        if self.sR[self.streamNum_header]=='data' and str.isnumeric(self.sR[1])==1 and str.isnumeric(self.sR[2])==1 and str.isnumeric(self.sR[3])==1 and str.isnumeric(self.sR[4])==1 and str.isnumeric(self.sR[5])==1:
            self.dataAvail=1  #todo: i tink this affects negative numbers
        elif self.sR[self.streamNum_header]!='data' or str.isnumeric(self.sR[1])!=1 or str.isnumeric(self.sR[2])!=1 or str.isnumeric(self.sR[3])!=1 or str.isnumeric(self.sR[4])!=1 or str.isnumeric(self.sR[5])!=1:
            self.dataAvail=0

    def readDataFlush(self):
        self.comObj.flush()
        self.readData()

    def parseData(self):
        self.arduinoTime.append(float(int(self.sR[self.streamNum_time])/1000))  
        self.positions.append(float(self.sR[self.streamNum_position]))
        self.currentState=int(self.sR[self.streamNum_state])
        self.arStates.append(self.currentState)
        self.lickValues.append(int(self.sR[self.streamNum_lickSensor]))
        self.lickDeltas.append(int(self.sR[self.streamNum_lickDeriv]))
        self.arduinoTrialTime.append(float(int(self.sR[self.streamNum_trialTime])/1000))

    def generic_StateHeader(self):
        # general state code
        #print('stateIt={}'.format(self.stateIt))
        while self.stateIt==0:
            self.generic_InitState()
        self.readDataFlush()
        if self.dataAvail==1:
            self.parseData()

    def generic_InitState(self):
        print('in state init {}'.format(self.currentState))
        self.cycleCount=1
        self.stateIt=1

    def updatePlotCheck(self):
        self.updateLickThresholds()
        self.updatePosPlot()
        self.cycleCount=0

    def conditionBlock_s1(self):
        if self.arduinoTime[-1]>2:  #todo: make this a variable
            self.dPos=abs(self.positions[-1]-self.positions[-2])
            
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
                self.waitForStateToUpdateOnTarget(1)

    def conditionBlock_s2(self):
        # if stimSwitch is less than task1's probablity then send to task #1
        if self.positions[-1]>self.distThr and self.task_switch<=self.sTask1_prob.get():
            self.comObj.write(struct.pack('>B', 3))
            print('moving spout; cueing stim task #1')
            self.waitForStateToUpdateOnTarget(2)

        # if stimSwitch is more than task1's probablity then send to task #2
        elif self.positions[-1]>self.distThr and self.stimSwitch<=self.sTask2_prob.get():
            self.comObj.write(struct.pack('>B', 4))
            print('moving spout; cueing stim task #2')
            self.waitForStateToUpdateOnTarget(2)

    def conditionBlock_s3(self):  #todo; mov could be a func
        if self.arduinoTime[-1]>2:
            self.dPos=abs(self.positions[-1]-self.positions[-2])
            if self.dPos>self.movThr and self.stillLatch==1:
                self.stillLatch=0
            if self.dPos<=self.movThr and self.stillLatch==0:
                self.stillTimeStart=self.arduinoTime[-1]
                self.stillLatch=1
            if self.dPos<=self.movThr and self.stillLatch==1:
                self.stillTime=self.arduinoTime[-1]-self.stillTimeStart
            if self.stillLatch==1 and self.stillTime>1:
                print('Still!')
                if self.outcomeSwitch<=self.positive1_Prob:
                    self.comObj.write(struct.pack('>B', 5))
                    print('will play dulcet tone')
                    self.waitForStateToUpdateOnTarget(3)
                # if stimSwitch is more than task1's probablity then send to task #2
                elif self.outcomeSwitch>self.positive1_Prob:
                    self.comObj.write(struct.pack('>B', 6))
                    print('will play ominous tone')
                    self.waitForStateToUpdateOnTarget(3)

    def conditionBlock_s4(self):  #todo; mov could be a func
        if self.arduinoTime[-1]>2:
            self.dPos=abs(self.positions[-1]-self.positions[-2])
            if self.dPos>self.movThr and self.stillLatch==1:
                self.stillLatch=0
            if self.dPos<=self.movThr and self.stillLatch==0:
                self.stillTimeStart=self.arduinoTime[-1]
                self.stillLatch=1
            if self.dPos<=self.movThr and self.stillLatch==1:
                self.stillTime=self.arduinoTime[-1]-self.stillTimeStart
            if self.stillLatch==1 and self.stillTime>1:
                print('Still!')
                if self.outcomeSwitch<=self.positive1_Prob:
                    self.comObj.write(struct.pack('>B', 6))
                    print('will play dulcet tone')
                    self.waitForStateToUpdateOnTarget(4)
                # if stimSwitch is more than task1's probablity then send to task #2
                elif self.outcomeSwitch>self.positive1_Prob:
                    self.comObj.write(struct.pack('>B', 5))
                    print('will play ominous tone')
                    self.waitForStateToUpdateOnTarget(self.currentState)
    
    def conditionBlock_tones(self):
        if self.arduinoTrialTime[-1]>2:
            self.dPos=abs(self.positions[-1]-self.positions[-2])
            if self.dPos>self.movThr and self.stillLatch==1:
                self.stillLatch=0
            if self.dPos<=self.movThr and self.stillLatch==0:
                self.stillTimeStart=self.arduinoTime[-1]
                self.stillLatch=1
            if self.dPos<=self.movThr and self.stillLatch==1:
                self.stillTime=self.arduinoTime[-1]-self.stillTimeStart
            if self.stillLatch==1 and self.stillTime>1:
                print('Still!')
                self.comObj.write(struct.pack('>B', 13))
                print('off to save')
                self.waitForStateToUpdateOnTarget(self.currentState)

    def saveData(self):
        self.exportArray=np.array([self.arduinoTime,self.positions,self.arStates,
            self.lickValues,self.lickDeltas,self.arduinoTrialTime])
        np.savetxt('{}_{}_trial_{}.csv'.format(self.aString.get(),self.dateStr,self.currentTrial), 
            self.exportArray, delimiter=",",fmt="%f")

    def handShake(self):
        print('should be good; will take you to wait state (S1)')
        self.comObj.write(struct.pack('>B', 1))
        print('hands')
        self.waitForStateToUpdateOnTarget(self.currentState) #todo self.currentState right?
        print('did maint call')

    def waitForStateToUpdateOnTarget(self,maintState): 
    # keeps the program cranking while you wait for the MC to update state after a python driven change.
    # !!!!! messes with global variables
    # maintState is the state you are maintaining (the one you are in)
        self.maintState=maintState
        while self.currentState==self.maintState:      
            self.stateIt=0  
            self.readDataFlush()
            if self.dataAvail==1:
                self.parseData()
                self.currentState=int(self.sR[self.streamNum_state])

    def runTask(self):
        self.makeContainers()
        self.initTaskProbs()

        # plotting variables
        self.uiUpdateDelta=4
        print(self.uiUpdateDelta)
        
        # Start the task (will iterate through trials)
        while self.currentTrial<=int(self.totalTrials.get()):
            self.updatePosPlot()
            self.initTime=0  # debug
            try:
                #S0 -----> hand shake (initialization state)
                if self.currentState==0:
                    td=[float(0)]  #debug #document: inset inits before the while!
                    while self.currentState==0:
                        self.generic_StateHeader() # gets data
                        if self.dataAvail==1:
                            td.append(float(self.arduinoTime[-1]-self.initTime)) #todo: jank but useful to track in self
                            #print(td[-1])
                            #print(np.var(td))
                            self.initTime=self.arduinoTime[-1]
                            if len(td)>300: #todo: bigtime jank here
                                if np.var(td[-98:-1])<0.01:
                                    print('cond fine') 
                                    self.handShake()  

                #S1 -----> trial wait state
                elif self.currentState==1:
                    print('in s1')
                    while self.currentState==1:
                        self.generic_StateHeader()
                        if self.dataAvail==1:
                            if int(self.cycleCount) % int(self.uiUpdateDelta)==0:
                                self.updatePlotCheck()
                            self.conditionBlock_s1()
                            self.cycleCount=self.cycleCount+1;

                #S2 -----> trial initiation state
                elif self.currentState==2:
                    self.task_switch=random.random()
                    while self.currentState==2:
                        self.generic_StateHeader()
                        if self.dataAvail==1:
                            if int(self.cycleCount) % int(self.uiUpdateDelta)==0:
                                self.updatePlotCheck()
                            self.conditionBlock_s2()
                            self.cycleCount=self.cycleCount+1;

                #S3 -----> stim task #1 cue
                elif self.currentState==3:
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
                    self.outcomeSwitch=random.random() # debug
                    while self.currentState==4:
                        self.generic_StateHeader()
                        if self.dataAvail==1:
                            if int(self.cycleCount) % int(self.uiUpdateDelta)==0:
                                self.updatePlotCheck()
                            self.conditionBlock_s4()
                            self.cycleCount=self.cycleCount+1;

                #S5 -----> pos tone
                elif self.currentState==5:
                    while self.currentState==5:
                        self.generic_StateHeader()
                        if self.dataAvail==1:
                            if int(self.cycleCount) % int(self.uiUpdateDelta)==0:
                                self.updatePlotCheck()
                            self.conditionBlock_tones()
                            self.cycleCount=self.cycleCount+1;

                #S6 -----> neg tone
                elif self.currentState==6:
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
                print('last trial = {} and the last state was {}. I will try to save last trial ...'.format(self.currentTrial,self.currentState))
                self.comObj.write(struct.pack('>B', 0))
                self.saveData() 
                print('save was a success; now I will close com port and quit')
                self.comObj.close()
                exit()

        print('NORMAL: peace out')
        print('I completed {} trials.'.format(self.currentTrial-1))
        self.comObj.write(struct.pack('>B', 0))  #todo: abstract reset state
        self.comObj.close()
        exit()

#rando todo
#print('lickThr= {}'.format(self.lickThr[0]))
#print('mean dt = {}'.format(np.mean(np.diff(self.arduinoTrialTime))))  #todo: make histo
root = Tk()
my_gui = pyDiscrim_mainGUI(root)
root.mainloop()