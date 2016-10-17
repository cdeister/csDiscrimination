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

## Globals
animalString = 'testAnimal'
movThr=40       # in position units (The minimum ammount of movement allowed)
movTimeThr=2    # in seconds (The time the mouse must be still)
# initialization
stillTime=float(0)
stillLatch=0
stillTimeStart=float(0)
dPos=float(0)
distThr=1000;  # This is the distance the mouse needs to move to initiate a stimulus trial.

# # # # # # # # # # # # # # # # # # # # # # # # # # #
# initialize data containers and session Variables  #
# # # # # # # # # # # # # # # # # # # # # # # # # # #

# containers
positions=[]            # This is the x-position of an optical mouse attached to a USB host shield
arStates=[]             # Store the state the arduino thinks it is in.
arduinoTime=[]          # This is the time as reported by the arduino, which resets every trial. 
lickValues=[]
lickDeltas=[]
arduinoTrialTime=[]
detected_licks=[]

# session variables (user won't change)
currentTrial=1
currentState=0
totalTrials=10


# These are variables that can change if the task is altered.
# We name the data streams so that we can change their order easier if needed. 
# They are position indicides that we use to parse the serial lines. 
streamNum_header=0
streamNum_time=1
streamNum_position=2
streamNum_state=3
streamNum_lickSensor=4
streamNum_lickDeriv=5
streamNum_trialTime=6
tt1=[float(1),float(2)]

