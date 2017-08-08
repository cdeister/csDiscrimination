# pyDiscrim:
# A Python 3 program that interacts with a microcontroller to perform state-based behavioral tasks.
#
# Version 3.99 -- Significant Trial Plot Improvements
# > Can now resize all trial plots on the fly.
# > Refactoring of line & axes code.
# > Repositioned some stuff
# questions? --> Chris Deister --> cdeister@brown.edu


from tkinter import *
import tkinter.filedialog as fd
import serial
import numpy as np
import matplotlib 
import matplotlib.mlab as mlab
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt
import time
import datetime
import random
import struct
import sys
import os
import pandas as pd
import scipy.stats as stats

class pdUtil:

    def getPath(self):

        self.selectPath = fd.askdirectory(title =\
            "what what?")

    def getFilePath(self):

        self.selectPath = fd.askopenfilename(title =\
            "what what?",defaultextension='.csv')

    def setSessionPath(self):
        dirPathFlg=os.path.isdir(self.dirPath.get())
        if dirPathFlg==False:
            os.mkdir(self.dirPath)
        self.dirPath.set(self.dirPath)
        self.setSesPath=1

    def mapAssign(self,l1,l2):
        for x in range(0,len(l1)):
            if type(l2[x])==int:
                exec('self.{}=int({})'.format(l1[x],l2[x])) 
            elif type(l2[x])==float:
                exec('self.{}=float({})'.format(l1[x],l2[x])) 

    def mapAssignStringEntries(self,l1,l2):
        for x in range(0,len(l1)):
            a=[l2[x]]
            exec('self.{}.set(a[0])'.format(l1[x]))

    def refreshVars(self,varLabels,varValues,refreshType):
        
        if refreshType==0: #reset
            pdUtil.mapAssign(self,varLabels,varValues)

        if refreshType==1: #refresh from entries
            for x in range(0,len(varLabels)):
                a=eval('float(self.{}_tv.get())'.format(varLabels[x]))
                if a.is_integer():
                    a=int(a)
                eval('self.{}_tv.set("{}")'.format(varLabels[x],str(a)))
                varValues[x]=a

            pdUtil.mapAssign(self,varLabels,varValues)
        
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
        pdUtil.mapAssignStringEntries(self,varNames,varVals)

    def exportAnimalMeta(self):
        self.metaNames=[\
        'comPath','dirPath','animalIDStr','totalTrials','sampsToPlot',\
        'uiUpdateSamps','ux_adaptThresh','lickValuesOrDeltas',\
        'lickThresholdStrValA','lickThresholdStrValB',\
        'lickPlotMax','currentSessionTV']
        sesVarVals=[self.comPath.get(),self.dirPath.get(),\
        self.animalIDStr.get(),self.totalTrials.get(),\
        self.sampsToPlot.get(),self.uiUpdateSamps.get(),\
        self.ux_adaptThresh.get(),self.lickValuesOrDeltas.get(),\
        self.lickThresholdStrValA.get(),self.lickThresholdStrValB.get(),\
        self.lickPlotMax.get(),self.currentSessionTV.get()]
        self.animalMetaDF=pd.DataFrame([sesVarVals],columns=self.metaNames)
        self.animalMetaDF.to_csv('{}{}_animalMeta.csv'.\
            format(self.dirPath.get() + '/',self.animalIDStr.get()))

class pdVariables:

    def setStateNames(self):
        self.stateNames=\
        ['bootState','waitState','initiationState','cue1State',\
        'cue2State','stim1State','stim2State','catchState','saveState',\
        'rewardState','rewardState2','neutralState','punishState',\
        'endState','defaultState']

        self.stateIDs=[0,1,2,3,4,5,6,7,13,21,22,23,24,25,29]
        pdUtil.mapAssign(self,self.stateNames,self.stateIDs)
        self.stateBindings=pd.Series(self.stateIDs,index=self.stateNames)

    def setSessionVars(self):
        # session vars
        self.sessionVarIDs=['ranTask','trialDataExists','sessionDataExists',\
        'comObjectExists','taskProbsRefreshed','stateVarsRefreshed',\
        'currentTrial','currentState','currentSession','sessionTrialCount']
        self.sessionVarVals=[0,0,0,0,0,0,1,0,1,1]
        pdUtil.mapAssign(self,self.sessionVarIDs,self.sessionVarVals)

    def setStateVars(self):
        self.stateVarLabels=['acelValThr','acelSamps','distThr',\
        'timeOutDuration','waitStillTime','genStillTime','cue1Dur','cue2Dur',\
        'biasRange','shapeC1_LPortProb','shapeC2_LPortProb','biasPCut','biasMuCut',\
        'lBiasDelta','rBiasDelta']

        self.stateVarValues=[10,100,100,2,1,1,1.5,1.5,10,0.5,0.5,0.1,0.05,0.10,0.10]
        pdUtil.mapAssign(self,self.stateVarLabels,self.stateVarValues)

    def setTaskProbs(self):
        self.t1ProbLabels='sTask1_prob','sTask1_target_prob',\
            'sTask1_distract_prob','sTask1_target_reward_prob',\
            'sTask1_target_punish_prob','sTask1_distract_reward_prob',\
            'sTask1_distract_punish_prob'
        self.t1ProbValues=[0.5,0.5,0.5,1.0,0.0,0.0,1.0]
        pdUtil.mapAssign(self,self.t1ProbLabels,self.t1ProbValues)

        self.t2ProbLabels='sTask2_prob','sTask2_target_prob',\
        'sTask2_distract_prob','sTask2_target_reward_prob',\
        'sTask2_target_punish_prob','sTask2_distract_reward_prob',\
        'sTask2_distract_punish_prob'
        self.t2ProbValues=[0.5,0.5,0.5,1.0,0.0,0.0,1.0]
        pdUtil.mapAssign(self,self.t2ProbLabels,self.t2ProbValues)

class pdSerial:

    def syncSerial(self):
        ranHeader=0
        self.trialDataExists=0
        while ranHeader==0:
            gaveFeedback=0
            ranHeader=1
            loopCount=0
        while ranHeader==1:
            self.comObj.write(struct.pack('>B', self.bootState))
            pdSerial.serial_readDataFlush(self)
            if self.serDataAvail==1:
                self.currentState=int(self.sR[self.stID_state])
                if self.currentState!=self.bootState:
                    if gaveFeedback==0:
                        print('mc state is not right, \
                            thinks it is #: {}'.format(self.currentState))
                        print('will force boot state, \
                            might take a second or so ...')
                        print('!!!! ~~> UI may become \
                            unresponsive for 1-30 seconds or so, \
                            but I havent crashed ...')
                        gaveFeedback=1
                    loopCount=loopCount+1
                    if loopCount % 5000 ==0:
                        print('still syncing: state #: {}; loop #: \
                            {}'.format(self.currentState,loopCount))
                elif self.currentState==self.bootState:
                    print('ready: mc is in state #: {}'\
                        .format(self.currentState))
                    return

    def serial_initComObj(self):
        if self.comObjectExists==0:
            print('Opening serial port: {}'.format(self.comPath.get()))
            self.comObj = serial.Serial(self.comPath.get(),\
                self.baudSelected.get()) 
            pdSerial.syncSerial(self)
            self.comObjectExists=1


            # update the GUI
            self.comPathLabel.config(text="COM Object Connected ***",\
                justify=LEFT,fg="green",bg="black") 
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
            if self.trialDataExists==1:
                pdData.data_saveTrialData(self)
            pdSerial.syncSerial(self)
            self.comObj.close()
            self.comObjectExists=0
            print('> i closed the COM object')
            
            # update the GUI
            self.comPathLabel.config(text="COM Port Location:",\
                justify=LEFT,fg="black",bg="white")
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
        pdSerial.serial_readData(self,'data')

    def serial_readData(self,header):
        self.sR=self.comObj.readline().strip().decode()
        self.sR=self.sR.split(',')
        #todo: abstract length below:
        if len(self.sR)==7 and self.sR[self.stID_header]==header \
        and str.isnumeric(self.sR[1])==1 and str.isnumeric(self.sR[2])==1 :
            self.serDataAvail=1
        elif len(self.sR)!=7 or self.sR[self.stID_header] != header \
        or str.isnumeric(self.sR[1])!=1 or str.isnumeric(self.sR[2])!=1:
            self.serDataAvail=0

