import json
import numpy as np
import copy
import pickle



def getStateID(slot="",value="",act = ""):
    if (act != ""):

        if(act == "request" ):
            return state_tree["request"][value]
        elif(act != "request" and slot == "" and value == ""):
            return state_tree[act]
        else:
            return state_tree[act][slot][value]

    else:
        return state_tree[slot][value]

# This function is to get the action correpond to the right turn of state
#
def getDS_action(log_data,turn_index):

    turn = log_data["turns"][turn_index]  # turn is a dict
    # parsing act
    #
    re_not = False
    dialog_actions = np.zeros((ACTIONS,1))
    dialog_acts = turn["output"]["dialog-acts"]
    for a in dialog_acts:
        dialog_action = np.zeros((ACTIONS,1))
        act = ""
        slot = ""
        value = ""
        if (len(a["slots"]) > 0):
            slot = a["slots"][0][0]
            value = a["slots"][0][1]
        act = a["act"]
        if (getActionID(slot,value,act) != -1):
            dialog_action[getActionID(slot,value,act)] = 1

            dialog_actions = np.concatenate((dialog_actions,dialog_action),axis=1)
            re_not = True
    if(re_not == True):
        dialog_actions = dialog_actions[:,1:]
    #print("actions = ",dialog_actions)
    return dialog_actions

def getActionID(slot,value,act):
    
    if (act == "offer"):
        return action_tree[act]
    elif (act == "inform" or act == "select"):   # regard select as inform
        return action_tree["inform"][slot]
    elif (act ==  "confirm"):
        return action_tree[act][slot][value]
    elif (act == "expl-conf" or act == "impl-conf"):  # regarf expl-conf and impl-conf as confirm
        act = "confirm"
        return action_tree[act][slot][value]
    elif (act not in action_tree):
        return -1
    else :
        return action_tree[act]

# This function will return a state's key for the state_act hash table 
def StateHash(state_value,state_hash):
    state_value = state_value.reshape(STATES,1)
    #print("state_hash shape is : ",state_hash.shape[1]-1)
    #print("state_hash value is", np.where(state_hash == 1))
    for t in range(state_hash.shape[1]):

        #print("state_hash[i] shape :", state_hash[t].shape[1])
        #print("state_value is :",state_value)
        #print("state_value  shape is :",state_value.shape)
        #print("state_hash[t] is :", state_hash[:,t])
        #print("state_hash[t].shape is :", state_hash[:,t].shape)
        temp = np.reshape(state_hash[:,t],(STATES,1))
        #print("norm = :",np.linalg.norm(temp-state_value))
        if (np.array_equal(temp,state_value) == True):   # check if two state is same
            #print("the state_hash and state_value is not diff")
            return [t,state_hash]
    state_hash = np.concatenate((state_hash,state_value),axis=1)
    #print("state_hash shape is ",state_hash.shape)
    return [state_hash.shape[1]-1,state_hash]


    #parsing transcript

    

if __name__ == "__main__":

#   First, read in the attribute (area, food, name, area)

    json_data = open('scripts/config/ontology_dstc2.json').read()
    attributes = json.loads(json_data)
    requestable = attributes["requestable"]

#   Building the state tree 
#   
#   I build the state_tree that are consist of multi-level dict 
#   
#               ----- food ----- chinese
#               |         |----- african
#               |         |------
#               |           .
#   state_tree--|-----pricerange
#               |
#               |-----name
#               |
#               |-----area
#               |
#               |-----ack
#               |
#               |-----affirm
#               |                               |---- chisese
#               |----- ....         |-----food------- african
#               |                   |           |---- ....
#               |----- confirm -----
#
#
#   build food subtree = ["chinese", "african", .....],
# 
    food = attributes["informable"]["food"]
    food.append("dontcare")
    FOOD = len(food)
    ff={}
    i = 0
    for f in food:
        ff[f] = i
        i += 1
    food = ff

    pricerange = attributes["informable"]["pricerange"]
    pricerange.append("dontcare")
    PRICERANGE = len(pricerange)
    pp = {}
    for p in pricerange:
        pp[p] = i
        i += 1
    pricerange = pp
# build name subtree
    name = attributes["informable"]["name"]
    name.append("dontcare")
    NAME = len(name)
    nn = {}
    for n in name:
        nn[n] = i
        i += 1
    name = nn
#   build area subtree
    area = attributes["informable"]["area"]
    area.append("dontcare")
    AREA = len(area)
    aa = {}
    for a in area:
        aa[a] = i
        i += 1
    area = aa

    s_v = {"food":food,"pricerange":pricerange,"name":name,"area":area}
    S_V = FOOD+PRICERANGE+NAME+AREA
    i = 12

#   store the id in the subtree
    confirm = copy.deepcopy(s_v)
    deny = copy.deepcopy(s_v)
    inform = copy.deepcopy(s_v)
    request = {}
    for key in confirm.keys():
        for value in confirm[key]:
            confirm[key][value] = S_V+i
            i += 1
    for key in deny.keys():
        for value in deny[key]:
            deny[key][value] = S_V+i
            i += 1
    for key in inform.keys():
        for value in inform[key]:
            inform[key][value] = S_V+i
            i += 1
    for value in requestable:
        request[value] = S_V+i
        i += 1

    STATES = S_V+i

#   combine subtree to whole tree
    
    state_tree = {"food":food,"pricerange":pricerange,"name":name,"area":area,"ack":S_V,"affirm":S_V+1,"bye":S_V+2,"hello":S_V+3 ,"help":S_V+4, "negate":S_V+5,"null":S_V+6,"repeat":S_V+7,"reqalts":S_V+8,"thankyou":S_V+9,"reqmore":S_V+10,"restart":S_V+11,"confirm":s_v, "deny": s_v, "inform":s_v,"request":request
                  }


