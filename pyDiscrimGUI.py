# pyDiscrim
#
# A Python 3 program that interacts with a microcontroller to 
# perform state-based behavioral tasks.
#
# Version 1.1
# questions? --> Chris Deister --> cdeister@brown.edu

from tkinter import *
import tkinter.filedialog as fd
import serial
import numpy as np
import matplotlib 
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

class pdVariables:

    def setStateNames(self):
        self.stMapD = {'bootState':0,'waitState':1,'initiationState':2,\
        'cue1State':3,'cue2State':4,'stim1State':5,'stim2State':6,'catchState':7,\
        'saveState':13,'rewardState1':21,'rewardState2':22,'neutralState':23,'punishState1':24,\
        'endState':25,'defaultState':29}
        pdVariables.dictToPandas(self,self.stMapD,'self.stateMap')

    def setSessionVars(self):
        # session vars
        self.ranTask=0
        self.trialDataExists=0
        self.sessionDataExists=0
        self.currentTrial=1
        self.sessionTrialCount=1

        self.sesVarD = {'currentSession':1,'dirPath':"/",'animalIDStr':"an1",\
        'uiUpdateSamps':100,'lickThresholdStrValA':550,'lickThresholdStrValB':550,'totalTrials':150,\
        'sampsToPlot':1000,'comPath':"/dev/cu.usbmodem2762721"}
        pdVariables.dictToPandas(self,self.sesVarD,'self.sesVarBindings')

    def setStateVars(self):
        self.stVarD = {'acelValThr':10,'acelSamps':100,'distThr':100,'tOutDur1':2,'tOutDur2':2,\
        'waitStillTime':1.5,'genStillTime':1.5,'cue1Dur':1.5,'cue2Dur':1.5,'biasRange':5,\
        'shapeC1_LPortProb':0.5,'shapeC2_LPortProb':0.5,'biasPCut':0.05,'biasMuCut':0.4,\
        'lBiasDelta':0.1,'rBiasDelta':0.1,'rwdTime1':1.5,'rwdTime2':1.5,'minStim1Time':1,\
        'minStim2Time':1,'max1ReportTime':20,'max2ReportTime':20,'neutralTime':1,'correctBias':0}
        pdVariables.dictToPandas(self,self.stVarD,'self.stateVarBindings')
        
    def setTaskProbs(self):

        self.task1D = {'t1Prob':0.5,'t1LeftProb':0.5,'task1RightProb':0.5,\
        't1LeftRewardProb':1.0,'t1LeftPunishProb':0.0, 't1RightRewardProb':0.0,\
        't1RightPunishProb':1.0,'t1ShapingProb':1.0,'t1ShapingRewardProb':1.0,\
        't1ShapeTime':1}
        pdVariables.dictToPandas(self,self.task1D,'self.task1Bindings')

        self.task2D = {'t2Prob':0.5,'t2LeftProb':0.5,'task2RightProb':0.5,\
        't2LeftRewardProb':1.0,'t2LeftPunishProb':0.0, 't2RightRewardProb':0.0,\
        't2RightPunishProb':1.0,'t2ShapingProb':1.0,'t2ShapingRewardProb':1.0,\
        't2ShapeTime':1}
        pdVariables.dictToPandas(self,self.task2D,'self.task2Bindings')

    def dictToPandas(self,dictName,bindingName):
        tLab=[]
        tVal=[]
        for key in list(dictName.keys()):
            tLab.append(key)
            tVal.append(dictName[key])
        exec('{}=pd.Series(tVal,index=tLab)'.format(bindingName))

    def pandasToDict(self,pdName,dictName):
        varIt=0
        for k in list(pdName.index):
            a=pdName[varIt]
            dictName[k]=a
            varIt=varIt+1

class pdUtil:

    def getPath(self):

        self.selectPath = fd.askdirectory(title ="what what?")

    def getFilePath(self):

        self.selectPath = fd.askopenfilename(title ="what what?",defaultextension='.csv')

    def setSessionPath(self):
        dirPathFlg=os.path.isdir(self.dirPath_tv.get())
        if dirPathFlg==False:
            os.mkdir(self.dirPath_tv)
        self.dirPath.set(self.dirPath_tv)
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

    def refreshDictFromGui(self,dictName):
        for key in list(dictName.keys()):
            a=eval('self.{}_tv.get()'.format(key))
            try:
                a=float(a)
                if a.is_integer():
                    a=int(a)
                exec('dictName["{}"]={}'.format(key,a))
            except:
                exec('dictName["{}"]="{}"'.format(key,a))


    def refreshGuiFromDict(self,dictName):

        for key in list(dictName.keys()):
            eval('self.{}_tv.set(dictName["{}"])'.format(key,key))

    def exportAnimalMeta(self):
        pdVariables.dictToPandas(self,self.stMapD,'self.stateMap')
        self.stateMap.to_csv('{}{}_stateMap.csv'.format(self.dirPath_tv.get() + '/',self.animalIDStr_tv.get()))

        pdUtil.refreshDictFromGui(self,self.sesVarD)
        pdVariables.dictToPandas(self,self.sesVarD,'self.sesVarBindings')
        self.sesVarBindings.to_csv('{}{}_sesVars.csv'.format(self.dirPath_tv.get() + '/',self.animalIDStr_tv.get()))
        
        pdVariables.dictToPandas(self,self.stVarD,'self.stateVarBindings')
        self.stateVarBindings.to_csv('{}{}_stateVars.csv'.format(self.dirPath_tv.get() + '/',self.animalIDStr_tv.get()))
        
        pdVariables.dictToPandas(self,self.task1D,'self.task1Bindings')
        self.task1Bindings.to_csv('{}{}_task1Probs.csv'.format(self.dirPath_tv.get() + '/',self.animalIDStr_tv.get()))
        
        pdVariables.dictToPandas(self,self.task2D,'self.task2Bindings')
        self.task2Bindings.to_csv('{}{}_task2Probs.csv'.format(self.dirPath_tv.get() + '/',self.animalIDStr_tv.get()))

class pdSerial:
    def syncSerial(self):
        lBS=self.stMapD['bootState']
        ranHeader=0
        self.trialDataExists=0
        while ranHeader==0:
            gaveFeedback=0
            ranHeader=1
            loopCount=0
        while ranHeader==1:
            self.comObj.write(struct.pack('>B',lBS))
            pdSerial.serial_readDataFlush(self)
            if self.serDataAvail==1:
                self.currentState = int(self.sR[self.stID_state])
                if self.currentState != lBS:
                    if gaveFeedback==0:
                        print('mc state is not right, thinks it is #: {}'.format(self.currentState))
                        print('will force boot state, might take a second or so ...')
                        print('!!!! ~~> UI may become unresponsive for 1-30 seconds or so, but I havent crashed ...')
                        gaveFeedback=1
                    loopCount=loopCount+1
                    if loopCount % 5000 ==0:
                        print('still syncing: state #: {}; loop #: {}'.format(self.currentState,loopCount))
                elif self.currentState==lBS:
                    print('ready: mc is in state #: {}'.format(self.currentState))
                    return

    def serial_initComObj(self):
        if self.comObjectExists==0:
            print('Opening serial port: {}'.format(self.comPath_tv.get()))
            self.comObj = serial.Serial(self.comPath_tv.get(),self.baudSelected.get()) 
            pdSerial.syncSerial(self)
            self.comObjectExists=1

            # update the GUI
            self.comPathLabel.config(text="COM Object Connected ***",justify=LEFT,fg="green",bg="black") 
            self.comPathEntry.config(state=DISABLED)
            self.baudPick.config(state=DISABLED)
            self.createCom_button.config(state=DISABLED)
            self.startBtn.config(state=NORMAL)
            self.closeComObj_button.config(state=NORMAL)
            self.syncComObj_button.config(state=NORMAL)
        
    def serial_closeComObj(self):
        if self.comObjectExists==1:
            if self.trialDataExists==1:
                pdData.data_saveTrialData(self)
            pdSerial.syncSerial(self)
            self.comObj.close()
            self.comObjectExists=0
            print('> i closed the COM object')
            
            # update the GUI
            self.comPathLabel.config(text="COM Port Location:",justify=LEFT,fg="black",bg="white")
            self.comPathEntry.config(state=NORMAL)
            self.baudPick.config(state=NORMAL)
            self.createCom_button.config(state=NORMAL)
            self.startBtn.config(state=DISABLED)
            self.closeComObj_button.config(state=DISABLED)
            self.syncComObj_button.config(state=DISABLED)

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
        self.cueSelected=[]
        self.stimSelected=[]
        self.shapingTrial=[]
        self.rewardPort=[]
        self.punishedPort=[]
        self.selectedPort=[]

        self.rewardContingency=[] 
        self.choiceOutcome=[]

        self.PooledTasks=[]
        
        self.sRewardTarget=[];
        self.sPunishTarget=[];
        self.sOutcome=[]; 
        self.trialSampRate=[]
        self.trialTimes=[]
        self.rcCol=[]
        self.toCol=[]
        self.shapingReport=[]
        self.leftReward=[]
        self.waitLicks0=[]
        self.waitLicks1=[]
        self.waitConditionMetTime=[]
        self.trialLeft1Prob=[]
        self.trialLeft2Prob=[]
        
        self.stimLicks0=[]
        self.stimLicks1=[]
        self.stimLeftLickTimes=[]
        self.stimRightLickTimes=[]
        self.stimLeftLickInds=[]
        self.stimRightLickInds=[]

        self.rewardLicks0=[]
        self.rewardLicks1=[]
        self.rewardLeftLickTimes=[]
        self.rewardRightLickTimes=[]
        self.rewardLeftLickInds=[]
        self.rewardRightLickInds=[]

        self.presLeftFreq=[]
        self.presRightFreq=[]
        self.lickedLeft=[]
        self.lickedRight=[]
        self.smoothedLickBias=[]
        self.completedTrials=[]

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
        self.thrLicksB_time=[]
        self.thrLicksA_time=[]
        self.thrLicksB_stateTime=[]
        self.thrLicksA_stateTime=[]
        self.thrLicksB_state=[]
        self.thrLicksA_state=[]
        self.stateLickCount0=[]
        self.stateLickCount1=[]
        
        # debug/time roundtrips
        self.pyStatesRS = []
        self.pyStatesRT = []
        self.pyStatesTT = []
        self.pyStatesTS = []

    def correct9DOF(self,rOrient,maxDelta):
        cTheta=rOrient-self.lastOrientation
        rollCorrectTheta=cTheta
        if cTheta>maxDelta: # rolled from 180 to -180 (pos to neg)
            rollCorrectTheta=(cTheta-180)*-1
        elif cTheta<-maxDelta: # rolled -180 over to positive
            rollCorrectTheta=(cTheta+180)*-1
        return rollCorrectTheta
         
    def data_parseData(self):
        self.mcTrialTime.append(float(int(self.sR[self.stID_time])/self.timeBase))
        self.mcStateTime.append(float(int(self.sR[self.stID_trialTime])/self.timeBase))

        orientWRoll=int(self.sR[self.stID_pos])
        noRollOrient=pdData.correct9DOF(self,orientWRoll,290)
        
        self.orientation.append(orientWRoll)
        
        self.lastOrientation=self.orientation[-1]
        
        self.posDelta.append(noRollOrient)
        
        self.absolutePosition.append(self.lastPos+noRollOrient)
        self.lastPos=self.absolutePosition[-1]
        self.currentState=int(self.sR[self.stID_state])
        self.arStates.append(self.currentState)
        self.lickValsA.append(int(self.sR[self.stID_lickSensor_a]))
        self.lickValsB.append(int(self.sR[self.stID_lickSensor_b]))
        pdAnalysis.lickDetection(self)
        self.trialDataExists=1

    def data_saveTrialData(self):
        self.dateSvStr = datetime.datetime.fromtimestamp(time.time()).strftime('%H%M_%m%d%Y')

        saveStreams='mcTrialTime','mcStateTime','absolutePosition','posDelta','orientation','arStates',\
        'lickValsA','lickValsB','stateLickCount0','stateLickCount1','stillTime','motionTime','anState_acceleration',\
        'pdAnalysis_acelThreshold','pyStatesRS','pyStatesRT','pyStatesTS','pyStatesTT','thrLicksA','thrLicksB',\
        'thrLicksA_time','thrLicksB_time','thrLicksA_stateTime','thrLicksB_stateTime','thrLicksA_state','thrLicksB_state'

        self.tCo=[]
        for x in range(0,len(saveStreams)):
            exec('self.tCo=self.{}'.format(saveStreams[x]))
            if x==0:
                self.rf=pd.DataFrame({'{}'.format(saveStreams[x]):self.tCo})
            elif x != 0:
                self.tf=pd.DataFrame({'{}'.format(saveStreams[x]):self.tCo})
                self.rf=pd.concat([self.rf,self.tf],axis=1)

        self.rf.to_csv('{}{}_{}_s{}_trial_{}.csv'.\
            format(self.dirPath_tv.get() + '/', self.animalIDStr_tv.get(),\
                self.dateSvStr, self.sesVarD['currentSession'],self.currentTrial))
        self.trialDataExists=0
    
    def data_saveSessionData(self):
        self.dateSvStr = datetime.datetime.fromtimestamp(time.time()).\
        strftime('%H%M_%m%d%Y')

        saveStreams='rewardContingency','choiceOutcome','PooledTasks','cueSelected','stimSelected','sRewardTarget',\
        'sPunishTarget','sOutcome','trialTimes','rcCol','toCol','shapingReport','waitLicks0','waitLicks1','stimLicks0',\
        'stimLicks1','waitConditionMetTime','smoothedLickBias','trialSampRate','trialLeft1Prob','trialLeft2Prob',\
        'stimLeftLickTimes','stimRightLickTimes','stimLeftLickInds','stimRightLickInds','leftReward',\
        'lickedLeft','lickedRight','presLeftFreq','presRightFreq','smoothedLickBias'
        
        self.tCo=[]
        for x in range(0,len(saveStreams)):
            exec('self.tCo=self.{}'.format(saveStreams[x]))
            if x==0:
                self.rf=pd.DataFrame({'{}'.format(saveStreams[x]):self.tCo})
            elif x != 0:
                self.tf=pd.DataFrame({'{}'.format(saveStreams[x]):self.tCo})
                self.rf=pd.concat([self.rf,self.tf],axis=1)

        self.rf.to_csv('{}{}_{}_s{}_sessionData.csv'.\
            format(self.dirPath_tv.get() + '/', self.animalIDStr_tv.get(),\
                self.dateSvStr, self.sesVarD['currentSession']))
        self.sessionDataExists=0