class pdData:

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

    def data_sessionContainers(self):
        self.sessionDataExists=0
        self.rewardContingency=[] 
        self.trialOutcome=[]
        self.PooledTasks=[]

        self.cuePresented=[];
        self.sStims=[];
        self.sRewardTarget=[];
        self.sPunishTarget=[];
        self.sOutcome=[]; 
        self.trialSampRate=[]
        self.trialTimes=[]
        self.rcCol=[]
        self.toCol=[]
        self.shapingReport=[]
        self.waitLicks0=[]
        self.waitLicks1=[]
        self.stimLicks0=[]
        self.stimLicks1=[]
        self.waitConditionMetTime=[]
        self.cue1Time=[]
        self.cue2Time=[]
        self.trialLeft1Prob=[]
        self.trialLeft2Prob=[]

    def data_trialContainers(self):
        self.trialDataExists=0
        # state & timing
        self.arStates=[]          
        self.mcTrialTime=[]
        self.mcStateTime=[]

        # motion
        self.stillTime=[]
        self.motionTime=[]
        self.lastPos=0
        self.lastOrientation=0  
        self.absolutePosition=[]
        self.orientation=[]
        self.posDelta=[]
        self.anState_acceleration=[]
        self.pdAnalysis_acelThreshold=[]
        self.pdAnalysis_distanceThreshold=[]

        # lick vars
        self.lickThresholdLatchA=0
        self.lickThresholdLatchB=0
        self.lastLickCountA=0
        self.lastLickCountB=0
        self.lickValsA=[]
        self.lickValsB=[]
        self.thrLicksA=[]
        self.thrLicksB=[]
        self.stateLickCount0=[]
        self.stateLickCount1=[]
        
        # debug/time roundtrips
        self.pyStatesRS = []
        self.pyStatesRT = []
        self.pyStatesTT = []
        self.pyStatesTS = []
         
    def data_parseData(self):
        self.mcTrialTime.append(float(int(\
            self.sR[self.stID_time])/self.timeBase))
        self.mcStateTime.append(float(int(\
            self.sR[self.stID_trialTime])/self.timeBase))

        
        cOr=int(self.sR[self.stID_pos])

        cTheta=cOr-self.lastOrientation
        
        rollCorrectTheta=cTheta
        
        if cTheta>250: # rolled from 180 to -180 (pos to neg)
            
            rollCorrectTheta=(cTheta-180)*-1
        elif cTheta<-250: # rolled -180 over to positive
            
            rollCorrectTheta=(cTheta+180)*-1
        
        self.orientation.append(cOr)
        
        self.lastOrientation=self.orientation[-1]
        
        self.posDelta.append(rollCorrectTheta)
        
        self.absolutePosition.append(self.lastPos+rollCorrectTheta)
        self.lastPos=self.absolutePosition[-1]


        self.currentState=int(self.sR[self.stID_state])
        self.arStates.append(self.currentState)
        self.lickValsA.append(int(self.sR[self.stID_lickSensor_a]))
        self.lickValsB.append(int(self.sR[self.stID_lickSensor_b]))
        pdAnalysis.lickDetection(self)
        self.trialDataExists=1

    def data_saveTrialData(self):
        self.dateSvStr = datetime.datetime.fromtimestamp(time.time()).strftime('%H%M_%m%d%Y')

        saveStreams='mcTrialTime','mcStateTime','absolutePosition',\
        'posDelta','orientation','arStates','lickValsA','lickValsB',\
        'thrLicksA','thrLicksB','stateLickCount0','stateLickCount1',\
        'stillTime','motionTime','anState_acceleration',\
        'pdAnalysis_acelThreshold','pyStatesRS','pyStatesRT','pyStatesTS',\
        'pyStatesTT'


        self.tCo=[]
        for x in range(0,len(saveStreams)):
            exec('self.tCo=self.{}'.format(saveStreams[x]))
            if x==0:
                self.rf=pd.DataFrame({'{}'.format(saveStreams[x]):self.tCo})
            elif x != 0:
                self.tf=pd.DataFrame({'{}'.format(saveStreams[x]):self.tCo})
                self.rf=pd.concat([self.rf,self.tf],axis=1)

        self.rf.to_csv('{}{}_{}_s{}_trial_{}.csv'.\
            format(self.dirPath.get() + '/', self.animalIDStr.get(),\
                self.dateSvStr, self.currentSession, self.currentTrial))
        self.trialDataExists=0
    
    def data_saveSessionData(self):
        self.dateSvStr = datetime.datetime.fromtimestamp(time.time()).\
        strftime('%H%M_%m%d%Y')

        saveStreams='rewardContingency','trialOutcome','PooledTasks',\
        'cuePresented','sStims','sRewardTarget',\
        'sPunishTarget','sOutcome','trialTimes','rcCol',\
        'toCol','shapingReport','waitLicks0','waitLicks1',\
        'stimLicks0','stimLicks1','waitConditionMetTime',\
        'smoothedLickBias','difLicks','trialSampRate','trialLeft1Prob','trialLeft2Prob'

        self.tCo=[]
        for x in range(0,len(saveStreams)):
            exec('self.tCo=self.{}'.format(saveStreams[x]))
            if x==0:
                self.rf=pd.DataFrame({'{}'.format(saveStreams[x]):self.tCo})
            elif x != 0:
                self.tf=pd.DataFrame({'{}'.format(saveStreams[x]):self.tCo})
                self.rf=pd.concat([self.rf,self.tf],axis=1)

        self.rf.to_csv('{}{}_{}_s{}_sessionData.csv'.\
            format(self.dirPath.get() + '/', self.animalIDStr.get(),\
                self.dateSvStr, self.currentSession))
        self.sessionDataExists=0

