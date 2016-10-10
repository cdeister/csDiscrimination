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
import os
#----------------------------------------------------------------------------------------------------

# # # # # # # # # # # # # # # # # # # # # # # # 
# Flow Variables: USERS WILL EDIT *****       #
# # # # # # # # # # # # # # # # # # # # # # # #

animalString = 'testAnimal'
segPlot=500
totalTrials=4
maxTrialTime=1
minTime=1
dataCount=3   # how many data streams are we saving? (todo: do i still use this)
pltDelay=0.0000001 # this can be changed, but doesn't need to be. We have to have a plot delay, but it can be tiny.
comPort='/dev/cu.usbmodem1411'
baudRate=9600
uiUpdateDelta=5


#----------------------------------------------------------------------------------------------------

# # # # # # # # # # # # # # # # # # # # # # # # # # #
# initialize data containers and session Variables  #
# # # # # # # # # # # # # # # # # # # # # # # # # # #

positions=[]            # This is the x-position of an optical mouse attached to a USB host shield
arStates=[]             # Store the state the arduino thinks it is in.
arduinoTime=[]          # This is the time as reported by the arduino, which resets every trial. 

arState=0  #todo: change this to curState
currentTrial=1

# These are variables that can change if the task is altered.
# We name the data streams so that we can change their order easier if needed. 
# They are position indicides that we use to parse the serial lines. 
streamNum_header=0
streamNum_time=1
streamNum_position=2
streamNum_state=3
lowDelta=0

#----------------------------------------------------------------------------------------------------

# # # # # # # # # # # # # # # # # # # # # # # # 
# Functions and Dynamic Variables             #
# # # # # # # # # # # # # # # # # # # # # # # #
dateStr = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M')

def savedata(dataList):
    exportArray=numpy.array(dataList)
    numpy.savetxt('{}_{}_trial_{}.csv'.format(animalString,dateStr,currentTrial), exportArray, delimiter=",",fmt="%f")


#def update_posPlot(): (todo: make the plotting functions)

#----------------------------------------------------------------------------------------------------

# # # # # # # # # # # # # # # # # # # # # # # # 
# Plotting and State-Specific Variables       #
# # # # # # # # # # # # # # # # # # # # # # # #

# ----- (Start) Plotting variables
stateDiagX=[0,1,2,3,3,4,4,0]
stateDiagY=[0,2,2,1,3,1,3,4]
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
arduino.write(b'0')


