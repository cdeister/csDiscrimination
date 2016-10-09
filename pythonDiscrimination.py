# pythonDiscrimination:
# This is a python script that runs sensory discrimination tasks in a state-based manner.
# It works with microcontrolors. It can easily be modified to suit different needs.
#
# version 2.0
# 10/04/2016
# questions? --> Chris Deister --> cdeister@Bbrown.edu
#

# includes
#
import serial
import numpy
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import time
import datetime
import os
#----------------------------------------------------------------------------------------------------

# # # # # # # # # # # # # # # # # # # # # # # # 
# Flow Variables: USERS WILL EDIT *****       #
# # # # # # # # # # # # # # # # # # # # # # # #

animalString = 'testAnimal'
segPlot=100
totalTrials=4
maxTrialTime=1
minTime=1
dataCount=3   # how many data streams are we saving? (todo: do i still use this)
pltDelay=0.00001 # this can be changed, but doesn't need to be. We have to have a plot delay, but it can be tiny.
comPort='/dev/cu.usbmodem1411'
baudRate=9600


#----------------------------------------------------------------------------------------------------

# # # # # # # # # # # # # # # # # # # # # # # # # # #
# initialize data containers and session Variables  #
# # # # # # # # # # # # # # # # # # # # # # # # # # #

positions=[]            # This is the x-position of an optical mouse attached to a USB host shield
arStates=[]             # Store the state the arduino thinks it is in.
arduinoTime=[]          # This is the time as reported by the arduino, which resets every trial. 
arduinoStateTimes=[]    # This is the arduino reported time but corrected for the start of the state.

arState=0  #todo: change this to curState
currentTrial=1