class pdPlot:

    def taskPlotWindow(self):
        self.trialFramePosition='+370+0' # can be specified elsewhere
        self.updateTrialAxes=0
        self.statePlotMin=0
        self.statePlotMax=25
        
        self.distPlotMinVal=-400
        self.distPlotMaxVal=1200

        self.lickAMin=0
        self.lickAMax=1300

        self.trialFig = plt.figure(100,figsize=(6.5,5.7), dpi=100)
        self.trialFig.suptitle('state 0', fontsize=10)

        self.initX=np.arange(2000)
        self.initY=np.random.randint(5, size=2000)

        self.stateAxes=plt.subplot(221)
        self.stateAxes.set_ylabel('current state')
        self.stateAxes.set_ylim([self.statePlotMin,self.statePlotMax])
        self.stateAxes.set_xticks([])
        self.stateLine,=self.stateAxes.plot(self.initY,color="darkgreen")

        self.positionAxes=plt.subplot(222)
        self.positionAxes.set_ylabel('animal position')
        self.positionAxes.set_ylim([self.distPlotMinVal,self.distPlotMaxVal])
        self.positionAxes.set_xticks([])
        self.positionLine,=self.positionAxes.plot(self.initY,color="orchid",lw=2)
        self.positionThreshLine,=self.positionAxes.plot([0,2000],[100,100],color="black",lw=0.5)

        self.leftLickAxes=plt.subplot(223)
        self.leftLickAxes.set_ylabel('lick sensor values')
        self.leftLickAxes.set_title('left lick sensor')
        self.leftLickAxes.set_ylim([self.lickAMin,self.lickAMax])
        self.lickLeftValLine,=self.leftLickAxes.plot(self.initY,color="red")
        self.lickLeftThreshLine,=self.leftLickAxes.plot([0,2000],[600,600],color="black",lw=0.5)

        self.rightLickAxes=plt.subplot(224)
        self.rightLickAxes.set_yticks([])
        self.rightLickAxes.set_ylim([self.lickAMin,self.lickAMax])
        self.rightLickAxes.set_title('right lick sensor')
        self.lickRightValLine,=self.rightLickAxes.plot(self.initY,color="cornflowerblue")
        self.lickRightThreshLine,=self.rightLickAxes.plot([0,2000],[600,600],color="black",lw=0.5)

        mng = plt.get_current_fig_manager()
        eval('mng.window.wm_geometry("{}")'.format(self.trialFramePosition))
        plt.show(block=False)
        # we need to draw once before we set artists, so they can cache at init

        self.stateAxes.draw_artist(self.stateLine)
        self.stateAxes.draw_artist(self.stateAxes.patch)

        self.positionAxes.draw_artist(self.positionLine)
        self.positionAxes.draw_artist(self.positionThreshLine)
        self.positionAxes.draw_artist(self.positionAxes.patch)

        self.leftLickAxes.draw_artist(self.lickLeftValLine)
        self.leftLickAxes.draw_artist(self.lickLeftThreshLine)
        self.leftLickAxes.draw_artist(self.leftLickAxes.patch)

        self.rightLickAxes.draw_artist(self.lickRightValLine)
        self.rightLickAxes.draw_artist(self.lickRightThreshLine)
        self.rightLickAxes.draw_artist(self.rightLickAxes.patch)

        self.trialFig.canvas.flush_events()
        self.lastSplit=2000 #todo: why do i use this?

    def updateTaskPlot(self):
        splt=int(self.sampsToPlot.get())
        if splt != self.lastSplit:
            self.stateAxes.set_xlim([0,splt])
            self.positionAxes.set_xlim([0,splt])
            self.leftLickAxes.set_xlim([0,splt])
            self.rightLickAxes.set_xlim([0,splt])

        self.lastSplit=splt

        if self.updateTrialAxes==1:
            print('debug: a')
            self.stateAxes.set_ylim([self.statePlotMin,self.statePlotMax])
            print('debug: b')
            self.positionAxes.set_ylim([self.distPlotMinVal,self.distPlotMaxVal])
            print('debug: c')
            self.leftLickAxes.set_ylim([self.lickAMin,self.lickAMax])
            print('debug: d')
            self.rightLickAxes.set_ylim([self.lickAMin,self.lickAMax])
            print('debug: e')
            self.updateTrialAxes=0

        tLeftLickThr=int(self.lickThresholdStrValA.get())
        tRightLickThr=int(self.lickThresholdStrValB.get())

        stPltData=np.array(self.arStates[-int(splt):])
        posPltData=np.array(self.absolutePosition[-int(splt):])
        posThreshPltData=[self.distThr,self.distThr]
        lickLeftPltData=self.lickValsA[-int(splt):]
        lickLeftThreshData=[tLeftLickThr,tLeftLickThr]
        
        lickRightPltData=self.lickValsB[-int(splt):]
        lickRightThreshData=[tRightLickThr,tRightLickThr]
        x0=np.arange(len(stPltData))
        x1=[0,splt]
        
        np.random.seed()

        # update the line data
        self.stateLine.set_xdata(x0)
        self.stateLine.set_ydata(stPltData)

        self.positionLine.set_xdata(x0)
        self.positionLine.set_ydata(posPltData)
        self.positionThreshLine.set_xdata(x1)
        self.positionThreshLine.set_ydata(posThreshPltData)

        self.lickLeftValLine.set_xdata(x0)
        self.lickLeftValLine.set_ydata(lickLeftPltData)
        self.lickLeftThreshLine.set_xdata(x1)
        self.lickLeftThreshLine.set_ydata(lickLeftThreshData)

        self.lickRightValLine.set_xdata(x0)
        self.lickRightValLine.set_ydata(lickRightPltData)
        self.lickRightThreshLine.set_xdata(x1)
        self.lickRightThreshLine.set_ydata(lickRightThreshData)

        # make new line visual data
        self.stateAxes.draw_artist(self.stateLine)
        self.stateAxes.draw_artist(self.stateAxes.patch)

        self.positionAxes.draw_artist(self.positionLine)
        self.positionAxes.draw_artist(self.positionThreshLine)
        self.positionAxes.draw_artist(self.positionAxes.patch)

        self.leftLickAxes.draw_artist(self.lickLeftValLine)
        self.leftLickAxes.draw_artist(self.lickLeftThreshLine)
        self.leftLickAxes.draw_artist(self.leftLickAxes.patch)

        self.rightLickAxes.draw_artist(self.lickRightValLine)
        self.rightLickAxes.draw_artist(self.lickRightThreshLine)
        self.rightLickAxes.draw_artist(self.rightLickAxes.patch)

        # redraw and update
        self.trialFig.canvas.draw_idle()
        self.trialFig.canvas.flush_events()

    def resizeTaskPlot(self):

        self.resizeControlPosition='+610+660'
        resizeTrialPlotsFrame = Toplevel()
        eval('resizeTrialPlotsFrame.wm_geometry("{}")'.format(self.resizeControlPosition))

        resizeTrialPlotsFrame.title('Resize Trial Plots')
        self.resizeTrialPlotsFrame=resizeTrialPlotsFrame
        
        self.minLabel = Label(resizeTrialPlotsFrame, text="Min:",width=6).grid(row=0,column=1)
        self.maxLabel = Label(resizeTrialPlotsFrame, text="Max:",width=6).grid(row=0,column=2)

        stateRow=1
        self.stAxesLabel = Label(resizeTrialPlotsFrame, text="State:",width=6).grid(row=stateRow,column=0)
        self.stPlotMinTV=StringVar(resizeTrialPlotsFrame)
        self.stPlotMinTV.set(self.statePlotMin)
        self.stMinE=Entry(master=resizeTrialPlotsFrame,textvariable=self.stPlotMinTV,width=6)
        self.stMinE.grid(row=stateRow, column=1)
        self.stPlotMaxTV=StringVar(resizeTrialPlotsFrame)
        self.stPlotMaxTV.set(self.statePlotMax)
        self.stmxE=Entry(master=resizeTrialPlotsFrame,textvariable=self.stPlotMaxTV,width=6)
        self.stmxE.grid(row=stateRow, column=2)

        posRow=2
        self.dAxesLabel = Label(resizeTrialPlotsFrame, text="Position:",width=6).grid(row=posRow,column=0)
        self.distPlotMinTV=StringVar(resizeTrialPlotsFrame)
        self.distPlotMinTV.set(self.distPlotMinVal)
        self.dmnE=Entry(master=resizeTrialPlotsFrame,textvariable=self.distPlotMinTV,width=6)
        self.dmnE.grid(row=posRow, column=1)
        self.distPlotMaxTV=StringVar(resizeTrialPlotsFrame)
        self.distPlotMaxTV.set(self.distPlotMaxVal)
        self.dmxE=Entry(master=resizeTrialPlotsFrame,textvariable=self.distPlotMaxTV,width=6)
        self.dmxE.grid(row=posRow, column=2)

        lickRow=3
        self.lAxesLabel = Label(resizeTrialPlotsFrame, text="Lick:",width=6).grid(row=lickRow,column=0)
        self.lickPlotMinTV=StringVar(resizeTrialPlotsFrame)
        self.lickPlotMinTV.set(self.lickAMin)
        self.lkMinE=Entry(master=resizeTrialPlotsFrame,textvariable=self.lickPlotMinTV,width=6)
        self.lkMinE.grid(row=lickRow, column=1)
        self.lickPlotMaxTV=StringVar(resizeTrialPlotsFrame)
        self.lickPlotMaxTV.set(self.lickAMax)
        self.lkMaxE=Entry(master=resizeTrialPlotsFrame,textvariable=self.lickPlotMaxTV,width=6)
        self.lkMaxE.grid(row=lickRow, column=2)

        self.setAxesBtn = Button(master=resizeTrialPlotsFrame, text='Set', command=lambda:pdPlot.setAxesBtnCB(self))
        self.setAxesBtn.configure(width=6)
        self.setAxesBtn.grid(row=4, column=2)

    def setAxesBtnCB(self):

        self.statePlotMin=int(self.stPlotMinTV.get())
        self.statePlotMax=int(self.stPlotMaxTV.get())
        self.distPlotMinVal=int(self.distPlotMinTV.get())
        self.distPlotMaxVal=int(self.distPlotMaxTV.get())
        self.lickAMin=int(self.lickPlotMinTV.get())
        self.lickAMax=int(self.lickPlotMaxTV.get())

        self.updateTrialAxes=1

    def gaussian(self,xSpan, mu, sig):

        return np.exp(-np.power(xSpan - mu, 2.) / (2 * np.power(sig, 2.)))
        
    def smoothData(self,fKern,sData):
        ogMean=np.mean(sData)
        mid=int(len(fKern)*0.5)
        padRands=np.pad(sData,(mid,mid),'mean')
        smoothed=np.convolve(fKern,padRands)
        trimSmooth=smoothed[2*mid:(-2*mid)+1]
        newMean=np.mean(trimSmooth)
        trimSmooth=(trimSmooth-newMean)+ogMean
        return trimSmooth

    def makeSessionPlotWindow(self):
        # make and position the figure
        self.sessionFramePosition='+985+0' # can be specified elsewhere
        self.sessionFig = plt.figure(101,figsize=(6,6), dpi=80)
        self.sessionFig.suptitle('session stats', fontsize=10)
        mng = plt.get_current_fig_manager()
        eval('mng.window.wm_geometry("{}")'.format(self.sessionFramePosition))

        self.biasAxis=plt.subplot2grid((8,8), (0, 0), colspan=5,rowspan=4)
        self.biasLineNormCount,=self.biasAxis.plot([],[],marker="o",\
            markeredgecolor="cornflowerblue",markerfacecolor="none",lw=0)
        self.biasLineZero,=self.biasAxis.plot([0,int(self.totalTrials.get())],\
            [0,0],'k:')
        self.biasLineSmoothedBias,=self.biasAxis.plot([],[],'k-')
        # mess with axis params
        self.biasAxis.set_ylim([-1.6,1.6])
        self.biasAxis.set_xlim([0,int(self.totalTrials.get())])
        self.biasAxis.set_ylabel('left/right bias')
        self.biasAxis.set_xlabel('trial number')
        # plot once to cache, this allows artist to update later
        plt.show(block=False)
        # set artists (zero line doesn't update)
        self.biasAxis.draw_artist(self.biasLineNormCount)
        self.biasAxis.draw_artist(self.biasLineSmoothedBias)
        self.biasAxis.draw_artist(self.biasAxis.patch)

        self.figSc=[8,8]
        self.lcAxSc=[0,6]
        self.lcAxCR=[2,2]
        self.rcAxSc=[2,6]
        self.rcAxCR=[2,2]
        self.sdAxSc=[5,0]
        self.sdAxCR=[3,3]

        numBins=5
        self.leftCountAxis=plt.subplot2grid((self.figSc),(self.lcAxSc), \
            colspan=self.lcAxCR[0],rowspan=self.lcAxCR[0])
        n, binsl,patchesl=self.leftCountAxis.hist([],numBins,normed=1,facecolor='red',alpha=1)
        self.leftCountAxis.set_yticks([])
        self.leftCountAxis.set_xticks([])

        self.rightCountAxis=plt.subplot2grid((self.figSc),(self.rcAxSc),\
            colspan=self.rcAxCR[0],rowspan=self.rcAxCR[0])
        o,binsr,patchesr=self.rightCountAxis.hist([],numBins,normed=1,facecolor='cornflowerblue',alpha=1)
        self.rightCountAxis.set_yticks([])
        self.leftCountAxis.axis([0, 20, 0, 1])
        self.rightCountAxis.axis([0, 20, 0, 1])
        self.rightCountAxis.set_xlabel('lick counts')

        numBins=5
        self.sampDiffAxis=plt.subplot2grid((self.figSc),(self.sdAxSc), colspan=self.sdAxCR[0],rowspan=self.sdAxCR[1])
        p,binsp,patchesp=self.sampDiffAxis.hist([],numBins,normed=1,facecolor='darkviolet',alpha=1)
        self.sampDiffAxis.axis([0, 1, 0, 1])
        self.sampDiffAxis.set_xlabel('mean dt (ms)')

        plt.show(block=False)
        self.sessionFig.canvas.flush_events()

        # add a 'best fit' line
        # y = mlab.normpdf( bins, np.mean(x), np.std(x))
        # self.line12b, = self.ax12.plot(bins, y, 'k-', linewidth=1)
        
    def updateSessionPlot(self):
        normVMax=np.max(np.array(np.max(self.stimLicks0),np.max(self.stimLicks1)))
        normVMin=np.min(np.array(np.min(self.stimLicks0),np.min(self.stimLicks1)))
        normVal=np.max(np.array([np.abs(normVMax),np.abs(normVMin)]))
        self.difLicks=(np.array(self.stimLicks0/normVal)-np.array(self.stimLicks1/normVal))

        tKern=pdPlot.gaussian(self,np.linspace(-0.5, 0.5, self.biasRange+1), 0, 0.1)
        smtLB=pdPlot.smoothData(self,tKern,self.difLicks)
        self.smoothedLickBias=smtLB
        self.biasP=stats.ttest_1samp(self.smoothedLickBias[-self.biasRange:],0).pvalue
        print("%.4g" % self.biasP)

        x10=np.arange(len(self.difLicks))
        y10=self.difLicks
        x10c=np.arange(len(self.smoothedLickBias))
        y10c=self.smoothedLickBias

        self.biasLineNormCount.set_xdata(x10)
        self.biasLineNormCount.set_ydata(y10)
        self.biasLineSmoothedBias.set_xdata(x10c)
        self.biasLineSmoothedBias.set_ydata(y10c)
        self.biasAxis.draw_artist(self.biasLineNormCount)
        self.biasAxis.draw_artist(self.biasLineSmoothedBias)
        self.biasAxis.draw_artist(self.biasAxis.patch)
        self.biasAxis.set_title('bias p={}'.format("%.4g" % self.biasP))

        self.sessionFig.canvas.draw_idle()
        self.sessionFig.canvas.flush_events()
        

        numBins=10
        plt.sca(self.leftCountAxis)
        plt.cla()
        plt.sca(self.rightCountAxis)
        plt.cla()
        plt.sca(self.sampDiffAxis)
        plt.cla()

        self.leftCountAxis=plt.subplot2grid((self.figSc),(self.lcAxSc), \
            colspan=self.lcAxCR[0],rowspan=self.lcAxCR[0])
        n, binsl,patchesl=self.leftCountAxis.hist(np.nonzero(self.stimLicks0),\
            numBins,normed=1,facecolor='red',alpha=1)
        self.rightCountAxis=plt.subplot2grid((self.figSc),(self.rcAxSc),\
            colspan=self.rcAxCR[0],rowspan=self.rcAxCR[0])
        o,binsr,patchesr=self.rightCountAxis.hist(np.nonzero(self.stimLicks1),\
            numBins,normed=1,facecolor='cornflowerblue',alpha=1)
        self.leftCountAxis.set_yticks([])
        self.leftCountAxis.set_xticks([])
        self.rightCountAxis.set_yticks([])
        self.leftCountAxis.axis([0, 20, 0, 0.3])
        self.rightCountAxis.axis([0, 20, 0, 0.3])
        self.rightCountAxis.set_xlabel('lick counts')
        numBins=10
        self.sampDiffAxis=plt.subplot2grid((self.figSc),(self.sdAxSc), \
            colspan=self.sdAxCR[0],rowspan=self.sdAxCR[1])
        p,binsp,patchesp=self.sampDiffAxis.hist(np.array(self.trialSampRate)*100,numBins,\
            normed=1,facecolor='darkviolet',alpha=1)
        self.sampDiffAxis.axis([0, 1, 0, 1])
        self.sampDiffAxis.set_xlabel('mean dt (ms)')
        plt.show(block=False)
        self.sessionFig.canvas.flush_events()

