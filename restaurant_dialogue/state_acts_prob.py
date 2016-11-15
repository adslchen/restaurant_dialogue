import numpy as np
from util import Counter
import pickle



def toTuple(a):
    try:
        return tuple(toTuple(i) for i in a)
    except TypeError:
        return a
ID_act_prob = {}
ID = 0
actionCounter = Counter()
with open('state-acts.txt','rb') as f:
    next(f) ##skip line 0
    for line in f:
            
        if line[0]!='#':
            action = -1  #from action 0 
            for a in line :
                if a !=' ':
                    action = action + 1
                if a =='1':
                    actionCounter[action] = actionCounter[action]+1
        else :
                
            ###Calculate Prob
            totalCount = 0
            ID_act_prob[ID] = np.array([actionCounter[n] for n in range(232)])
            for i in range(232):
                if actionCounter[i] !=0:
                    totalCount+= actionCounter[i]
            ID_act_prob[ID] = ID_act_prob[ID]*1.0/totalCount ##calulate prob

            ID = ID+1 ## nextID
            actionCounter = Counter() ##reinitialize after each state ID
    totalCount = 0
    ID_act_prob[ID] = np.array([actionCounter[n] for n in range(232)])
    for i in range(232):
        if actionCounter[i] !=0:
            totalCount+= actionCounter[i]
    ID_act_prob[ID] = ID_act_prob[ID]*1.0/totalCount ##calulate prob

IDtoState = np.load('states_ID.txt.npy')
print ID
print(IDtoState.shape)
IDtoState = IDtoState.transpose()
state_act_prob = {}
IDtoState = toTuple(IDtoState)
print len(IDtoState)
for state in range(len(IDtoState)):
    state_act_prob[IDtoState[state]] = ID_act_prob[state]


print state_act_prob[IDtoState[0]] 
#print state_act_prob[IDtoState[1]]
#print state_act_prob[IDtoState[1424]] 
#with open('state_act_prob.pickle', 'wb') as f:
 #   pickle.dump(state_act_prob, f)
