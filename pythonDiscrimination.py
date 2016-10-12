# pythonDiscrimination:
# This is a python script that runs sensory discrimination tasks in a state-based manner.
# It works with microcontrolors. It can easily be modified to suit different needs.
#
# version 2.1 (new plotting scheme)
# 10/09/2016
# questions? --> Chris Deister --> cdeister@Bbrown.edu
#

# includes
#
import serial
import numpy
import matplotlib.pyplot as plt
import time
import datetime
#import os
import random
import math
import struct

#----------------------------------------------------------------------------------------------------

# # # # # # # # # # # # # # # # # # # # # # # # 
# Flow Variables: USERS WILL EDIT *****       #
# # # # # # # # # # # # # # # # # # # # # # # #
#
# animal details
animalString = 'testAnimal'

# session variables
totalTrials=10
stimTask1_Prob=0.5
positive1_Prob=0.5
positive2_Prob=0.5

# data streaming micro-controller location
comPort='/dev/cu.usbmodem1411'
baudRate=9600

# plotting variables
uiUpdateDelta=5
segPlot=500
pltDelay=0.0000001 # this can be changed, but doesn't need to be. We have to have a plot delay, but it can be tiny.



#----------------------------------------------------------------------------------------------------

# # # # # # # # # # # # # # # # # # # # # # # # # # #
# initialize data containers and session Variables  #
# # # # # # # # # # # # # # # # # # # # # # # # # # #

# containers
positions=[]            # This is the x-position of an optical mouse attached to a USB host shield
arStates=[]             # Store the state the arduino thinks it is in.
arduinoTime=[]          # This is the time as reported by the arduino, which resets every trial. 
lickValues=[]

# session variables (user won't change)
currentTrial=1
currentState=0
lowDelta=0              # for handshake (todo: clean up)


# These are variables that can change if the task is altered.
# We name the data streams so that we can change their order easier if needed. 
# They are position indicides that we use to parse the serial lines. 
streamNum_header=0
streamNum_time=1
streamNum_position=2
streamNum_state=3
streamNum_lickSensor=4

#----------------------------------------------------------------------------------------------------

# # # # # # # # # # # # # # # # # # # # # # # # 
# Functions and Dynamic Variables             #
# # # # # # # # # # # # # # # # # # # # # # # #
dateStr = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M')


def savedata(dataList):
    exportArray=numpy.array(dataList)
    numpy.savetxt('{}_{}_trial_{}.csv'.format(animalString,dateStr,currentTrial), exportArray, delimiter=",",fmt="%f")

def updatePosPlot(sampNum,yData1,xData2,yData2,stateIn,trialIn,yData3): # todo: organize this better
    plt.subplot(3,2,1)
    lA=plt.plot(yData1[-sampNum:-1],'k-')
    plt.ylim(-1000,6000)
    plt.xlim(0,sampNum)
    plt.ylabel('position')
    plt.xlabel('time since session start (sec)')

    plt.subplot(3,2,2)
    lB=plt.plot(yData3[-sampNum:-1],'k-')
    plt.ylim(0,256)
    plt.xlim(0,sampNum)
    plt.ylabel('lick value')
    plt.xlabel('time since session start (sec)')

    plt.subplot(3,2,5)
    lC=plt.plot(xData2,yData2,'ro',markersize=smMrk)
    lD=plt.plot(xData2[stateIn],yData2[stateIn],'go',markersize=lrMrk)
    plt.axis('equal')
    plt.ylim(0,10)
    plt.xlim(0,10)
    plt.title(trialIn)

    plt.pause(pltDelay)
    lA.pop(0).remove()
    lB.pop(0).remove()
    lC.pop(0).remove()
    lD.pop(0).remove()

def parseData():
    global currentState
    global arduinoTime
    global positions
    global arStates
    global lickValues
    arduinoTime.append(float(int(cR[streamNum_time])/1000))
    positions.append(float(cR[streamNum_position]))
    currentState=int(cR[streamNum_state])
    arStates.append(currentState)
    lickValues.append(int(cR[streamNum_lickSensor]))