class pdAnalysis:
    # todo: I think I should just enforce a pattern where all vartiables are treated as text variables. 
    # todo: point is I can safely assume here that the probs aren't updated anywhere else, but not necessarily true for all?
    # todo: this number formating is janktastic
    def shapingUpdateLeftRightProb(self):

        meanBias=np.mean(np.array(self.smoothedLickBias[-self.biasRange:]))
        print('mean bias={}'.format(meanBias)) # debug

        if self.biasP<self.biasPCut and meanBias>self.biasMuCut and (self.shapeC1_LPortProb>=self.lBiasDelta):  # leftward bias
            self.shapeC1_LPortProb=float("%.3g" % (self.shapeC1_LPortProb-self.lBiasDelta))
            self.shapeC2_LPortProb=self.shapeC1_LPortProb
            print('left bias detected; updated probs: {},{}'.format(self.shapeC1_LPortProb,self.shapeC2_LPortProb))

        elif self.biasP<self.biasPCut and meanBias<-self.biasMuCut and (self.shapeC1_LPortProb<=(1-self.rBiasDelta)):  # rightward bias
            self.shapeC1_LPortProb=float("%.3g" % (self.shapeC1_LPortProb+self.rBiasDelta))
            self.shapeC2_LPortProb=self.shapeC1_LPortProb
            print('right bias detected; updated probs: {},{}'.format(self.shapeC1_LPortProb,self.shapeC2_LPortProb))

        if self.shapeC1_LPortProb > 1.0: #todo: this is stupid; I should add the condition above, but ...
            self.shapeC1_LPortProb=1.0
            self.shapeC2_LPortProb=self.shapeC1_LPortProb

        if self.shapeC1_LPortProb <0.0: #todo: this is stupid; I should add the condition above, but ...
            self.shapeC1_LPortProb=0.0
            self.shapeC2_LPortProb=self.shapeC1_LPortProb

        self.shapeC1_LPortProb_tv.set("%.3g" % self.shapeC1_LPortProb) # make sure gui understands
        self.shapeC2_LPortProb_tv.set("%.3g" % self.shapeC2_LPortProb) # make sure gui understands
        

    def getQunat(self,pyList,quantileCut):

        tA=np.abs(np.array(pyList))

    def updateLickThresholdA(self,dataSpan):  
    #todo: should be one function for all

        if self.ux_adaptThresh.get()==1:
            tA=np.abs(np.array(dataSpan))
            self.lickThresholdStrValA.set(str(np.percentile(\
                tA[np.where(tA != 0)[0]],75)))
            self.lickMinMaxA=[min(dataSpan),max(dataSpan)]

    def updateLickThresholdB(self,dataSpan,quantileCut):

        if self.ux_adaptThresh.get()==1:
            tA=np.abs(np.array(dataSpan))
            self.lickThresholdStrValB.set(str(np.percentile(\
                tA[np.where(tA != 0)[0]],quantileCut)))
            self.lickMinMaxB=[min(dataSpan),max(dataSpan)]

    def lickDetection(self):
        aThreshold=int(self.lickThresholdStrValA.get())
        bThreshold=int(self.lickThresholdStrValB.get())
            
        if self.lickValsA[-1]>aThreshold and self.lickThresholdLatchA==0:
            self.thrLicksA.append(1)
            self.lastLickCountA=self.lastLickCountA+1
            self.stateLickCount0.append(self.lastLickCountA)
            
            self.lastLickA=self.mcTrialTime[-1]    
            self.lickThresholdLatchA=1
        
        elif self.lickValsA[-1]<=aThreshold or self.lickThresholdLatchA==1:
            self.thrLicksA.append(0)
            self.stateLickCount0.append(self.lastLickCountA)
            # self.lickThresholdLatchA=1;
            

        if self.lickValsB[-1]>bThreshold and self.lickThresholdLatchB==0:
            self.thrLicksB.append(1)
            self.lastLickCountB=self.lastLickCountB+1
            self.stateLickCount1.append(self.lastLickCountB)
            
            self.lastLickB=self.mcTrialTime[-1]
            self.lickThresholdLatchB=1
            

        elif self.lickValsB[-1]<=bThreshold or self.lickThresholdLatchB==1:
            self.thrLicksB.append(0)
            self.stateLickCount1.append(self.lastLickCountB)
            # self.lickThresholdLatchB=1;

        if self.lickThresholdLatchA and self.lickValsA[-1]<=aThreshold:
            self.lickThresholdLatchA=0;

        if self.lickThresholdLatchB and self.lickValsB[-1]<=bThreshold:
            self.lickThresholdLatchB=0;


    def lickDetectionDebug(self):

        if self.lickValsA[-1]>int(self.lickThresholdStrValA.get()):
            self.thrLicksA[-1]=1
            self.lastLickCountA=self.lastLickCountA+1
            self.stateLickCount0[-1]=self.lastLickCountA+1


        if self.lickValsB[-1]>int(self.lickThresholdStrValB.get()):
            self.thrLicksB[-1]=1
            self.lastLickCountB=self.lastLickCountB+1
            self.stateLickCount1[-1]=self.lastLickCountB+1

    def checkMotion(self,acelThr,sampThr):
        self.anState_acceleration.append(np.mean(np.array(\
            self.posDelta[-int(sampThr):])))
        self.pdAnalysis_acelThreshold.append(acelThr)
        if self.anState_acceleration[-1]<acelThr:
            lastLatch=self.stillLatch
            self.stillLatch=1
            latchDelta=self.stillLatch-lastLatch
            if latchDelta!=0:
                self.stillTimeStart=self.mcStateTime[-1]
            self.stillTime.append(self.mcStateTime[-1]-self.stillTimeStart)
            self.motionTime.append(0)
        elif self.anState_acceleration[-1]>=acelThr:
            lastLatch=self.stillLatch
            self.stillLatch=0
            latchDelta=lastLatch-self.stillLatch
            if latchDelta!=0:
                self.motionTimeStart=self.mcStateTime[-1]
            self.stillTime.append(0)
            self.motionTime.append(self.mcStateTime[-1]-self.motionTimeStart)

class pdState:

    def switchState(self,targetState):
        if self.currentState==targetState:
            print('no thanks; you chose the state you are in, no infinite loops for me :)')
            return
        self.targetState=targetState
        if self.trialDataExists==1:
            self.pyStatesRS.append(self.targetState)
            self.pyStatesRT.append(self.mcTrialTime[-1])
        print('pushing: s{} -> s{}'.format(self.currentState,targetState))
        self.comObj.write(struct.pack('>B', targetState))
        pdState.exitState(self,self.currentState)

    def exitState(self,cState): 
        self.cState=cState
        while self.currentState==self.cState:
            pdSerial.serial_readDataFlush(self)
            if self.serDataAvail==1:
                pdData.data_parseData(self)
                self.currentState=int(self.sR[self.stID_state])
        if self.trialDataExists==1:
            self.pyStatesTS.append(self.currentState)
            self.pyStatesTT.append(self.mcTrialTime[-1])

    def stateHeader(self,upSt):
        self.upSt=upSt
        ranHeader=0 # set the latch, the header runs once per entry.
        while ranHeader==0:
            self.cycleCount=1
            self.lastPos=0 # reset where we think the animal is
            self.lastLickCountA=0
            self.lastLickCountB=0
            self.entryTime=self.mcTrialTime[-1] # log state entry time
            self.stillTimeStart=0
            self.stillLatch=0
            self.trialFig.suptitle('trial # {}; state # {}'.format(self.currentTrial,self.currentState), fontsize=10)
            ranHeader=1 # fire the latch
        
    def coreState(self):
        uiUp=int(self.uiUpdateSamps.get())
        self.fireCallback=0
        pdSerial.serial_readDataFlush(self)
        if self.serDataAvail==1:
            pdData.data_parseData(self)
            if self.cycleCount % uiUp == 0:
                pdTask.updatePlotCheck(self)
            self.fireCallback=1
            self.cycleCount=self.cycleCount+1;

