'''
Green Monster GUI Revamp
Utilities for the whole program
Code Commissioned 2019-01-16
Code by A.J. Zec
Alarm Handler GUI spinoff
Cameron Clarke 2019-05-28
'''
import tkinter as tk
import subprocess, os
import csv
import alarm_object
from time import gmtime, strftime, localtime, strptime, mktime
from distutils.util import strtobool

green_color = '#3C8373'
lightgrey_color = '#E0E0E0'
lightergrey_color = '#E7E7E7'
grey_color = '#C0C0C0'
darkgrey_color = '#909090' # Maybe swap this for yellow everywhere?
red_button_color = '#9E1A1A'
red_color = '#ff0000'
yellow_color = '#ffff00'
orange_color = '#ff8800'
green_color = '#00ff00'
black_color = '#000000'
white_color = '#ffffff'
defaultKey = "NULL"

recentAlarmButtons = [-1,-1,-1,-1,-1]
camguinIDdict = {
    ("mean","ana"),("integral","ana"),
    ("burst","tree"),("mul","tree"),
    ("asym","prefix"),("diff","prefix"),("yield","prefix")
    }
#void camguin(TString ana = "help", TString tree = "mul", TString branch = "asym_vqwk_04_0ch0", TString leaf = "hw_sum", TString cut = "defaultCuts", Int_t overWriteCut = 0, TString histMode = "defaultHist", Int_t stabilityRing = 0, Int_t runNumber = 0, Int_t splitNumber = -1, Int_t nRuns = -1){

# Cameron Alarm Methods

def parse_textfile(fileArray):
  fileArray.mutex.acquire()
  fileArray.filearray = []
  try:
    with open(fileArray.filename) as csv_file:
      csv_reader = csv.reader(csv_file, delimiter=fileArray.delim)
      for row in csv_reader:
        rowList = []
        for col in row:
          rowList.append(col)
        fileArray.filearray.append(rowList)
  except IOError:
    print("Error, no textfile {} found".format(fileArray.filename))
    return []
  finally:
    fileArray.mutex.release()
    return fileArray.filearray

def parse_config(fa):
  fa.mutex.acquire()
  try:
    for each in fa.filearray:
      # Assume the conf file is all single entries per line, '=' separated
      if len(each)==2:
        eachKey = each[0].replace(' ','')
        eachVal = each[1].replace(' ','')
        fa.conf[eachKey] = eachVal
  finally:
    fa.mutex.release()


def update_config(alarmHandlerGUI):
  alarmHandlerGUI.filename = alarmHandlerGUI.conf.conf.get('alarmFilename',defaultKey)
  alarmHandlerGUI.histfilename = alarmHandlerGUI.conf.conf.get('historyFilename',defaultKey)
  alarmHandlerGUI.externalFilename = alarmHandlerGUI.conf.conf.get('externalFilename',defaultKey) # FIXME: make this a list to iterate through
  alarmHandlerGUI.externalParameterFileStaleTime = float(alarmHandlerGUI.conf.conf.get('staleExternalTime',defaultKey))
  alarmHandlerGUI.timeWait = int(alarmHandlerGUI.conf.conf.get('timeWaitHistory',defaultKey))
  alarmHandlerGUI.cooldownLength = int(alarmHandlerGUI.conf.conf.get('alarmCooldownTime',defaultKey))
  alarmHandlerGUI.remoteName = alarmHandlerGUI.conf.conf.get('remoteSoundServer',defaultKey)
  alarmHandlerGUI.showGrid = bool(strtobool(alarmHandlerGUI.conf.conf.get('showGrid',defaultKey)))
  alarmHandlerGUI.alertTheUser = bool(strtobool(alarmHandlerGUI.conf.conf.get('turnSoundOn',defaultKey)))
  alarmHandlerGUI.alertTheUserSound = alarmHandlerGUI.conf.conf.get('defaultAlertSound',defaultKey)
  alarmHandlerGUI.alertTheUserSoundNow = alarmHandlerGUI.conf.conf.get('defaultAlertSound',defaultKey)
  alarmHandlerGUI.includeExpert = bool(strtobool(alarmHandlerGUI.conf.conf.get('includeExpertPage',defaultKey)))

def write_conf(conf):
  outFile = open(conf.get("alarmConfig",defaultKey) ,'w+')
  wr = csv.writer(outFile,delimiter='=')
  outArray = []
  for key, each in conf.items():
    localAr = []
    key = key + "                          "
    key = key[:20]
    localAr.append(key)
    localAr.append(" "+each)
    outArray.append(localAr)
  if len(conf)!=0:
    filearrayrows=zip(*conf)
    wr.writerows(outArray)

