# AlarmHandlerGUI
Alarm Handler GUI in python for reading EPICS, ROOT, JAPAN, and anything you can think of

Main file is AlarmHandler.py

Running:

`python3 AlarmHandler.py`

or, from stable apar@adaq2 utilize a ~/bin/ script called `AlarmHandler`

The GUI is constructed with python GUI module TKinter and its sister module ttk.

# Development

1) Merge expert-GUI and master branches together
2) Clean each tab (remove redundant memory allocations, like in the main tabs)
3) Replace the entire memory management and storage system with a SQL-like database and better OOP framework