class pdCallbacks:

    def defineOutcome(self,rwCnt):
        tRCnt=str(self.rewardContingency[-1])
        sPres=int(tRCnt[0])
        rwdSpout=int(tRCnt[1])
        offSpout=abs(int(tRCnt[1])-1)

        targetMinLicked=eval('self.stateLickCount{}[-1]>=\
            self.minTarget{}Licks'.format(rwdSpout,sPres))
        targetMaxLicked=eval('self.stateLickCount{}[-1]>=\
            self.maxTarget{}Licks'.format(rwdSpout,sPres))
        distractMinLicked=eval('self.stateLickCount{}[-1]>=\
            self.minOffTarget{}Licks'.format(offSpout,sPres))
        distractMaxLicked=eval('self.stateLickCount{}[-1]>=\
            self.maxTarget{}Licks'.format(offSpout,sPres))

        if targetMinLicked==1 and targetMaxLicked == 0 and distractMinLicked == 0:

            print('licked spout {}: on target -> reward'.format(rwdSpout))
            exec('self.trialOutcome.append({}1)'.format(sPres))
            if rwdSpout==0:
                pdState.switchState(self,self.rewardState)
            elif rwdSpout==1:
                pdState.switchState(self,self.rewardState2)
            print(self.trialOutcome[-1])

        elif targetMinLicked==0 and distractMinLicked == 1:
            print('licked spout {}: off target -> punish'.format(offSpout))
            exec('self.trialOutcome.append({}2)'.format(sPres))
            pdState.switchState(self,self.punishState)
            print(self.trialOutcome[-1])

        elif targetMinLicked==1 and distractMinLicked == 1:
            print('licked both spouts: ambiguous -> punish')
            exec('self.trialOutcome.append({}3)'.format(sPres))
            pdState.switchState(self,self.neutralState)
            print(self.trialOutcome[-1])

    def waitStateCB(self):  
        pdAnalysis.checkMotion(self,self.acelValThr,self.acelSamps)
        if self.stillLatch==1 and self.stillTime[-1]>self.waitStillTime:
            print('Still in wait state ==> S1 --> S2')
            self.waitConditionMetTime.append(self.mcStateTime[-1])
            self.waitLicks0.append(self.stateLickCount0[-1])
            self.waitLicks1.append(self.stateLickCount1[-1])
            pdState.switchState(self,self.initiationState)

    def initiationStateHead(self):
        t1P=self.sTask1_prob
        self.task_switch=random.random()
        if self.task_switch<=t1P:
            self.cueSelected=1
        elif self.task_switch>t1P:
            self.cueSelected=2

    def initiationStateCB(self):
        aT=self.acelValThr  
        aS=self.acelSamps   
        pdAnalysis.checkMotion(self,aT,aS)
        if self.absolutePosition[-1]>self.distThr:
            print('moving spout; cue stim task #{}'.format(self.cueSelected))
            eval('pdState.switchState(self,self.cue{}State)'.\
                format(self.cueSelected))

    def cue1StateHead(self):
        self.startCue1=self.mcStateTime[-1]
        self.outcomeSwitch=random.random()
        o1P=self.sTask1_target_prob
        if self.outcomeSwitch<=o1P:
            self.stimSelected=1
            self.sStims.append(1)
        elif self.outcomeSwitch>o1P:
            self.stimSelected=2
            self.sStims.append(2)

    def cue1StateCB(self):
        pdAnalysis.checkMotion(self,self.acelValThr,self.acelSamps)
        if self.mcStateTime[-1]>self.cue1Dur:
            self.cue1Time.append(self.mcStateTime[-1]-self.startCue1) 
            self.cuePresented.append(1)
            eval('pdState.switchState(self,self.stim{}State)'.\
                format(self.stimSelected))
            exec('self.rewardContingency.append({}{})'.\
                format(self.stimSelected,self.stimSelected-1))
            print(self.rewardContingency[-1])
            print('Still: Task 1 --> Stim {}: Rwd On Spout {}'.\
                format(self.stimSelected,self.stimSelected-1))
            
            
    def cue2StateHead(self):
        self.startCue2=self.mcTrialTime[-1]
        self.outcomeSwitch=random.random()
        o2P=self.sTask2_target_prob
        if self.outcomeSwitch<=o2P:
            self.stimSelected=2
            self.sStims.append(2)
        elif self.outcomeSwitch>o2P:
            self.stimSelected=1
            self.sStims.append(1)

    def cue2StateCB(self): 
        pdAnalysis.checkMotion(self,self.acelValThr ,self.acelSamps)
        if self.mcStateTime[-1]>self.cue2Dur:
            self.cue2Time.append(self.mcTrialTime[-1]-self.startCue2)
            self.cuePresented.append(2)
            print('Still: Task 2 --> Stim {}: Rwd On Spout {}'.\
                format(self.stimSelected,self.stimSelected-1))
            eval('pdState.switchState(self,self.stim{}State)'.\
                format(self.stimSelected))
            exec('self.rewardContingency.append({}{})'.\
                format(self.stimSelected,self.stimSelected-1))
            print(self.rewardContingency[-1])
    
    def stim1StateCB(self):
        self.minStim1Time=0
        self.minTarget1Licks=1
        self.maxTarget1Licks=100
        self.maxOffTarget1Licks=1
        self.minOffTarget1Licks=1
        self.reportMax1Time=20

        if self.mcStateTime[-1]>self.minStim1Time:
            if self.mcStateTime[-1]<self.reportMax1Time:
                pdCallbacks.defineOutcome(self,self.rewardContingency)

            elif self.mcStateTime[-1]>=self.reportMax1Time:
                self.trialOutcome.append(10)
                print('timed out: did not report')
                pdState.switchState(self,self.neutralState)

    def stim2StateCB(self):
        self.minStim2Time=0
        self.minTarget2Licks=1
        self.maxTarget2Licks=100
        self.maxOffTarget2Licks=1
        self.minOffTarget2Licks=1
        self.reportMax2Time=10

        if self.mcStateTime[-1]>self.minStim2Time:
            if self.mcStateTime[-1]<self.reportMax2Time:
                pdCallbacks.defineOutcome(self,self.rewardContingency)
            elif self.mcStateTime[-1]>=self.reportMax2Time:
                self.trialOutcome.append(20)
                print('timed out: did not report')
                pdState.switchState(self,self.neutralState) 

    def shaping_stim1StateHead(self):
        self.minStim1Time=1 #todo: variable shape time
        diceRoll=random.random()
        if diceRoll<=self.shapeC1_LPortProb:
            print('debug: roll={},{}'.format(self.shapeC1_LPortProb,diceRoll))
            self.leftReward=1
            self.shapingReport.append(10)
            print('will reward left')
        elif diceRoll>self.shapeC1_LPortProb:
            print('debug: roll={},{}'.format(self.shapeC1_LPortProb,diceRoll))
            self.leftReward=0
            self.shapingReport.append(11)
            print('will reward right')

    def shaping_stim1StateCB(self):
        if self.mcStateTime[-1]>self.minStim1Time:
            if self.leftReward:
                self.stimLicks0.append(self.stateLickCount0[-1])
                self.stimLicks1.append(self.stateLickCount1[-1])
                pdState.switchState(self,self.rewardState)
            elif self.leftReward !=1:
                self.stimLicks0.append(self.stateLickCount0[-1])
                self.stimLicks1.append(self.stateLickCount1[-1])
                pdState.switchState(self,self.rewardState2)

    def shaping_stim2StateHead(self):
        self.minStim2Time=1

        diceRoll=random.random()
        if diceRoll<=self.shapeC2_LPortProb:
            print('debug: roll={},{}'.format(self.shapeC2_LPortProb,diceRoll))
            self.leftReward=1
            self.shapingReport.append(20)
            print('will reward left')
        elif diceRoll>self.shapeC2_LPortProb:
            print('debug: roll={},{}'.format(self.shapeC2_LPortProb,diceRoll))
            self.leftReward=0
            self.shapingReport.append(21)
            print('will reward right')

    def shaping_stim2StateCB(self):
        if self.mcStateTime[-1]>self.minStim2Time:
            if self.leftReward:
                self.stimLicks0.append(self.stateLickCount0[-1])
                self.stimLicks1.append(self.stateLickCount1[-1])
                pdState.switchState(self,self.rewardState)
            elif self.leftReward !=1:
                self.stimLicks0.append(self.stateLickCount0[-1])
                self.stimLicks1.append(self.stateLickCount1[-1])
                pdState.switchState(self,self.rewardState2)

    def rewardStateCB(self):
        self.reward1Time=1
        if self.mcStateTime[-1]<self.reward1Time:
            print('rewarding left port')
            pdState.switchState(self,self.saveState)

    def rewardState2CB(self):
        self.reward2Time=1
        if self.mcStateTime[-1]<self.reward2Time:
            print('rewarding right port')
            pdState.switchState(self,self.saveState)

    def neutralStateCB(self):
        self.neutralTime=1
        if self.mcStateTime[-1]<0.1:
            print('no reward')
            pdState.switchState(self,self.saveState)

    def punishStateCB(self):
        if self.mcTrialTime[-1]-self.entryTime>=self.timeOutDuration:
            print('timeout of {} seconds is over'.format(self.timeOutDuration))
            pdState.switchState(self,self.saveState)