# These are variables that can change if the task is altered.
# We name the data streams so that we can change their order easier if needed. 
# They are position indicides that we use to parse the serial lines. 
streamNum_header=0
streamNum_time=1
streamNum_position=2
streamNum_state=3

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
distThr=1000;  # This is the distance the mouse needs to move to initiate a stimulus trial.


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
        # Step through states ...


        #S0 -----> hand shake (initialization state)
        if arState==0:
            arduino.flush() # I don't know if this is needed.
            cR=arduino.readline().decode().strip()
            cR=cR.split(',')
            # We are waiting until we get a good serial read (should start with data)
            if len(cR)==dataCount+1: #(todo: unnecessary)
                if cR[streamNum_header]=='data':
                    print('found some dope shit on rx')
                    arduino.readline()
                    arduino.write(b'1')
                    arState=int(cR[streamNum_state])
                    print(arState)

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
                    stateStart=arduinoTime[-1]
                    stateIt=1;

                arduinoStateTimes.append(float(int(cR[streamNum_time])/1000)-stateStart)

                # update plots (todo: make this a function all states use it)
                plt.subplot(3,1,1)
                linesA=plt.plot(arduinoTime[-segPlot:-1],positions[-segPlot:-1],'k-')
                plt.ylim(-1000,2000)
                plt.ylabel('position')
                plt.xlabel('time since session start (sec)')

                plt.subplot(3,2,1)
                linesD=plt.plot(arduinoTime[-segPlot:-1],positions[-segPlot:-1],'k-')
                plt.ylim(-1000,2000)
                plt.ylabel('lick rate (not yet)')
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
    

                # S1 specific stuff
                # we are going to wait for the animal to be still for some specific time.
                if arduinoStateTimes[-1]>2:
                    dPos=abs(positions[-1]-positions[-2])

                    if dPos>movThr and stillLatch==1:
                        stillLatch=0


                    if dPos<=movThr and stillLatch==0:
                        stillTimeStart=arduinoStateTimes[-1]
                        stillLatch=1


                    if dPos<=movThr and stillLatch==1:
                        stillTime=arduinoStateTimes[-1]-stillTimeStart

                    if stillLatch==1 and stillTime>1:
                        stateIt=0
                        arduino.write(b'2')
                        print('out of wait')






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
                    stateStart=arduinoTime[-1]
                    stateIt=1;

                arduinoStateTimes.append(float(int(cR[streamNum_time])/1000)-stateStart)


                plt.subplot(3,1,1)
                linesA=plt.plot(arduinoTime[-segPlot:-1],positions[-segPlot:-1],'k-')
                plt.ylim(-1000,2000)
                plt.ylabel('position')
                plt.xlabel('time since session start (sec)')


                plt.subplot(3,2,5)
                linesB=plt.plot(stateDiagX,stateDiagY,'ro',markersize=smMrk)
                linesC=plt.plot(stateDiagX[arState],stateDiagY[arState],'go',markersize=lrMrk)
                plt.ylim(min(stateDiagY)-1,max(stateDiagY)+1)
                plt.xlim(min(stateDiagX)-1,max(stateDiagX)+1)
                plt.title(currentTrial)

                plt.pause(pltDelay)


                linesA.pop(0).remove()
                linesB.pop(0).remove()
                linesC.pop(0).remove()

                if positions[-1]>distThr:
                    stateIt=0
                    arduino.write(b'3')
                    print(arState)


        # ----------------- state 1 trial wait state
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
                    stateStart=arduinoTime[-1]
                    stateIt=1;

                arduinoStateTimes.append(float(int(cR[streamNum_time])/1000)-stateStart)


                plt.subplot(3,1,1)
                linesA=plt.plot(arduinoTime[-segPlot:-1],positions[-segPlot:-1],'k-')
                plt.ylim(-1000,2000)
                plt.ylabel('position')
                plt.xlabel('time since session start (sec)')


                plt.subplot(3,2,5)
                linesB=plt.plot(stateDiagX,stateDiagY,'ro',markersize=smMrk)
                linesC=plt.plot(stateDiagX[arState],stateDiagY[arState],'go',markersize=lrMrk)
                plt.ylim(min(stateDiagY)-1,max(stateDiagY)+1)
                plt.xlim(min(stateDiagX)-1,max(stateDiagX)+1)
                plt.title(currentTrial)

                plt.pause(pltDelay)


                linesA.pop(0).remove()
                linesB.pop(0).remove()
                linesC.pop(0).remove()
                if positions[-1]>2000:
                    arduino.write(b'7')
                    print('met condition a')
                if positions[-1]<-200:
                    stateIt=0
                    arduino.write(b'2')
                    print('met condition b')
        

        # ----------------- (S7: save state)
        elif arState==7:
            print('entered save state') # debug
            arduino.flush()
            cR=arduino.readline().strip().decode()
            cR=cR.split(',')
            if cR[0]=='data':
                arState=int(cR[3])
                arduinoTime.append(float(int(cR[1])/1000))
                positions.append(float(cR[2]))
                arStates.append(arState)

                if stateIt==0:
                    stateStart=arduinoTime[-1]
                    stateIt=1;

                arduinoStateTimes.append(float(int(cR[streamNum_time])/1000)-stateStart)


                plt.subplot(3,1,1)
                linesA=plt.plot(arduinoTime[-segPlot:-1],positions[-segPlot:-1],'k-')
                plt.ylim(-1000,2000)
                plt.ylabel('position')
                plt.xlabel('time since session start (sec)')


                plt.subplot(3,2,5)
                linesB=plt.plot(stateDiagX,stateDiagY,'ro',markersize=smMrk)
                linesC=plt.plot(stateDiagX[arState],stateDiagY[arState],'go',markersize=lrMrk)
                plt.ylim(min(stateDiagY)-1,max(stateDiagY)+1)
                plt.xlim(min(stateDiagX)-1,max(stateDiagX)+1)
                plt.title(currentTrial)

                plt.pause(pltDelay)

                linesA.pop(0).remove()
                linesB.pop(0).remove()
                linesC.pop(0).remove()

                savedata([arduinoTime,positions,arStates])
                # iterate the trial number

                currentTrial=currentTrial+1
                # then flush data
                arduinoTime=[]
                positions=[]
                arStates=[]
                print('trial done')
                # then transition to wait state
                stateIt=0
                arduino.write(b'1')
                time.sleep(0.01)  # do i need this?
                print(arState)    # debug               

    except:
        print(dPos)
        print('EXCEPTION: peace out bitches')
        print('last trial = {} and the last state was {}. I will try to save last trial ...'.format(currentTrial,arState))
        arduino.write(b'0')
        savedata([arduinoTime,positions,arStates])
        print('save was a success; now I will close com port and quit')
        arduino.close()
        exit()


print('NORMAL: peace out bitches')
print('I completed {} trials.'.format(currentTrial-1))
arduino.write(b'0')
arduino.close()
exit()