def init_historyList(HL):
  tmpHistList = []
  for each in HL.filearray:
    tmpDict = {}
    for entry in each:
      #print(entry)
      entryPair1, entryPair2 = entry.split(HL.paramDelim,1)
      if entryPair1 == "Time":
        entryPair2 = entryPair2.replace(' ','')
        tmpTimeList = entryPair2[entryPair2.find("(")+1:entryPair2.find(")")]
        tmpTimeList = tmpTimeList.split(',')
        tmpTimeMap = {}
        for ents in tmpTimeList:
          #print(ents)
          a, b = ents.split('=')
          tmpTimeMap[a] = b
        tmpDict[entryPair1] = strptime("{}-{}-{} {}:{}:{}".format(tmpTimeMap["tm_year"],tmpTimeMap["tm_mon"],tmpTimeMap["tm_mday"],tmpTimeMap["tm_hour"],tmpTimeMap["tm_min"],tmpTimeMap["tm_sec"]),"%Y-%m-%d %H:%M:%S")
      else:
        tmpDict[entryPair1] = entryPair2 
    tmpHistList.append(tmpDict)
  return tmpHistList

def append_historyList(HL,OL,i):
  freshAlarm = 1
  localStr = "{}, {}, {}".format(OL.objectList[0][OL.objectList[2][i].parentIndices[0]].value,OL.objectList[1][OL.objectList[2][i].parentIndices[1]].value[:25],OL.objectList[2][i].value[:35]) # FIXME there are better ways to do this...
  for hl in HL.historyList: # Loop over all objects, check to see if they are already in the history, and if so then check their time stamp against right now + wait time
    #print("History time: {}, local time: {}, wait time: {}".format(mktime(hl.get("Time",defaultKey)), mktime(localtime()), HL.timeWait))
    if hl.get("Name",defaultKey) == localStr and hl.get("Time",defaultKey) != "NULL" and mktime(hl.get("Time",defaultKey)) > mktime(localtime()) - HL.timeWait:
      freshAlarm = 0
  if freshAlarm == 1:
    tmpDict = {}
    tmpList = []
    tmpDict["Name"] = localStr
    tmpList.append("Name={}".format(localStr))
    for eachKey, eachItem in OL.objectList[2][i].parameterList.items():
      tmpDict[eachKey] = eachItem
      tmpList.append("{}={}".format(eachKey,eachItem))
    tmpDict["Time"] = localtime()
    tmpList.append("Time={}".format(localtime()))
    HL.historyList.append(tmpDict)
    HL.filearray.append(tmpList)

def write_historyFile(HL):
  outFile = open(HL.filename,'w+')
  wr = csv.writer(outFile,delimiter=HL.delim)
  if len(HL.filearray)!=0:
    filearrayrows=zip(*HL.filearray)
    wr.writerows(HL.filearray)
    return HL.filearray

def backup_clear_hist(HL):
  tmpFileStore = HL.filename
  # Make a new unique name
  tmpFolderName = HL.filename[:HL.filename.rfind("/")+1] + "history_saves"
  HL.filename = tmpFolderName + HL.filename[HL.filename.rfind("/"):HL.filename.find(".csv")] + "_Save_{}.csv".format(mktime(localtime())) 
  saveFileName = "Alarms Saved to {}".format(HL.filename)
  print(saveFileName)
  # Save the backup
  write_historyFile(HL) 

  # Clear the current history
  HL.filename = tmpFileStore 
  HL.historyList = []
  HL.filearray = []
  return saveFileName

def update_objectList(OL,fileArray,alarmList):
  # Loop through column 3 (i = 2) and for each parameterList entry check if all column=4 entries have column3[i] as its parent
  # if it does then update it's child [0].value to be == key result
  # if parameterList key doesn't exist in list of col4 then make a new object and make it have name-value
  found = 0
  if len(OL.objectList)>=4: # Error out if there aren't 5 columns
    for i in range(0,len(OL.objectList[2])):
      for j in range(0,len(OL.objectList[3])):
        found = 0
        if OL.objectList[3][j].parentIndices[2]==OL.objectList[2][i].columnIndex: # Then the analysis is the parent of the current paramter
          counter=[]
          for k in range(0,len(OL.objectList[3])):
            counter.append(0)
          for k in range(0,len(OL.objectList[4])):
            counter[OL.objectList[4][k].parentIndices[3]] += 1 # Count how many times we see our parent, and only edit the first time
            if OL.objectList[4][k].parentIndices[3]==OL.objectList[3][j].columnIndex and counter[OL.objectList[4][k].parentIndices[3]]==1: # If our parent has our grandparent and If the item two on the right is the first to have the one on the right's columnIndex as a parent then show it - this allows us to append the prior value as a history if that is ever desired in the future FIXME FUTURE HISTORY IMPROVEMENT
              found = 1
              OL.objectList[4][k].value = alarmList[i].pList.get(OL.objectList[3][OL.objectList[4][k].parentIndices[3]].value,defaultKey) # Update the 5th column's key list
              #print("Value =  {}".format(alarmList[i].pList.get(OL.objectList[3][OL.objectList[4][k].parentIndices[3]].value,defaultKey)))
    if found==0:
      print("Available parameters don't contain the desired value, please add it")
  else:
    print("Incorrect alarm.csv file type")