class pdWindow:

    def addMainBlock(self,startRow):
        self.startRow = startRow
        self.blankLine(self.master,startRow)

        self.mainCntrlLabel = Label(self.master, text="Main Controls:")\
        .grid(row=startRow,column=0,sticky=W)

        self.quitBtn = \
        Button(self.master,text="Exit Program",command = \
            lambda: pdWindow.mwQuitBtn(self), width=self.col2BW)
        self.quitBtn.grid(row=startRow+1, column=2)

        self.startBtn = Button(self.master, text="Start Task",\
            width=10, command=lambda: pdTask.runSession(self) ,state=DISABLED)
        self.startBtn.grid(row=startRow+1, column=0,sticky=W,padx=10)

        self.endBtn = Button(self.master, text="End Task",width=self.col2BW, \
            command=lambda:pdState.switchState(\
                self,self.endState),state=DISABLED)
        self.endBtn.grid(row=startRow+2, column=0,sticky=W,padx=10)

        self.stateEditBtn = Button(self.master, text="State Editor",\
            width=self.col2BW, command=self.stateEditWindow,state=NORMAL)
        self.stateEditBtn.grid(row=startRow+2,column=2,sticky=W,padx=10)

    def addSerialBlock(self,startRow):
        self.startRow = startRow

        # @@@@@ --> Serial Block
        self.comPathLabel = Label(self.master,\
            text="COM Port Location:",justify=LEFT)
        self.comPathLabel.grid(row=startRow,column=0,sticky=W)

        self.comPath=StringVar(self.master)
        self.comPathEntry=Entry(self.master,textvariable=self.comPath)
        self.comPathEntry.grid(row=startRow+1, column=0)
        self.comPathEntry.config(width=24)
        
        if sys.platform == 'darwin':
            self.comPath.set('/dev/cu.usbmodem2762721')
        elif sys.platform == 'win':
            self.comPath.set('COM11')

        self.baudEntry_label = Label(\
            self.master,text="BAUD Rate:",justify=LEFT)
        self.baudEntry_label.grid(row=startRow+2, column=0,sticky=W)

        self.baudSelected=IntVar(self.master)
        self.baudSelected.set(115200)
        self.baudPick = OptionMenu(self.master,\
            self.baudSelected,115200,19200,9600)
        self.baudPick.grid(row=startRow+2, column=0,sticky=E)
        self.baudPick.config(width=14)

        self.createCom_button = Button(self.master,\
            text="Start Serial",width=self.col2BW, \
            command=lambda: pdSerial.serial_initComObj(self))
        self.createCom_button.grid(row=startRow+0, column=2)
        self.createCom_button.config(state=NORMAL)

        self.syncComObj_button = Button(self.master,\
            text="Sync Serial",width=self.col2BW, \
            command=lambda: pdSerial.syncSerial(self))
        self.syncComObj_button.grid(row=startRow+1, column=2)
        self.syncComObj_button.config(state=DISABLED)  

        self.closeComObj_button = Button(self.master,\
            text="Close Serial",width=self.col2BW, \
            command=lambda: pdSerial.serial_closeComObj(self))
        self.closeComObj_button.grid(row=startRow+2, column=2)
        self.closeComObj_button.config(state=DISABLED)

    def addSessionBlock(self,startRow):
        # @@@@@ --> Session Block
        self.sesPathFuzzy=1 # This variable is set when we guess the path.

        self.animalID='yourID'
        self.dateStr = datetime.datetime.\
        fromtimestamp(time.time()).strftime('%H:%M (%m/%d/%Y)')

        self.blankLine(self.master,startRow)
        self.sessionStuffLabel = Label(self.master,\
            text="Session Stuff: ",justify=LEFT)\
        .grid(row=startRow+1, column=0,sticky=W)

        self.timeDisp = Label(self.master, text=' #{} started: '\
            .format(self.currentSession) + self.dateStr,justify=LEFT)
        self.timeDisp.grid(row=startRow+2,column=0,sticky=W)

        self.dirPath=StringVar(self.master)
        self.pathEntry=Entry(self.master,textvariable=\
            self.dirPath,width=24,bg='grey')
        self.pathEntry.grid(row=startRow+3,column=0,sticky=W)
        self.dirPath.set(os.path.join(os.getcwd(),self.animalID))

        self.setPath_button = Button(self.master,text="<- Set Path",\
            command=lambda: pdWindow.mwPathBtn(self),width=self.col2BW)
        self.setPath_button.grid(row=startRow+3,column=2)

        self.aIDLabel=Label(self.master, text="animal id:")\
        .grid(row=startRow+4,column=0,sticky=W)
        self.animalIDStr=StringVar(self.master)
        self.animalIDEntry=Entry(self.master,textvariable=\
            self.animalIDStr,width=14,bg='grey')
        self.animalIDEntry.grid(row=startRow+4,column=0,sticky=E)
        self.animalIDStr.set(self.animalID)

        self.totalTrials_label = Label(self.master,text="total trials:")\
        .grid(row=startRow+5,column=0,sticky=W)
        self.totalTrials=StringVar(self.master)
        self.totalTrials.set('100')
        self.totalTrials_entry=Entry(self.master,textvariable=\
            self.totalTrials,width=10).\
        grid(row=startRow+5,column=0,sticky=E)

        self.curSession_label = Label(self.master,text="current session:")\
        .grid(row=startRow+6,column=0,sticky=W)
        self.currentSessionTV=StringVar(self.master)
        self.currentSessionTV.set(self.currentSession)
        self.curSession_entry=Entry(self.master,textvariable=\
            self.currentSessionTV,width=10)
        self.curSession_entry.grid(row=startRow+6,column=0,sticky=E)

        self.taskProbsBtn = Button(self.master,text='Task Probs',\
            width=self.col2BW,\
            command=self.taskProbWindow)
        self.taskProbsBtn.grid(row=startRow+4, column=2)
        self.taskProbsBtn.config(state=NORMAL)

        self.stateTogglesBtn = Button(self.master,text = 'State Toggles',\
            width=self.col2BW,\
            command=self.stateToggleWindow)
        self.stateTogglesBtn.grid(row=startRow+5, column=2)
        self.stateTogglesBtn.config(state=NORMAL)
        
        self.stateVarsBtn = Button(self.master,text = 'State Vars',\
            width=self.col2BW,\
            command = self.stateVarWindow)
        self.stateVarsBtn.grid(row=startRow+6, column=2)
        self.stateVarsBtn.config(state=NORMAL)

        self.loadAnimalMetaBtn = Button(self.master,text = 'Load Metadata',\
            width = self.col2BW, command = \
            lambda: pdWindow.mwLoadMetaBtn(self))
        self.loadAnimalMetaBtn.grid(row=startRow+1, column=2)
        self.loadAnimalMetaBtn.config(state=NORMAL)

        self.saveCurrentMetaBtn=Button(self.master,text="Save Cur. Meta",\
            command=lambda:pdUtil.exportAnimalMeta(self), width=self.col2BW)
        self.saveCurrentMetaBtn.grid(row=startRow+2,column=2)

    def addPlotBlock(self,startRow):
        self.blankLine(self.master,startRow)
        self.plotBlock_label = Label(self.master,text="Plotting:")
        self.plotBlock_label.grid(row=startRow+1, column=0,sticky=W)
        
        self.sampPlot_label = Label(self.master,text="samples / plot:")
        self.sampPlot_label.grid(row=startRow+2,column=0,sticky=W)
        self.sampsToPlot=StringVar(self.master)
        self.sampPlot_entry=Entry(self.master,width=5,textvariable=\
            self.sampsToPlot)
        self.sampPlot_entry.grid(row=startRow+2, column=0,sticky=E)
        self.sampsToPlot.set('1000')

        self.uiUpdateSamps_label = Label(self.master, text="samples / UI update:")
        self.uiUpdateSamps_label.grid(row=startRow+3, column=0,sticky=W)
        self.uiUpdateSamps=StringVar(self.master)
        self.uiUpdateSamps_entry=Entry(self.master,width=5,textvariable=\
            self.uiUpdateSamps)
        self.uiUpdateSamps_entry.grid(row=startRow+3, column=0,sticky=E)
        self.uiUpdateSamps.set('500')


        self.togglePlotWinBtn=Button(self.master,text = 'Toggle Plot',\
            width=self.col2BW,\
            command=lambda:pdPlot.taskPlotWindow(self))
        self.togglePlotWinBtn.grid(row=startRow+2, column=2)
        self.togglePlotWinBtn.config(state=NORMAL)

        self.debugWindowBtn=Button(self.master,text = 'Debug Toggles',\
            width=self.col2BW,\
            command=self.debugWindow)
        self.debugWindowBtn.grid(row=startRow+3, column=2)
        self.debugWindowBtn.config(state=NORMAL)

        self.perfWindowBtn=Button(self.master,text = 'Session Plot',\
            width=self.col2BW,\
            command=lambda:pdPlot.makeSessionPlotWindow(self))
        self.perfWindowBtn.grid(row=startRow+4, column=2)
        self.perfWindowBtn.config(state=NORMAL)


        self.xVarsToPlot=StringVar(self.master)
        self.yVarsToPlot=StringVar(self.master)


        self.lickMinMaxA=[-5,10]
        self.initPltRng=2.5
        self.pltDelay=0.000001 
        self.segPlot=10000
        self.lastPos=0
        self.lastOrientation=0

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
        self.ux_adaptThreshToggle.grid(row=startRow+2, \
            column=0,sticky=W,padx=5)
        self.ux_adaptThreshToggle.select()

        self.lickValuesOrDeltas=StringVar(self.master)
        self.ux_lickValuesToggle=Checkbutton(self.master, \
            text="Lk Val?   |",variable=self.lickValuesOrDeltas)
        self.ux_lickValuesToggle.grid(row=startRow+3, \
            column=0,sticky=W,padx=5)
        self.ux_lickValuesToggle.select()

        self.lickThresholdA_label = Label(self.master, text="Thr A:")
        self.lickThresholdA_label.grid(row=startRow+2,\
            column=0,padx=84,sticky=E)
        self.lickThresholdStrValA=StringVar(self.master)
        
        self.lickThresholdB_label = Label(self.master,text="Thr B:")
        self.lickThresholdB_label.grid(row=startRow+3,column=0,padx=84,sticky=E)
        self.lickThresholdStrValB=StringVar(self.master)

        self.aThrEntry=Entry(self.master,width=6,textvariable=\
            self.lickThresholdStrValA)
        self.aThrEntry.grid(row=startRow+2, column=0,sticky=E,padx=5)
        self.bThrEntry=Entry(self.master,width=6,textvariable=\
            self.lickThresholdStrValB)
        self.bThrEntry.grid(row=startRow+3, column=0,sticky=E,padx=5)
        
        self.lickThresholdStrValA.set(400)
        self.lickThresholdStrValB.set(400)
        self.lickThresholdLatchA=0;
        self.lickThresholdLatchB=0;
        self.lastLickA=0;
        self.lastLickB=0;

        # plot stuff
        self.lickMax_label = Label(self.master, text="Lick Max:")
        self.lickMax_label.grid(row=startRow+4,column=0,sticky=W,padx=76)
        self.lickPlotMax=StringVar(self.master)
        self.lickMax_entry=Entry(self.master,width=6,textvariable=\
            self.lickPlotMax)
        self.lickMax_entry.grid(row=startRow+4, column=0,sticky=E,padx=5)
        self.lickPlotMax.set('2000')

    def pdWindowPopulate(self):
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

        pdWindow.addSerialBlock(self,serStart)
        pdWindow.addSessionBlock(self,sesStart)
        pdWindow.addPlotBlock(self,plotStart)
        pdWindow.addLickDetectionBlock(self,lickStart)
        pdWindow.addMainBlock(self,mainStart)
        pdWindow.pdWindowCallback(self)

    def pdWindowCallback(self):
        # look in whatever it thinks the working dir 
        # is and look for metadata to populate
        self.dirAnimalMetaExists=os.path.isfile(\
            self.dirPath.get() + '.lastMeta.csv')
        self.trialFramePosition='+375+0'
        self.resizeControlPosition='+620+575'
        self.debugTogglePosition="+375+575"
        self.sessionFramePosition='+950+0'

        pyDiscrim.debugWindow(self)
        pdPlot.taskPlotWindow(self)
        pdPlot.resizeTaskPlot(self)
        pdPlot.makeSessionPlotWindow(self)

    def mwQuitBtn(self):
        if self.ranTask==0 or self.comObjectExists==0:  
            print('*** bye: closed without saving ***')
            exit()
        else: 
            print('!!!! going down')
            if self.trialDataExists==1:
                pdData.data_saveTrialData(self)
            if self.sessionDataExists==1:
                pdData.data_saveSessionData(self)
                print('... saved some remaining data')
            if self.comObjectExists==1:
                pdSerial.syncSerial(self)
                print('... resyncd serial state')
                self.comObj.close()
                print('... closed the com obj')
            exit()

    def mwPathBtn(self):
        pdUtil.getPath(self)
        self.dirPath.set(self.selectPath)

        self.pathEntry.config(bg='white')
        self.animalIDStr.set(os.path.basename(self.selectPath))
        self.animalIDEntry.config(bg='white')
        self.sesPathFuzzy=0
        metaString='{}{}_animalMeta.csv'.format(\
            self.selectPath + '/',self.animalIDStr.get())
        stateString='{}{}_stateMap.csv'.format(\
            self.selectPath + '/',self.animalIDStr.get())
        self.loadedMeta=os.path.isfile(metaString)
        self.loadedStates=os.path.isfile(stateString)
        if self.loadedMeta is True:
            tempMeta=pd.read_csv(metaString,index_col=0)
            pdUtil.parseMetaDataStrings(self,tempMeta)
            print("loaded {}'s previous settings".format(\
                self.animalIDStr.get()))
        if self.loadedStates is True:
            tempStates=pd.Series.from_csv(stateString)
            print("loaded {}'s \
                previous state assignments, but didn't parse them".\
                format(self.animalIDStr.get()))

    def mwSaveMetaBtn(self):
        metaString='{}{}_animalMeta.csv'.format(\
            self.pathSet,self.animalIDStr.get())
        stateString='{}{}_stateMap.csv'.format(\
            self.pathSet,self.animalIDStr.get())
        self.loadedMeta=os.path.isfile(metaString)
        self.loadedStates=os.path.isfile(stateString)
        if self.loadedMeta is True:
            tempMeta=pd.read_csv(metaString,index_col=0)
        if self.loadedStates is True:
            tempStates=pd.Series.from_csv(stateString)
        
        tempMeta.to_csv('.lastMeta.csv')
        tempStates.to_csv('.lastStates.csv')

    def mwLoadMetaBtn(self):
        aa=fd.askopenfilename(\
            title = "what what?",defaultextension='.csv')
        tempMeta=pd.read_csv(aa,index_col=0)
        aa=tempMeta.dtypes.index
        varNames=[]
        varVals=[]
        for x in range(0,len(tempMeta.columns)):
            varNames.append(aa[x])
            varVals.append(tempMeta.iloc[0][x])
        pdUtil.mapAssignStringEntries(self,varNames,varVals)

