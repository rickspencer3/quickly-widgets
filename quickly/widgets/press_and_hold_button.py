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

"""A Button that fires a tick event as long as the user holds it down.
So long as the user is holding down the button, it will fire a tick
event every 250 milliseconds by default.

Using
#create the button and connect to the tick event
pah = PressAndHoldButton()
pah.connect('tick',__handle_on_tick)

def __handle_on_tick(widget, data=None):
    #do something once

Configuring
#Change the timeout period in milliseconds by adjusting the
#timeout property
pah.timeout = 10000

#set the label as a normal button
pah.set_labe("Press and Hold")

Extending
A PressAndHoldButton is gtk.Button

"""

import gobject
import gtk

class PressAndHoldButton(gtk.Button):
    def __init__(self):
        """Create a PressAndHoldButton

        After creating it, you can change the frequency of the tick
        event by setting timeout property in milliseconds. The default
        timeout period is 250 milliseconds.

        """

        gtk.Button.__init__(self)
        self.timeout = 250
        self.connect("pressed",self.__pressed)
        self.connect("released",self.__released)
        self.__continue_ticking = True

    def __pressed(self, widget, data=None):
        self.__continue_ticking = True
        widget.emit("tick",self)
        gobject.timeout_add(self.timeout, self.__tick)

    def __released(self, widget, data=None):
        self.__continue_ticking = False

    def __tick(self, data=None):
        if self.__continue_ticking:
            self.emit("tick",self)
        return self.__continue_ticking

    __gsignals__ = {'tick' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
		(gobject.TYPE_PYOBJECT,)),
		}