def write_textfile(OL,fileArray):
  print("Writing text file to disk")
  fileArray.mutex.acquire()
  try: 
    fileArray.filearray = []
    # for each in OL.objectList
    #   define the start and stop indices
    #   find all child columns whose start and stop indices lie within
    #   while that condition is true print from left to right
  
    if len(OL.objectList)>1:
      i = len(OL.objectList)-1 # i = 5-1 = 4, last column
      for j in range(0,len(OL.objectList[i])): # Take the 5th column and make entries out of all of its parents values, in sequence
        entryarray = []
        parents = OL.objectList[i][j].parentIndices
        for k in range(0,len(parents)):
          entryarray.append(OL.objectList[k][parents[k]].value)
        entryarray.append(OL.objectList[i][j].value)
        fileArray.filearray.append(entryarray)
    outFile = open(fileArray.filename,'w+')
    wr = csv.writer(outFile,delimiter=fileArray.delim)
    filearrayrows=zip(*fileArray.filearray)
    wr.writerows(fileArray.filearray)
  finally:
    fileArray.mutex.release()
    return fileArray.filearray

def add_to_filearray(OL,fileArray,but):
  fileArray.mutex.acquire()
  try:
    i,j = but.indices
    j = OL.activeObjectColumnIndicesList[i]
    file_ind = OL.objectList[i][j].indexEnd+1
    addedLine = []
    for parent in range(0,i):
      addedLine.append(OL.objectList[parent][OL.activeObjectColumnIndicesList[parent]].value)
    for child in range(i,len(OL.objectList)):
      addedLine.append("NULL")
    fileArray.filearray.insert(file_ind,addedLine)
  finally:
    fileArray.mutex.release()
    return fileArray.filearray

def silence_filearray_menu(OL,fileArray,butMenu):
  fileArray.mutex.acquire()
  try:
    i,j = butMenu.indices
    # For it and its children set alarmStatus = "OK"
    if OL.objectList[i][j].userSilenceStatus == "Silenced":
      OL.objectList[i][j].userSilenceStatus = "Alert" 
      OL.objectList[i][j].alarm.userSilenceSelfStatus = "Alert" 
      OL.objectList[2][j].parameterList["User Silence Status"] = "Alert"
    elif OL.objectList[i][j].userSilenceStatus == "Alert":
      OL.objectList[i][j].userSilenceStatus = "Silenced" 
      OL.objectList[i][j].alarm.userSilenceSelfStatus = "Silenced" 
      OL.objectList[2][j].parameterList["User Silence Status"] = "Silenced"
      OL.objectList[i][j].color = yellow_color
    for q in range(OL.objectList[i][j].indexStart,OL.objectList[i][j].indexEnd+1):
      if fileArray.filearray[q][3] == "User Silence Status": # Update the filearray too
        fileArray.filearray[q][4] = OL.objectList[i][j].userSilenceStatus
  finally:
    fileArray.mutex.release()

def notify_acknowledge_filearray_menu(OL,fileArray,butMenu):
  fileArray.mutex.acquire()
  try:
    i,j = butMenu.indices
    tmpStat = OL.objectList[i][j].userNotifyStatus.split(' ')
    if OL.objectList[i][j].parameterList.get("Trip Counter",defaultKey) != "NULL":
      OL.objectList[i][j].parameterList["Trip Counter"] = "0"
    if tmpStat[0] == "Cooldown":
      OL.objectList[i][j].userNotifyStatus = "OK" # The user is manually OKing this alarm... 
      OL.objectList[i][j].parameterList["User Notify Status"] = "OK"
      OL.objectList[i][j].alarm.userNotifySelfStatus = "OK"
    else:
      # The user is just now acknowledging, therefore start the cooldown
      OL.objectList[i][j].userNotifyStatus = "Cooldown {}".format(int(OL.cooldownLength))
      OL.objectList[i][j].parameterList["User Notify Status"] = "Cooldown {}".format(int(OL.cooldownLength))
      OL.objectList[i][j].alarm.userNotifySelfStatus = "Cooldown {}".format(int(OL.cooldownLength))
      #OL.objectList[i][j].color = yellow_color
    for q in range(OL.objectList[i][j].indexStart,OL.objectList[i][j].indexEnd+1):
      if fileArray.filearray[q][3] == "User Notify Status": # Update the filearray too
        #print("Printing to filearray[{}][{}] User Notify Status = {}".format(q,4,OL.objectList[i][j].userNotifyStatus))
        fileArray.filearray[q][4] = OL.objectList[i][j].userNotifyStatus
  finally:
    fileArray.mutex.release()

