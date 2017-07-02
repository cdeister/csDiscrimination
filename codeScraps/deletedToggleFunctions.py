#deleted pyDiscrim functions that could be handy

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