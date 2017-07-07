### BEGIN LICENSE
# Copyright (C) 2010 Rick Spencer rick.spencer@canonical.com
#This program is free software: you can redistribute it and/or modify it 
#under the terms of the GNU General Public License version 3, as published 
#by the Free Software Foundation.
#
#This program is distributed in the hope that it will be useful, but 
#WITHOUT ANY WARRANTY; without even the implied warranties of 
#MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR 
#PURPOSE.  See the GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License along 
#with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE

try:
 import pygtk
 pygtk.require("2.0")
 import gtk
 import threading
 import time
 import gobject
 import gettext
 from gettext import gettext as _
 gettext.textdomain('quickly-widgets')

except:
 print "couldn't load depencies"

class AsynchTaskProgressBox( gtk.HBox ):
 """AsynchTaskProgressBox: encapsulates a pulstating progressbar, a cancel
 button, and a long running task. Use an AsynchTaskProgressBox when you want
 a window to perform a long running task in the background without freezing 
 the UI for the user.

 """

 def __init__(self, run_function, params = None, cancelable = True):
  """Create an AsycnTaskProgressBox

  Keyword arguments:
  run_function -- the function to run asynchronously
  params -- optional dictionary of parameters to be pass into run_function
  cancelable -- optional value to determine whether to show cancel button. Defaults to True.
  Do not use a value with the key of 'kill' in the params dictionary

  """

  gtk.HBox.__init__( self, False, 2 )

  self.progressbar = gtk.ProgressBar()
  self.progressbar.show()
  self.pack_start(self.progressbar, True)

  self.cancel_button = gtk.Button(stock=gtk.STOCK_CANCEL)
  if cancelable:
   self.cancel_button.show()
  if params is None:
   params = {}
  params["update_progress_function"] = self.update
  self.cancel_button.set_sensitive(False)
  self.cancel_button.connect("clicked",self.__stop_clicked)
  self.pack_end(self.cancel_button, False)
  
  self.run_function = run_function
  self.pulse_thread = None
  self.work_thread = None
  self.params = params

  self.connect("destroy", self.__destroy)
  
 __gsignals__ = {'complete' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
		(gobject.TYPE_PYOBJECT,)),
		'cancelrequested' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
		(gobject.TYPE_PYOBJECT,))
		}
 
 def start(self, caption = "Working"):
  """executes run_function asynchronously and starts pulsating the progressbar
  Keyword arguments:
  caption -- optional text to display in the progressbar
  """
  #Throw an exception if the user tries to start an operating thread
  if self.pulse_thread != None:
   raise RuntimeError("AsynchTaskProgressBox already started.")

  #Create and start a thread to run the users task
  #pass in a callback and the user's params
  self.work_thread = KillableThread(self.run_function, self.__on_complete, self.params)
  self.work_thread.start()
  
  #create a thread to display the user feedback
  self.pulse_thread = PulseThread(self.progressbar, caption)
  self.pulse_thread.start()

  #enable the button so the user can try to kill the task
  self.cancel_button.set_sensitive( True )

 def update(self, fraction = None, displaytext = "Working"):
  """updates the progress bar with a given percentage and/or changes the 
  caption.
  Keyword arguments:
  fraction -- the current percentage complete
  displaytext -- the new caption to display"""
  if self.pulse_thread != None:
   self.pulse_thread.update(fraction, displaytext)
  
 #call back function for after run_function returns
 def __on_complete( self, data ):
  self.emit("complete", data)
  self.kill()

 #call back function for cancel button
 def __stop_clicked( self, widget, data = None ):
  self.cancel()

 def cancel(self):
  self.kill()
  #emit the cancelrequested event
  #note that this only signals that the kill function was called
  #the thread may or may not have actually stopped
  self.emit("cancelrequested", self)

 def kill( self ):
  """
  Stops pulstating the progressbar if the progressbar is working.
  Sets the value of 'kill' to True in the run_function.
 
  """

  #stop the pulse_thread and remove a reference to it if there is one
  if self.pulse_thread != None:
   self.pulse_thread.kill()
   self.pulse_thread = None

  #disable the cancel button since the task is about to be told to stop
  gobject.idle_add(self.__disable_cancel_button)

  #tell the users function tostop if it's thread exists
  if self.work_thread != None:
   self.work_thread.kill()

 #called when the widget is destroyed, attempts to clean up
 #the work thread and the pulse thread
 def __destroy(self, widget, data = None):
  if self.work_thread != None:
   self.work_thread.kill()
  if self.pulse_thread != None:
   self.pulse_thread.kill() 

 def __disable_cancel_button(self):
  gtk.gdk.threads_enter()
  self.cancel_button.set_sensitive( False )
  gtk.gdk.threads_leave()