def edit_filearray_menu(OL,fileArray,butMenu):
  fileArray.mutex.acquire()
  try:
    i,j = butMenu.indices
    file_ind_start = OL.objectList[i][j].indexStart
    file_ind_stop = OL.objectList[i][j].indexEnd
    for k in range(file_ind_start,file_ind_stop+1): # +1 is so it will do the first one if both ==
      fileArray.filearray[k][i] = butMenu.editValue # i is the column... where our data word exists
  finally:
    fileArray.mutex.release
    return fileArray.filearray

def subshift(L, start, end, insert_at):
  temp = L[start:end]
  L = L[:start] + L[end:]
  return L[:insert_at] + temp + L[insert_at:]

def move_filearray_menu(OL,fileArray,butMenu):
  fileArray.mutex.acquire()
  try:
    i,j = butMenu.indices
    mvN = butMenu.moveN
    # Shift fileArray down by moveN, make it == the values at tmpFA[moveNind][i]
    # Shift fileArray[+moveNind] up by size of moved bit
    file_ind_start = OL.objectList[i][j].indexStart
    file_ind_stop = OL.objectList[i][j].indexEnd
    #print("col {}, entry {}, move by {}, start file ind {}, end file ind {}, position to plant into {}".format(i,j,mvN,file_ind_start,file_ind_stop,OL.objectList[i][j+mvN].indexEnd))
    #inplace_shift(fileArray.filearray,file_ind_start,file_ind_stop-file_ind_start+1,file_ind_distance+file_ind_start)
    if mvN>0:
      #fileArray.filearray = subshift(fileArray.filearray,file_ind_start,file_ind_stop+1,OL.objectList[i][j+mvN].indexEnd)
      fileArray.filearray = subshift(fileArray.filearray,file_ind_start,file_ind_stop+1,OL.objectList[i][j+mvN].indexEnd-(file_ind_stop-file_ind_start))
    if mvN<0:
      fileArray.filearray = subshift(fileArray.filearray,file_ind_start,file_ind_stop+1,OL.objectList[i][j+mvN].indexStart)
  finally:
    fileArray.mutex.release()
    return fileArray.filearray

def copy_filearray_menu(OL,fileArray,butMenu):
  fileArray.mutex.acquire()
  try:
    i,j = butMenu.indices
    copyN = butMenu.copyName
    copyFileArray = []
    file_ind_start = OL.objectList[i][j].indexStart
    file_ind_stop = OL.objectList[i][j].indexEnd
    #print("col {}, entry {}, copy newName = {}, start file ind {}, end file ind {}".format(i,j,copyN,file_ind_start,file_ind_stop))
    if copyN != None:
      for l in range(file_ind_start,file_ind_stop+1):
        copyFileArray.append(fileArray.filearray[l].copy())
      for h in range(0,len(copyFileArray)):
        copyFileArray[h][i] = copyN
    for k in reversed(range(0,len(copyFileArray))):
      fileArray.filearray.insert(file_ind_stop+1,copyFileArray[k])
  finally:
    fileArray.mutex.release()
    return fileArray.filearray

def delete_filearray_menu(OL,fileArray,butMenu):
  fileArray.mutex.acquire()
  try:
    i,j = butMenu.indices
    file_ind_start = OL.objectList[i][j].indexStart
    file_ind_stop = OL.objectList[i][j].indexEnd
    for k in range(file_ind_start,file_ind_stop+1): # +1 is so it will do the first one if both ==
      del fileArray.filearray[file_ind_start]
  finally:
    fileArray.mutex.release()
    return fileArray.filearray

def add_filearray_menu(OL,fileArray,butMenu):
  fileArray.mutex.acquire()
  try:
    i,j = butMenu.indices
    file_ind = OL.objectList[i][j].indexEnd+1
    addedLine = []
    for parent in range(0,i):
      addedLine.append(OL.objectList[parent][OL.activeObjectColumnIndicesList[parent]].value)
      #addedLine.append(OL.objectList[parent][OL.selectedButtonColumnIndicesList[parent]].value)
    for child in range(i,len(OL.objectList)):
      addedLine.append("NULL")
    fileArray.filearray.insert(file_ind,addedLine)
  finally:
    fileArray.mutex.release()
    return fileArray.filearray