class pdTask:

    def taskHeader(self):
        pdData.data_sessionContainers(self)
        self.endBtn.config(state=NORMAL)
        self.startBtn.config(state=DISABLED)
        print('started at state #: {}'.format(self.currentState))
        pdData.data_serialInputIDs(self)
        self.uiUpdateDelta=int(self.uiUpdateSamps.get())
        self.ranTask=self.ranTask+1
        self.shouldRun=1
        self.currentSession=self.currentSessionTV.get()

        np.random.seed()
        self.t1RCPairs=[10,21] # stim 1, reward left; stim 2 reward right
        self.t2RCPairs=[11,20]

    def runSession(self):
        pdTask.taskHeader(self)
        self.sessionStartTime=time.time()
        self.currentTrial=1
        trialCounter=1
        while self.currentTrial <=int(self.totalTrials.get()) and self.shouldRun==1:
            pdTask.trial(self)
        pdData.data_saveSessionData(self)

        self.currentSessionTV.set(int(self.currentSessionTV.get())+1)
        self.currentSession=int(self.currentSessionTV.get())
        pdUtil.exportAnimalMeta(self)
        
        self.endBtn.config(state=DISABLED)
        self.startBtn.config(state=NORMAL)
        
        self.stateBindings.to_csv('{}{}_stateMap.csv'\
            .format(self.dirPath.get() + '/',self.animalIDStr.get()))
        print('I completed {} trials.'.format(self.currentTrial-1))
        print('!!!!!!! --> Session #:{} Finished'\
            .format(int(self.currentSessionTV.get())-1))
        self.updateDispTime()
        pdSerial.syncSerial(self)
    
    def trial(self):
        self.trialStartTime=time.time()
        try:
            #S0 -----> hand shake (initialization state)
            if self.currentState==self.bootState:
                pdData.data_trialContainers(self)
                pdSerial.serial_readDataFlush(self)
                while self.currentState==self.bootState:
                    pdSerial.serial_readDataFlush(self)
                    if self.serDataAvail==1:
                        pdData.data_parseData(self)
                        pdState.switchState(self,self.waitState)
            
            #S1 -----> trial wait state
            elif self.currentState==self.waitState:
                pdState.stateHeader(self,1)
                while self.currentState==self.waitState:
                    pdState.coreState(self)
                    if self.fireCallback:
                        pdCallbacks.waitStateCB(self)

            
            #S2 -----> trial initiation state
            elif self.currentState==self.initiationState:
                pdState.stateHeader(self,1)
                pdCallbacks.initiationStateHead(self)
                while self.currentState==self.initiationState:
                    pdState.coreState(self)
                    if self.fireCallback:
                        pdCallbacks.initiationStateCB(self)
            
            #S3 -----> cue #1
            elif self.currentState==self.cue1State:
                pdState.stateHeader(self,1)
                pdCallbacks.cue1StateHead(self)
                while self.currentState==self.cue1State:
                    pdState.coreState(self)
                    if self.fireCallback:
                        pdCallbacks.cue1StateCB(self)

            #S4 -----> cue #2
            elif self.currentState==self.cue2State:
                pdState.stateHeader(self,1)
                pdCallbacks.cue2StateHead(self)
                while self.currentState==self.cue2State:    
                    pdState.coreState(self)
                    if self.fireCallback:
                        pdCallbacks.cue2StateCB(self)

            #S5 -----> stim tone #1
            elif self.currentState==self.stim1State:
                pdState.stateHeader(self,1)
                pdCallbacks.shaping_stim1StateHead(self)
                while self.currentState==self.stim1State:
                    pdState.coreState(self)
                    if self.fireCallback:
                        pdCallbacks.shaping_stim1StateCB(self)

            #S6 -----> stim tone #2
            elif self.currentState==self.stim2State:
                pdState.stateHeader(self,1)
                pdCallbacks.shaping_stim2StateHead(self)
                while self.currentState==self.stim2State:
                    pdState.coreState(self)
                    if self.fireCallback:
                        pdCallbacks.shaping_stim2StateCB(self)
            
            #S21 -----> reward state
            elif self.currentState==self.rewardState:
                pdState.stateHeader(self,0)
                while self.currentState==self.rewardState:
                    pdState.coreState(self)
                    if self.fireCallback:
                        pdCallbacks.rewardStateCB(self)
            #S22 -----> reward state
            elif self.currentState==self.rewardState2:
                pdState.stateHeader(self,0)
                while self.currentState==self.rewardState2:
                    pdState.coreState(self)
                    if self.fireCallback:
                        pdCallbacks.rewardStateCB(self)

            #S23 -----> neutral state
            elif self.currentState==self.neutralState:
                pdState.stateHeader(self,0)
                while self.currentState==self.neutralState:
                    pdState.coreState(self)
                    if self.fireCallback:
                        pdCallbacks.neutralStateCB(self)

            #S24 -----> punish state
            elif self.currentState==self.punishState:
                pdState.stateHeader(self,0)
                while self.currentState==self.punishState:
                    pdState.coreState(self)
                    if self.fireCallback:
                        pdCallbacks.punishStateCB(self)

            #S13: save state
            elif self.currentState==self.saveState:
                # self.updatePerfPlot() # if self.pf_frame.winfo_exists():
                # deal with trial data

                if self.currentTrial % self.biasRange==0:
                    pdAnalysis.shapingUpdateLeftRightProb(self)

                self.trialLeft1Prob.append(self.shapeC1_LPortProb)
                self.trialLeft2Prob.append(self.shapeC2_LPortProb)
                self.trialSampRate.append(np.mean(np.diff(np.array(self.mcTrialTime))))
                print('debug: mean dt={}'.format(self.trialSampRate[-1]))

                pdData.data_saveTrialData(self)
                pdData.data_trialContainers(self)
                self.trialEndTime=time.time()

                # append to session data
                trialTime=self.trialEndTime-self.trialStartTime
                self.trialTimes.append(trialTime)
                pdPlot.updateSessionPlot(self)
                
                print('last trial took: {} seconds'.format(trialTime))
                self.currentTrial=self.currentTrial+1
                self.sessionTrialCount=self.sessionTrialCount+1 
                # in case you run a second session
                print('trial {} done, saved its data'\
                    .format(self.currentTrial-1))
                pdState.switchState(self,self.bootState)
 

            #S25: end session state
            elif self.currentState==self.endState:
                print('About to end the session ...')
                if self.trialDataExists==1:
                    pdData.data_saveTrialData(self)
                    self.currentTrial=self.currentTrial+1
                    self.sessionTrialCount=self.sessionTrialCount+1 
                    # in case you run a second session
                    pdData.data_trialContainers(self)
                self.shouldRun=0  # session interput

        except:
            pdUtil.exportAnimalMeta(self)
            self.exceptionCallback()

    def updatePlotCheck(self):
        if plt.fignum_exists(100):
            pdPlot.updateTaskPlot(self)
        self.cycleCount=0