#   Building the action_tree
#
    confirm = copy.deepcopy(s_v)
    inform = copy.deepcopy(request)
    request2 = copy.deepcopy(request)
    track = 0           # track is to calculate the ID
    for key in confirm.keys():
        for value in confirm[key]:
            confirm[key][value] += 5
            track = confirm[key][value]
    for key in inform.keys():
        track += 1
        inform[key] = track
    
    offer_n = track+1
    track += 1
    request_n = track+1
    track += 1
    welcomemsg_n = track+1
    track += 1
    


    action_tree  = {"affirm":0, "bye":1, "canthear":2, "confirm-domain":3, "negate":4, "confirm":confirm, "inform":inform,"offer":offer_n, "request": request_n,"welcomemsg":welcomemsg_n }
    ACTIONS = track+1
   # print("ACTIONS + ",ACTIONS) 
    # Read in the directory name contain training data 
    dirs = []
    with open('scripts/config/dstc2_train.flist') as f:
        dirs = f.read().splitlines()

    # each data is a dictionary in raw_data : key = directory name, value = data
    raw_datas = {}
    data_states = {}
    states_acts = {}
    state_hash = np.zeros((STATES,1))
    state_hash = np.reshape(state_hash,(STATES,1))
    #print(state_hash.shape)
    for di in dirs:
        dirlabel = 'data/'+di+'/label.json'
        dirlog = 'data/'+di+'/log.json'
        dirstate = 'data/'+di+'/states'
        #dirlabel = 'data/Mar13_S0A1/voip-b772dbf437-20130402_143019/label.json'
        json_data = open(dirlabel).read()
        label_data = json.loads(json_data)
        json_data = open(dirlog).read()
        log_data = json.loads(json_data)
        states = np.zeros((STATES,1))

        print("Processin", dirlabel, "...")
        for turn in label_data["turns"]:
            # save the last state's slot 
            state = np.copy(states[:,states.shape[1]-1].reshape(states.shape[0],1))            
            state[216:,0].fill(0)

            turn_index = turn["turn-index"]
            # for each turn of the dialogue
            for label in turn["semantics"]["json"]: #label is a dict
                act = ""
                slot = ""
                value = ""
                # find the act, slot, and value 
                if (len(label["slots"]) != 0):
                    if (label["slots"][0][0] == "this"):
                        #print(label)
                        #continue"
                        if (len(log_data["turns"][turn_index]["output"]["dialog-acts"][0]["slots"]) != 0):
                            slot = log_data["turns"][turn_index]["output"]["dialog-acts"][0]["slots"][0][1]
                            value = "dontcare"
                            if(slot not in state_tree):
                                continue
                        else:
                            continue
                    else:
                        slot = label["slots"][0][0]
                        value = label["slots"][0][1]
                act = label["act"]
                #print("act ",act)
                #print("slots ",slot)
                #print("value ",value)
                state[getStateID(slot,value,act)] = 1
                if ( act == 'inform'):
                    state[getStateID(slot,value,"")] = 1
                    
                elif ( act == 'deny'):
                    state[getStateID(slot,value,"")] = -1
                    
                elif (act == 'restart'):
                    state[:215,0].fill(0)

            # add the state-actions pairs
            actions = getDS_action(log_data,turn_index) 
            #print("ysys")
            if ( actions.any() != 0 ):
                #print(states.shape)
                #print(yee)
                [ID,state_hash] = StateHash(state,state_hash)
                #print(ID)
                #print(states_acts)
                if (ID not in states_acts):
                    states_acts[ID] = actions
                else:
                    states_acts[ID] = np.concatenate((states_acts[ID],actions),axis=1)
                #print("states_acts now is :",states_acts)
                #raw_input()
                # Add the states to the states of this episode 
                states = np.concatenate((states,state),axis=1)
            #print("states shape = ",states.shape)
            #print("state = ",np.where(state == 1))
            #print("state_hash = ",np.where(state_hash == 1))
            #raw_input()

            #check state is in state_hash
            #is_in_state_hash = False
            #for k in range(state_hash.shape[1]):
            #    print("state_hash[:,k] ", state_hash[:,k].shape)
            #    print("state ", state.shape)
            #    if(np.array_equal(state,state_hash[:,k].reshape(STATES,1)) == True):
            #       is_in_state_hash = True
            #if is_in_state_hash == False:
            #       print("The miss in state is in ",dirlabel)

        f = open('state-acts.txt','w')
        states = states[:,1:]
        for key in states_acts.keys():
                #f.write(str(key)+' ')
                #for r in range(states_acts[key].shape[1]):
            temp = str(key)
            np.savetxt(f,np.transpose(states_acts[key]),fmt='%00i',header='{} {}'.format("ID=",temp) )

        data_states[dirlabel] = states
        np.save(dirstate,states)
    #with open('state-acts.json','w') as fp:
    #    json.dump(states_acts,fp,sort_keys=True,indent=4)
    #with file('states_ID.txt','w') as outfile:
     
    np.save('states_ID.txt',state_hash)    
        #outfile.write('{0} ')
    f = open('state-acts.txt','w')
    for key in states_acts.keys():
                #f.write(str(key)+' ')
                #for r in range(states_acts[key].shape[1]):
        temp = str(key)
        np.savetxt(f,np.transpose(states_acts[key]),fmt='%00i',header='{} {}'.format("ID=",temp) )

    #for row in range(state_hash.shape[1]):
    #    f.write()
        #for key in states_acts.keys():
        #    print(state_hash.shape)
        #np.save(dirstate,states)