def write_filearray(fileArray):
  fileArray.mutex.acquire()
  try:
    outFile = open(fileArray.filename,'w+')
    wr = csv.writer(outFile,delimiter=fileArray.delim)
    if len(fileArray.filearray)!=0:
      filearrayrows=zip(*fileArray.filearray)
      wr.writerows(fileArray.filearray)
      print("Writing file array to disk")
  finally:
    fileArray.mutex.release()
    return fileArray.filearray

def create_objects(fileArray,cooldownLength):
  ncolumns = 0
  if len(fileArray.filearray)>0: 
    ncolumns = len(fileArray.filearray[len(fileArray.filearray)-1]) # FIXME should this just be hardcoded to 5 layers or should I keep it generic??
  nlines = len(fileArray.filearray)
  if fileArray.filearray == [] or fileArray.filearray == [[]] or fileArray.filearray == None:
    nlines = 0
    ncolumns = 0 # Sanity Check
    print("Error: Empty alarm file given to Parity Alarm Handler")
  localObjectList = []
  colRow = []
  line_previous = []
  for i in range(0,ncolumns):
    localObjectList.append([])
    colRow.append(0)
    line_previous.append("NULL")
  for lineN in range(0,nlines):
    line = fileArray.filearray[lineN]
    if len(line) != ncolumns:
      #print("Error, line {} = {} has the wrong number of entries for alarm handling parsing".format(lineN,line))
      return None
    isnew = 0
    for column in range(0,ncolumns):
      if (isnew == 1 or (line[column] != line_previous[column]) or (line[column] == "NULL")): # This is a new value, so initialize it and store values
        isnew = 1
        colRow[column] += 1
        newObject = alarm_object.ALARM_OBJECT() # call initializer
        newObject.indexStart = lineN
        newObject.indexEnd = lineN
        newObject.parentIndices = []
        newObject.column = column
        newObject.columnIndex = colRow[column]-1
        if column == 0:
          newObject.name = "New Alarm Type"
        else:
          newObject.name = line[column-1]
        newObject.value = line[column]
#       newObject.add_parameter_history(newObject.value) # Commenting out then assumes you are only recording value history
        newObject.alarmStatus = "OK"
        newObject.userSilenceStatus = "Alert"
        newObject.cooldownLength = cooldownLength
        newObject.userNotifyStatus = "OK"
        #newObject.parameterList["User Silence Status"] = newObject.userSilenceStatus
        newObject.color = lightgrey_color
        localObjectList[column].append(newObject)
        if column != 0:
          for indices in range(0,column): # for parent objects grab their index (assuming my parent was the most recently added one to the object list)
            localObjectList[column][colRow[column]-1].parentIndices.append(0)
            localObjectList[column][colRow[column]-1].parentIndices[indices] = localObjectList[indices][len(localObjectList[indices])-1].columnIndex
        # FIXME try to find a way to catalogue the following children in a level 2 object
        if (column==4 and isnew==1):
          localObjectList[2][localObjectList[column][colRow[3]-1].parentIndices[2]].add_parameter(localObjectList[3][colRow[3]-1],localObjectList[4][colRow[4]-1]) # FIXME Using colRow[4]-1 will always append the final entry of the values column [4] true for a parameter [3] to be the parameter list value.. consider first for history sake?

##### Silence Read
          if localObjectList[3][colRow[3]-1].value == "User Silence Status":
            localObjectList[2][localObjectList[column][colRow[3]-1].parentIndices[2]].userSilenceStatus = localObjectList[4][colRow[4]-1].value 
            localObjectList[2][localObjectList[column][colRow[3]-1].parentIndices[2]].alarm.userSilenceSelfStatus = localObjectList[4][colRow[4]-1].value 
            # Check for user silenced status
            #print("user silence status: {}".format(localObjectList[2][localObjectList[column][colRow[3]-1].parentIndices[2]].userSilenceStatus))
            # Editing the parameterList entry..... instead of the object value itself...
            localObjectList[2][localObjectList[column][colRow[3]-1].parentIndices[2]].add_parameter(localObjectList[3][colRow[3]-1],localObjectList[4][colRow[4]-1])
            # Also check each alarm status, in case the alarm status entry is earlier in fileArray than silence status
            # FIXME This will loop through column3 and overwrite its prior entries for parent coloration.... this is bad.
            for p in range(0,colRow[3]): 
              if localObjectList[2][localObjectList[column][p].parentIndices[2]].alarmStatus != "OK" and localObjectList[2][localObjectList[column][p].parentIndices[2]].userSilenceStatus == "Alert":
                for q1 in range(0,column):
                  localObjectList[q1][localObjectList[column][p].parentIndices[q1]].color = red_color
              elif localObjectList[2][localObjectList[column][p].parentIndices[2]].userSilenceStatus == "Silenced":
                for q2 in range(0,column):
                  localObjectList[q2][localObjectList[column][p].parentIndices[q2]].color = yellow_color
              elif localObjectList[2][localObjectList[column][p].parentIndices[2]].alarmStatus == "OK" and localObjectList[2][localObjectList[column][p].parentIndices[2]].userSilenceStatus != "Silenced":
                for q3 in range(0,column):
                  localObjectList[q3][localObjectList[column][p].parentIndices[q3]].color = lightgrey_color
          #print("Checking {}?=Alarm Status and Checking {}!?=OK and Checking {}?=Alert".format(localObjectList[3][colRow[3]-1].value,localObjectList[4][colRow[4]-1].value,localObjectList[2][colRow[2]-1].userSilenceStatus))