#----------------------------------------------------------------------------------------------------

# # # # # # # # # # # # # # # # # # # # # # # # 
# Plotting and State-Specific Variables       #
# # # # # # # # # # # # # # # # # # # # # # # #

# ----- (Start) Plotting variables
stateDiagX=[1,1,3,5,5,7,7,7,7,9,9,9,9,1]
stateDiagY=[3,5,5,6,4,8,6,4,2,8,6,4,2,7]
smMrk=10
lrMrk=20
stateIt=0;
postionMin=-2000;
positionMax=6000;
lickMin=0
lickMax=30
tt1=[float(1),float(2)]


# ~~~~~~~~~> (End) Plotting Variables

# ----- (Start) S1 Variables
# user variable
movThr=40       # in position units (The minimum ammount of movement allowed)
movTimeThr=2    # in seconds (The time the mouse must be still)

# initialization
stillTime=float(0)
stillLatch=0
stillTimeStart=float(0)
dPos=float(0)


# ~~~~~~~~~> (End) S1 Variables


# ----- (Start) S2 Variables
distThr=5000;  # This is the distance the mouse needs to move to initiate a stimulus trial.


# ~~~~~~~~~> (End) S2 Variables

#----------------------------------------------------------------------------------------------------

# # # # # # # # # # # # # # # # # # # # # # # # 
# This is the task block                      #
# # # # # # # # # # # # # # # # # # # # # # # #

# Start serial communication
arduino = serial.Serial(comPort, baudRate) #Creating our serial object named arduinoData
# just in case we left it in a weird state lets flip back to the init state 0
arduino.write(struct.pack('>B', 0))