# Start the task (will iterate through trials)
while currentTrial<=totalTrials:
    try:
        #S0 -----> hand shake (initialization state)
        if arState==0:
            arduino.flush() # I don't know if this is needed.
            cR=arduino.readline().decode().strip()
            cR=cR.split(',')
            # We are waiting until we get a good serial read (should start with data)
            if cR[streamNum_header]=='data':
                if stateIt==0:
                    print('found some dope shit on rx')
                    print('... wait while I make sure it''s ready')
                    stateIt=1
                    # update plots (todo: make this a function all states use it)
                    plt.subplot(3,2,1)
                    linesA=plt.plot(positions[-segPlot:-1],'k-')
                    plt.ylim(-1000,6000)
                    plt.xlim(0,segPlot)
                    plt.ylabel('position')
                    plt.xlabel('time since session start (sec)')

                    plt.subplot(3,2,2)
                    linesD=plt.plot(positions[-segPlot:-1],'k-')
                    plt.ylim(-1000,6000)
                    plt.xlim(0,segPlot)
                    plt.ylabel('position')
                    plt.xlabel('time since session start (sec)')

                    plt.subplot(3,2,5)
                    linesB=plt.plot(stateDiagX,stateDiagY,'ro',markersize=smMrk)
                    linesC=plt.plot(stateDiagX[arState],stateDiagY[arState],'go',markersize=lrMrk)
                    plt.ylim(min(stateDiagY)-1,max(stateDiagY)+1)
                    plt.xlim(min(stateDiagX)-1,max(stateDiagX)+1)
                    plt.title(currentTrial)

                    plt.subplot(3,2,6)

                    plt.pause(pltDelay)

                    # clean up plot data (memory managment)
                    linesA.pop(0).remove()
                    linesB.pop(0).remove()
                    linesC.pop(0).remove()
                    linesD.pop(0).remove()

                ttd=abs(tt1[1]-tt1[0])
                tt1[0]=tt1[1]
                tt1[1]=float(int(cR[streamNum_time])/1000)
                if ttd<0.1:
                    lowDelta=lowDelta+1
                    if lowDelta>40:
                        print('should be good; will take you to wait state (S1)')
                        arduino.write(b'1')
                        while arState==0:
                            stateIt=0
                            cR=arduino.readline().strip().decode()
                            cR=cR.split(',')
                            arState=int(cR[streamNum_state])

        #S1 -----> trial wait state
        #
        # entry conditions: S0->S1 or S7->S1
        # exit contisions: needs to be still for 2 seconds
        #
        elif arState==1:
            # general state code
            arduino.flush()
            cR=arduino.readline().strip().decode()
            cR=cR.split(',')
            if cR[streamNum_header]=='data':
                arState=int(cR[streamNum_state])
                arduinoTime.append(float(int(cR[streamNum_time])/1000))
                positions.append(float(cR[streamNum_position]))
                arStates.append(arState)

                # we do certain things if we just entered, this is the flag for that.
                if stateIt==0:
                    print('in state 1')
                    cycleCount=1
                    stateIt=1

                uiUpdate=int(cycleCount) % int(uiUpdateDelta)

                if uiUpdate==0:
                    # update plots (todo: make this a function all states use it)
                    plt.subplot(3,2,1)
                    linesA=plt.plot(positions[-segPlot:-1],'k-')
                    plt.ylim(-1000,6000)
                    plt.xlim(0,segPlot)
                    plt.ylabel('position')
                    plt.xlabel('time since session start (sec)')

                    # update plots (todo: make this a function all states use it)
                    plt.subplot(3,2,2)
                    linesD=plt.plot(positions[-segPlot:-1],'k-')
                    plt.ylim(-1000,6000)
                    plt.xlim(0,segPlot)
                    plt.ylabel('position')
                    plt.xlabel('time since session start (sec)')

                    plt.subplot(3,2,5)
                    linesB=plt.plot(stateDiagX,stateDiagY,'ro',markersize=smMrk)
                    linesC=plt.plot(stateDiagX[arState],stateDiagY[arState],'go',markersize=lrMrk)
                    plt.ylim(min(stateDiagY)-1,max(stateDiagY)+1)
                    plt.xlim(min(stateDiagX)-1,max(stateDiagX)+1)
                    plt.title(currentTrial)


                    plt.pause(pltDelay)

                    # clean up plot data (memory managment)
                    linesA.pop(0).remove()
                    linesB.pop(0).remove()
                    linesC.pop(0).remove()
                    linesD.pop(0).remove()

                    cycleCount=0

                # S1 specific stuff
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
                        arduino.write(b'2')
                        print('Still! ==> Out of wait')
                        while arState==1:
                            stateIt=0
                            cR=arduino.readline().strip().decode()
                            cR=cR.split(',')
                            arState=int(cR[streamNum_state])
                cycleCount=cycleCount+1;


        #S2 -----> trial initiation state
        #
        # entry conditions: S1->S2
        # exit contisions: needs to wait for a cue then walk some distance
        #
        elif arState==2:
            arduino.flush()
            cR=arduino.readline().strip().decode()
            cR=cR.split(',')
            if cR[0]=='data':
                arState=int(cR[3])
                arduinoTime.append(float(int(cR[1])/1000))
                positions.append(float(cR[2]))
                arStates.append(arState)

                if stateIt==0:
                    print('in state 2')
                    cycleCount=1;
                    stateIt=1;

                uiUpdate=int(cycleCount) % int(uiUpdateDelta)

                if uiUpdate==0:
                    # update plots (todo: make this a function all states use it)
                    plt.subplot(3,2,1)
                    linesA=plt.plot(positions[-segPlot:-1],'k-')
                    plt.ylim(-1000,6000)
                    plt.xlim(0,segPlot)
                    plt.ylabel('position')
                    plt.xlabel('time since session start (sec)')

                    # update plots (todo: make this a function all states use it)
                    plt.subplot(3,2,2)
                    linesD=plt.plot(positions[-segPlot:-1],'k-')
                    plt.ylim(-1000,6000)
                    plt.xlim(0,segPlot)
                    plt.ylabel('position')
                    plt.xlabel('time since session start (sec)')


                    plt.subplot(3,2,5)
                    linesB=plt.plot(stateDiagX,stateDiagY,'ro',markersize=smMrk)
                    linesC=plt.plot(stateDiagX[arState],stateDiagY[arState],'go',markersize=lrMrk)
                    plt.ylim(min(stateDiagY)-1,max(stateDiagY)+1)
                    plt.xlim(min(stateDiagX)-1,max(stateDiagX)+1)
                    plt.title(currentTrial)


                    plt.pause(pltDelay)

                    # clean up plot data (memory managment)
                    linesA.pop(0).remove()
                    linesB.pop(0).remove()
                    linesC.pop(0).remove()
                    linesD.pop(0).remove()

                    cycleCount=0

                if positions[-1]>distThr:
                    arduino.write(b'3')
                    print('moved to spout')
                    while arState==2:
                        stateIt=0
                        cR=arduino.readline().strip().decode()
                        cR=cR.split(',')
                        arState=int(cR[streamNum_state])

                cycleCount=cycleCount+1;


        #S3 -----> stim state 1
        elif arState==3:
            arduino.flush()
            cR=arduino.readline().strip().decode()
            cR=cR.split(',')
            if cR[0]=='data':
                arState=int(cR[3])
                arduinoTime.append(float(int(cR[1])/1000))
                positions.append(float(cR[2]))
                arStates.append(arState)

                if stateIt==0:
                    print('in state 3')
                    cycleCount=1;
                    stateIt=1;

                uiUpdate=int(cycleCount) % int(uiUpdateDelta)

                if uiUpdate==0:
                    # update plots (todo: make this a function all states use it)
                    plt.subplot(3,2,1)
                    linesA=plt.plot(positions[-segPlot:-1],'k-')
                    plt.ylim(-1000,6000)
                    plt.xlim(0,segPlot)
                    plt.ylabel('position')
                    plt.xlabel('time since session start (sec)')

                    # update plots (todo: make this a function all states use it)
                    plt.subplot(3,2,2)
                    linesD=plt.plot(positions[-segPlot:-1],'k-')
                    plt.ylim(-1000,6000)
                    plt.xlim(0,segPlot)
                    plt.ylabel('position')
                    plt.xlabel('time since session start (sec)')



                    plt.subplot(3,2,5)
                    linesB=plt.plot(stateDiagX,stateDiagY,'ro',markersize=smMrk)
                    linesC=plt.plot(stateDiagX[arState],stateDiagY[arState],'go',markersize=lrMrk)
                    plt.ylim(min(stateDiagY)-1,max(stateDiagY)+1)
                    plt.xlim(min(stateDiagX)-1,max(stateDiagX)+1)
                    plt.title(currentTrial)


                    plt.pause(pltDelay)

                    # clean up plot data (memory managment)
                    linesA.pop(0).remove()
                    linesB.pop(0).remove()
                    linesC.pop(0).remove()
                    linesD.pop(0).remove()

                    cycleCount=0

                if positions[-1]>2000:
                    arduino.write(b'7')
                    print('met condition a')
                    while arState==3:
                        stateIt=0
                        cR=arduino.readline().strip().decode()
                        cR=cR.split(',')
                        arState=int(cR[streamNum_state])

                if positions[-1]<-200:
                    arduino.write(b'2')
                    print('met condition b')
                    while arState==3:
                        stateIt=0
                        cR=arduino.readline().strip().decode()
                        cR=cR.split(',')
                        arState=int(cR[streamNum_state])

                cycleCount=cycleCount+1;
        

        # ----------------- (S7: save state)
        elif arState==7:
            print('entered save state') # debug
            savedata([arduinoTime,positions,arStates])
            if currentTrial>1:
                linesE.pop(0).remove()
            plt.subplot(3,2,6)
            linesE=plt.plot(positions,'r-')
            plt.ylim(-1000,6000)
            plt.ylabel('position')
            plt.xlabel('time since session start (sec)')

            plt.pause(pltDelay)

            # clean up plot data (memory managment)

            arduinoTime=[]
            positions=[]
            arStates=[]
            currentTrial=currentTrial+1
            print('trial done')
            arduino.write(b'1')
            while arState==7:
                stateIt=0
                cR=arduino.readline().strip().decode()
                cR=cR.split(',')
                arState=int(cR[streamNum_state])          
    except:
        print(dPos)
        print('EXCEPTION: peace out bitches')
        print('last trial = {} and the last state was {}. I will try to save last trial ...'.format(currentTrial,arState))
        arduino.write(b'0')
        savedata([arduinoTime,positions,arStates])
        print('save was a success; now I will close com port and quit')
        arduino.close()
        arduinoTime=[]
        positions=[]
        arStates=[]
        exit()


print('NORMAL: peace out bitches')
print('I completed {} trials.'.format(currentTrial-1))
arduino.write(b'0')
arduino.close()
exit()