##### Alarm status read 




          if localObjectList[3][colRow[3]-1].value == "Alarm Status":
            for q in range(0,column):
              #print("Alert!!! Alarm not ok")
              localObjectList[q][localObjectList[column][colRow[3]-1].parentIndices[q]].alarmStatus = localObjectList[4][colRow[4]-1].value
              localObjectList[q][localObjectList[column][colRow[3]-1].parentIndices[q]].alarm.alarmSelfStatus = localObjectList[4][colRow[4]-1].value
              for o in range(0,colRow[4]):
                if localObjectList[4][o].value != "OK":
                  localObjectList[q][localObjectList[column][colRow[3]-1].parentIndices[q]].color = red_color
              if localObjectList[2][localObjectList[column][colRow[3]-1].parentIndices[2]].userSilenceStatus == "Silenced":
                # If the silence status was read before then don't overwrite its color indication
                localObjectList[q][localObjectList[column][colRow[3]-1].parentIndices[q]].color = yellow_color



#### Post all check again about alarm status in case order reversed



          # Only dark grey if alarmed and silenced 
          #if localObjectList[3][colRow[3]-1].value == "Alarm Status" and localObjectList[4][colRow[4]-1].value != "OK" and localObjectList[2][localObjectList[column][colRow[3]-1].parentIndices[2]].userSilenceStatus == "Silenced":
          # Dark grey if silenced at all
          if localObjectList[2][localObjectList[column][colRow[3]-1].parentIndices[2]].userSilenceStatus == "Silenced":
            for q in range(0,column):
              #print("Alert!!! Alarm silenced")
              #localObjectList[q][localObjectList[column][colRow[3]-1].parentIndices[q]].alarmStatus = localObjectList[4][colRow[4]-1].value
              #localObjectList[q][localObjectList[column][colRow[3]-1].parentIndices[q]].alarm.alarmSelfStatus = localObjectList[4][colRow[4]-1].value
              localObjectList[q][localObjectList[column][colRow[3]-1].parentIndices[q]].color = yellow_color
          ### This one records just the value/name parameter history
          localObjectList[2][localObjectList[column][colRow[3]-1].parentIndices[2]].add_parameter_history(localObjectList[4][colRow[4]-1].value)