class pdPlot:

    def positionPlot(self,gridBnd,gridCoord,colS,rowS):
        self.pXMin=-50
        self.pXMax=200
        self.positionAxes=plt.subplot2grid(gridBnd,gridCoord,colspan=colS,rowspan=rowS)
        self.positionAxes.set_ylim([self.pXMin,self.pXMax])
        self.positionAxes.set_yticks([])
        self.positionAxes.set_xticks([])
        self.positionAxes.set_title('pos',fontsize=10)
        self.positionLine,=self.positionAxes.plot([],color="olive",lw=1)
        self.positionThreshLine,=self.positionAxes.plot([0,2000],[20,20],color="black",lw=1,linestyle='--')

        plt.show(block=False)
        self.trialFig.canvas.flush_events()

        self.positionAxes.draw_artist(self.positionLine)
        self.positionAxes.draw_artist(self.positionThreshLine)
        self.positionAxes.draw_artist(self.positionAxes.patch)

    def lickLeftValPlot(self,gridBnd,gridCoord,colS,rowS):
        self.lXMin=0
        self.lXMax=1500
        self.leftLickAxes=plt.subplot2grid(gridBnd,gridCoord,colS,rowS)
        self.leftLickAxes.set_yticks([])
        self.leftLickAxes.set_xticks([])
        self.leftLickAxes.set_title('left',fontsize=10)
        self.leftLickAxes.set_ylim([self.lXMin,self.lXMax])
        self.lickLeftValLine,=self.leftLickAxes.plot([],color=self.pClrs['left'])
        self.lickLeftThreshLine,=self.leftLickAxes.plot([0,2000],[600,600],color="black",lw=1,linestyle='--')

        plt.show(block=False)
        self.trialFig.canvas.flush_events()

        self.leftLickAxes.draw_artist(self.lickLeftValLine)
        self.leftLickAxes.draw_artist(self.lickLeftThreshLine)
        self.leftLickAxes.draw_artist(self.leftLickAxes.patch)

    def lickRightValPlot(self,gridBnd,gridCoord,colS,rowS):
        self.rXMin=0
        self.rXMax=1500
        self.rightLickAxes=plt.subplot2grid(gridBnd,gridCoord,colS,rowS)
        self.rightLickAxes.set_yticks([])
        self.rightLickAxes.set_xticks([])
        self.rightLickAxes.set_title('right',fontsize=10)
        self.rightLickAxes.set_ylim([self.rXMin,self.rXMax])
        self.lickRightValLine,=self.rightLickAxes.plot([],color=self.pClrs['right'])
        self.lickRightThreshLine,=self.rightLickAxes.plot([0,2000],[600,600],color="black",lw=1,linestyle='--')

        plt.show(block=False)
        self.trialFig.canvas.flush_events()

        self.rightLickAxes.draw_artist(self.lickRightValLine)
        self.rightLickAxes.draw_artist(self.lickRightThreshLine)
        self.rightLickAxes.draw_artist(self.rightLickAxes.patch)

    def trialPlotFig(self):
        self.pClrs={'right':'#D9220D','cBlue':'#33A4F3','cPurp':'#6515D9',\
        'cOrange':'#F7961D','left':'cornflowerblue','cGreen':'#29AA03'}
        # plt.style.use('dark_background')
        self.trialFramePosition='+370+0' # can be specified elsewhere
        
        self.updateTrialAxes=0

        trialPlotOpts={'distPlotMinVal':-400,'distPlotMaxVal':1200,'lickAMin':0,'lickAMax':1300}
        self.trialPlotOpts=trialPlotOpts

        self.trialFig = plt.figure(100,figsize=(6.5,3.5), dpi=100)
        self.trialFig.suptitle('state 0',fontsize=10)
        self.trialSubCR=[3,6]
        self.trialFig.subplots_adjust(wspace=0.1,hspace=0.1)
        mng = plt.get_current_fig_manager()
        eval('mng.window.wm_geometry("{}")'.format(self.trialFramePosition))
        plt.show(block=False)
        self.trialFig.canvas.flush_events()

        pdPlot.positionPlot(self,self.trialSubCR,(0,3),1,1)
        pdPlot.lickLeftValPlot(self,self.trialSubCR,(0,4),1,1)
        pdPlot.lickRightValPlot(self,self.trialSubCR,(0,5),1,1)

        #start state
        self.stPlotX={'boot':0.10,'wait':0.10,'init':0.10,'cue1':0.30,'cue2':0.30,\
        'stm1':0.50,'stm2':0.50,'lRwd':0.80,'TOb':0.80,'TOa':0.70,'rRwd':0.70,'save':0.40}
        
        self.stPlotY={'boot':0.90,'wait':0.65,'init':0.40,'cue1':0.52,'cue2':0.28,\
        'stm1':0.52,'stm2':0.28,'lRwd':0.52,'TOb':0.28,'TOa':0.675,'rRwd':0.125,'save':0.90}

        # # todo:link actual state dict to plot state dict, now its a hack
        self.stPlotRel={'0':0,'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'21':7,\
        '24':8,'24':9,'22':10,'13':11}
        
        self.stAxes = plt.subplot2grid(self.trialSubCR,(0, 0),colspan=3,rowspan=3)
        self.stAxes.set_ylim([-0.02,1.02])
        self.stAxes.set_xlim([-0.02,1.02])
        self.stAxes.set_axis_off()
        self.stMrkSz=28
        self.txtOff=-0.02

        self.pltX=[]
        for xVals in list(self.stPlotX.values()):
            self.pltX.append(xVals)
        self.pltY=[]
        for yVals in list(self.stPlotY.values()):
            self.pltY.append(yVals)

        self.stPLine,=self.stAxes.plot(self.pltX,self.pltY,\
            marker='o',markersize=self.stMrkSz,markeredgewidth=2,\
            markerfacecolor="white",markeredgecolor="black",lw=0)
        k=0
        for stAnTxt in list(self.stPlotX.keys()):
            tASt="{}".format(stAnTxt)
            self.stAxes.text(self.pltX[k],self.pltY[k]+self.txtOff,tASt,\
                horizontalalignment='center',fontsize=9,fontdict={'family': 'monospace'})
            k=k+1

        self.curStLine,=self.stAxes.plot(self.pltX[0],self.pltY[0],\
            marker='o',markersize=self.stMrkSz+2,markeredgewidth=2,\
            markerfacecolor=self.pClrs['cPurp'],\
            markeredgecolor='black',lw=0,alpha=0.5)

        plt.show(block=False)
        self.trialFig.canvas.flush_events()

        # start port
        self.portPltVrs={'lPX':0.25,'rPX':0.75,'prsY':0.75,'rptY':0.2,'labDelt':0.12,'lineDelt':0.1}
        self.portAxes = plt.subplot2grid(self.trialSubCR, (1,3), colspan=3,rowspan=2)
        self.portAxes.set_ylim([0,1])
        self.portAxes.set_xlim([0,1])
        self.portAxes.set_axis_off()
        rTxtOff=0.2

        self.leftSelectedLine,=self.portAxes.plot(self.portPltVrs['lPX'],self.portPltVrs['prsY'],\
            marker='o',markersize=25,markeredgewidth=2,markerfacecolor="white",markeredgecolor=self.pClrs['left'])
        self.rightSelectedLine,=self.portAxes.plot(self.portPltVrs['rPX'],self.portPltVrs['prsY'],\
            marker='o',markersize=25, markeredgewidth=2, markerfacecolor="white", markeredgecolor=self.pClrs['right'])
        self.portAxes.plot([self.portPltVrs['lPX']+self.portPltVrs['lineDelt'],self.portPltVrs['rPX']-self.portPltVrs['lineDelt']],\
            [self.portPltVrs['prsY'],self.portPltVrs['prsY']],'k:')
        self.portAxes.text(0.5,self.portPltVrs['prsY']+self.portPltVrs['labDelt'],'presented',\
            horizontalalignment='center',fontsize=11, fontdict={'family': 'monospace'})
        self.portAxes.text(self.portPltVrs['lPX'],self.portPltVrs['prsY'],'L',horizontalalignment='center',\
            verticalalignment='center',fontsize=10, fontdict={'family': 'monospace'})
        self.portAxes.text(self.portPltVrs['rPX'],self.portPltVrs['prsY'],'R',horizontalalignment='center',\
            verticalalignment='center',fontsize=10, fontdict={'family': 'monospace'})
        self.leftPortPresText=self.portAxes.text(self.portPltVrs['lPX'],self.portPltVrs['prsY']-rTxtOff,'0.5',\
            horizontalalignment='center',verticalalignment='center',fontsize=10, fontdict={'family': 'monospace'})
        self.rightPortPresText=self.portAxes.text(self.portPltVrs['rPX'],self.portPltVrs['prsY']-rTxtOff,'0.5',\
            horizontalalignment='center',verticalalignment='center',fontsize=10, fontdict={'family': 'monospace'})
        plt.show(block=False)
        self.trialFig.canvas.flush_events()

        plotArgsT={'marker':'o','markersize':'25','markeredgewidth':'2'}
        self.leftReportLine,=self.portAxes.plot(self.portPltVrs['lPX'],self.portPltVrs['rptY'],**plotArgsT, markerfacecolor="white",\
         markeredgecolor=self.pClrs['left'])
        self.rightReportLine,=self.portAxes.plot(self.portPltVrs['rPX'],self.portPltVrs['rptY'],marker='o',\
            markersize=25,markeredgewidth=2, markerfacecolor="white", markeredgecolor=self.pClrs['right'])
        self.portAxes.plot([self.portPltVrs['lPX']+self.portPltVrs['lineDelt'],self.portPltVrs['rPX']-self.portPltVrs['lineDelt']],\
            [self.portPltVrs['rptY'],self.portPltVrs['rptY']],'k:')
        self.portAxes.text(0.5,self.portPltVrs['rptY']+self.portPltVrs['labDelt'],'reported',horizontalalignment='center',fontsize=11, \
            fontdict={'family': 'monospace'})
        self.portAxes.text(self.portPltVrs['lPX'],self.portPltVrs['rptY'],'L',horizontalalignment='center',verticalalignment='center',\
            fontsize=10, fontdict={'family': 'monospace'})
        self.portAxes.text(self.portPltVrs['rPX'],self.portPltVrs['rptY'],'R',horizontalalignment='center',verticalalignment='center',\
            fontsize=10, fontdict={'family': 'monospace'})
        self.leftPortReportText=self.portAxes.text(self.portPltVrs['lPX'],self.portPltVrs['rptY']-rTxtOff,'0.0',\
            horizontalalignment='center',verticalalignment='center',fontsize=10, fontdict={'family': 'monospace'})
        self.rightPortReportText=self.portAxes.text(self.portPltVrs['rPX'],self.portPltVrs['rptY']-rTxtOff,'0.0',\
            horizontalalignment='center',verticalalignment='center',fontsize=10, fontdict={'family': 'monospace'})

        self.trialFig.canvas.draw_idle()
        plt.show(block=False)

        self.stAxes.draw_artist(self.stPLine)
        self.stAxes.draw_artist(self.curStLine)
        self.stAxes.draw_artist(self.stAxes.patch)

        self.portAxes.draw_artist(self.leftSelectedLine)
        self.portAxes.draw_artist(self.rightSelectedLine)
        self.portAxes.draw_artist(self.leftReportLine)
        self.portAxes.draw_artist(self.rightReportLine)
        self.portAxes.draw_artist(self.leftPortReportText)
        self.portAxes.draw_artist(self.rightPortReportText)
        self.portAxes.draw_artist(self.portAxes.patch)


        self.trialFig.canvas.flush_events()
        self.lastSplit=2000 #todo: why do i use this?

    def updateTrialFig(self):
        splt=int(self.sampsToPlot_tv.get())
        if splt != self.lastSplit:
            self.positionAxes.set_xlim([0,splt])
            self.leftLickAxes.set_xlim([0,splt])
            self.rightLickAxes.set_xlim([0,splt])

        self.lastSplit=splt
        if self.updateTrialAxes==1:
            self.positionAxes.set_ylim([self.pXMin,self.pXMax])
            self.leftLickAxes.set_ylim([self.lXMin,self.lXMax])
            self.rightLickAxes.set_ylim([self.lXMin,self.lXMax])
            self.updateTrialAxes=0

        tLeftLickThr=int(self.lickThresholdStrValA_tv.get())
        tRightLickThr=int(self.lickThresholdStrValB_tv.get())

        stPltData=np.array(self.arStates[-int(splt):])
        posPltData=np.array(self.absolutePosition[-int(splt):])
        posThreshPltData=[self.stVarD['distThr'],self.stVarD['distThr']]
        lickLeftPltData=self.lickValsA[-int(splt):]
        lickLeftThreshData=[tLeftLickThr,tLeftLickThr]
        lickRightPltData=self.lickValsB[-int(splt):]
        lickRightThreshData=[tRightLickThr,tRightLickThr]
        
        x0=np.arange(len(stPltData))
        x1=[0,splt]
        if self.stateLickCount0[-1]>0 and self.currentState:
            self.leftReportLine.set_markerfacecolor("gray")
            self.leftPortPresText.set_text('{}'.format("%.3g" % self.task1D['t1LeftProb']))
        elif self.stateLickCount0[-1]==0:
            self.leftReportLine.set_markerfacecolor("white")
            self.leftPortPresText.set_text('{}'.format("%.3g" % self.task1D['t1LeftProb']))
        if self.stateLickCount1[-1]>0:
            self.rightReportLine.set_markerfacecolor("gray")
            self.rightPortPresText.set_text('{}'.format("%.3g" % (1-self.task1D['t1LeftProb'])))
        elif self.stateLickCount1[-1]==0:
            self.rightReportLine.set_markerfacecolor("white")
            self.rightPortPresText.set_text('{}'.format("%.3g" % (1-self.task1D['t1LeftProb'])))
        
        if len(self.stimSelected)==self.currentTrial:
            if (self.punishedPort[-1]==1):
                    self.leftSelectedLine.set_markerfacecolor("red")
            elif (self.punishedPort[-1]==2):
                self.rightSelectedLine.set_markerfacecolor("red")
            elif (self.punishedPort[-1]==0): # wipe both and the right one will fill
                self.leftSelectedLine.set_markerfacecolor("white")
                self.rightSelectedLine.set_markerfacecolor("white")
            if (self.rewardPort[-1]==1):
                self.leftSelectedLine.set_markerfacecolor("green")
            elif (self.rewardPort[-1]==2):
                self.rightSelectedLine.set_markerfacecolor("green")
            elif (self.rewardPort[-1]==0):
                self.rightSelectedLine.set_markerfacecolor("white")

        np.random.seed()

        self.curStLine.set_xdata(self.pltX[self.stPlotRel['{}'.format(self.currentState)]])
        self.curStLine.set_ydata(self.pltY[self.stPlotRel['{}'.format(self.currentState)]])
        self.stAxes.draw_artist(self.stPLine)
        self.stAxes.draw_artist(self.curStLine)
        self.stAxes.draw_artist(self.stAxes.patch)


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
        
        self.positionAxes.draw_artist(self.positionLine)
        self.positionAxes.draw_artist(self.positionThreshLine)
        self.positionAxes.draw_artist(self.positionAxes.patch)

        self.leftLickAxes.draw_artist(self.lickLeftValLine)
        self.leftLickAxes.draw_artist(self.lickLeftThreshLine)
        self.leftLickAxes.draw_artist(self.leftLickAxes.patch)

        self.rightLickAxes.draw_artist(self.lickRightValLine)
        self.rightLickAxes.draw_artist(self.lickRightThreshLine)
        self.rightLickAxes.draw_artist(self.rightLickAxes.patch)
        self.portAxes.draw_artist(self.leftPortReportText)
        self.portAxes.draw_artist(self.rightPortReportText)
        self.portAxes.draw_artist(self.leftSelectedLine)
        self.portAxes.draw_artist(self.rightSelectedLine)
        self.portAxes.draw_artist(self.leftReportLine)
        self.portAxes.draw_artist(self.rightReportLine)
        self.portAxes.draw_artist(self.portAxes.patch)

        self.trialFig.canvas.draw_idle()
        self.trialFig.canvas.flush_events()

    def trailFigResizeCntrls(self):

        self.resizeControlPosition='+158+740'
        resizeTrialPlotsFrame = Toplevel()
        eval('resizeTrialPlotsFrame.wm_geometry("{}")'.format(self.resizeControlPosition))

        resizeTrialPlotsFrame.title('Resize Trial Plots')
        self.resizeTrialPlotsFrame=resizeTrialPlotsFrame

        self.minLabel = Label(resizeTrialPlotsFrame, text="Min:",width=6).grid(row=0,column=1)
        self.maxLabel = Label(resizeTrialPlotsFrame, text="Max:",width=6).grid(row=0,column=2)

        posRow=2
        self.dAxesLabel = Label(resizeTrialPlotsFrame, text="Position:",width=6).grid(row=posRow,column=0)
        self.distPlotMin_tv=StringVar(resizeTrialPlotsFrame)
        self.distPlotMin_tv.set(self.pXMin)
        self.dmnE=Entry(master=resizeTrialPlotsFrame,textvariable=self.distPlotMin_tv,width=6)
        self.dmnE.grid(row=posRow, column=1)
        self.distPlotMax_tv=StringVar(resizeTrialPlotsFrame)
        self.distPlotMax_tv.set(self.pXMax)
        self.dmxE=Entry(master=resizeTrialPlotsFrame,textvariable=self.distPlotMax_tv,width=6)
        self.dmxE.grid(row=posRow, column=2)

        lickRow=3
        self.lAxesLabel = Label(resizeTrialPlotsFrame, text="Lick:",width=6).grid(row=lickRow,column=0)
        self.lickPlotMin_tv=StringVar(resizeTrialPlotsFrame)
        self.lickPlotMin_tv.set(self.lXMin)
        self.lkMinE=Entry(master=resizeTrialPlotsFrame,textvariable=self.lickPlotMin_tv,width=6)
        self.lkMinE.grid(row=lickRow, column=1)
        self.lickPlotMax_tv=StringVar(resizeTrialPlotsFrame)
        self.lickPlotMax_tv.set(self.lXMax)
        self.lkMaxE=Entry(master=resizeTrialPlotsFrame,textvariable=self.lickPlotMax_tv,width=6)
        self.lkMaxE.grid(row=lickRow, column=2)

        self.setAxesBtn = Button(master=resizeTrialPlotsFrame, text='Set', command=lambda:pdPlot.setAxesBtnCB(self))
        self.setAxesBtn.configure(width=6)
        self.setAxesBtn.grid(row=4, column=2)

    def setAxesBtnCB(self):
        self.pXMin=int(self.distPlotMin_tv.get())
        self.pXMax=int(self.distPlotMax_tv.get())
        self.lXMin=int(self.lickPlotMin_tv.get())
        self.lXMax=int(self.lickPlotMax_tv.get())
        self.rXMin=int(self.lickPlotMin_tv.get())
        self.rXMax=int(self.lickPlotMax_tv.get())

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

    def sessionFig(self):
        self.tTrials=int(self.totalTrials_tv.get())
        self.lastTTrials=int(self.totalTrials_tv.get())
        self.updateSessionAxes=0

        # make and position the figure
        self.sessionFramePosition='+370+440' # todo: want to specify this in a log
        self.sessionFig=plt.figure(101,figsize=(6.5,5),dpi=100)
        self.sessionFig.suptitle('session stats',fontsize=10)
        self.sessionFig.subplots_adjust(wspace=0.7,hspace=0.5)
        self.sesFigSubplotDim=[9,9]

        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # @@@@@@@@@ 1) Bias Axes @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        #
        # panel 1 is a plot of stimulus state licks that go left or right
        
        self.biasAxis=plt.subplot2grid(self.sesFigSubplotDim, (0, 0), colspan=4,rowspan=4)
        self.leftLickLine,=self.biasAxis.plot([],[],\
            marker="o",markeredgecolor="black",markerfacecolor=self.pClrs['left'],markersize=12,lw=0,alpha=0.7)
        self.rightLickLine,=self.biasAxis.plot([],[],\
            marker="o",markeredgecolor="black",markerfacecolor=self.pClrs['right'],markersize=12,lw=0,alpha=0.7)
        self.leftPresLine,=self.biasAxis.plot([],[],color=self.pClrs['left'])
        self.rightPresLine,=self.biasAxis.plot([],[],color=self.pClrs['right'])

        self.biasLineSmoothedBias,=self.biasAxis.plot([],[],'k-')
        self.biasLineZero,=self.biasAxis.plot([0,self.tTrials],[0,0],'k:')
        
        self.biasAxis.set_ylim([-1.1,1.1])
        self.biasAxis.set_xlim([0,self.tTrials])
        self.biasAxis.set_ylabel('count side bias (l-r)')
        self.biasAxis.set_xlabel('trial number')

        # plot once to cache, this allows artist to update later
        mng = plt.get_current_fig_manager()
        eval('mng.window.wm_geometry("{}")'.format(self.sessionFramePosition))
        plt.show(block=False)
        self.sessionFig.canvas.flush_events()

        self.biasAxis.draw_artist(self.leftLickLine)
        self.biasAxis.draw_artist(self.rightLickLine)
        self.biasAxis.draw_artist(self.leftPresLine)
        self.biasAxis.draw_artist(self.rightPresLine)
        self.biasAxis.draw_artist(self.biasLineZero)
        self.biasAxis.draw_artist(self.biasLineSmoothedBias)
        self.biasAxis.draw_artist(self.biasAxis.patch)

        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # @@@@@@@@@ 2) Outcome Axes @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        #
        # Panel 2 is a plot of the trial's choice outcome. 
        # 0 for wrong choice and 1 for right choice.
        # All other types of choice are 2.
        #
        self.outcomeAxis=plt.subplot2grid(self.sesFigSubplotDim,(0,6),colspan=4,rowspan=4)
        self.outcomeLine,=self.outcomeAxis.plot([],[],marker="o",markeredgecolor="black",\
            markerfacecolor="cornflowerblue",markersize=12,lw=0,alpha=0.5,markeredgewidth=2)
        self.outcomeAxis.axis([-2.1,2.1,self.tTrials+2,-2])
        self.outcomeAxis.yaxis.tick_right()
        self.outcomeAxis.set_title('Correct T1: {} , T2: {}'.format(0,0),fontsize=10)

        # cahce once 
        plt.show(block=False)
        self.sessionFig.canvas.flush_events()

        self.outcomeAxis.draw_artist(self.outcomeLine)
        self.outcomeAxis.draw_artist(self.outcomeAxis.patch)

        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # @@@@@@@@@ 3) Lick Histogram Axes @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        #
        # raw lick count histograms
        #
        self.lickHistScales=[0,20,0,0.5]
        numBins=5
        self.leftCountAxis=plt.subplot2grid(self.sesFigSubplotDim,[0,4],colspan=2,rowspan=2)
        n, binsl,patchesl=self.leftCountAxis.hist([],numBins,normed=1,facecolor=self.pClrs['left'])
        self.leftCountAxis.set_yticks([])
        self.leftCountAxis.set_xticks([])

        self.rightCountAxis=plt.subplot2grid(self.sesFigSubplotDim,[2,4],colspan=2,rowspan=2)
        o,binsr,patchesr=self.rightCountAxis.hist([],numBins,normed=1,facecolor=self.pClrs['right'])
        self.leftCountAxis.axis(self.lickHistScales)
        self.rightCountAxis.axis(self.lickHistScales)
        self.rightCountAxis.set_xlabel('lick counts')
        self.rightCountAxis.set_yticks([])


        # Histograms don't have the same artist scheme as lines or text.
        # So, nothing to assign. I still cache:
        plt.show(block=False)
        self.sessionFig.canvas.flush_events()

        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # @@@@@@@@@ 4) Stim Lick Raster @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        #
        # stim lick raster
        self.stimLickXMax=3
        self.stimLickAxes=plt.subplot2grid(self.sesFigSubplotDim,[5,0],colspan=3,rowspan=4)
        self.stimLickAxes.axis([0,self.stimLickXMax,self.tTrials+2, -2])
        self.stimLickAxes.set_xlabel('time since stimulus (s)')
        self.stimLickAxes.set_ylabel('trial number')
        self.stimLickLeftLine,=self.stimLickAxes.plot(np.random.random_sample(self.tTrials)*self.stimLickXMax,np.arange(self.tTrials),\
            marker="o",markeredgecolor="black",markerfacecolor=self.pClrs['left'],markersize=6,lw=0,alpha=0.8)
        self.stimLickRightLine,=self.stimLickAxes.plot(np.random.random_sample(self.tTrials)*self.stimLickXMax,np.arange(self.tTrials),\
            marker="o",markeredgecolor="black",markerfacecolor=self.pClrs['right'],markersize=6,lw=0,alpha=0.8)
        
        plt.show(block=False)
        self.sessionFig.canvas.flush_events()
        # todo: make a pixel grid
        self.stimLickAxes.draw_artist(self.stimLickLeftLine)
        self.stimLickAxes.draw_artist(self.stimLickRightLine)
        self.stimLickAxes.draw_artist(self.stimLickAxes.patch)

        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # @@@@@@@@@ 5) reward Lick Raster @@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        #
        # reward lick raster
        self.rwdRasterXMax=1
        self.rwdLickAxes=plt.subplot2grid(self.sesFigSubplotDim,[5,3],colspan=3,rowspan=4)
        self.rwdLickAxes.set_yticks([])
        self.rwdLickAxes.axis([0,self.rwdRasterXMax,self.tTrials+2,-2])
        self.rwdLickAxes.set_xlabel('time since reward (ms)')
        self.rwdLickLeftLine,=self.rwdLickAxes.plot(np.random.random_sample(self.tTrials)*\
            self.rwdRasterXMax,np.arange(self.tTrials),\
            marker="o",markeredgecolor="black",markerfacecolor=self.pClrs['left'],markersize=5,lw=0,alpha=0.8)
        self.rwdLickRightLine,=self.rwdLickAxes.plot(np.random.random_sample(self.tTrials)*\
            self.rwdRasterXMax,np.arange(self.tTrials),\
            marker="o",markeredgecolor="black",markerfacecolor=self.pClrs['right'],markersize=5,lw=0,alpha=0.8)

        plt.show(block=False)
        self.sessionFig.canvas.flush_events()
        self.rwdLickAxes.draw_artist(self.rwdLickLeftLine)
        self.rwdLickAxes.draw_artist(self.rwdLickRightLine)
        self.rwdLickAxes.draw_artist(self.rwdLickAxes.patch)
   
    def updateSessionFig(self):

        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # @@@@@@@@@ 0) Update Axes Scales If Needed @@@@@@@@@@@@@@@@@@@@@
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        #
        # if user changed trial count, rescale x-axis

        self.tTrials=int(self.totalTrials_tv.get())
        if self.tTrials!=self.lastTTrials:
            self.biasAxis.set_xlim([0,self.tTrials])
            self.stimLickAxes.axis([0,self.stimLickXMax,self.tTrials,0])
            self.rwdLickAxes.axis([0,self.rwdRasterXMax,self.tTrials,0])
            self.biasLineZero.set_xdata([0,self.tTrials])
        self.lastTTrials=self.tTrials

        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # @@@@@@@@@ 1) Bias Axes @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        #

        # Calculate how often a left choice, or right choice has been offered.
        if self.rewardPort[-1]==1:
            self.leftReward.append(1) #todo: do I need this?
        else:
            self.leftReward.append(0)

        self.presLeftFreq.append(np.mean(np.array(self.leftReward[-5:])))
        self.presRightFreq.append(np.mean(np.array(self.leftReward[-5:]))-1)
        tKern=pdPlot.gaussian(self,np.linspace(-0.5,0.5,21), 0, 0.05)
        smtLB=np.mean(np.array(self.lickedLeft[-5:]))
        smtRB=np.mean(np.array(self.lickedRight[-5:]))
        

        self.smoothedLickBias.append(np.array(smtLB)-np.array(smtRB))
        if len(self.smoothedLickBias)>3:
            self.biasP=stats.ttest_1samp(np.array(self.smoothedLickBias[-5:]),0).pvalue
        
        self.completedTrials.append(self.currentTrial)
        
        cueNP=np.array(self.cueSelected)
        chNP=np.array(self.choiceOutcome)

        self.t1Count=len(cueNP[cueNP==1])
        self.t2Count=len(cueNP[cueNP==2])
        
        self.t1Choices=chNP[cueNP==1]
        self.t2Choices=chNP[cueNP==2]
        
        if self.t1Count>0:
            self.t1Correct=len(self.t1Choices[self.t1Choices==1])/self.t1Count
        elif self.t1Count==0 or len(self.t1Choices)==0:
            self.t1Correct=0.0
        if self.t2Count>0:
            self.t2Correct=len(self.t2Choices[self.t2Choices==1])/self.t2Count
        elif self.t2Count==0 or len(self.t2Choices)==0:
            self.t2Correct=0.0
        self.outcomeAxis.set_title('Correct T1: {} , T2: {}'.\
            format("%.3g" % self.t1Correct,"%.3g" % self.t2Correct))


        x10=self.completedTrials
        self.leftLickLine.set_xdata(x10)
        self.rightLickLine.set_xdata(x10)
        self.leftPresLine.set_xdata(x10)
        self.rightPresLine.set_xdata(x10)
        self.biasLineSmoothedBias.set_xdata(np.arange(len(self.smoothedLickBias)))
        self.outcomeLine.set_ydata(x10)


        self.leftLickLine.set_ydata(self.lickedLeft)
        self.rightLickLine.set_ydata(np.array(self.lickedRight)*-1)
        self.leftPresLine.set_ydata(self.presLeftFreq)
        self.rightPresLine.set_ydata(self.presRightFreq)
        self.biasLineSmoothedBias.set_ydata(self.smoothedLickBias) 
        self.outcomeLine.set_xdata(self.choiceOutcome)

        self.biasAxis.draw_artist(self.leftLickLine)
        self.biasAxis.draw_artist(self.rightLickLine)
        self.biasAxis.draw_artist(self.leftPresLine)
        self.biasAxis.draw_artist(self.rightPresLine)
        self.biasAxis.draw_artist(self.biasLineZero)
        self.biasAxis.draw_artist(self.biasLineSmoothedBias)
        self.biasAxis.draw_artist(self.biasAxis.patch)
        self.outcomeAxis.draw_artist(self.outcomeLine)
        self.outcomeAxis.draw_artist(self.outcomeAxis.patch)


        # self.biasAxis.set_title('bias p={}'.format("%.3g" % self.biasP))
        self.stimLickLeftLine.set_xdata(self.stimLeftLickTimes)
        self.stimLickLeftLine.set_ydata(self.stimLeftLickInds)
        
        self.stimLickRightLine.set_xdata(self.stimRightLickTimes)
        self.stimLickRightLine.set_ydata(self.stimRightLickInds)
        
        self.stimLickAxes.draw_artist(self.stimLickLeftLine)
        self.stimLickAxes.draw_artist(self.stimLickRightLine)
        self.stimLickAxes.draw_artist(self.stimLickAxes.patch)

        self.sessionFig.canvas.draw_idle()
        self.sessionFig.canvas.flush_events()

        self.rwdLickLeftLine.set_xdata(self.rewardLeftLickTimes)
        self.rwdLickLeftLine.set_ydata(self.rewardLeftLickInds)
        self.rwdLickRightLine.set_xdata(self.rewardRightLickTimes)
        self.rwdLickRightLine.set_ydata(self.rewardRightLickInds)

        self.rwdLickAxes.draw_artist(self.rwdLickLeftLine)
        self.rwdLickAxes.draw_artist(self.rwdLickRightLine)
        self.rwdLickAxes.draw_artist(self.rwdLickAxes.patch)

        self.sessionFig.canvas.draw_idle()
        self.sessionFig.canvas.flush_events()

        numBins=10
        plt.sca(self.leftCountAxis)
        plt.cla()
        plt.sca(self.rightCountAxis)
        plt.cla()

        self.leftCountAxis=plt.subplot2grid(self.sesFigSubplotDim,[0,4],colspan=2,rowspan=2)
        n, binsl,patchesl=self.leftCountAxis.hist(np.nonzero(self.stimLicks0),\
            numBins,normed=1,facecolor=self.pClrs['left'])
        self.rightCountAxis=plt.subplot2grid(self.sesFigSubplotDim,[2,4],colspan=2,rowspan=2)
        o,binsr,patchesr=self.rightCountAxis.hist(np.nonzero(self.stimLicks1),\
            numBins,normed=1,facecolor=self.pClrs['right'])
        self.leftCountAxis.set_yticks([])
        self.leftCountAxis.set_xticks([])
        self.rightCountAxis.set_yticks([])
        self.leftCountAxis.axis([0,20,0,0.5])
        self.rightCountAxis.axis([0,20,0,0.5])
        self.rightCountAxis.set_xlabel('lick counts')
        
        plt.show(block=False)
        self.sessionFig.canvas.flush_events()

class pdAnalysis:

    def shapingUpdateLeftRightProb(self):
        bR=self.stVarD['biasRange']
        bL1P=self.stVarD['shapeC1_LPortProb']
        bL2P=self.stVarD['shapeC2_LPortProb']
        bPC=self.stVarD['biasPCut']
        bMC=self.stVarD['biasMuCut']
        lBD=self.stVarD['lBiasDelta']
        rBD=self.stVarD['rBiasDelta']

        meanBias=np.mean(np.array(self.smoothedLickBias[-5:]))
        if self.biasP<bPC and meanBias>bMC and (bL1P>lBD):  # leftward bias
            self.task1D['t1LeftProb']=float("%.2g" % (self.task1D['t1LeftProb']-lBD))
            self.task2D['t2LeftProb']=self.task1D['t1LeftProb']
            print('left bias detected; updated probs: {},{}'.\
                format(self.stVarD['shapeC1_LPortProb'],self.stVarD['shapeC2_LPortProb']))

        elif self.biasP<bPC and meanBias<-bMC and (bL1P<(1-rBD)):  # rightward bias
            self.task1D['t1LeftProb']=float("%.2g" % (self.task1D['t1LeftProb']+rBD))
            self.task2D['t1LeftProb']=self.task1D['t1LeftProb']
            print('right bias detected; updated probs: {},{}'.\
                format(self.stVarD['shapeC1_LPortProb'],self.stVarD['shapeC2_LPortProb']))
        
        if self.stVarD['shapeC1_LPortProb']>1.0: 
            self.stVarD['shapeC1_LPortProb']=1.0
            self.stVarD['shapeC2_LPortProb']=1.0

        if self.stVarD['shapeC1_LPortProb']<0.0: #todo: this is stupid; I should add the condition above, but ...
            self.stVarD['shapeC1_LPortProb']=0.0
            self.stVarD['shapeC2_LPortProb']=0.0

    def getLickTimesByState(self):
        tmpAStates=np.array([self.thrLicksA_state])
        tmpBStates=np.array([self.thrLicksB_state])
        tmpAStateTimes=np.array([self.thrLicksA_stateTime])
        tmpBStateTimes=np.array([self.thrLicksB_stateTime])
        tmpASpikeInd=self.currentTrial*np.array([self.thrLicksA])
        tmpBSpikeInd=self.currentTrial*np.array([self.thrLicksB])

        stATimes=tmpAStateTimes[(tmpAStates==self.stMapD['stim1State']) | (tmpAStates==self.stMapD['stim2State'])]
        stAInds=tmpASpikeInd[(tmpAStates==self.stMapD['stim1State']) | (tmpAStates==self.stMapD['stim2State'])]
        if len(stATimes)>0:
            self.stimLeftLickTimes=self.stimLeftLickTimes+stATimes.tolist()
            self.stimLeftLickInds=self.stimLeftLickInds+stAInds.tolist()
            self.lickedLeft.append(1)
            self.stimLicks0.append(len(self.stimLeftLickInds))
        else:
            self.stimLicks0.append(0)
            self.lickedLeft.append(0)
   
        stBTimes=tmpBStateTimes[(tmpBStates==self.stMapD['stim1State']) | (tmpBStates==self.stMapD['stim2State'])]
        stBInds=tmpBSpikeInd[(tmpBStates==self.stMapD['stim1State']) | (tmpBStates==self.stMapD['stim2State'])]
        if len(stBTimes)>0:
            self.stimRightLickTimes=self.stimRightLickTimes+stBTimes.tolist()
            self.stimRightLickInds=self.stimRightLickInds+stBInds.tolist()
            self.lickedRight.append(1)
            self.stimLicks1.append(len(self.stimRightLickInds))
        else:
            self.lickedRight.append(0)
            self.stimLicks1.append(0)

    def rewardLickTimes(self):
        tmpAStates=np.array([self.thrLicksA_state])
        tmpBStates=np.array([self.thrLicksB_state])
        tmpAStateTimes=np.array([self.thrLicksA_stateTime])
        tmpBStateTimes=np.array([self.thrLicksB_stateTime])
        tmpASpikeInd=self.currentTrial*np.array([self.thrLicksA])
        tmpBSpikeInd=self.currentTrial*np.array([self.thrLicksB])

        stATimes=tmpAStateTimes[(tmpAStates==self.stMapD['rewardState1']) |\
         (tmpAStates==self.stMapD['rewardState2'])]
        stAInds=tmpASpikeInd[(tmpAStates==self.stMapD['rewardState1']) |\
         (tmpAStates==self.stMapD['rewardState2'])]
        if len(stATimes)>0:
            self.rewardLeftLickTimes=self.rewardLeftLickTimes+stATimes.tolist()
            self.rewardLeftLickInds=self.rewardLeftLickInds+stAInds.tolist()
            self.rewardLicks0.append(len(self.rewardLeftLickInds))
        else:
            self.rewardLicks0.append(0)

   
        stBTimes=tmpBStateTimes[(tmpBStates==self.stMapD['rewardState1']) |\
         (tmpBStates==self.stMapD['rewardState2'])]
        stBInds=tmpBSpikeInd[(tmpBStates==self.stMapD['rewardState1']) |\
         (tmpBStates==self.stMapD['rewardState2'])]
        if len(stBTimes)>0:
            self.rewardRightLickTimes=self.rewardRightLickTimes+stBTimes.tolist()
            self.rewardRightLickInds=self.rewardRightLickInds+stBInds.tolist()
            self.rewardLicks1.append(len(self.rewardLeftLickInds))
        else:
            self.rewardLicks1.append(0)
        
    def getQunat(self,pyList,quantileCut):

        tA=np.abs(np.array(pyList))

    def updateLickThresholdA(self,dataSpan):  

        if self.ux_adaptThresh.get()==1:
            tA=np.abs(np.array(dataSpan))
            self.lickThresholdStrValA_tv.set(str(np.percentile(\
                tA[np.where(tA != 0)[0]],75)))
            self.lickMinMaxA=[min(dataSpan),max(dataSpan)]

    def updateLickThresholdB(self,dataSpan,quantileCut):

        if self.ux_adaptThresh.get()==1:
            tA=np.abs(np.array(dataSpan))
            self.lickThresholdStrValB_tv.set(str(np.percentile(\
                tA[np.where(tA != 0)[0]],quantileCut)))
            self.lickMinMaxB=[min(dataSpan),max(dataSpan)]

    def lickDetection(self):
        aThreshold=int(self.lickThresholdStrValA_tv.get())
        bThreshold=int(self.lickThresholdStrValB_tv.get())
            
        if self.lickValsA[-1]>aThreshold and self.lickThresholdLatchA==0:
            self.thrLicksA.append(1)
            self.thrLicksA_time.append(self.mcTrialTime[-1])
            self.thrLicksA_stateTime.append(self.mcStateTime[-1])
            self.thrLicksA_state.append(self.arStates[-1])
            self.lastLickCountA=self.lastLickCountA+1
            self.stateLickCount0.append(self.lastLickCountA)
            
            self.lastLickA=self.mcTrialTime[-1]    
            self.lickThresholdLatchA=1
        
        elif self.lickValsA[-1]<=aThreshold or self.lickThresholdLatchA==1:
            self.stateLickCount0.append(self.lastLickCountA)
            
        if self.lickValsB[-1]>bThreshold and self.lickThresholdLatchB==0:
            self.thrLicksB.append(1)
            self.thrLicksB_time.append(self.mcTrialTime[-1])
            self.thrLicksB_stateTime.append(self.mcStateTime[-1])
            self.thrLicksB_state.append(self.arStates[-1])
            self.lastLickCountB=self.lastLickCountB+1
            self.stateLickCount1.append(self.lastLickCountB)
            
            self.lastLickB=self.mcTrialTime[-1]
            self.lickThresholdLatchB=1
            
        elif self.lickValsB[-1]<=bThreshold or self.lickThresholdLatchB==1:
            self.stateLickCount1.append(self.lastLickCountB)

        if self.lickThresholdLatchA and self.lickValsA[-1]<=aThreshold:
            self.lickThresholdLatchA=0;

        if self.lickThresholdLatchB and self.lickValsB[-1]<=bThreshold:
            self.lickThresholdLatchB=0;

    def lickDetectionDebug(self):

        if self.lickValsA[-1]>int(self.lickThresholdStrValA_tv.get()):
            self.thrLicksA.append(1)
            self.thrLicksA_time.append(self.mcTrialTime[-1])
            self.thrLicksA_stateTime.append(self.mcStateTime[-1])
            self.thrLicksA_state.append(self.arStates[-1])
            self.lastLickCountA=self.lastLickCountA+1
            self.stateLickCount0[-1]=self.lastLickCountA+1

        if self.lickValsB[-1]>int(self.lickThresholdStrValB_tv.get()):
            self.thrLicksB.append(1)
            self.thrLicksB_time.append(self.mcTrialTime[-1])
            self.thrLicksB_stateTime.append(self.mcStateTime[-1])
            self.thrLicksB_state.append(self.arStates[-1])
            self.lastLickCountB=self.lastLickCountB+1
            self.stateLickCount1[-1]=self.lastLickCountB+1

    def checkMotion(self,acelThr,sampThr):
        self.anState_acceleration.append(np.mean(np.array(self.posDelta[-int(sampThr):])))
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
            print('no thanks; you chose the state you are in, \
                no infinite loops for me :)')
            return
        self.targetState=targetState
        if self.trialDataExists==1:
            self.pyStatesRS.append(self.targetState)
            self.pyStatesRT.append(self.mcTrialTime[-1])
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

    def stateHeader(self):
        ranHeader=0 # set the latch, the header runs once per entry.
        while ranHeader==0:
            self.cycleCount=1
            self.lastPos=0 # reset where we think the animal is
            self.lastLickCountA=0
            self.lastLickCountB=0
            self.entryTime=self.mcTrialTime[-1] # log state entry time
            self.stillTimeStart=int(0)
            self.stillLatch=0
            self.trialFig.suptitle('trial # {}; state # {}'.\
                format(self.currentTrial,self.currentState, fontsize=10))
            ranHeader=1 # fire the latch
        
    def coreState(self):
        uiUp=int(self.uiUpdateSamps_tv.get())
        self.fireCallback=0
        pdSerial.serial_readDataFlush(self)
        if self.serDataAvail==1:
            pdData.data_parseData(self)
            if self.cycleCount % uiUp == 0:
                pdTask.updatePlotCheck(self)
            self.fireCallback=1
            self.cycleCount=self.cycleCount+1;
        aT=self.stVarD['acelValThr']
        aS=self.stVarD['acelSamps']
        pdAnalysis.checkMotion(self,aT,aS)

class pdCallbacks:

    def waitStateCB(self):
        pdAnalysis.checkMotion(self,self.stVarD['acelValThr'],self.stVarD['acelSamps']) 
        if self.stillTime[-1]>self.stVarD['waitStillTime']:
            print('Still in wait state ==> S1 --> S2')
            self.waitConditionMetTime.append(self.mcStateTime[-1])
            self.waitLicks0.append(self.stateLickCount0[-1])
            self.waitLicks1.append(self.stateLickCount1[-1])
            pdState.switchState(self,self.stMapD['initiationState'])

    def initiationStateHead(self):
        t1P=self.task1D['t1Prob']
        self.task_switch=random.random()
        if self.task_switch<=t1P:
            self.cueSelected.append(1)
        elif self.task_switch>t1P:
            self.cueSelected.append(2)

    def initiationStateCB(self):
        dT=self.stVarD['distThr']  
        if self.absolutePosition[-1]>dT:
            print('moving spout; cue stim task #{}'.format(self.cueSelected[-1]))
            eval('pdState.switchState(self,self.stMapD["cue{}State"])'.\
                format(self.cueSelected[-1]))

    def cue1StateHead(self):

        self.outcomeSwitch=random.random()
        if (self.outcomeSwitch<=self.task1D['t1LeftProb']):
            self.stimSelected.append(1)
        elif (self.outcomeSwitch>self.task1D['t1LeftProb']):
            self.stimSelected.append(2)

        self.shapingSwitch=random.random()
        if self.shapingSwitch<=self.task1D['t1ShapingProb']:
            self.shapingTrial.append(1)
        elif self.shapingSwitch>self.task1D['t1ShapingProb']:
            self.shapingTrial.append(0)

        if self.stimSelected[-1]==1:
            self.rewardPort.append(1)
            self.punishedPort.append(2)

        elif self.stimSelected[-1]==2:
            self.rewardPort.append(2)
            self.punishedPort.append(1)

        if self.shapingTrial[-1]==1:
            self.punishedPort.append(0)

    def cue2StateHead(self):
        self.outcomeSwitch=random.random()
        if (self.outcomeSwitch<=self.task2D['t2LeftProb']):
            self.stimSelected.append(1)
        elif (self.outcomeSwitch>self.task2D['t2LeftProb']):
            self.stimSelected.append(2)

        self.shapingSwitch=random.random()
        if self.shapingSwitch<=self.task2D['t2ShapingProb']:
            self.shapingTrial.append(1)
        elif self.shapingSwitch>self.task2D['t2ShapingProb']:
            self.shapingTrial.append(0)

        if self.stimSelected[-1]==1:
            self.rewardPort.append(2)
            self.punishedPort.append(1)

        elif self.stimSelected[-1]==2:
            self.rewardPort.append(1)
            self.punishedPort.append(2)

        if self.shapingTrial[-1]==1:
            self.punishedPort.append(0)

    def cue1StateCB(self):
        if (self.mcStateTime[-1]>self.stVarD['cue1Dur']) and (self.stillTime[-1]>self.stVarD['genStillTime']):
            print('Still: Task 1 --> Stim {}: Rwd On Spout {}'.format(self.stimSelected[-1],self.rewardPort[-1]))
            exec('self.rewardContingency.append({}{})'.format(self.stimSelected[-1],self.rewardPort[-1]))
            eval('pdState.switchState(self,self.stMapD["stim{}State"])'.format(self.stimSelected[-1]))
            
    def cue2StateCB(self):
        if (self.mcStateTime[-1]>self.stVarD['cue2Dur']) and (self.stillTime[-1]>self.stVarD['genStillTime']):
            print('Still: Task 2 --> Stim {}: Rwd On Spout {}'.format(self.stimSelected[-1],self.rewardPort[-1]))
            eval('pdState.switchState(self,self.stMapD["stim{}State"])'.format(self.stimSelected[-1]))
            exec('self.rewardContingency.append({}{})'.format(self.stimSelected[-1],self.rewardPort[-1]))
    
    def stim1StateCB(self):
            
        if (self.shapingTrial[-1]==1):
            if (self.mcStateTime[-1]>self.task1D['t1ShapeTime']):
                if (self.rewardPort[-1]==1):
                    print('shape: reward left')
                    self.choiceOutcome.append(-1)
                    pdState.switchState(self,self.stMapD['rewardState1'])
                elif (self.rewardPort[-1]==2):
                    print('shape: reward right')
                    self.choiceOutcome.append(-2)
                    pdState.switchState(self,self.stMapD['rewardState2'])
                elif (self.rewardPort[-1]==0):
                    print('shape: no reward')
                    self.choiceOutcome.append(0)
                    pdState.switchState(self,self.stMapD['saveState'])

        elif (self.shapingTrial[-1]==0):
            if (self.mcStateTime[-1]>self.stVarD['minStim1Time']):
                if (self.rewardPort[-1]==1) and (self.stateLickCount0[-1]>0):
                    print('correct stim report: reward left')
                    self.choiceOutcome.append(1)
                    pdState.switchState(self,self.stMapD['rewardState1'])
                elif (self.rewardPort[-1]==2) and (self.stateLickCount1[-1]>0):
                    print('correct stim report: reward right')
                    self.choiceOutcome.append(2)
                    pdState.switchState(self,self.stMapD['rewardState2'])
                elif (self.rewardPort[-1]==1) and (self.stateLickCount1[-1]>0):
                    print('wrong stim report: Punish-> Time Out for {} seconds'.\
                        format(self.stVarD['tOutDur1']))
                    self.choiceOutcome.append(0)
                    pdState.switchState(self,self.stMapD['punishState1'])
                elif (self.rewardPort[-1]==2) and (self.stateLickCount0[-1]>0):
                    print('wrong stim report: Punish-> Time Out for {} seconds'.\
                        format(self.stVarD['tOutDur1']))
                    self.choiceOutcome.append(0)
                    pdState.switchState(self,self.stMapD['punishState1'])

        if (self.mcStateTime[-1]>self.stVarD['max1ReportTime']):
            print('timed out: did not report')
            self.choiceOutcome.append(0)
            pdState.switchState(self,self.stMapD['punishState1'])

    def stim2StateCB(self):
        if (self.shapingTrial[-1]==1):
            if (self.mcStateTime[-1]>self.task2D['t2ShapeTime']):
                if (self.rewardPort[-1]==1):
                    print('shape: reward left')
                    self.choiceOutcome.append(-1)
                    pdState.switchState(self,self.stMapD['rewardState1'])
                elif (self.rewardPort[-1]==2):
                    print('shape: reward right')
                    self.choiceOutcome.append(-2)
                    pdState.switchState(self,self.stMapD['rewardState2'])
                elif (self.rewardPort[-1]==0):
                    print('shape: no reward')
                    self.choiceOutcome.append(0)
                    pdState.switchState(self,self.stMapD['saveState'])

        elif (self.shapingTrial[-1]==0):
            if (self.mcStateTime[-1]>self.stVarD['minStim2Time']):
                if (self.rewardPort[-1]==1) and (self.stateLickCount0[-1]>0):
                    print('correct stim report: reward left')
                    self.choiceOutcome.append(1)
                    pdState.switchState(self,self.stMapD['rewardState1'])
                elif (self.rewardPort[-1]==2) and (self.stateLickCount1[-1]>0):
                    print('correct stim report: reward right')
                    self.choiceOutcome.append(2)
                    pdState.switchState(self,self.stMapD['rewardState2'])
                elif (self.rewardPort[-1]==1) and (self.stateLickCount1[-1]>0):
                    print('wrong stim report: Punish-> Time Out for {} seconds'.\
                        format(self.stVarD['tOutDur2']))
                    self.choiceOutcome.append(0)
                    pdState.switchState(self,self.stMapD['punishState1'])
                elif (self.rewardPort[-1]==2) and (self.stateLickCount0[-1]>0):
                    print('wrong stim report: Punish-> Time Out for {} seconds'.\
                        format(self.stVarD['tOutDur2']))
                    self.choiceOutcome.append(0)
                    pdState.switchState(self,self.stMapD['punishState1'])

        if (self.mcStateTime[-1]>self.stVarD['max2ReportTime']):
            print('timed out: did not report')
            self.choiceOutcome.append(0)
            pdState.switchState(self,self.stMapD['punishState1'])


    def rewardState1CB(self):
        if self.mcStateTime[-1]>=self.stVarD['rwdTime1']:
            pdState.switchState(self,self.stMapD['saveState'])

    def rewardState2CB(self):
        if self.mcStateTime[-1]>=self.stVarD['rwdTime2']:
            pdState.switchState(self,self.stMapD['saveState'])

    def neutralStateCB(self):
        if self.mcStateTime[-1]>self.stVarD['neutralTime']:
            print('no reward')
            pdState.switchState(self,self.stMapD['saveState'])

    def punishState1CB(self):
        if self.mcTrialTime[-1]-self.entryTime>=self.stVarD['tOutDur1']:
            print('timeout of {} seconds is over'.format(self.stVarD['tOutDur1']))
            pdState.switchState(self,self.stMapD['saveState'])

    def punishState2CB(self):
        if self.mcTrialTime[-1]-self.entryTime>=self.stVarD['tOutDur2']:
            print('timeout of {} seconds is over'.format(self.stVarD['tOutDur2']))
            pdState.switchState(self,self.stMapD['saveState'])

class pdWindow:

    def addMainBlock(self,startRow):
        self.startRow = startRow
        self.blankLine(self.master,startRow)

        self.mainCntrlLabel = Label(self.master, text="Main Controls:")\
        .grid(row=startRow,column=0,sticky=W)

        self.quitBtn = Button(self.master,text="Exit Program",command = \
            lambda: pdWindow.mwQuitBtn(self), width=self.col2BW)
        self.quitBtn.grid(row=startRow+1, column=2)

        self.startBtn = Button(self.master, text="Start Task",width=10,command=\
            lambda: pdTask.runSession(self) ,state=DISABLED)
        self.startBtn.grid(row=startRow+1, column=0,sticky=W,padx=10)

        self.endBtn = Button(self.master, text="End Task",width=self.col2BW, \
            command=lambda:pdState.switchState(self,self.stMapD['endState']),state=DISABLED)
        self.endBtn.grid(row=startRow+2, column=0,sticky=W,padx=10)

        self.stateEditBtn = Button(self.master, text="State Editor",\
            width=self.col2BW, command=self.stateEditWindow,state=NORMAL)
        self.stateEditBtn.grid(row=startRow+2,column=2,sticky=W,padx=10)

    def addSerialBlock(self,startRow):
        self.startRow = startRow

        # @@@@@ --> Serial Block
        self.comPathLabel = Label(self.master,text="COM Port Location:",justify=LEFT)
        self.comPathLabel.grid(row=startRow,column=0,sticky=W)

        self.comPath_tv=StringVar(self.master)
        self.comPathEntry=Entry(self.master,textvariable=self.comPath_tv)
        self.comPathEntry.grid(row=startRow+1, column=0)
        self.comPathEntry.config(width=24)
        
        if sys.platform == 'darwin':
            self.comPath_tv.set('/dev/cu.usbmodem2762721')
        elif sys.platform == 'win':
            self.comPath_tv.set('COM11')

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
        self.dateStr = datetime.datetime.fromtimestamp(time.time()).\
        strftime('%H:%M (%m/%d/%Y)')

        self.blankLine(self.master,startRow)
        self.sessionStuffLabel = Label(self.master,text="Session Stuff: ",justify=LEFT).\
        grid(row=startRow+1, column=0,sticky=W)

        self.timeDisp = Label(self.master, text=' #{} started: '\
            .format(self.sesVarD['currentSession']) + self.dateStr,justify=LEFT)
        self.timeDisp.grid(row=startRow+2,column=0,sticky=W)

        self.dirPath_tv=StringVar(self.master)
        self.pathEntry=Entry(self.master,textvariable=self.dirPath_tv,width=24,bg='grey')
        self.pathEntry.grid(row=startRow+3,column=0,sticky=W)
        self.dirPath_tv.set(os.path.join(os.getcwd(),self.animalID))

        self.setPath_button = Button(self.master,text="<- Set Path",\
            command=lambda:pdWindow.mwPathBtn(self),width=self.col2BW)
        self.setPath_button.grid(row=startRow+3,column=2)

        self.aIDLabel=Label(self.master, text="animal id:")\
        .grid(row=startRow+4,column=0,sticky=W)
        self.animalIDStr_tv=StringVar(self.master)
        self.animalIDEntry=Entry(self.master,textvariable=\
            self.animalIDStr_tv,width=14,bg='grey')
        self.animalIDEntry.grid(row=startRow+4,column=0,sticky=E)
        self.animalIDStr_tv.set(self.animalID)

        self.totalTrials_label = Label(self.master,text="total trials:")\
        .grid(row=startRow+5,column=0,sticky=W)
        self.totalTrials_tv=StringVar(self.master)
        self.totalTrials_tv.set('100')
        self.totalTrials_entry=Entry(self.master,textvariable=\
            self.totalTrials_tv,width=10).\
        grid(row=startRow+5,column=0,sticky=E)

        self.curSession_label = Label(self.master,text="current session:").grid(row=startRow+6,column=0,sticky=W)
        self.currentSession_tv=StringVar(self.master)
        self.currentSession_tv.set(self.sesVarD['currentSession'])
        self.curSession_entry=Entry(self.master,textvariable=\
            self.currentSession_tv,width=10)
        self.curSession_entry.grid(row=startRow+6,column=0,sticky=E)

        self.taskProbsBtn = Button(self.master,text='Task Probs',\
            width=self.col2BW,command=self.taskProbWindow)
        self.taskProbsBtn.grid(row=startRow+4, column=2)
        self.taskProbsBtn.config(state=NORMAL)

        self.stateTogglesBtn = Button(self.master,text = 'State Toggles',\
            width=self.col2BW,\
            command=self.stateToggleWindow)
        self.stateTogglesBtn.grid(row=startRow+5, column=2)
        self.stateTogglesBtn.config(state=NORMAL)
        
        self.stateVarsBtn = Button(self.master,text = 'State Vars',\
            width=self.col2BW,command = self.stateVarWindow)
        self.stateVarsBtn.grid(row=startRow+6, column=2)
        self.stateVarsBtn.config(state=NORMAL)

        self.loadAnimalMetaBtn = Button(self.master,text = 'Load Metadata',\
            width = self.col2BW,command = lambda: pdWindow.mwLoadMetaBtn(self))
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
        self.sampsToPlot_tv=StringVar(self.master)
        self.sampPlot_entry=Entry(self.master,width=5,textvariable=\
            self.sampsToPlot_tv)
        self.sampPlot_entry.grid(row=startRow+2, column=0,sticky=E)
        self.sampsToPlot_tv.set('1000')

        self.uiUpdateSamps_label = Label(self.master, text="samples / UI update:")
        self.uiUpdateSamps_label.grid(row=startRow+3, column=0,sticky=W)
        self.uiUpdateSamps_tv=StringVar(self.master)
        self.uiUpdateSamps_entry=Entry(self.master,width=5,textvariable=\
            self.uiUpdateSamps_tv)
        self.uiUpdateSamps_entry.grid(row=startRow+3, column=0,sticky=E)
        self.uiUpdateSamps_tv.set('500')


        self.togglePlotWinBtn=Button(self.master,text = 'Toggle Plot',\
            width=self.col2BW,\
            command=lambda:pdPlot.trialPlotFig(self))
        self.togglePlotWinBtn.grid(row=startRow+2, column=2)
        self.togglePlotWinBtn.config(state=NORMAL)

        self.debugWindowBtn=Button(self.master,text = 'Debug Toggles',\
            width=self.col2BW,\
            command=self.debugWindow)
        self.debugWindowBtn.grid(row=startRow+3, column=2)
        self.debugWindowBtn.config(state=NORMAL)

        self.lickMinMaxA=[-5,10]
        self.lastPos=0
        self.lastOrientation=0
        self.lickMin=0
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
        self.lickThresholdStrValA_tv=StringVar(self.master)
        
        self.lickThresholdB_label = Label(self.master,text="Thr B:")
        self.lickThresholdB_label.grid(row=startRow+3,column=0,padx=84,sticky=E)
        self.lickThresholdStrValB_tv=StringVar(self.master)

        self.aThrEntry=Entry(self.master,width=6,textvariable=\
            self.lickThresholdStrValA_tv)
        self.aThrEntry.grid(row=startRow+2, column=0,sticky=E,padx=5)
        self.bThrEntry=Entry(self.master,width=6,textvariable=\
            self.lickThresholdStrValB_tv)
        self.bThrEntry.grid(row=startRow+3, column=0,sticky=E,padx=5)
        
        self.lickThresholdStrValA_tv.set(400)
        self.lickThresholdStrValB_tv.set(400)
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

        # self.trialFramePosition='+375+0'
        # self.resizeControlPosition='+620+575'
        # self.debugTogglePosition="+375+350"
        # self.sessionFramePosition='+950+0'

        pyDiscrim.debugWindow(self)
        pdPlot.trialPlotFig(self)
        pdPlot.trailFigResizeCntrls(self)
        pdPlot.sessionFig(self)

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

    def loadMetaDataFromPath(self):
        stateString='{}{}_stateMap.csv'.format(self.selectPath + '/',self.animalIDStr_tv.get())
        sesString='{}{}_sesVars.csv'.format(self.selectPath + '/',self.animalIDStr_tv.get())
        stateVarString='{}{}_stateVars.csv'.format(self.selectPath + '/',self.animalIDStr_tv.get())
        t1PString='{}{}_task1Probs.csv'.format(self.selectPath + '/',self.animalIDStr_tv.get())
        t2PString='{}{}_task2Probs.csv'.format(self.selectPath + '/',self.animalIDStr_tv.get())

    def mwPathBtn(self):
        
        pdUtil.getPath(self)
        self.dirPath_tv.set(self.selectPath)
        self.pathEntry.config(bg='white')
        self.animalIDStr_tv.set(os.path.basename(self.selectPath))
        self.animalIDEntry.config(bg='white')
        self.sesPathFuzzy=0
        
        sesString='{}{}_sesVars.csv'.format(self.selectPath + '/',self.animalIDStr_tv.get())
        stMapString='{}{}_stateMap.csv'.format(self.selectPath + '/',self.animalIDStr_tv.get())
        stVarString='{}{}_stateVars.csv'.format(self.selectPath + '/',self.animalIDStr_tv.get())
        t1PString='{}{}_task1Probs.csv'.format(self.selectPath + '/',self.animalIDStr_tv.get())
        t2PString='{}{}_task2Probs.csv'.format(self.selectPath + '/',self.animalIDStr_tv.get())
        
        self.loadedSesVars=os.path.isfile(sesString)      
        self.loadedStates=os.path.isfile(stMapString)
        self.loadedStateVars=os.path.isfile(stVarString)
        self.loadedT1Probs=os.path.isfile(t1PString)
        self.loadedT2Probs=os.path.isfile(t2PString)
        
        if self.loadedSesVars is True:
            tempSesVar=pd.Series.from_csv(sesString)
            pdVariables.pandasToDict(self,tempSesVar,self.sesVarD)
            pdUtil.refreshGuiFromDict(self,self.sesVarD)

        if self.loadedStates is True:
            tempStMap=pd.Series.from_csv(stMapString)
            pdVariables.pandasToDict(self,tempStMap,self.stMapD)
                
        if self.loadedStateVars is True:
            tempStateVars=pd.Series.from_csv(stVarString)
            pdVariables.pandasToDict(self,tempStateVars,self.stVarD)
        
        if self.loadedT1Probs is True:
            tempT1Vars=pd.Series.from_csv(t1PString)
            pdVariables.pandasToDict(self,tempT1Vars,self.task1D)
        
        if self.loadedT2Probs is True:
            tempT2Vars=pd.Series.from_csv(t2PString)
            pdVariables.pandasToDict(self,tempT2Vars,self.task2D)


    def mwSaveMetaBtn(self):
        pdVariables.dictToPandas(self,self.stMapD,'self.stateMap')
        self.stateMap.to_csv('{}{}_stateMap.csv'.\
            format(self.dirPath_tv.get() + '/',self.animalIDStr_tv.get()))

        pdVariables.dictToPandas(self,self.sesVarD,'self.sesVarBindings')
        self.sesVarBindings.to_csv('{}{}_sesVars.csv'.\
            format(self.dirPath_tv.get() + '/',self.animalIDStr_tv.get()))
        
        pdVariables.dictToPandas(self,self.stVarD,'self.stateVarBindings')
        self.stateVarBindings.to_csv('{}{}_stateVars.csv'.\
            format(self.dirPath_tv.get() + '/',self.animalIDStr_tv.get()))
        
        pdVariables.dictToPandas(self,self.task1D,'self.task1Bindings')
        self.task1Bindings.to_csv('{}{}_task1Probs.csv'.\
            format(self.dirPath_tv.get() + '/',self.animalIDStr_tv.get()))
        
        pdVariables.dictToPandas(self,self.task2D,'self.task2Bindings')
        self.task2Bindings.to_csv('{}{}_task2Probs.csv'.\
            format(self.dirPath_tv.get() + '/',self.animalIDStr_tv.get()))

    def mwLoadMetaBtn(self):
        aa=fd.askopenfilename(title = "what what?",defaultextension='.csv')
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
        self.uiUpdateDelta=int(self.uiUpdateSamps_tv.get())
        self.ranTask=self.ranTask+1
        self.shouldRun=1
        self.sesVarD['currentSession']=int(self.currentSession_tv.get())

        np.random.seed()
        self.t1RCPairs=[10,21] # stim 1, reward left; stim 2 reward right
        self.t2RCPairs=[11,20]

    def runSession(self):
        pdTask.taskHeader(self)
        self.sessionStartTime=time.time()
        self.currentTrial=1
        trialCounter=1
        while self.currentTrial<=int(self.totalTrials_tv.get()) and self.shouldRun==1:
            pdTask.trial(self)
        pdData.data_saveSessionData(self)

        self.sesVarD['currentSession']=int(self.currentSession_tv.get())+1
        self.currentSession_tv.set(self.sesVarD['currentSession'])
        
        self.endBtn.config(state=DISABLED)
        self.startBtn.config(state=NORMAL)

        pdUtil.exportAnimalMeta(self)

        
        print('I completed {} trials.'.format(self.currentTrial-1))
        print('!!!!!!! --> Session #:{} Finished'.format(int(self.currentSession_tv.get())-1))
        
        self.updateDispTime()
        pdSerial.syncSerial(self)
    
    def trial(self):
        # make the dict states local, just for typing sake
        lBS=self.stMapD['bootState']
        lWS=self.stMapD['waitState']
        lIS=self.stMapD['initiationState']
        lC1S=self.stMapD['cue1State']
        lC2S=self.stMapD['cue2State']
        lS1S=self.stMapD['stim1State']
        lS2S=self.stMapD['stim2State']
        lCtS=self.stMapD['catchState']
        lSvS=self.stMapD['saveState']
        lR1S=self.stMapD['rewardState1']
        lR2S=self.stMapD['rewardState2']
        lNS=self.stMapD['neutralState']
        lPS=self.stMapD['punishState1']
        lES=self.stMapD['endState']

        self.trialStartTime=time.time()
        
        try:
            #S0 -----> hand shake (initialization state)
            if self.currentState==lBS:
                pdData.data_trialContainers(self)
                pdSerial.serial_readDataFlush(self)
                while self.currentState==lBS:
                    pdSerial.serial_readDataFlush(self)
                    if self.serDataAvail==1:
                        pdData.data_parseData(self)
                        pdState.switchState(self,lWS)
            
            #S1 -----> trial wait state
            elif self.currentState==lWS:
                pdState.stateHeader(self)
                while self.currentState==lWS:
                    pdState.coreState(self)
                    if self.fireCallback:
                        pdCallbacks.waitStateCB(self)

            
            #S2 -----> trial initiation state
            elif self.currentState==lIS:
                pdState.stateHeader(self)
                pdCallbacks.initiationStateHead(self)
                while self.currentState==lIS:
                    pdState.coreState(self)
                    if self.fireCallback:
                        pdCallbacks.initiationStateCB(self)
            
            #S3 -----> cue #1
            elif self.currentState==lC1S:
                pdState.stateHeader(self)
                pdCallbacks.cue1StateHead(self)
                while self.currentState==lC1S:
                    pdState.coreState(self)
                    if self.fireCallback:
                        pdCallbacks.cue1StateCB(self)

            #S4 -----> cue #2
            elif self.currentState==lC2S:
                pdState.stateHeader(self)
                pdCallbacks.cue2StateHead(self)
                while self.currentState==lC2S: 
                    pdState.coreState(self)
                    if self.fireCallback:
                        pdCallbacks.cue2StateCB(self)

            #S5 -----> stim tone #1
            elif self.currentState==lS1S:
                pdState.stateHeader(self)
                while self.currentState==lS1S:
                    pdState.coreState(self)
                    if self.fireCallback:
                        pdCallbacks.stim1StateCB(self)

            #S6 -----> stim tone #2
            elif self.currentState==lS2S:
                pdState.stateHeader(self)
                while self.currentState==lS2S:
                    pdState.coreState(self)
                    if self.fireCallback:
                        pdCallbacks.stim2StateCB(self)
            
            #S21 -----> reward state
            elif self.currentState==lR1S:
                pdState.stateHeader(self)
                while self.currentState==lR1S:
                    pdState.coreState(self)
                    if self.fireCallback:
                        pdCallbacks.rewardState1CB(self)
            #S22 -----> reward state
            elif self.currentState==lR2S:
                pdState.stateHeader(self)
                while self.currentState==lR2S:
                    pdState.coreState(self)
                    if self.fireCallback:
                        pdCallbacks.rewardState2CB(self)

            #S23 -----> neutral state
            elif self.currentState==lNS:
                pdState.stateHeader(self)
                while self.currentState==lNS:
                    pdState.coreState(self)
                    if self.fireCallback:
                        pdCallbacks.neutralStateCB(self)

            #S24 -----> punish state
            elif self.currentState==lPS:
                pdState.stateHeader(self)
                while self.currentState==lPS:
                    pdState.coreState(self)
                    if self.fireCallback:
                        pdCallbacks.punishState1CB(self)

            #S13: save state
            elif self.currentState==lSvS:
                pdTask.postTrialAnalysis(self)
                pdData.data_saveTrialData(self)
                pdData.data_trialContainers(self)
                pdTask.postTrialCleanup(self)
                pdState.switchState(self,lBS)

            #S25: end session state
            elif self.currentState==self.stMapD['endState']:
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
            pdPlot.updateTrialFig(self)
        self.cycleCount=0

    def postTrialAnalysis(self):
        pdAnalysis.getLickTimesByState(self)
        pdAnalysis.rewardLickTimes(self)
        if (self.currentTrial % self.stVarD['biasRange']==0) and (self.stVarD['correctBias']==1):
            pdAnalysis.shapingUpdateLeftRightProb(self)
        self.trialLeft1Prob.append(self.stVarD['shapeC1_LPortProb'])
        self.trialLeft2Prob.append(self.stVarD['shapeC2_LPortProb'])
        self.trialSampRate.append(np.mean(np.diff(np.array(self.mcTrialTime))))
        pdPlot.updateSessionFig(self)

    def postTrialCleanup(self):
        self.trialEndTime=time.time()
        trialTime=self.trialEndTime-self.trialStartTime
        self.trialTimes.append(trialTime)
        self.leftSelectedLine.set_markerfacecolor("white")
        self.rightSelectedLine.set_markerfacecolor("white")
        self.portAxes.draw_artist(self.leftSelectedLine)
        self.portAxes.draw_artist(self.rightSelectedLine)
        self.portAxes.draw_artist(self.portAxes.patch)
        self.trialFig.canvas.draw_idle()
        self.trialFig.canvas.flush_events()
        print('last trial took: {} seconds'.format(trialTime))
        self.currentTrial=self.currentTrial+1
        self.sessionTrialCount=self.sessionTrialCount+1 
        print('trial {} done, saved its data'.format(self.currentTrial-1))

class pyDiscrim:

    def __init__(self,master):
        self.master = master
        self.frame = Frame(self.master)
        root.wm_geometry("+0+0")
        pdVariables.setSessionVars(self)
        pdWindow.pdWindowPopulate(self)
        print('curTrial={}'.format(self.currentTrial))
        print('curSession={}'.format(self.sesVarD['currentSession']))
        pdVariables.setStateNames(self)
        pdVariables.setTaskProbs(self)
        pdVariables.setStateVars(self)
        pdData.data_serialInputIDs(self)
        pdData.data_serialInputIDs(self)
        pdData.data_sessionContainers(self)
        self.comObjectExists=0

    def blankLine(self,targ,startRow):
        self.guiBuf=Label(targ, text="")
        self.guiBuf.grid(row=startRow,column=0,sticky=W)

    def updateDispTime(self):
        self.dateStr = datetime.datetime.\
        fromtimestamp(time.time()).strftime('%H:%M (%m/%d/%Y)')
        self.timeDisp.config(text=' #{} started:'\
            .format(self.sesVarD['currentSession']) + self.dateStr)

    def debugWindow(self):
        self.debugTogglePosition="+130+660"
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

        self.sBtn_save = Button(st_frame, text="Save State", \
            command=lambda: pdState.switchState(self,\
                self.stMapD['saveState']),width=btWdth)
        self.sBtn_save.grid(row=sRw+1, column=sCl)
        self.sBtn_save.config(state=NORMAL)

        self.sBtn_endSession = Button(st_frame, text="End Session", \
            command=lambda: pdState.switchState(self,\
                self.stMapD['endState']),width=btWdth)
        self.sBtn_endSession.grid(row=sRw-2, column=sCl+1)
        self.sBtn_endSession.config(state=NORMAL)

        self.sBtn_boot = Button(st_frame, text="S0: Boot", \
            command=lambda: pdState.switchState(self,\
                self.stMapD['bootState']),width=btWdth)
        self.sBtn_boot.grid(row=sRw-1, column=sCl)
        self.sBtn_boot.config(state=NORMAL)

        self.sBtn_wait = Button(st_frame, text="S1: Wait", \
            command=lambda: pdState.switchState(self,\
                self.stMapD['waitState']),width=btWdth)
        self.sBtn_wait.grid(row=sRw, column=sCl)
        self.sBtn_wait.config(state=NORMAL)

        self.sBtn_initiate = Button(st_frame, text="S2: Initiate", \
            command=lambda: pdState.switchState(self,\
                self.stMapD['initiationState']),width=btWdth)
        self.sBtn_initiate.grid(row=sRw, column=sCl+1)
        self.sBtn_initiate.config(state=NORMAL)

        self.sBtn_cue1 = Button(st_frame, text="S3: Cue 1", \
            command=lambda: pdState.switchState(self,\
                self.stMapD['cue1State']),width=btWdth)
        self.sBtn_cue1.grid(row=sRw-1, column=sCl+2)
        self.sBtn_cue1.config(state=NORMAL)

        self.sBtn_cue2 = Button(st_frame, text="S4: Cue 2", \
            command=lambda: pdState.switchState(self,\
                self.stMapD['cue2State']),width=btWdth)
        self.sBtn_cue2.grid(row=sRw+1, column=sCl+2)
        self.sBtn_cue2.config(state=NORMAL)

        self.sBtn_stim1 = Button(st_frame, text="SS1: Stim 1", \
            command=lambda: pdState.switchState(self,\
                self.stMapD['stim1State']),width=btWdth)
        self.sBtn_stim1.grid(row=sRw-2, column=sCl+3)
        self.sBtn_stim1.config(state=NORMAL)

        self.sBtn_stim2 = Button(st_frame, text="SS1: Stim 2", \
            command=lambda: pdState.switchState(self,\
                self.stMapD['stim2State']),width=btWdth)
        self.sBtn_stim2.grid(row=sRw+2, column=sCl+3)
        self.sBtn_stim2.config(state=NORMAL)


        self.sBtn_catch = Button(st_frame, text="SC: Catch", \
            command=lambda: pdState.switchState(self,\
                self.stMapD['catchState']),width=btWdth)
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
                self,self.stMapD['neutralState']),width=btWdth)
        self.sBtn_neutral.grid(row=sRw, column=sCl+5)
        self.sBtn_neutral.config(state=NORMAL)

        self.sBtn_punish = Button(st_frame, text="SP: Punish", \
            command=lambda: pdState.switchState(\
                self,self.stMapD['punishState1']),width=btWdth)
        self.sBtn_punish.grid(row=sRw+0, column=sCl+4)
        self.sBtn_punish.config(state=NORMAL)

    def stateEditWindow(self):
        se_frame = Toplevel()
        se_frame.title('Set States')
        self.se_frame=se_frame
        self.populateVarFrameFromDict(self.stMapD,0,11,'state dictionary','se_frame')
        self.setStatesBtn = Button(se_frame, text = 'Set State IDs', width = 10, \
            command = lambda: pdUtil.refreshDictFromGui(self,self.stMapD))
        self.setStatesBtn.grid(row=len(self.stMapD)+2, column=1,sticky=E)

    def taskProbWindow(self):
        tb_frame = Toplevel()
        tb_frame.title('Task Probs')
        self.tb_frame=tb_frame
        self.populateVarFrameFromDict(self.task1D,0,0,'task 1','tb_frame')
        self.populateVarFrameFromDict(self.task2D,2,0,'task 2','tb_frame')
        self.setTaskProbsBtn = Button(tb_frame,text='Set Probs.',width = 10,\
            command = lambda: self.taskProbRefreshBtnCB())
        self.setTaskProbsBtn.grid(row=len(self.task1D)+2, column=1,sticky=W)

    def taskProbRefreshBtnCB(self):
        pdUtil.refreshDictFromGui(self,self.task1D)
        pdUtil.refreshDictFromGui(self,self.task2D)

    def stateVarWindow(self):
        frame_sv = Toplevel()
        frame_sv.title('State Vars')
        self.frame_sv=frame_sv
        self.populateVarFrameFromDict(self.stVarD,0,16,'state vars:','frame_sv')
        self.setStateVars = Button(frame_sv,text = 'Set Variables.', width = 9, command = lambda: pdUtil.refreshDictFromGui(self,self.stVarD))
        self.setStateVars.grid(row=len(self.stVarD)+2, column=1,sticky=W)

    def populateVarFrameFromDict(self,dictName,stCol,varPerCol,headerString,frameName):
        rowC=2
        stBCol=stCol+1
        spillCount=0
        exec('r_label = Label(self.{}, text="{}")'.format(frameName,headerString))
        exec('r_label.grid(row=1,column=stCol,sticky=W)'.format(dictName))
        for key in list(dictName.keys()):
            if varPerCol != 0:
                if (rowC % varPerCol)==0:
                    rowC=2
                    spillCount=spillCount+1
                    stCol=stCol+(spillCount+1)
                    stBCol=stCol+(spillCount+2)
            exec('self.{}_tv=StringVar(self.{})'.format(key,frameName))
            exec('self.{}_label = Label(self.{}, text="{}")'.format(key,frameName,key))
            exec('self.{}_entries=Entry(self.{},width=5,textvariable=self.{}_tv)'.format(key,frameName,key))
            exec('self.{}_label.grid(row={}, column=stBCol,sticky=W)'.format(key,rowC))
            exec('self.{}_entries.grid(row={}, column=stCol)'.format(key,rowC))
            exec('self.{}_tv.set({})'.format(key,dictName[key]))
            rowC=rowC+1
    
    def exceptionCallback(self):
        print('EXCEPTION thrown: I am going down')
        print('last trial = {} and the last state was {}.\
            I will try to save last trial ...'.\
            format(self.currentTrial,self.currentState))
        pdData.data_saveTrialData(self)
        pdData.data_saveSessionData(self)
        print('save was a success; now I will close com port and quit')
        print('I will try to reset the mc state before closing the port ...')
        self.comObj.close()
        #todo: add a timeout for the resync
        print('closed the com port cleanly')
        exit()

root = Tk()
app = pyDiscrim(root)
root.mainloop()