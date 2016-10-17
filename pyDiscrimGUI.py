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

        self.s13_button = Button(master, text="Save/Quit", bg='red', command=self.saveQuit)
        self.s13_button.grid(row=6, column=3)
        self.s13_button.config(state=DISABLED)

        self.currentTrial=1
        self.currentState=0
        self.totalTrials=10
        self.dPos=float(0)
        self.lickThr=[12,12]            #todo: ugh look away
        self.lickMinMax=[-5,10]

        ## Globals
        self.animalString = 'testAnimal'
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
        self.totalTrials=10
        self.lowDelta=0
        self.stateIt=0;


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

    def makeContainers(self):           #todo: this should be part of data class
        self.positions=[]            # This is the x-position of an optical mouse attached to a USB host shield
        self.arStates=[]             # Store the state the arduino thinks it is in.
        self.arduinoTime=[]          # This is the time as reported by the arduino, which resets every trial. 
        self.lickValues=[]
        self.lickDeltas=[]
        self.arduinoTrialTime=[]
        self.detected_licks=[]
        self.streamNum_header=0          #todo: this is obvious jank
        self.streamNum_time=1
        self.streamNum_position=2
        self.streamNum_state=3
        self.streamNum_lickSensor=4
        self.streamNum_lickDeriv=5
        self.streamNum_trialTime=6

    def cleanContainers(self):           #todo: this should be part of data class
        self.positions=[]            # This is the x-position of an optical mouse attached to a USB host shield
        self.arStates=[]             # Store the state the arduino thinks it is in.
        self.arduinoTime=[]          # This is the time as reported by the arduino, which resets every trial. 
        self.lickValues=[]
        self.lickDeltas=[]
        self.arduinoTrialTime=[]
        self.detected_licks=[]

    def parseData(self):            #todo: this should be part of data class (and a rational function)
        self.arduinoTime.append(float(int(self.sR[self.streamNum_time])/1000))  
        self.positions.append(float(self.sR[self.streamNum_position]))
        self.currentState=int(self.sR[self.streamNum_state])
        self.arStates.append(self.currentState)
        self.lickValues.append(int(self.sR[self.streamNum_lickSensor]))
        self.lickDeltas.append(int(self.sR[self.streamNum_lickDeriv]))
        self.arduinoTrialTime.append(float(int(self.sR[self.streamNum_trialTime])/1000))

    def updateLickThresholds(self):
        tA=np.abs(np.array(self.lickDeltas))
        self.lickThr = np.percentile(tA[np.where(tA != 0)[0]],[75,95])
        self.lickMinMax=[min(self.lickDeltas),max(self.lickDeltas)]

    def lickDetect(self):
        if self.lickDeltas[-1]>self.lickThr[0]:
            self.detected_licks.append(2)
        elif self.lickDeltas[-1]<=self.lickThr[0]:
            self.detected_licks.append(0)

    def waitForStateToUpdateOnTarget(self,maintState): 
        # keeps the program cranking while you wait for the MC to update state after a python driven change.
        # !!!!! messes with global variables
        # maintState is the state you are maintaining (the one you are in)
        self.maintState=maintState
        while self.currentState==self.maintState:      
            self.stateIt=0  
            self.readData()
            self.currentState=int(self.sR[self.streamNum_state])

    def updatePosPlot(self): # todo: organize this better (should be its own class I think)
        self.segPlot=300
        self.pltDelay=0.0000001 # this can be changed, but doesn't need to be. We have to have a plot delay, but it can be tiny.
        self.stateDiagX=[1,1,3,5,5,7,7,7,7,9,9,9,9,1]
        self.stateDiagY=[3,5,5,6,4,8,6,4,2,8,6,4,2,7]
        self.smMrk=10
        self.lrMrk=20
        self.stateIt=0;
        self.postionMin=-1000;
        self.positionMax=3000;
        self.lickMin=0
        self.lickMax=30

        plt.subplot(2,2,1)
        self.lA=plt.plot(self.arduinoTrialTime[-self.segPlot:-1],self.positions[-self.segPlot:-1],'k-')
        plt.ylim(-1000,3000)
        if len(self.arduinoTrialTime)>self.segPlot+5:
            plt.xlim(self.arduinoTrialTime[-self.segPlot],self.arduinoTrialTime[-1])
        elif len(self.arduinoTrialTime)<=self.segPlot+1:
            plt.xlim(0,12)
        plt.ylabel('position')
        plt.xlabel('time since trial start (sec)')


        # plt.subplot(2,2,3)
        # print('want to make lg')
        # #self.lG=plt.plot(self.arduinoTrialTime[-self.segPlot:-1],self.detected_licks[-self.segPlot:-1],'b-')
        # print('made lg')
        # plt.ylim(-1,3)
        # if len(self.arduinoTrialTime)>self.segPlot+2:
        #     plt.xlim(self.arduinoTrialTime[-self.segPlot],self.arduinoTrialTime[-1])
        # elif len(self.arduinoTrialTime)<=self.segPlot+1:
        #     plt.xlim(0,12)
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

    def initTaskProbs(self):
        self.stimTask1_Prob=0.5
        self.positive1_Prob=0.5
        self.positive2_Prob=0.5

    def readData(self):
        self.sR=self.comObj.readline().strip().decode()
        self.sR=self.sR.split(',')

    def readDataFlush(self):
        self.comObj.flush()
        self.sR=self.comObj.readline().strip().decode()
        self.sR=self.sR.split(',')

    def generic_StateHeader(self,descrState):
        # general state code
        self.descrState=descrState
        self.readDataFlush()

    def generic_InitState(self):
        print('in state init {}'.format(self.descrState))
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
        if self.positions[-1]>self.distThr and self.stimSwitch<=self.stimTask1_Prob:
            self.comObj.write(struct.pack('>B', 3))
            print('moving spout; cueing stim task #1')
            self.waitForStateToUpdateOnTarget(2)

        # if stimSwitch is more than task1's probablity then send to task #2
        elif self.positions[-1]>self.distThr and self.stimSwitch>self.stimTask1_Prob:
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
                    self.comObj.write(struct.pack('>B', 7))
                    print('will play dulcet tone')
                    self.waitForStateToUpdateOnTarget(4)
                # if stimSwitch is more than task1's probablity then send to task #2
                elif self.outcomeSwitch>self.positive1_Prob:
                    self.comObj.write(struct.pack('>B', 8))
                    print('will play ominous tone')
                    self.waitForStateToUpdateOnTarget(self.currentState)
    
    def conditionBlock_tones(self):
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
                self.comObg.write(struct.pack('>B', 13))
                print('off to save')
                self.waitForStateToUpdateOnTarget(self.currentState)

    def saveData(self):
        self.exportArray=np.array([self.arduinoTime,self.positions,self.arStates,
            self.lickValues,self.lickDeltas,self.arduinoTrialTime])
        np.savetxt('{}_{}_trial_{}.csv'.format(self.animalString,self.dateStr,self.currentTrial), 
            self.exportArray, delimiter=",",fmt="%f")

    def runTask(self):
        self.makeContainers()
        self.initTaskProbs()

        # plotting variables
        self.uiUpdateDelta=5
        print(self.uiUpdateDelta)
        
        # Start the task (will iterate through trials)
        while self.currentTrial<=self.totalTrials:
            try:
                #S0 -----> hand shake (initialization state)
                if self.currentState==0:
                    self.generic_StateHeader(self.currentState)
                    self.readDataFlush()

                    if self.sR[self.streamNum_header]=='data':
                        if self.stateIt==0:
                            self.stateIt=1
                            self.updatePosPlot()

                        self.ttd=abs(self.tt1[1]-self.tt1[0])
                        self.tt1[0]=self.tt1[1]
                        self.tt1[1]=float(int(self.sR[self.streamNum_time])/1000)
                        if self.ttd<0.1:
                            self.lowDelta=self.lowDelta+1
                            if self.lowDelta>20:
                                print('should be good; will take you to wait state (S1)')
                                self.comObj.write(struct.pack('>B', 1))
                                print('wrote 1')
                                self.waitForStateToUpdateOnTarget(0) #todo self.currentState right?

                #S1 -----> trial wait state
                elif self.currentState==1:
                    # wait for data
                    self.generic_StateHeader(1)
                    self.readDataFlush()
                    if self.sR[self.streamNum_header]=='data':
                        # then just crank
                        self.parseData()
                        if self.stateIt==0:     
                            self.generic_InitState()
                            #also, anything specific
                        if int(self.cycleCount) % int(self.uiUpdateDelta)==0:
                            self.updatePlotCheck()
                        self.conditionBlock_s1()
                        self.cycleCount=self.cycleCount+1;

                #S2 -----> trial initiation state
                elif self.currentState==2:
                    # wait for data
                    self.generic_StateHeader(2)
                    self.readDataFlush()
                    if self.sR[self.streamNum_header]=='data':
                        # then just crank
                        self.parseData()
                        if self.stateIt==0:
                            self.generic_InitState()
                            self.stimSwitch=random.random() #todo: make sure I am seeding this right
                        if int(self.cycleCount) % int(self.uiUpdateDelta)==0:
                            self.updatePlotCheck()

                        self.conditionBlock_s2()
                        self.cycleCount=self.cycleCount+1;

                #S3 -----> stim task #1 cue
                elif self.currentState==3:
                    # wait for data
                    self.generic_StateHeader(3)
                    self.readDataFlush()
                    if sR[self.streamNum_header]=='data':
                        # then just crank
                        parseData()
                        if self.stateIt==0:
                            self.generic_InitState()
                            self.outcomeSwitch=random.random() #todo: make sure I am seeding this right
                        
                        if int(self.cycleCount) % int(self.uiUpdateDelta)==0:
                            self.updatePlotCheck()

                        self.conditionBlock_s3()
                        cycleCount=cycleCount+1;

                #S4 -----> stim task #2 cue
                elif self.currentState==4:
                    # wait for data
                    self.generic_StateHeader(4)
                    self.readDataFlush()
                    if sR[self.streamNum_header]=='data':
                        # then just crank
                        parseData()
                        if self.stateIt==0:
                            self.generic_InitState()
                            self.outcomeSwitch=random.random() #todo: make sure I am seeding this right
                        
                        if int(self.cycleCount) % int(self.uiUpdateDelta)==0:
                            self.updatePlotCheck()

                        self.conditionBlock_s4()
                        cycleCount=cycleCount+1;

                #S5 -----> pos tone
                elif self.currentState==5:
                    # wait for data
                    self.generic_StateHeader(5)
                    self.readDataFlush()
                    if sR[self.streamNum_header]=='data':
                        # then just crank
                        parseData()
                        if self.stateIt==0:
                            self.generic_InitState()
                            # 5 specific?
                        
                        if int(self.cycleCount) % int(self.uiUpdateDelta)==0:
                            self.updatePlotCheck()

                        self.conditionBlock_tones()
                        cycleCount=cycleCount+1;

                #S6 -----> neg tone
                elif self.currentState==6:
                    # wait for data
                    self.generic_StateHeader(self.currentState)
                    self.readDataFlush()
                    if sR[self.streamNum_header]=='data':
                        # then just crank
                        parseData()
                        if self.stateIt==0:
                            self.generic_InitState()
                            # 5 specific?
                        
                        if int(self.cycleCount) % int(self.uiUpdateDelta)==0:
                            self.updatePlotCheck()

                        self.conditionBlock_tones()
                        cycleCount=cycleCount+1;

                #S7 -----> pos tone
                elif self.currentState==7:
                    # wait for data
                    self.generic_StateHeader(self.currentState)
                    self.readDataFlush()
                    if sR[self.streamNum_header]=='data':
                        # then just crank
                        parseData()
                        if self.stateIt==0:
                            self.generic_InitState()
                            # 5 specific?
                        
                        if int(self.cycleCount) % int(self.uiUpdateDelta)==0:
                            self.updatePlotCheck()

                        self.conditionBlock_tones()
                        cycleCount=cycleCount+1;

                #S8 -----> neg tone
                elif self.currentState==8:
                    # wait for data
                    self.generic_StateHeader(self.currentState)
                    self.readDataFlush()
                    if sR[self.streamNum_header]=='data':
                        # then just crank
                        parseData()
                        if self.stateIt==0:
                            self.generic_InitState()
                            # 5 specific?
                        
                        if int(self.cycleCount) % int(self.uiUpdateDelta)==0:
                            self.updatePlotCheck()

                        self.conditionBlock_tones()
                        cycleCount=cycleCount+1;


                # ----------------- (S13: save state)
                elif self.currentState==13:
                    print('in state 13; saving your bacon') # debug
                    self.saveData()                    # clean up plot data (memory managment)
                    print('lickThr= {}'.format(self.lickThr[0]))
                    print('mean dt = {}'.format(np.mean(np.diff(self.arduinoTrialTime))))  #todo: make histo
                    self.cleanContainers()
                    self.currentTrial=self.currentTrial+1
                    print('trial done')
                    self.comObj.write(struct.pack('>B', 1)) #todo: abstract wait
                    while currentState==13:
                        stateIt=0
                        self.readData()
                        self.currentState=int(self.sR[streamNum_state])          
            except:
                print(self.dPos)
                print('EXCEPTION: peace out bitches')
                print('last trial = {} and the last state was {}. I will try to save last trial ...'.format(self.currentTrial,self.currentState))
                self.comObj.write(struct.pack('>B', 0))
                self.saveData() 
                print('save was a success; now I will close com port and quit')
                self.comObj.close()
                exit()

        print('NORMAL: peace out bitches')
        print('I completed {} trials.'.format(self.currentTrial-1))
        self.comObj.write(struct.pack('>B', 0))  #todo: abstract reset state
        self.comObj.close()
        exit()


root = Tk()
my_gui = pyDiscrim_mainGUI(root)
root.mainloop()