##### User notify status read 




          if localObjectList[3][colRow[3]-1].value == "User Notify Status":
            #print("ALERT the user notify status is being read\n\n\n\n")
            for q in range(0,column):
              # Only update if silence is not silenced, if silenced then "OK"
              if localObjectList[q][localObjectList[column][colRow[3]-1].parentIndices[q]].userSilenceStatus == "Silenced":

                #print("OK")
                if q == 2:
                  localObjectList[q][localObjectList[column][colRow[3]-1].parentIndices[q]].parameterList["User Notify Status"] = "OK"
                localObjectList[q][localObjectList[column][colRow[3]-1].parentIndices[q]].userNotifyStatus = "OK"
                localObjectList[q][localObjectList[column][colRow[3]-1].parentIndices[q]].alarm.userNotifySelfStatus = "OK"
              # Else if we aren't OK but also aren't in a cooldown, then copy the alarm value for Latching purposes
              elif localObjectList[q][localObjectList[column][colRow[3]-1].parentIndices[q]].alarmStatus != "OK" and localObjectList[4][colRow[4]-1].value.split(' ')[0] != "Cooldown":
                #print("Reading object list, setting parameters, User Notify Status == {}".format(localObjectList[4][colRow[4]-1].value))
                if q == 2:
                  localObjectList[q][localObjectList[column][colRow[3]-1].parentIndices[q]].parameterList["User Notify Status"] = localObjectList[q][localObjectList[column][colRow[3]-1].parentIndices[q]].alarmStatus
                localObjectList[q][localObjectList[column][colRow[3]-1].parentIndices[q]].userNotifyStatus = localObjectList[q][localObjectList[column][colRow[3]-1].parentIndices[q]].alarmStatus
                localObjectList[q][localObjectList[column][colRow[3]-1].parentIndices[q]].alarm.userNotifySelfStatus = localObjectList[q][localObjectList[column][colRow[3]-1].parentIndices[q]].alarmStatus
              # Else just copy the dang value, this will be the initialized value or the OK status or the Cooldown
              else:
              #elif localObjectList[q][localObjectList[column][colRow[3]-1].parentIndices[q]].alarmStatus != "OK":
                #print("Updating with self status = {}".format(localObjectList[4][colRow[4]-1].value))
                if q == 2:
                  localObjectList[q][localObjectList[column][colRow[3]-1].parentIndices[q]].parameterList["User Notify Status"] = localObjectList[4][colRow[4]-1].value
                localObjectList[q][localObjectList[column][colRow[3]-1].parentIndices[q]].userNotifyStatus = localObjectList[4][colRow[4]-1].value
                localObjectList[q][localObjectList[column][colRow[3]-1].parentIndices[q]].alarm.userNotifySelfStatus = localObjectList[4][colRow[4]-1].value
              # Edit some colors for non-ok notify stati?
              #for o in range(0,colRow[4]):
                #if localObjectList[4][o].value != "OK":
                  #localObjectList[q][localObjectList[column][colRow[3]-1].parentIndices[q]].color = red_color



        if (column==4 and isnew!=1):
          ### This one records just the value/name parameter history
          localObjectList[2][localObjectList[column][colRow[3]-1].parentIndices[2]].add_parameter_history(localObjectList[4][colRow[4]-1].value)
      else:
        localObjectList[column][colRow[column]-1].indexEnd=lineN
      line_previous[column]=line[column]
  for i in range(0,len(localObjectList[2])): # The 3rd column is the list of alarm objects
    localObjectList[2][i].alarm = alarm_object.ALARM(localObjectList[2][i]) # NEW ALARM defined here per new object in middle column
    #print("New object's parameterList = {}".format(localObjectList[2][i].parameterList))
    #print("Creating alarm for object {} {}, type = {}".format(localObjectList[2][i].column,localObjectList[2][i].columnIndex,localObjectList[2][i].parameterList.get("Alarm Type",defaultKey)))
  return localObjectList
  
def update_extra_filearray(fileArray,extraFileArray):
  # Update the extra file array with whatever contents it happens to have on disk at the moment
  extraFileArray = alarm_object.FILE_ARRAY(extraFileArray.filename,extraFileArray.delim)
  fileArray.mutex.acquire()
  try: 

    if extraFileArray != None: # Then we have the correct format
      for i in range (0,len(extraFileArray.filearray)): # Check each line of extra array
        print("Reading extra fileArray {}, line {} = {}".format(extraFileArray.filename,i,extraFileArray.filearray[i]))
        # Check original file for contents matching comparison file, if first 4 columns can find a match then update, if not then append into the section with first 3/2/1 columns
        edittedEntry = False
        insertSpot = len(fileArray.filearray)
        for j in range (0,len(extraFileArray.filearray[i])-1):
          filled = [-1] * 4
          for k in range (0,len(fileArray.filearray)): # Check each line of original array
            if len(fileArray.filearray[k])>j and extraFileArray.filearray[i][j] == fileArray.filearray[k][j]: 
              # Then this entry has already been included in the main object list
              #print("Entry in extra fileArray {} being overwritten, line {} = {}".format(extraFileArray.filearray[i][j],i,extraFileArray.filearray[i]))
              #print("fileArray.filearay[{}] contains {}".format(k,extraFileArray.filearray[i][j]))
              if extraFileArray.filearray[i][0:4] == fileArray.filearray[k][0:4]: # only update for the case that I'm exactly replacing
                fileArray.filearray[k][4] = extraFileArray.filearray[i][4] 
                edittedEntry = True
              if extraFileArray.filearray[i][0:3] == fileArray.filearray[k][0:3]:
                insertSpot = k+1 # Update insertSpot for each entry with 3th level ana name matching
          if edittedEntry == False:
            if insertSpot == len(fileArray.filearray):
              #print("Appending {} below {}".format(extraFileArray.filearray[i],fileArray.filearray[len(fileArray.filearray)-1]))
              fileArray.filearray.append(extraFileArray.filearray[i])
            else:
              fileArray.filearray.insert(insertSpot,extraFileArray.filearray[i])
              #print("Inserting {} below {}".format(extraFileArray.filearray[i],fileArray.filearray[indices[x]]))
  finally:
    fileArray.mutex.release()
  