class PulseThread ( threading.Thread ):
 """Class for use by AsynchTaskProgressBox. Not for general use.

 """
 def __init__(self,progressbar,displaytext = _("Working")):
  threading.Thread.__init__(self)
  self.displaytext = displaytext
  self.setDaemon(False)
  self.progressbar = progressbar
  self.__kill = False
  self.fraction = float(0)

 def kill(self):
  self.__kill = True

 def update(self, fraction, displaytext):
  self.displaytext = displaytext
  self.fraction = fraction

 #As a subclass of Thread, this function runs when start() is called
 #It will cause the progressbar to pulse, showing that a task is running
 def run ( self ):
  self.progressbar.set_text(self.displaytext)
  #keep running until the __kill flag is set to True
  while not self.__kill:
   time.sleep(.1)
   #get ahold of the UI thread and command the progress bar to pulse
   gtk.gdk.threads_enter()
   if self.fraction == 0:
    self.progressbar.pulse()
   else:
    self.progressbar.set_fraction(self.fraction)
   self.progressbar.set_text(self.displaytext)
   gtk.gdk.threads_leave()
  #before exiting, reset the progressbar to show that no task is running
  gtk.gdk.threads_enter()
  self.progressbar.set_fraction(0)
  self.progressbar.set_text("")
  gtk.gdk.threads_leave()

class KillableThread( threading.Thread ):
 """Class for use by AsynchTaskProgressBox. Not for general use.

 """
 def __init__(self,run_function, on_complete,  params = None):
  threading.Thread.__init__(self)
  self.setDaemon(False)
  self.run_function = run_function
  self.params = params
  self.on_complete = on_complete

 #As a subclass of Thread, this function runs when start() is called
 #It will run the user's function on this thread
 def run( self ):
  #set up params and include the kill flag
  if self.params == None:
   self.params = {}
  self.params["kill"] = False
  #tell the function to run
  data = self.run_function(self.params)
  #return any data from the function so it can be sent in the complete signal
  self.on_complete(data)

 #Tell the user's function that it should stop
 #Note the user's function may not check this
 def kill( self ):
  self.params["kill"] = True

class TestWindow(gtk.Window):
 """For testing and demonstrating AsycnTaskProgressBox.

 """
 def __init__(self):
  #create a window a VBox to hold the controls
  gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
  self.set_title("AsynchTaskProgressBox Test Window")
  windowbox = gtk.VBox(False, 2)
  windowbox.show()
  self.add(windowbox)

  #create params for use by the function that should run asynchronously
  params = {"start": 100, "stop": 110}

  #pass in the function and the params, then add to the window
  self.thread_progressbox = AsynchTaskProgressBox(self.asynch_function, params)
  self.thread_progressbox.show()
  windowbox.add(self.thread_progressbox)

  #start the task, and set the text for the progressbar to "Testing"
  #This will start the function and start the progressbar pulsating
  self.thread_progressbox.start("Testing")

  #connect to the complete event to respond when the task is complete
  self.thread_progressbox.connect("complete",self.complete_function)

  #connect to the cancel requested event for demonstration purposes
  self.thread_progressbox.connect("cancelrequested", self.canceled_function)

  #create a button for starting the task and add it to the window
  start_button = gtk.Button(stock=gtk.STOCK_EXECUTE)
  start_button.show()
  windowbox.add(start_button)
  start_button.connect("clicked",self.start_clicked) 
  self.show()
  
  #finish wiring up the window
  self.connect("destroy", self.destroy)

  #start up gtk.main in a threaded environment  
  gtk.gdk.threads_init()
  gtk.gdk.threads_enter()
  gtk.main()
  gtk.gdk.threads_leave()

 #called when the window is destroyed
 def destroy(self, widget, data = None):
  gtk.main_quit()
 
 #start the AsynchTaskProgressBox when the button is clicked
 def start_clicked(self, widget, data = None):
  self.thread_progressbox.start("Testing")

 #The function to run asynchronously
 def asynch_function( self, params ):
  # do something interminate and cpu intensive at startup
  print "starting..."
  time.sleep(2)
  #pull values from the params that were set above
  total = float(abs(params["stop"]-params["start"]))
  for x in range(params["start"],params["stop"]):
   #check if to see if the user has told the task to stop
   if params["kill"] == True:
    #return a string if the user stopped the task
    return "stopped at " + str(x)
   else:
    #if the user did not try to stop the task, go ahead and do something
    print x
    fraction=abs(x-params["start"])/total
    # call the update_progress_function function with the current percentage and caption
    params["update_progress_function"](fraction=fraction, displaytext=str(x))
   #this is a processor intensive task, so
   #sleep the loop to keep the UI from bogging down
   time.sleep(.5)
  #if the loop completes, return a string
  return "counted all"

 #called when the task completes
 def complete_function(self, widget, data = None):
  print "returned " + str(data)
 
 def canceled_function(self, widget, data=None):
  print "cancel requested"
if __name__== "__main__":
 test = TestWindow()