# # # # # # # # # # # # # # # # # # # # # # # # 
# Functions and Dynamic Variables             #
# # # # # # # # # # # # # # # # # # # # # # # #
dateStr = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M')



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


    def initComObj(self):
        self.comObj
        print('Opening serial port')
        # Start serial communication
        self.comObj = serial.Serial(self.comPath.get(), self.baudSelected.get()) #Creating our serial object named arduinoData
        # just in case we left it in a weird state lets flip back to the init state 0
        self.comObj.write(struct.pack('>B', 0)) # todo: init state should be abstracted
        print(self.baudSelected.get())  #debug
        print(type(arduino))            #debug

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
        print(selectedStateNumber)
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

    def parseData(self):            #todo: this should be part of data class (and a rational function)
        self.streamNum_header=0          #todo: this is obvious jank
        self.streamNum_time=1
        self.streamNum_position=2
        self.streamNum_state=3
        self.streamNum_lickSensor=4
        self.streamNum_lickDeriv=5
        self.streamNum_trialTime=6
        self.arduinoTime.append(float(int(cR[streamNum_time])/1000))  
        self.positions.append(float(cR[streamNum_position]))
        self.currentState=int(cR[streamNum_state])
        self.arStates.append(currentState)
        self.lickValues.append(int(cR[streamNum_lickSensor]))
        self.lickDeltas.append(int(cR[streamNum_lickDeriv]))
        self.arduinoTrialTime.append(float(int(cR[streamNum_trialTime])/1000))

        self.lickThr=[12,12]            #todo: ugh look away
        self.lickMinMax=[-5,10]
        if self.lickDeltas[-1]>self.lickThr[0]:
            self.detected_licks.append(2)
        elif self.lickDeltas[-1]<=self.lickThr[0]:
            self.detected_licks.append(0)


    def readData(self):
        self.sR=self.comObj.readline().strip().decode()
        self.sR=self.sR.split(',')

    def waitForStateToUpdateOnTarget(self,maintState):   #todo: This reference to cR is dangerous
        # keeps the program cranking while you wait for the MC to update state after a python driven change.
        # !!!!! messes with global variables
        # maintState is the state you are maintaining (the one you are in)

        self.maintState=maintState
        self.currentState
        self.stateIt
        self.sR
        while self.currentState==self.maintState:
                    self.stateIt=0  
                    self.sR=self.readData()
                    self.currentState=int(self.sR[self.streamNum_state]) 


    #----------------------------------------------------------------------------------------------------

    # # # # # # # # # # # # # # # # # # # # # # # # 
    # Plotting Specific Stuff                     #
    # # # # # # # # # # # # # # # # # # # # # # # #


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
        lA=plt.plot(self.arduinoTrialTime[-self.segPlot:-1],self.positions[-self.segPlot:-1],'k-')
        plt.ylim(-1000,3000)
        if len(self.arduinoTrialTime)>self.segPlot+5:
            plt.xlim(self.arduinoTrialTime[-self.segPlot],self.arduinoTrialTime[-1])
        elif len(self.arduinoTrialTime)<=self.segPlot+1:
            plt.xlim(0,12)
        plt.ylabel('position')
        plt.xlabel('time since trial start (sec)')


        plt.subplot(2,2,3)
        lG=plt.plot(self.arduinoTrialTime[-self.segPlot:-1],self.detected_licks[-self.segPlot:-1],'b-')
        plt.ylim(-1,3)
        if len(self.arduinoTrialTime)>self.segPlot+2:
            plt.xlim(self.arduinoTrialTime[-self.segPlot],self.arduinoTrialTime[-1])
        elif len(arduinoTrialTime)<=self.segPlot+1:
            plt.xlim(0,12)
        plt.ylabel('licks (binary)')
        plt.xlabel('time since trial start (sec)')

        plt.subplot(2,2,2)
        lC=plt.plot(stateDiagX,stateDiagY,'ro',markersize=smMrk)
        lD=plt.plot(stateDiagX[currentState],stateDiagY[currentState],'go',markersize=lrMrk)
        plt.ylim(0,10)
        plt.xlim(0,10)
        plt.title(currentTrial)

        plt.pause(pltDelay)
        lA.pop(0).remove()
        lC.pop(0).remove()
        lD.pop(0).remove()
        lG.pop(0).remove()


    def runTask(self):
        ## Globals
        global animalString
        global lickThr
        global lickMinMax
        global movThr
        global movTimeThr
        global stillTime
        global stillLatch
        global stillTimeStart
        global dPos
        global distThr
        global positions
        global arStates
        global arduinoTime
        global lickValues
        global lickDeltas
        global arduinoTrialTime
        global detected_licks
        global currentTrial
        global currentState
        global streamNum_header
        global streamNum_time
        global streamNum_position
        global streamNum_state
        global streamNum_lickSensor
        global streamNum_lickDeriv
        global streamNum_trialTime
        global tt1
        global dateStr
        global totalTrials

        # session variables
        stimTask1_Prob=0.5
        positive1_Prob=0.5
        positive2_Prob=0.5
        lowDelta=0 # for handshake (todo: clean up)

        # plotting variables
        uiUpdateDelta=5

        def readDataFlush(self):
        print('l1')
        global arduino
        arduino.flush()
        sR=arduino.readline().strip().decode()
        sR=sR.split(',')
        return sR

        # Start the task (will iterate through trials)
        while currentTrial<=totalTrials:
            try:
                #S0 -----> hand shake (initialization state)
                print('start; current = {}'.format(currentState))

                if currentState==0:
                    print('going to flush')
                    cR=readDataFlush(self)
                    print('just flushed')

                    if cR[streamNum_header]=='data':
                        if stateIt==0:
                            print('found some dope shit on rx')
                            print('... wait while I make sure it''s ready')
                            stateIt=1
                            updatePosPlot(self)

                        ttd=abs(tt1[1]-tt1[0])
                        tt1[0]=tt1[1]
                        tt1[1]=float(int(cR[streamNum_time])/1000)
                        if ttd<0.1:
                            lowDelta=lowDelta+1
                            if lowDelta>600:
                                print('should be good; will take you to wait state (S1)')
                                arduino.write(struct.pack('>B', 1))
                                waitForStateToUpdateOnTarget(self,arduino,0)

                #S1 -----> trial wait state
                #
                # entry conditions: S0->S1 or S7->S1
                # exit contisions: needs to be still for 2 seconds
                #
                elif currentState==1:
                    # general state code
                    cR=readDataFlush(self,arduino)
                    if cR[streamNum_header]=='data':
                        parseData(self)

                        # we do certain things if we just entered, this is the flag for that.
                        if stateIt==0:
                            print('in state 1')
                            cycleCount=1
                            stateIt=1

                        if int(cycleCount) % int(uiUpdateDelta)==0:
                            tA=np.abs(np.array(lickDeltas))
                            lickThr = np.percentile(tA[np.where(tA != 0)[0]],[75,95])
                            #del tA
                            lickMinMax=[min(lickDeltas),max(lickDeltas)]
                            updatePosPlot(self)
                            cycleCount=0

                        # S1 conditionals
                        # we are going to wait for the animal to be still for some specific time.
                        if arduinoTime[-1]>2:
                            dPos=abs(positions[-1]-positions[-2])
                            
                            if dPos>movThr and stillLatch==1:
                                stillLatch=0

                            if dPos<=movThr and stillLatch==0:
                                stillTimeStart=arduinoTime[-1]
                                stillLatch=1

                            if dPos<=movThr and stillLatch==1:
                                stillTime=arduinoTime[-1]-stillTimeStart

                            if stillLatch==1 and stillTime>1:
                                arduino.write(struct.pack('>B', 2))
                                print('Still! ==> Out of wait')
                                waitForStateToUpdateOnTarget(self,arduino,1)
                        
                        cycleCount=cycleCount+1;


                #S2 -----> trial initiation state
                #
                # entry conditions: S1->S2
                # exit contisions: needs to wait for a cue then walk some distance
                #
                elif currentState==2:
                    cR=readDataFlush(self,arduino)
                    if cR[0]=='data':
                        parseData(self)
                        if stateIt==0:
                            print('in state 2')
                            cycleCount=1;
                            stateIt=1;
                            stimSwitch=random.random()

                        if int(cycleCount) % int(uiUpdateDelta)==0:
                            tA=np.abs(np.array(lickDeltas))
                            lickThr = np.percentile(tA[np.where(tA > 0)[0]],[75,95])
                            #del tA
                            lickMinMax=[min(lickDeltas),max(lickDeltas)]
                            updatePosPlot(self)
                            cycleCount=0

                        # if stimSwitch is less than task1's probablity then send to task #1
                        if positions[-1]>distThr and stimSwitch<=stimTask1_Prob:
                            arduino.write(struct.pack('>B', 3))
                            print('moving spout; cueing stim task #1')
                            waitForStateToUpdateOnTarget(self,arduino,2)

                        # if stimSwitch is more than task1's probablity then send to task #2
                        elif positions[-1]>distThr and stimSwitch>stimTask1_Prob:
                            arduino.write(struct.pack('>B', 4))
                            print('moving spout; cueing stim task #2')
                            waitForStateToUpdateOnTarget(self,arduino,2)

                        cycleCount=cycleCount+1;


                #S3 -----> stim task #1 cue
                elif currentState==3:
                    cR=readDataFlush(self,arduino)
                    if cR[0]=='data':
                        parseData(self)
                        if stateIt==0:
                            print('in state 3; stim task #1')
                            cycleCount=1;
                            stateIt=1;
                            outcomeSwitch=random.random()

                        if int(cycleCount) % int(uiUpdateDelta)==0:
                            updatePosPlot(self)
                            cycleCount=0


                        # S1 conditionals
                        # we are going to wait for the animal to be still for some specific time.
                        if arduinoTime[-1]>2:
                            dPos=abs(positions[-1]-positions[-2])
                            
                            if dPos>movThr and stillLatch==1:
                                stillLatch=0

                            if dPos<=movThr and stillLatch==0:
                                stillTimeStart=arduinoTime[-1]
                                stillLatch=1

                            if dPos<=movThr and stillLatch==1:
                                stillTime=arduinoTime[-1]-stillTimeStart

                            if stillLatch==1 and stillTime>1:
                                print('Still! ==> Out of wait')

                                if outcomeSwitch<=positive1_Prob:
                                    arduino.write(struct.pack('>B', 5))
                                    print('will play dulcet tone')
                                    waitForStateToUpdateOnTarget(self,arduino,3)


                                # if stimSwitch is more than task1's probablity then send to task #2
                                elif outcomeSwitch>positive1_Prob:
                                    arduino.write(struct.pack('>B', 6))
                                    print('will play ominous tone')
                                    waitForStateToUpdateOnTarget(self,arduino,3)

                        cycleCount=cycleCount+1;


                #S4 -----> stim task #2 cue
                elif currentState==4:
                    cR=readDataFlush(self,arduino)
                    if cR[0]=='data':
                        parseData(self)

                        if stateIt==0:
                            print('in state 4; stim task #2')
                            cycleCount=1;
                            stateIt=1;
                            outcomeSwitch=random.random()

                        if int(cycleCount) % int(uiUpdateDelta)==0:
                            updatePosPlot(self)
                            cycleCount=0

                        # S1 conditionals
                        # we are going to wait for the animal to be still for some specific time.
                        if arduinoTime[-1]>2:
                            dPos=abs(positions[-1]-positions[-2])
                            
                            if dPos>movThr and stillLatch==1:
                                stillLatch=0

                            if dPos<=movThr and stillLatch==0:
                                stillTimeStart=arduinoTime[-1]
                                stillLatch=1

                            if dPos<=movThr and stillLatch==1:
                                stillTime=arduinoTime[-1]-stillTimeStart

                            if stillLatch==1 and stillTime>1:
                                print('Still! ==> Out of wait')

                                if outcomeSwitch<=positive1_Prob:
                                    arduino.write(struct.pack('>B', 7))
                                    print('will play dulcet tone')
                                    waitForStateToUpdateOnTarget(self,arduino,4)


                                # if stimSwitch is more than task1's probablity then send to task #2
                                elif outcomeSwitch>positive1_Prob:
                                    arduino.write(struct.pack('>B', 8))
                                    print('will play ominous tone')
                                    waitForStateToUpdateOnTarget(self,arduino,4)
                                

                        cycleCount=cycleCount+1;

                #S5 -----> pos tone
                elif currentState==5:
                    cR=readDataFlush(self,arduino)
                    if cR[0]=='data':
                        parseData(self)

                        if stateIt==0:
                            print('in state 5; playing something good')
                            cycleCount=1;
                            stateIt=1;

                        if int(cycleCount) % int(uiUpdateDelta)==0:
                            updatePosPlot(self)
                            cycleCount=0

                        # S1 conditionals
                        # we are going to wait for the animal to be still for some specific time.
                        if arduinoTime[-1]>2:
                            dPos=abs(positions[-1]-positions[-2])
                            
                            if dPos>movThr and stillLatch==1:
                                stillLatch=0

                            if dPos<=movThr and stillLatch==0:
                                stillTimeStart=arduinoTime[-1]
                                stillLatch=1

                            if dPos<=movThr and stillLatch==1:
                                stillTime=arduinoTime[-1]-stillTimeStart

                            if stillLatch==1 and stillTime>1:
                                print('Still! ==> Out of wait')
                                arduino.write(struct.pack('>B', 13))
                                print('off to save')
                                while currentState==5:
                                    stateIt=0
                                    cR=readData(self,arduino)
                                    currentState=int(cR[streamNum_state])

                        cycleCount=cycleCount+1;

                #S6 -----> neg tone
                elif currentState==6:
                    cR=readDataFlush(self,arduino)
                    if cR[0]=='data':
                        parseData(self)

                        if stateIt==0:
                            print('in state 6; playing something bad')
                            cycleCount=1;
                            stateIt=1;

                        if int(cycleCount) % int(uiUpdateDelta)==0:
                            updatePosPlot(self)
                            cycleCount=0

                        # S1 conditionals
                        # we are going to wait for the animal to be still for some specific time.
                        if arduinoTime[-1]>2:
                            dPos=abs(positions[-1]-positions[-2])
                            
                            if dPos>movThr and stillLatch==1:
                                stillLatch=0

                            if dPos<=movThr and stillLatch==0:
                                stillTimeStart=arduinoTime[-1]
                                stillLatch=1

                            if dPos<=movThr and stillLatch==1:
                                stillTime=arduinoTime[-1]-stillTimeStart

                            if stillLatch==1 and stillTime>1:
                                print('Still! ==> Out of wait')
                                arduino.write(struct.pack('>B', 13))
                                print('off to save')
                                while currentState==6:
                                    stateIt=0
                                    cR=readData(self,arduino)
                                    currentState=int(cR[streamNum_state])

                        cycleCount=cycleCount+1;


                #S7 -----> pos tone
                elif currentState==7:
                    cR=readDataFlush(arduino)
                    if cR[0]=='data':
                        parseData()

                        if stateIt==0:
                            print('in state 7; playing something good')
                            cycleCount=1;
                            stateIt=1;

                        if int(cycleCount) % int(uiUpdateDelta)==0:
                            updatePosPlot()
                            cycleCount=0

                        # S1 conditionals
                        # we are going to wait for the animal to be still for some specific time.
                        if arduinoTime[-1]>2:
                            dPos=abs(positions[-1]-positions[-2])
                            
                            if dPos>movThr and stillLatch==1:
                                stillLatch=0

                            if dPos<=movThr and stillLatch==0:
                                stillTimeStart=arduinoTime[-1]
                                stillLatch=1

                            if dPos<=movThr and stillLatch==1:
                                stillTime=arduinoTime[-1]-stillTimeStart

                            if stillLatch==1 and stillTime>1:
                                print('Still! ==> Out of wait')
                                arduino.write(struct.pack('>B', 13))
                                print('off to save')
                                while currentState==7:
                                    stateIt=0
                                    cR=readData(arduino)
                                    currentState=int(cR[streamNum_state])

                        cycleCount=cycleCount+1;

                #S8 -----> neg tone
                elif currentState==8:
                    cR=readDataFlush(arduino)
                    if cR[0]=='data':
                        parseData()

                        if stateIt==0:
                            print('in state 8; playing something bad')
                            cycleCount=1;
                            stateIt=1;

                        if int(cycleCount) % int(uiUpdateDelta)==0:
                            updatePosPlot()
                            cycleCount=0

                        # S1 conditionals
                        # we are going to wait for the animal to be still for some specific time.
                        if arduinoTime[-1]>2:
                            dPos=abs(positions[-1]-positions[-2])
                            
                            if dPos>movThr and stillLatch==1:
                                stillLatch=0

                            if dPos<=movThr and stillLatch==0:
                                stillTimeStart=arduinoTime[-1]
                                stillLatch=1

                            if dPos<=movThr and stillLatch==1:
                                stillTime=arduinoTime[-1]-stillTimeStart

                            if stillLatch==1 and stillTime>1:
                                print('Still! ==> Out of wait')
                                arduino.write(struct.pack('>B', 13))
                                print('off to save')
                                while currentState==8:
                                    stateIt=0
                                    cR=readData(arduino)
                                    currentState=int(cR[streamNum_state])

                        cycleCount=cycleCount+1;
                

                # ----------------- (S13: save state)
                elif currentState==13:
                    print('in state 13; saving your bacon') # debug
                    savedata([arduinoTime,positions,arStates,lickValues,lickDeltas,arduinoTrialTime])
                    # clean up plot data (memory managment)
                    print('lickThr= {}'.format(lickThr[0]))
                    print('mean dt = {}'.format(np.mean(np.diff(arduinoTrialTime))))
                    arduinoTime=[]
                    positions=[]
                    arStates=[]
                    lickValues=[]
                    lickDeltas=[]
                    arduinoTrialTime=[]
                    detected_licks=[]
                    currentTrial=currentTrial+1
                    print('trial done')
                    arduino.write(struct.pack('>B', 1))
                    while currentState==13:
                        stateIt=0
                        cR=readData(self,arduino)
                        currentState=int(cR[streamNum_state])          
            except:
                print(dPos)
                print('EXCEPTION: peace out bitches')
                print('last trial = {} and the last state was {}. I will try to save last trial ...'.format(currentTrial,currentState))
                arduino.write(struct.pack('>B', 0))
                exportArray=np.array([arduinoTime,positions,arStates,lickValues,lickDeltas,arduinoTrialTime])
                np.savetxt('{}_{}_trial_{}.csv'.format(animalString,dateStr,currentTrial), exportArray, delimiter=",",fmt="%f")
                print('save was a success; now I will close com port and quit')
                arduino.close()
                arduinoTime=[]
                positions=[]
                arStates=[]
                lickValues=[]
                lickDeltas=[]
                arduinoTrialTime=[]
                detected_licks=[]
                exit()


        print('NORMAL: peace out bitches')
        print('I completed {} trials.'.format(currentTrial-1))
        arduino.write(struct.pack('>B', 0))
        arduino.close()
        exit()


root = Tk()
my_gui = pyDiscrim_mainGUI(root)
root.mainloop()