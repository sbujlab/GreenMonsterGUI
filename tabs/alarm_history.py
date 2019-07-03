'''
Green Monster GUI Revamp
Containing ADC18s Tab
Code Commissioned 2019-01-16
Code by A.J. Zec
Alarm Handler GUI Update
Cameron Clarke 2019-05-28
'''

import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
import utils as u

class ALARM_HISTORY(tk.Frame):
  def __init__(self, alarmHandlerWindow, tab, OL, fileArray, alarmLoop, HL):
    self.activeAlarms = 0
    pass

    # The Alarm History is a page that will store information of previous alarms in Labels.
    
    # The kinds of alarms to display should be any alarm status that takes place, and the conditions for adding an alarm at the bottom of the list should be contingent upon that information not being superfluous.
    # An alarm which blinks on and off should not be added to the alarm handler many times, but instead we should utilize the UserNotifyStatus as our indicator of alarm. 
    # i.e. every time that the UserNotifyStatus turns not OK and not countdown then we want to add a new entry to our alarm handler
    # Silenced Alarms should be ignored.

    # The information should store the entire parameter list, though the information that is displayed at top level should be the 3 level name, the alarm status violation and the comparator that failed the test, and the time at which the alarm was initiated.

    # The routine should look exactly like the alarm_object Global Alarm Status decision loop, but instead of one global alarm status it will pick out each fresh alarm (that is not othewise currently active/non-user notify accepted) and add it to the list (a history text file).
    # The History Text file will be read after each checking/writing loop and used to display the alarm history on the screen. The top level details are put into the TLabel and the extra details are put into an information panel for the user to select (similar to the parameterList panel in other windows, but based on history, not an active alarm object)
    # An active alarm should be red, and allow the user to interact with that alarm similar to the alarm handler page (red, green, yellow, orange buttons mimicked).
    # An inactive alarm should still persist permenantly in full-history mode, but only the most recent N alarms should be displayed in default display mode. The Full-history mode should be a scrollable TFrame (basically just a redraw of truncated history to include full file contents).
    # The alarm history list is an independent alarmHistory object which contains just a historyArray file, owned by the main program (like the alarm_object and filearray lists for simplicity), which is comprised of a list of lists, where the columns are [parameter = value] pairs and the rows are individual history entries.

    self.alarmFrame = tk.LabelFrame(tab, text='Alarm Handler Viewer', background=u.lightgrey_color)
    self.pDataFrame = tk.LabelFrame(tab, text='Alarm Parameter Display', background=u.white_color)
    self.pDataFrame.disp = []
    self.colTitles = {0:"Alarms"}
    self.NperCol = 100
    OL.currentlySelectedButton = -1
    OL.displayPList = 0
    self.colsp = 1
    self.CBTextSuffix1 = ["\nFind Alarm","\nPause" ,"\nSilence","\nShow Parameters"]
    self.CBTextSuffix2 = ["\nFind Alarm","\nUnpause","\nUnsilence" ,"\nHide Parameters"]

    self.alarmCols = []
    self.initialize_cols(OL)
    self.displayFrames = []
    self.buttonMenus = []
    self.make_screen(OL,fileArray,HL)

  def make_screen(self,OL,fileArray,HL):
    for i in range(0,len(self.alarmCols)):
      self.alarmCols[i].destroy()
    self.alarmCols = []
    self.initialize_cols(OL)
    for each in self.displayFrames:
      each.destroy()
    self.displayFrames = self.initialize_displayFrames(OL,fileArray)
    for each in self.buttonMenus:
      each.destroy()
    self.buttonMenus = self.initialize_menus(OL,fileArray)
    self.alarmFrame.grid_forget()
    self.alarmFrame.grid(column=0, row=1, sticky='NW')
    self.erase_pDataFrame()
    if OL.currentlySelectedButton != -1 and OL.displayPList == 1:
      self.display_parameter_list(OL,fileArray,2,OL.currentlySelectedButton)
      self.pDataFrame.grid(column=1,row=1, sticky='NE')
    self.erase_grid_all_col()
    self.layout_grid_all_col(OL,fileArray)
    #if OL.currentlySelectedButton != -1:
    #  OL.currentlySelectedButton = OL.selectedButtonColumnIndicesList[2] #Overwrite with expert list in case in use
    #  self.select_button(OL,fileArray,self.displayFrames[OL.currentlySelectedButton].butt)
    #print("currently selected button = {}".format(OL.currentlySelectedButton))

  def initialize_cols(self,OL):
    for i in range(0, int(1.0*len(OL.objectList[2])/self.NperCol)+1):
      self.alarmCols.append(tk.LabelFrame(self.alarmFrame, text=self.colTitles.get(i,"ctd."), background=u.lightgrey_color))
      self.alarmCols[i].grid(column=i,row=0,pady=10,padx=10,sticky='N')

  def update_displayFrame(self,OL,localBut):
    i,j = localBut.indices
    a,b = localBut.indicesHistory
    #self.displayFrames[j].radioButGreen.grid_forget()
    self.displayFrames[b].radioButRed.grid_forget()
    #self.displayFrames[b].radioButYellow.grid_forget()
    #self.displayFrames[b].radioButOrange.grid_forget()

    self.displayFrames[b].alarmStatus = 0
    self.displayFrames[b].greenAlarmStatus = 0
    self.displayFrames[b].userNotifyStatus = 0
    self.displayFrames[b].userSilenceStatus = 0

    if OL.objectList[2][j].userNotifyStatus != "OK" and OL.objectList[2][j].userNotifyStatus.split(' ')[0] != "Cooldown" and OL.objectList[2][j].userSilenceStatus != "Silenced":
      # Then we are alarmed
      self.displayFrames[b].alarmStatus = 0
      self.displayFrames[b].radioButRed.grid(row=0,column=0,sticky='W')
      self.displayFrames[b].radioButRed.config(text=OL.objectList[2][j].alarmStatus, value = self.displayFrames[b].alarmStatus)
    if OL.objectList[2][j].userNotifyStatus.split(' ')[0] == "Cooldown" and OL.objectList[2][j].userSilenceStatus != "Silenced":
      self.displayFrames[b].radioButOrange.grid(row=0,column=0,sticky='W')
      self.displayFrames[b].radioButOrange.config(text=OL.objectList[2][j].userNotifyStatus.split(' ')[1])
    ##### Silence takes precedent over alarm and over notify/acknowledge
    #if OL.objectList[2][j].alarmStatus == "OK" and OL.objectList[2][j].userSilenceStatus == "Silenced":
    #  self.displayFrames[j].radioButYellow.grid(row=0,column=0,sticky='W')
    #  self.displayFrames[j].radioButYellow.config(text=OL.objectList[2][j].userSilenceStatus)
    if OL.objectList[2][j].alarmStatus != "OK" and OL.objectList[2][j].userSilenceStatus == "Silenced":
      self.displayFrames[b].radioButYellow.grid(row=0,column=0,sticky='W')
      self.displayFrames[b].radioButYellow.config(text=OL.objectList[2][j].alarmStatus)
    #if OL.objectList[2][j].alarmStatus == "OK" and OL.objectList[2][j].userSilenceStatus != "Silenced" and OL.objectList[2][j].userNotifyStatus.split(' ')[0] == "OK":
    ####  # Add check on userNotifyStatus so that the user will keep seeing the alarm indicator on even after the alarm itself has disappeared
    #  self.displayFrames[j].radioButGreen.grid(row=0,column=0,sticky='W')
    #  self.displayFrames[j].radioButGreen.config(text='   ')
    

  def initialize_displayFrames(self,OL,fileArray): # Needs a short row to contain [name = value, alarm status = type, alarm stat !OK, user silence stat, alarm stat OK], context menu displays full parameter list
    lgrid = []
    localActive = 0
    if len(OL.objectList)>(2) and len(OL.objectList[2])>0:
      for i in range(0,len(OL.objectList[2])):
        if OL.objectList[2][i].userNotifyStatus == "OK":
          continue # Ignore all non-alarming entries
        # Loop over the list of objects, creating displayFrames
        localStr = "{}, {}, {}".format(OL.objectList[0][OL.objectList[2][i].parentIndices[0]].value,OL.objectList[1][OL.objectList[2][i].parentIndices[1]].value[:25],OL.objectList[2][i].value[:25])
        if len(localStr) > 30:
          localStr = "{}, {}\n{}".format(OL.objectList[0][OL.objectList[2][i].parentIndices[0]].value,OL.objectList[1][OL.objectList[2][i].parentIndices[1]].value[:25],OL.objectList[2][i].value[:35])
        disp = tk.LabelFrame(self.alarmCols[int(1.0*self.activeAlarms/self.NperCol)], text=localStr, font=('Helvetica 8'), background=u.lightgrey_color) # FIXME want red alarm full label frame?
        disp.redStat = tk.IntVar()
        disp.orangeStat = tk.IntVar()
        disp.yellowStat = tk.IntVar()
        disp.greenStat = tk.IntVar()
        disp.alarmStatus = 0
        disp.greenAlarmStatus = 0
        disp.userNotifyStatus = 0
        disp.userSilenceStatus = 0
        if OL.objectList[2][i].alarmStatus != "OK":
          disp.alarmStatus = 0
          disp.greenAlarmStatus = 0
        if OL.objectList[2][i].userSilenceStatus != "Alert":
          disp.userSilenceStatus = 0 
        if OL.objectList[2][i].userSilenceStatus != "Silenced" and OL.objectList[2][i].userNotifyStatus.split(' ')[0] == "Cooldown":
          # Not silenced, and in Cooldown time period, then show this button instead
          disp.userNotifyStatus = 0
        lgrid.append(disp)

        disp.butt = tk.Button(lgrid[localActive], text="Value = {}".format(OL.objectList[2][i].parameterList.get("Value",u.defaultKey)), justify='center', background=u.lightgrey_color) # loop over displayFrames
        #disp.butt = tk.Button(lgrid[i], text="Value = {}".format(OL.objectList[2][i].parameterList.get("Value",u.defaultKey)), justify='center', background=OL.objectList[2][i].color) # loop over displayFrames
        disp.butt.indices = (2,OL.objectList[2][i].columnIndex)
        disp.butt.indicesHistory = (2,localActive)
        disp.butt.config(command = lambda but=disp.butt: self.select_disp_button(OL,fileArray,but))
        disp.butt.grid(row=0,column=1,sticky='W')
        disp.radioButRed = tk.Radiobutton(lgrid[localActive], text=OL.objectList[2][i].alarmStatus, indicatoron=False, justify='left', value=lgrid[localActive].alarmStatus, variable=lgrid[localActive].redStat, fg=u.white_color, bg=u.lightgrey_color,
            activebackground=u.grey_color, activeforeground=u.black_color, selectcolor = u.red_color, highlightbackground=u.red_color, highlightcolor=u.red_color, highlightthickness=1)
        disp.radioButRed.indices = (2,i)
        disp.radioButRed.indicesHistory = (2,localActive)
        disp.radioButRed.config(command = lambda radRed=disp.radioButRed: self.select_red_button(OL,fileArray,radRed))
        disp.radioButOrange = tk.Radiobutton(lgrid[localActive], text=OL.objectList[2][i].userNotifyStatus, indicatoron=False, justify='center', value=lgrid[localActive].userNotifyStatus, variable=lgrid[localActive].orangeStat, fg=u.black_color, bg=u.lightgrey_color,
            activebackground=u.grey_color, activeforeground=u.black_color, selectcolor = u.orange_color, highlightbackground=u.orange_color, highlightcolor=u.orange_color, highlightthickness=1)
        disp.radioButOrange.indices = (2,i)
        disp.radioButOrange.indicesHistory = (2,localActive)
        disp.radioButOrange.config(command = lambda radOrange=disp.radioButOrange: self.select_orange_button(OL,fileArray,radOrange))
        disp.radioButYellow = tk.Radiobutton(lgrid[localActive], text=OL.objectList[2][i].userSilenceStatus, indicatoron=False, justify='center', value=lgrid[localActive].userSilenceStatus, variable=lgrid[localActive].yellowStat, fg=u.black_color, bg=u.lightgrey_color,
            activebackground=u.grey_color, activeforeground=u.black_color, selectcolor = u.yellow_color, highlightbackground=u.yellow_color, highlightcolor=u.yellow_color, highlightthickness=1)
        disp.radioButYellow.indices = (2,i)
        disp.radioButYellow.indicesHistory = (2,localActive)
        disp.radioButYellow.config(command = lambda radYellow=disp.radioButYellow: self.select_yellow_button(OL,fileArray,radYellow))
        disp.radioButGreen = tk.Radiobutton(lgrid[localActive], text=OL.objectList[2][i].alarmStatus, indicatoron=False, justify='right', value=lgrid[localActive].greenAlarmStatus, variable=lgrid[localActive].greenStat, fg=u.black_color, bg=u.lightgrey_color,
            activebackground=u.grey_color, activeforeground=u.black_color, selectcolor = u.green_color, highlightbackground=u.green_color, highlightcolor=u.green_color, highlightthickness=1)
        disp.radioButGreen.indices = (2,i)
        disp.radioButGreen.indicesHistory = (2,localActive)
        #print("OL 2,{} alarm status = {}".format(i,OL.objectList[2][i].alarmStatus))
        disp.radioButGreen.config(command = lambda radGreen=disp.radioButGreen: self.select_green_button(OL,fileArray,radGreen))
        #if (OL.objectList[2][i].alarmStatus != "OK" or (OL.objectList[2][i].userNotifyStatus.split(' ')[0] != "OK" and OL.objectList[2][i].userNotifyStatus.split(' ')[0] != "Cooldown")) and OL.objectList[2][i].userSilenceStatus != "Silenced":
        if OL.objectList[2][i].userNotifyStatus != "OK" and OL.objectList[2][i].userNotifyStatus.split(' ')[0] != "Cooldown" and OL.objectList[2][i].userSilenceStatus != "Silenced":
          disp.alarmStatus = 0
          disp.radioButRed.grid(row=0,column=0,sticky='W')
          disp.radioButRed.config(text=OL.objectList[2][i].alarmStatus, value = disp.alarmStatus)
        if OL.objectList[2][i].userNotifyStatus.split(' ')[0] == "Cooldown" and OL.objectList[2][i].userSilenceStatus != "Silenced":
          disp.radioButOrange.grid(row=0,column=0,sticky='W')
          disp.radioButOrange.config(text=OL.objectList[2][i].userNotifyStatus.split(' ')[1])
        # Silence takes precedent over alarm and over notify/acknowledge
        #if OL.objectList[2][i].alarmStatus == "OK" and OL.objectList[2][i].userSilenceStatus == "Silenced":
        #  disp.radioButYellow.grid(row=0,column=0,sticky='W')
        #  disp.radioButYellow.config(text=OL.objectList[2][i].userSilenceStatus)
        if OL.objectList[2][i].alarmStatus != "OK" and OL.objectList[2][i].userSilenceStatus == "Silenced":
          disp.radioButYellow.grid(row=0,column=0,sticky='W')
          disp.radioButYellow.config(text=OL.objectList[2][i].alarmStatus)
        #if OL.objectList[2][i].alarmStatus == "OK" and OL.objectList[2][i].userSilenceStatus != "Silenced" and OL.objectList[2][i].userNotifyStatus.split(' ')[0] == "OK":
        ####  # Add check on userNotifyStatus so that the user will keep seeing the alarm indicator on even after the alarm itself has disappeared
        #  disp.radioButGreen.grid(row=0,column=0,sticky='W')
        #  disp.radioButGreen.config(text='   ')
        localActive += 1
    return lgrid

  def initialize_menus(self,OL,fileArray):
    grid = []
    #print("Adding menus, len(self.alarmCols) = {} times".format(len(self.alarmCols)))
    for i in range(0, len(self.displayFrames)):
      if len(OL.objectList[2])>=i:
        buttMenu = tk.Menu(self.displayFrames[i].butt, tearoff=0) # Is having the owner be button correct?
        buttMenu.indices = (2,OL.objectList[2][i].columnIndex)
        buttMenu.indicesHistory = (2,i)
        buttMenu.moveN = 0
        buttMenu.editValue = None
        buttMenu.add_command(label = 'Information', command = lambda butMenu = buttMenu: self.button_information_menu(OL,fileArray,butMenu))
        buttMenu.add_command(label = 'Acknowledge Alarm', command = lambda butMenu = buttMenu: self.button_notify_acknowledge_menu(OL,fileArray,butMenu))
        buttMenu.add_command(label = 'Silence', command = lambda butMenu = buttMenu: self.button_silence_menu(OL,fileArray,butMenu))
        self.displayFrames[i].butt.bind("<Button-3>",lambda event, butMenu = buttMenu: self.do_popup(event,butMenu))
      grid.append(buttMenu)
    return grid

  def do_popup(self,event,butMenu):
    butMenu.tk_popup(event.x_root,event.y_root,0)

  def layout_grid_all_col(self,OL,fileArray):
    for i in range(0,len(self.displayFrames)):
      self.displayFrames[i].grid(column=int(1.0*i/self.NperCol),row=i%self.NperCol,columnspan=self.colsp,padx=10,pady=10,sticky='W')
    #self.buttonMenus = self.initialize_menus(OL,fileArray)

  def erase_grid_all_col(self):
    for i in range(0,len(self.displayFrames)):
      self.displayFrames[i].grid_forget()

  def erase_pDataFrame(self):
    for k in range(0,len(self.pDataFrame.disp)):
      self.pDataFrame.disp[k].grid_forget()
    self.pDataFrame.grid_forget()

  def refresh_button(self,OL,fileArray,but):
    i,j = but.indices
    #OL.selectedButtonColumnIndicesList[i] = j # Update the currently clicked button index
    OL.set_clicked(i,j) # Update that object's color to dark grey
    if i==2:
      OL.currentlySelectedButton=OL.selectedButtonColumnIndicesList[2]
    #self.set_button_clicked(OL,fileArray,i,j) # Re-organize the grid and change the non-clicked buttons back to regular light grey
    #self.buttons[i][j].config(background=OL.objectList[i][j].color) # Update that button to be the newly update object's new color (could just use but.config)

  def select_button(self,OL,fileArray,but):
    i,j = but.indices
    a,b = but.indicesHistory
    OL.currentlySelectedButton = j
    OL.selectedButtonColumnIndicesList[i] = j
    for k in range(0,i): # When selecting a button update that as the one to show
      OL.selectedButtonColumnIndicesList[k] = OL.objectList[k][OL.objectList[i][j].parentIndices[k]].columnIndex
    for k in range(i+1,len(OL.selectedButtonColumnIndicesList)): 
      #print("Erasing selectedButtonIndex at {}".format(k))
      OL.selectedButtonColumnIndicesList[k] = -1
    OL.set_clicked(i,j) # Update that object's color to dark grey
    for l in range(0,len(OL.objectList[2][j].parentIndices)):
      OL.set_clicked(l,OL.objectList[2][j].parentIndices[l])
    for k in range(0,len(self.displayFrames)):
      if k == b:
        self.displayFrames[k].butt.config(background=u.darkgrey_color) 
      else:
        self.displayFrames[k].butt.config(background=u.lightgrey_color) 
    if OL.currentlySelectedButton != -1 and OL.displayPList == 1:
      self.display_parameter_list(OL,fileArray,2,OL.currentlySelectedButton)
      self.pDataFrame.grid(column=1,row=1, sticky='NE')
    #self.displayFrames[b].config(background=OL.objectList[i][j].color) # Update that button to be the newly update object's new color (could just use but.config)

  def select_disp_button(self,OL,fileArray,but):
    i,j = but.indices
    self.select_button(OL,fileArray,but)
    #self.update_GUI(OL,fileArray)

  def select_red_button(self,OL,fileArray,but):
    i,j = but.indices
    a,b = but.indicesHistory
    self.select_button(OL,fileArray,but)
    # Add a feature where clicking the red button counts as an alarm acknowledge
    self.displayFrames[b].greenAlarmStatus = 1
    u.notify_acknowledge_filearray_menu(OL,fileArray,but)
    alStat = 0 # Always maintain buttons in activated state, just hide them
    but.config(value=alStat)
    self.update_displayFrame(OL,but)
    self.select_button(OL,fileArray,but)
    #self.update_GUI(OL,fileArray)

  def select_orange_button(self,OL,fileArray,but):
    i,j = but.indices
    a,b = but.indicesHistory
    self.select_button(OL,fileArray,but)
    # If the user has acknowledged the alarm then we will be in a cooldown state and this button is visible, now if the user clicks again they will force->"OK" the userNotifyStatus to skip the cooldown period # FIXME this may not be desired behavior...
    u.notify_acknowledge_filearray_menu(OL,fileArray,but)
    OL.objectList[2][j].userNotifyStatus = "OK"
    OL.objectList[2][j].alarm.userNotifySelfStatus = "OK"
    OL.objectList[2][j].alarmStatus = "OK"
    OL.objectList[2][j].alarm.alarmSelfStatus = "OK"
    OL.objectList[2][j].parameterList["Alarm Status"] = "OK"
    notStat = 0 # Always maintain buttons in activated state, just hide them
    but.config(value=notStat)
    self.update_displayFrame(OL,but)
    self.select_button(OL,fileArray,but)
    #self.update_GUI(OL,fileArray)

  def select_yellow_button(self,OL,fileArray,but):
    i,j = but.indices
    a,b = but.indicesHistory
    self.select_button(OL,fileArray,but)
    u.silence_filearray_menu(OL,fileArray,but)
    silStat = 0 # Always maintain buttons in activated state, just hide them
    but.config(value=silStat)
    self.update_displayFrame(OL,but)
    self.select_button(OL,fileArray,but)
    #self.update_GUI(OL,fileArray)

  def select_green_button(self,OL,fileArray,but):
    i,j = but.indices
    a,b = but.indicesHistory
    self.select_button(OL,fileArray,but)
    alStat = 0 # Always maintain buttons in activated state, just hide them
    but.config(value=alStat)
    #self.update_GUI(OL,fileArray)

  def update_GUI(self,OL,fileArray,HL):
    fileArray.filearray = u.write_filearray(fileArray)
    #OL.objectList = u.create_objects(fileArray,OL.cooldownLength)
    self.make_screen(OL,fileArray,HL)

  def display_parameter_list(self,OL,fileArray,i,j):
    self.erase_pDataFrame()
    self.pDataFrame.disp = []
    OL.displayPList = 1
    localPlist = OL.objectList[i][j].parameterList.copy()
    #self.pDataFrame.pack(padx=20,pady=10,anchor='nw')
    self.pDataFrame.grid(column=1,row=1,sticky='NW')
    k = 0
    for key in localPlist:
      self.pDataFrame.disp.append(tk.Label(self.pDataFrame, text="{} = {}".format(key, localPlist[key]), background=u.lightgrey_color)) # FIXME want red alarm full label frame?
      self.pDataFrame.disp[k].grid(row=k,column=0,padx=10,pady=10,sticky='W')
      k+=1


  def button_information_menu(self,OL,fileArray,butMenu):
    i,j = butMenu.indices
    a,b = butMenu.indicesHistory
    self.display_parameter_list(OL,fileArray,i,j)
    self.select_button(OL,fileArray,self.displayFrames[b].butt)
    #self.update_GUI(OL,fileArray)

  def button_silence_menu(self,OL,fileArray,butMenu):
    i,j = butMenu.indices
    a,b = butMenu.indicesHistory
    self.select_button(OL,fileArray,self.displayFrames[b].butt)
    u.silence_filearray_menu(OL,fileArray,butMenu)
    self.update_displayFrame(OL,self.displayFrames[b].radioButYellow)
    self.select_button(OL,fileArray,self.displayFrames[b].butt)
    #self.update_GUI(OL,fileArray)

  def button_notify_acknowledge_menu(self,OL,fileArray,butMenu):
    i,j = butMenu.indices
    a,b = butMenu.indicesHistory
    self.select_button(OL,fileArray,self.displayFrames[b].butt)
    if OL.objectList[2][j].userNotifyStatus.split(' ')[0] != "Cooldown" and OL.objectList[2][j].userNotifyStatus.split(' ')[0] != "OK":
      self.displayFrames[b].greenAlarmStatus = 1
      u.notify_acknowledge_filearray_menu(OL,fileArray,butMenu)
    elif OL.objectList[2][j].userNotifyStatus.split(' ')[0] == "Cooldown":
      u.notify_acknowledge_filearray_menu(OL,fileArray,butMenu)
      OL.objectList[2][j].userNotifyStatus = "OK"
      OL.objectList[2][j].alarm.userNotifySelfStatus = "OK"
      OL.objectList[2][j].alarmStatus = "OK"
      OL.objectList[2][j].alarm.alarmSelfStatus = "OK"
      OL.objectList[2][j].parameterList["Alarm Status"] = "OK"
    self.update_displayFrame(OL,self.displayFrames[b].radioButGreen)
    self.select_button(OL,fileArray,self.displayFrames[b].butt)
    #self.update_GUI(OL,fileArray)

  def refresh_screen(self,OL,fileArray,alarmLoop,HL):
    self.update_GUI(OL,fileArray,HL)
    #if OL.selectedButtonColumnIndicesList[2] != -1:
    #  self.refresh_button(OL,fileArray,self.displayFrames[OL.selectedButtonColumnIndicesList[2]].butt)