class pyDiscrim:

    def __init__(self,master):
        self.master = master
        self.frame = Frame(self.master)
        root.wm_geometry("+0+0")
        pdVariables.setSessionVars(self)
        pdWindow.pdWindowPopulate(self)
        print('curTrial={}'.format(self.currentTrial))
        print('curSession={}'.format(self.currentSession))
        pdVariables.setStateNames(self)
        pdVariables.setTaskProbs(self)
        pdVariables.setStateVars(self)
        pdData.data_serialInputIDs(self)
        pdData.data_serialInputIDs(self)
        pdData.data_sessionContainers(self)

    def blankLine(self,targ,startRow):
        self.guiBuf=Label(targ, text="")
        self.guiBuf.grid(row=startRow,column=0,sticky=W)

    def updateDispTime(self):
        self.dateStr = datetime.datetime.\
        fromtimestamp(time.time()).strftime('%H:%M (%m/%d/%Y)')
        self.timeDisp.config(text=' #{} started:'\
            .format(self.currentSession) + self.dateStr)
    
    def makeMetaFrame(self):
        sesVarVals=[]
        self.saveVars_session_ids=\
        ['sessionTrialCount','currentTrial','timeOutDuration']
        for x in range(0,len(self.saveVars_session_ids)):
            exec('sesVarVals.append(self.{})'\
                .format(self.saveVars_session_ids[x]))

        self.sessionDF=pd.DataFrame([sesVarVals],\
            columns=self.saveVars_session_ids)

    def updateMetaFrame(self):
        # updates are series
            sesVarVals=[]
            for x in range(0,len(self.saveVars_session_ids)):
                exec('sesVarVals.append(self.{})'\
                    .format(self.saveVars_session_ids[x]))
            ds=pd.Series(sesVarVals,index=self.saveVars_session_ids)
            self.sessionDF=self.sessionDF.append(ds,ignore_index=True)

    def debugWindow(self):
        self.debugTogglePosition="+370+660"
        dbgFrame = Toplevel()
        eval('dbgFrame.wm_geometry("{}")'.format(self.debugTogglePosition))
        dbgFrame.title('Debug Toggles')
        self.dbgFrame=dbgFrame

        self.mFwdBtn=Button(master=dbgFrame,\
            text="Move +",width=10,command=lambda:self.dbMv(100))
        self.mFwdBtn.grid(row=0, column=0)
        self.mFwdBtn.config(state=NORMAL)

        self.mBwdBtn=Button(master=dbgFrame,\
            text="Move -",width=10,command=lambda:self.dbMv(-100))
        self.mBwdBtn.grid(row=1, column=0)
        self.mBwdBtn.config(state=NORMAL)

        self.lickABtn=Button(master=dbgFrame,\
            text="Lick Left",width=10, command=lambda:self.dbLick(2000,0))
        self.lickABtn.grid(row=0, column=1)
        self.lickABtn.config(state=NORMAL)

        self.lickBBtn=Button(master=dbgFrame,\
            text="Lick Right",width=10, command=lambda:self.dbLick(2000,1))
        self.lickBBtn.grid(row=1, column=1)
        self.lickBBtn.config(state=NORMAL)

    def dbMv(self,delta):
        if len(self.absolutePosition)>0:
            self.absolutePosition[-1]=self.absolutePosition[-1]+delta
            self.posDelta[-1]=delta
            self.lastPos=self.lastPos+delta
        elif len(self.absolutePosition)==0:
            self.lastPos=int(delta)

    def dbLick(self,val,spout):
        if len(self.lickValsA)>0 and spout == 0:
            self.lickValsA[-1]=self.lickValsA[-1]+val
            pdAnalysis.lickDetectionDebug(self)

        if len(self.lickValsB)>0 and spout == 1:
            self.lickValsB[-1]=self.lickValsB[-1]+val
            pdAnalysis.lickDetectionDebug(self)

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
            command=lambda: pdState.switchState(self,self.saveState),\
            width=btWdth)
        self.sBtn_save.grid(row=sRw+1, column=sCl)
        self.sBtn_save.config(state=NORMAL)

        self.sBtn_endSession = Button(st_frame, text="End Session", \
            command=lambda: pdState.switchState(\
                self,self.endState),width=btWdth)
        self.sBtn_endSession.grid(row=sRw-2, column=sCl+1)
        self.sBtn_endSession.config(state=NORMAL)

        self.sBtn_boot = Button(st_frame, text="S0: Boot", \
            command=lambda: pdState.switchState(\
                self,self.bootState),width=btWdth)
        self.sBtn_boot.grid(row=sRw-1, column=sCl)
        self.sBtn_boot.config(state=NORMAL)

        self.sBtn_wait = Button(st_frame, text="S1: Wait", \
            command=lambda: pdState.switchState(\
                self,self.waitState),width=btWdth)
        self.sBtn_wait.grid(row=sRw, column=sCl)
        self.sBtn_wait.config(state=NORMAL)

        self.sBtn_initiate = Button(st_frame, text="S2: Initiate", \
            command=lambda: pdState.switchState(\
                self,self.initiationState),width=btWdth)
        self.sBtn_initiate.grid(row=sRw, column=sCl+1)
        self.sBtn_initiate.config(state=NORMAL)

        self.sBtn_cue1 = Button(st_frame, text="S3: Cue 1", \
            command=lambda: pdState.switchState(\
                self,self.cue1State),width=btWdth)
        self.sBtn_cue1.grid(row=sRw-1, column=sCl+2)
        self.sBtn_cue1.config(state=NORMAL)

        self.sBtn_cue2 = Button(st_frame, text="S4: Cue 2", \
            command=lambda: pdState.switchState(\
                self,self.cue2State),width=btWdth)
        self.sBtn_cue2.grid(row=sRw+1, column=sCl+2)
        self.sBtn_cue2.config(state=NORMAL)

        self.sBtn_stim1 = Button(st_frame, text="SS1: Stim 1", \
            command=lambda: pdState.switchState(\
                self,self.stim1State),width=btWdth)
        self.sBtn_stim1.grid(row=sRw-2, column=sCl+3)
        self.sBtn_stim1.config(state=NORMAL)

        self.sBtn_stim2 = Button(st_frame, text="SS1: Stim 2",\
            command=lambda: pdState.switchState(\
                self,self.stim2State),width=btWdth)
        self.sBtn_stim2.grid(row=sRw+2, column=sCl+3)
        self.sBtn_stim2.config(state=NORMAL)


        self.sBtn_catch = Button(st_frame, text="SC: Catch", \
            command=lambda: pdState.switchState(\
                self,self.catchState),width=btWdth)
        self.sBtn_catch.grid(row=sRw, column=sCl+3)
        self.sBtn_catch.config(state=NORMAL)

        self.sBtn_reward = Button(st_frame, text="SR1: Reward1", \
            command=lambda: pdState.switchState(self,21),width=btWdth)
        self.sBtn_reward.grid(row=sRw-1, column=sCl+4)
        self.sBtn_reward.config(state=NORMAL)

        self.sBtn_reward2 = Button(st_frame, text="SR2: Reward 2", \
            command=lambda: pdState.switchState(self,22),width=btWdth)
        self.sBtn_reward2.grid(row=sRw+1, column=sCl+4)
        self.sBtn_reward2.config(state=NORMAL)

        self.sBtn_neutral = Button(st_frame, text="SN: Neutral", \
            command=lambda: pdState.switchState(\
                self,self.neutralState),width=btWdth)
        self.sBtn_neutral.grid(row=sRw, column=sCl+5)
        self.sBtn_neutral.config(state=NORMAL)

        self.sBtn_punish = Button(st_frame, text="SP: Punish", \
            command=lambda: pdState.switchState(\
                self,self.punishState),width=btWdth)
        self.sBtn_punish.grid(row=sRw+0, column=sCl+4)
        self.sBtn_punish.config(state=NORMAL)

    def stateEditWindow(self):
        se_frame = Toplevel()
        se_frame.title('Set States')
        self.se_frame=se_frame

        self.populateVarFrames(self.stateNames,self.stateIDs,0,'se_frame')
        
        self.setStatesBtn = Button(se_frame, text = 'Set State IDs', \
            width = 15, command = lambda: self.stateNumsRefreshBtnCB())
        self.setStatesBtn.grid(row=len(self.stateNames)+2, column=0)

    def taskProbWindow(self):
        tb_frame = Toplevel()
        tb_frame.title('Task Probs')
        self.tb_frame=tb_frame
        self.populateVarFrames(self.t1ProbLabels,\
            self.t1ProbValues,0,'tb_frame')
        self.populateVarFrames(self.t2ProbLabels,\
            self.t2ProbValues,2,'tb_frame')
        
        self.setTaskProbsBtn = Button(\
            tb_frame,text='Set Probs.',width = 10,\
            command = lambda: self.taskProbRefreshBtnCB())
        self.setTaskProbsBtn.grid(row=len(self.t1ProbValues)+2, column=0,sticky=E)

    def taskProbRefreshBtnCB(self):
        pdUtil.refreshVars(self,self.t1ProbLabels,self.t1ProbValues,1)
        pdUtil.refreshVars(self,self.t2ProbLabels,self.t2ProbValues,1)

    def stateVarWindow(self):
        frame_sv = Toplevel()
        frame_sv.title('Task Probs')
        self.frame_sv=frame_sv

        self.populateVarFrames(self.stateVarLabels,\
            self.stateVarValues,0,'frame_sv')
        self.setStateVars = Button(frame_sv,\
            text = 'Set Variables.', width = 10, \
            command = self.stateVarRefreshBtnCB)
        self.setStateVars.grid(row=len(self.stateVarValues)+2, column=0)  

    def stateVarRefreshBtnCB(self):

        pdUtil.refreshVars(self,self.stateVarLabels,self.stateVarValues,1)

    def stateNumsRefreshBtnCB(self):

        pdUtil.refreshVars(self,self.stateNames,self.stateIDs,1)

    def populateVarFrames(self,varLabels,varValues,stCol,frameName):
        for x in range(0,len(varLabels)):
            exec('self.{}_tv=StringVar(self.{})'.\
                format(varLabels[x],frameName))
            exec('self.{}_label = Label(self.{}, text="{}")'\
                .format(varLabels[x],frameName,varLabels[x]))
            exec('self.{}_entries=Entry(self.{},\
                width=6,textvariable=self.{}_tv)'\
                .format(varLabels[x],frameName,varLabels[x]))
            exec('self.{}_label.grid(row=x, column=stCol+1)'\
                .format(varLabels[x]))
            exec('self.{}_entries.grid(row=x, column=stCol)'\
                .format(varLabels[x]))
            exec('self.{}_tv.set({})'.format(varLabels[x],varValues[x]))

    def exceptionCallback(self):
        print('EXCEPTION thrown: I am going down')
        print('last trial = {} and the last state was {}. \
            I will try to save last trial ...'\
            .format(self.currentTrial,self.currentState))
        pdData.data_saveTrialData(self)
        print('save was a success; now \
            I will close com port and quit')
        print('I will try to reset the mc state \
            before closing the port ...')
        self.comObj.close()
        #todo: add a timeout for the resync
        print('closed the com port cleanly')
        exit()

root = Tk()
app = pyDiscrim(root)
root.mainloop()