# Start the task (will iterate through trials)
while currentTrial<=totalTrials:
    try:
        #S0 -----> hand shake (initialization state)
        if currentState==0:
            arduino.flush() # I don't know if this is needed.
            cR=arduino.readline().decode().strip()
            cR=cR.split(',')
            # We are waiting until we get a good serial read (should start with data)
            if cR[streamNum_header]=='data':
                if stateIt==0:
                    print('found some dope shit on rx')
                    print('... wait while I make sure it''s ready')
                    stateIt=1
                    updatePosPlot(segPlot,positions,stateDiagX,stateDiagY,currentState,currentTrial,lickValues)

                ttd=abs(tt1[1]-tt1[0])
                tt1[0]=tt1[1]
                tt1[1]=float(int(cR[streamNum_time])/1000)
                if ttd<0.1:
                    lowDelta=lowDelta+1
                    if lowDelta>40:
                        print('should be good; will take you to wait state (S1)')
                        arduino.write(struct.pack('>B', 1))
                        while currentState==0:
                            stateIt=0
                            cR=arduino.readline().strip().decode()
                            cR=cR.split(',')
                            currentState=int(cR[streamNum_state])

        #S1 -----> trial wait state
        #
        # entry conditions: S0->S1 or S7->S1
        # exit contisions: needs to be still for 2 seconds
        #
        elif currentState==1:
            # general state code
            arduino.flush()
            cR=arduino.readline().strip().decode()
            cR=cR.split(',')
            if cR[streamNum_header]=='data':
                parseData()

                # we do certain things if we just entered, this is the flag for that.
                if stateIt==0:
                    print('in state 1')
                    cycleCount=1
                    stateIt=1

                if int(cycleCount) % int(uiUpdateDelta)==0:
                    updatePosPlot(segPlot,positions,stateDiagX,stateDiagY,currentState,currentTrial,lickValues)
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
                        
                        while currentState==1:
                            stateIt=0
                            cR=arduino.readline().strip().decode()
                            cR=cR.split(',')
                            currentState=int(cR[streamNum_state])
                
                cycleCount=cycleCount+1;


        #S2 -----> trial initiation state
        #
        # entry conditions: S1->S2
        # exit contisions: needs to wait for a cue then walk some distance
        #
        elif currentState==2:
            arduino.flush()
            cR=arduino.readline().strip().decode()
            cR=cR.split(',')
            if cR[0]=='data':
                parseData()
                if stateIt==0:
                    print('in state 2')
                    cycleCount=1;
                    stateIt=1;
                    stimSwitch=random.random()

                if int(cycleCount) % int(uiUpdateDelta)==0:
                    updatePosPlot(segPlot,positions,stateDiagX,stateDiagY,currentState,currentTrial,lickValues)
                    cycleCount=0

                # if stimSwitch is less than task1's probablity then send to task #1
                if positions[-1]>distThr and stimSwitch<=stimTask1_Prob:
                    arduino.write(struct.pack('>B', 3))
                    print('moving spout; cueing stim task #1')
                    while currentState==2:
                        stateIt=0
                        cR=arduino.readline().strip().decode()
                        cR=cR.split(',')
                        currentState=int(cR[streamNum_state])

                # if stimSwitch is more than task1's probablity then send to task #2
                elif positions[-1]>distThr and stimSwitch>stimTask1_Prob:
                    arduino.write(struct.pack('>B', 4))
                    print('moving spout; cueing stim task #2')
                    while currentState==2: # todo: can make these calls a function
                        stateIt=0
                        cR=arduino.readline().strip().decode()
                        cR=cR.split(',')
                        currentState=int(cR[streamNum_state])

                cycleCount=cycleCount+1;


        #S3 -----> stim task #1 cue
        elif currentState==3:
            arduino.flush()
            cR=arduino.readline().strip().decode()
            cR=cR.split(',')
            if cR[0]=='data':
                parseData()

                if stateIt==0:
                    print('in state 3; stim task #1')
                    cycleCount=1;
                    stateIt=1;
                    outcomeSwitch=random.random()

                if int(cycleCount) % int(uiUpdateDelta)==0:
                    updatePosPlot(segPlot,positions,stateDiagX,stateDiagY,currentState,currentTrial,lickValues)
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
                            while currentState==3:
                                stateIt=0
                                cR=arduino.readline().strip().decode()
                                cR=cR.split(',')
                                currentState=int(cR[streamNum_state])


                        # if stimSwitch is more than task1's probablity then send to task #2
                        elif outcomeSwitch>positive1_Prob:
                            arduino.write(struct.pack('>B', 6))
                            print('will play ominous tone')
                            while currentState==3: # todo: can make these calls a function
                                stateIt=0
                                cR=arduino.readline().strip().decode()
                                cR=cR.split(',')
                                currentState=int(cR[streamNum_state])

                cycleCount=cycleCount+1;


        #S4 -----> stim task #2 cue
        elif currentState==4:
            arduino.flush()
            cR=arduino.readline().strip().decode()
            cR=cR.split(',')
            if cR[0]=='data':
                parseData()

                if stateIt==0:
                    print('in state 4; stim task #2')
                    cycleCount=1;
                    stateIt=1;
                    outcomeSwitch=random.random()

                if int(cycleCount) % int(uiUpdateDelta)==0:
                    updatePosPlot(segPlot,positions,stateDiagX,stateDiagY,currentState,currentTrial,lickValues)
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
                            while currentState==4:
                                stateIt=0
                                cR=arduino.readline().strip().decode()
                                cR=cR.split(',')
                                currentState=int(cR[streamNum_state])


                        # if stimSwitch is more than task1's probablity then send to task #2
                        elif outcomeSwitch>positive1_Prob:
                            arduino.write(struct.pack('>B', 8))
                            print('will play ominous tone')
                            while currentState==4: # todo: can make these calls a function
                                stateIt=0
                                cR=arduino.readline().strip().decode()
                                cR=cR.split(',')
                                currentState=int(cR[streamNum_state])
                        

                cycleCount=cycleCount+1;

        #S5 -----> pos tone
        elif currentState==5:
            arduino.flush()
            cR=arduino.readline().strip().decode()
            cR=cR.split(',')
            if cR[0]=='data':
                parseData()

                if stateIt==0:
                    print('in state 5; playing something good')
                    cycleCount=1;
                    stateIt=1;

                if int(cycleCount) % int(uiUpdateDelta)==0:
                    updatePosPlot(segPlot,positions,stateDiagX,stateDiagY,currentState,currentTrial,lickValues)
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
                            cR=arduino.readline().strip().decode()
                            cR=cR.split(',')
                            currentState=int(cR[streamNum_state])

                cycleCount=cycleCount+1;

        #S6 -----> neg tone
        elif currentState==6:
            arduino.flush()
            cR=arduino.readline().strip().decode()
            cR=cR.split(',')
            if cR[0]=='data':
                parseData()

                if stateIt==0:
                    print('in state 6; playing something bad')
                    cycleCount=1;
                    stateIt=1;

                if int(cycleCount) % int(uiUpdateDelta)==0:
                    updatePosPlot(segPlot,positions,stateDiagX,stateDiagY,currentState,currentTrial,lickValues)
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
                            cR=arduino.readline().strip().decode()
                            cR=cR.split(',')
                            currentState=int(cR[streamNum_state])

                cycleCount=cycleCount+1;


        #S7 -----> pos tone
        elif currentState==7:
            arduino.flush()
            cR=arduino.readline().strip().decode()
            cR=cR.split(',')
            if cR[0]=='data':
                parseData()

                if stateIt==0:
                    print('in state 7; playing something good')
                    cycleCount=1;
                    stateIt=1;

                if int(cycleCount) % int(uiUpdateDelta)==0:
                    updatePosPlot(segPlot,positions,stateDiagX,stateDiagY,currentState,currentTrial,lickValues)
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
                            cR=arduino.readline().strip().decode()
                            cR=cR.split(',')
                            currentState=int(cR[streamNum_state])

                cycleCount=cycleCount+1;

        #S8 -----> neg tone
        elif currentState==8:
            arduino.flush()
            cR=arduino.readline().strip().decode()
            cR=cR.split(',')
            if cR[0]=='data':
                parseData()

                if stateIt==0:
                    print('in state 8; playing something bad')
                    cycleCount=1;
                    stateIt=1;

                if int(cycleCount) % int(uiUpdateDelta)==0:
                    updatePosPlot(segPlot,positions,stateDiagX,stateDiagY,currentState,currentTrial,lickValues)
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
                            cR=arduino.readline().strip().decode()
                            cR=cR.split(',')
                            currentState=int(cR[streamNum_state])

                cycleCount=cycleCount+1;
        

        # ----------------- (S13: save state)
        elif currentState==13:
            print('in state 13; saving your bacon') # debug
            savedata([arduinoTime,positions,arStates,lickValues])
            if currentTrial>1:
                linesE.pop(0).remove()
            plt.subplot(3,3,6)
            linesE=plt.plot(positions,'r-')
            plt.ylim(-1000,6000)
            plt.ylabel('position')
            plt.xlabel('time since session start (sec)')

            plt.pause(pltDelay)

            # clean up plot data (memory managment)

            arduinoTime=[]
            positions=[]
            arStates=[]
            lickValues=[]
            currentTrial=currentTrial+1
            print('trial done')
            arduino.write(struct.pack('>B', 1))
            while currentState==13:
                stateIt=0
                cR=arduino.readline().strip().decode()
                cR=cR.split(',')
                currentState=int(cR[streamNum_state])          
    except:
        print(dPos)
        print('EXCEPTION: peace out bitches')
        print('last trial = {} and the last state was {}. I will try to save last trial ...'.format(currentTrial,currentState))
        arduino.write(struct.pack('>B', 0))
        savedata([arduinoTime,positions,arStates,lickValues])
        print('save was a success; now I will close com port and quit')
        arduino.close()
        arduinoTime=[]
        positions=[]
        arStates=[]
        lickValues=[]
        exit()


print('NORMAL: peace out bitches')
print('I completed {} trials.'.format(currentTrial-1))
arduino.write(struct.pack('>B', 0))
arduino.close()
exit()