def append_object(OL,coli): 
  colLen = len(OL.objectList[coli])
  if colLen>0:
    lastIndexCol = OL.objectList[coli][colLen-1].indexEnd+1
  else:
    lastIndexCol = 0 # This is the first object of any row
  newObject = alarm_object.ALARM_OBJECT()
  newObject.indexStart = lastIndexCol
  newObject.indexEnd = lastIndexCol
  newObject.column = coli
  newObject.columnIndex = colLen
  if coli != 0:
    #if colLen != 0:
    i_index = coli-1
    j_index = OL.selectedButtonColumnIndicesList[i_index]
    newObject.parentIndices = OL.objectList[i_index][j_index].parentIndices.copy()
    newObject.parentIndices.append(OL.objectList[i_index][j_index].columnIndex)
  OL.objectList[coli].append(newObject)

  if coli < len(OL.objectList)-1:
    append_object(OL,coli+1)

def insert_object(OL,coli): 
  colLen = len(OL.objectList[coli])
  originalLengthColumn = OL.selectedColumnButtonLengthList[coli]
  insertColumnsLocations = OL.activeObjectColumnIndicesList.copy() # These are the locations (++) we will be inserting new objects (and buttons)

  #colIndexInsert = []
  #startIndexInsert = []
  #endIndexInsert = []
  #for i in range(0,len(OL.objectList)):  # Fill from 0, but use from coli
  #  colIndexInsert.append(insertColumnsLocations[i]+1)
  #  startIndexInsert.append(OL.objectList[i][insertColumnsLocations[i]].indexEnd+1)
  #  endIndexInsert.append(OL.objectList[i][insertColumnsLocations[i]].indexEnd+2)
  # Go through the items whose children contain the affected (moved down) objects and update their start and endIndex+1, for row 3 (analyses) update parameter list with new NULL parameter in correct placement
  # Go through the items which are moved down and move them down, also if their parent was moved down then update parentIndices+1
  # Go through columns and insert new objects in the new colIndex position, give parentIndices appropriately for updated information
  for j in range(insertColumnsLocations[coli]+1,len(OL.objectList[coli])): # Rows below first new button
    OL.objectList[coli][j].columnIndex += 1
    OL.objectList[coli][j].indexStart += 1
    OL.objectList[coli][j].indexEnd += 1
  for i in range(coli+1,len(OL.objectList)): # Rows to the right, below right buttons, update parent indices too
    for j in range(insertColumnsLocations[i]+1,len(OL.objectList[i])):
      OL.objectList[i][j].columnIndex += 1
      OL.objectList[i][j].indexStart += 1
      OL.objectList[i][j].indexEnd += 1
      OL.objectList[i][j].parentIndices[i-1] += 1
  for i in range(0,coli): # Rows to the left, left of and below selected location
    OL.objectList[i][insertColumnsLocations[i]].indexEnd += 1
    OL.objectList[i][insertColumnsLocations[i]].numberChildren += 1
    for j in range(insertColumnsLocations[i]+1,len(OL.objectList[i])):
      OL.objectList[i][j].indexEnd += 1

  newObjects = []
  for i in range(coli,len(OL.objectList)):
    newObjects.append(alarm_object.ALARM_OBJECT())
    newObjects[i-coli].indexStart = OL.objectList[i][insertColumnsLocations[i]].indexEnd + 1
    newObjects[i-coli].indexEnd = OL.objectList[i][insertColumnsLocations[i]].indexEnd + 2
    newObjects[i-coli].column = i
    newObjects[i-coli].columnIndex = insertColumnsLocations[i]+1 # Sketchy FIXME
    if coli>0:
      newObjects[i-coli].parentIndices = OL.objectList[i-1][insertColumnsLocations[i-1]].parentIndices.copy()
      if i>coli:
        newObjects[i-coli].parentIndices.append(OL.objectList[i-1][insertColumnsLocations[i-1]].columnIndex+1)
      else:
        newObjects[i-coli].parentIndices.append(OL.objectList[i-1][insertColumnsLocations[i-1]].columnIndex)

  for i in range(coli,len(OL.objectList)):
    OL.selectedButtonColumnIndicesList[i]+=1
    OL.selectedColumnButtonLengthList[i]+=1
    OL.activeObjectColumnIndicesList[i]+=1
  for i in range(coli,len(OL.objectList)):
    OL.objectList[i].insert(insertColumnsLocations[i]+1,newObjects[i-coli])

def is_number(s):
  try:
    complex(s) # for int, long, float and complex
  except ValueError:
    return False
  return True

