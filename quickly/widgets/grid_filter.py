# -*- coding: utf-8 -*-
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

"""Widgets and Objects for filtering a DictionaryGrid
GridFilter is as gtk.VBox that provides filtering UI for a 
DictionaryGrid. Provides multiple filters, and choosing 
between "And" and "Or" filtering. Provides default filters appropriate
for each column.

GridFilter row is a gtk.HBox that is a container for displaying FilterCombos.

FilterCombos display a filter and handle filtering of rows to
display and hide in the associated DictionaryGrid. The GridColumns
determine the type of filter to use by default.

Using
#create a DictionaryGrid and use it to create a GridFilter
grid = DictionaryGrid(dictionaries=dicts)
grid.show()

filt = GridFilter(grid)
filt.show()

Configuring
#Create a custom filter combo and use it for a column
#the filter functions should take a stored value and a value to filter against
for each row and return True if the results should cause the row to
be displayed and False if the row should not be displayed

blank_filter = BlankFilterBox()
blank_filter.append("=",custom_equals_function )
blank_filter.append("<>",custom_no_equals_function )

filter_hints = {"status":blank_filter}
filt = GridFilter(grid, filter_hints)
filt.show()

Extending
A custom filter combo is easiest to create by deriving from BlankFilterBox
and using the BlankFilterBox.append function to display new filters.

class StringFilterBox( BlankFilterBox ):
 def __init__(self):
  BlankFilterBox.__init__(self)
  self.append("contains",lambda x,y: x.find(y) > -1)
  self.append("does not contain",lambda x,y: x.find(y) == -1)
  self.append("starts with",lambda x,y: x.startswith(y))
  self.append("ends with",lambda x,y: x.endswith(y))

Filter UI could be created to use widgets other than gtk.Combo so long as
the widget has a get_model function that returns a gtk.ListStore with
filtering functions stored as the last value (column) in the liststore.

"""

import sys
import datetime
import gettext
from gettext import gettext as _
gettext.textdomain('quickly-widgets')

try:
 import pygtk
 pygtk.require("2.0")
 import gtk
 import gobject

except Exception, inst:
 print "some dependencies for GridFilter are not available"
 raise inst

class GridFilter( gtk.VBox ):
 """GridFilter: A widget that provides a user interface for filtering a
 treeview. A GridFilter hosts one ore more GridRows, which in turn host
 an active filter.

 """
 def __init__(self, grid, filter_hints={} ):
  """Create a GridFilter for filtering an associated treeview.
  This class is used by BugsPane.

  arguments:
  grid - A DictionaryGrid to filter

  options arguments:
  filter_hints - a dictionary of column keys to FilterCombo types to
  provide custom filtering. 
 
  """

  gtk.VBox.__init__( self, False, 10 )
  self.grid = grid  
  self.store = grid.get_model()
  self.filter_hints = filter_hints

  #create the and/or radio buttons
  radio_box = gtk.HBox(False,2)
  radio_box.show()
  self.pack_start(radio_box, False, False)
  self.and_button = gtk.RadioButton(None,_("M_atch All of the following"), True)
  self.and_button.show()
  self.and_button.connect("toggled",self.__filter_changed)
  radio_box.pack_start(self.and_button, False, False)
  or_button = gtk.RadioButton(self.and_button,_("Match any _of the following"), True)
  or_button.show()
  radio_box.pack_start(or_button, False, False)
  self.rows = []
  self._add_row(self)

 def _add_row(self, widget, data=None):
  """_add_row: internal signal handler that receives a request 
  from a FilterRow to add a new row. Sets up and adds the row to the GridFilter.

  Do not call directly
  """

  #TODO: I suppose this is leaking references to filter rows
  row = FilterRow(self.grid, len(self.rows) > 0, self.filter_hints )
  row.connect('add_row_requested',self._add_row)
  row.connect('remove_row_requested',self._remove_row)
  row.connect('refilter_requested',self.__filter_changed)
  row.show()
  self.rows.append(row)
  self.pack_start(row, False, False)
 
 def _remove_row(self, widget, data=None):
  """_remove_row: internal signal handler that receives a 
  request from a FilterRow to remove itself from the GridFilter.

  Do not call directly
  """

  self.rows.remove(widget)
  self.remove(widget)
  self.__filter_changed(self)

 def __filter_changed(self,widget, data=None):
  """__filter_changed: internal signal handler that handles 
  requests to reapply the fitlers in the GridFilter's FilterRows.

  """

  filt = self.store.filter_new()
  sort_mod = gtk.TreeModelSort(filt)
  filt.set_visible_func(self.__filter_func, data )
  filt.refilter()
  self.grid.set_model(sort_mod)
  
 def __filter_func(self, model, iter, data):
  """filter_func: called for each row in the treeview model in response to
  a __filter_changed signal. Determines for each row whether it should be
  visible based on the FilterRows in the GridFilter.


  Do not call directly
  """
  #determine whether this is an "and" or an "or" filter
  match_all = self.and_button.get_active()

  for r in self.rows:
   rez = r.is_match(iter.copy(),model)  #check the result of each filter
   if match_all:                        #if it's an "and" filter
    if not rez:                         #and if the filter does not match
     return False                       #then the row should not be visible
   else:                                #but if it's an "or" filter
    if rez:                             #and it is a match
     return True                        #return that the row should be visible
  return match_all  #all filters match an "and" or none matched an "or" 
  
class FilterRow( gtk.HBox):
 """FilterRow: A widget that displays a single filter in a GridFilter.
 Typically, this class will not be used directly, but only via a GridFilter.   
 
 """
 wait_for_input = False

 def __init__(self, grid, removable=True, filter_hints={}):
  """Create a FilterRow to be used in a GridFilter.
  A FitlerRow is comprised of a combo that lists the treeview headings.
  The combo stores the string to display for the heading, as well as
  the widget that is used to filter each heading. When the user changes
  the value in the dropdown, the FilterRow retrieves the correct filter from
  the combo, and displays that filter to the user.

  The FilterRow also handles offering UI for the user to add and remove
  FilterRows for the GridFilter containing it.
     
  grid -  

  keyword arguments:
  removable - True if the row should be able to be removed from the GridFilter
               Typicall False for the first row.

  filter_hints - a dictionary of keys mapped to custom filters to apply to the
  column designated by the key

  """

  gtk.HBox.__init__( self, False, 10 )
  self.store = grid.get_model()
  self.grid = grid

  heading_combo_store = gtk.ListStore(gobject.TYPE_STRING,gobject.TYPE_PYOBJECT,gobject.TYPE_INT)

  #apply default combos
  for i, k in enumerate(self.grid.keys):
   if k in filter_hints:
    filt_combo = filter_hints[k]
   else:
    filt_combo = grid.get_columns()[i].default_filter()
         
   column_title = grid.get_columns()[i].get_title()
   heading_combo_store.append([column_title,filt_combo,i])

   filt_combo.connect("changed",self.__filter_changed)
   filt_combo.show()
 
  self.column_combo = gtk.ComboBox(heading_combo_store)
  cell = gtk.CellRendererText()
  self.column_combo.pack_start(cell, True)
  self.column_combo.add_attribute(cell, 'text', 0)

  self.filter_space = gtk.HBox(False,1)
  self.filter_space.show()

  self.column_combo.show()
  vb = gtk.VBox(False, 5)
  vb.show()
  vb.pack_start(self.column_combo, True, False)
  self.pack_start(vb,False, False)
  self.column_combo.connect("changed",self.__column_changed)
  self.column_combo.set_active(0)

  self.pack_start(self.filter_space, False, False)

  button_box = gtk.HBox(False,2)
  button_box.show()
  self.pack_start(button_box,False,False)

  #add a button that can create a new row in the grid filter
  add_button = gtk.Button(stock = gtk.STOCK_ADD)
  add_button.show()
  vb2 = gtk.VBox(False, 5)
  vb2.show()
  vb2.pack_start(add_button, True, False)
  button_box.pack_start(vb2, False, False)
  add_button.connect("clicked",lambda x: self.emit('add_row_requested',self) )

  #add a button to remove the row if applicable
  if removable:
   rm_button = gtk.Button(stock = gtk.STOCK_REMOVE)
   rm_button.show()
   vb3 = gtk.VBox(False, 5)
   vb3.show()
   vb3.pack_start(rm_button, True, False)
   rm_button.connect('clicked', lambda x: self.emit("remove_row_requested",self) )
   button_box.pack_start(vb3)

 __gsignals__ = {'add_row_requested' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
		(gobject.TYPE_PYOBJECT,)),
		'remove_row_requested' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
		(gobject.TYPE_PYOBJECT,)),
		'refilter_requested' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
		(gobject.TYPE_PYOBJECT,))
		}
 
 def __column_changed(self, widget, data = None):
  """column_changed: internal signal handler for the user changing
  the combo for the column that they wish to apply the filter to.
  removes the other filter widgets and replaces them widgets stored in
  the filter widget.

  """

  if len(self.filter_space.get_children()) > 0:
   self.filter_space.remove(self.filter_space.get_children()[0])   
  iter = widget.get_model().get_iter(widget.get_active())
  filter_box = widget.get_model().get_value(iter,1)
  self.filter_space.pack_start(filter_box, False, False)

 def __filter_changed(self,widget, data=None):
  """filter_changed: internal signal handler called when the FilterRow has changed.
  Used to tell the GridFilter to refilter. Only emits if the filter is 
  active (a heading is selected in the combo and the user has entered
  text in the filter.

  """
  
  #if not self.wait_for_input:
  #if self.__get_current_filter_combo().get_active > -1:
  self.emit('refilter_requested',self)

 def __get_current_filter_combo(self):
  """get_current_filter_combo: internal function that retrieves
  the combobox stored for the filter for the user selected treeview column.

  """
  iter = self.column_combo.get_model().get_iter(self.column_combo.get_active())
  return self.column_combo.get_model().get_value(iter,1)

 def is_match(self, store_iter, model):
  """is_match: returns true if the filter set in the FilterRow matches
  the value specified in the column and row. Used to determine whether 
  to hide or show a row.

  Typically called for each treeview row and each FilterRow in response
  to a change in one of the FilterRows.

  arguments:
  store_iter: the iter pointing the the row in the treeview to test
  model: the treeview model containing the rows being tested

  """
  col_iter = self.column_combo.get_model().get_iter(self.column_combo.get_active())
  filter_widget = self.column_combo.get_model().get_value(col_iter,1)
  treeview_col = self.column_combo.get_model().get_value(col_iter,2)

  orig_val = model.get_value(store_iter.copy(), treeview_col)
  return filter_widget.filter(orig_val)

class BlankFilterBox( gtk.HBox):
 """BlankFilterBox provides a base class for FilterCombos, as
 well as an empty combo that can be used without subclassing
 by calling BlankFilterBox.append

 """
 __gsignals__ = {'changed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
		(gobject.TYPE_PYOBJECT,)),
		}


 def __init__(self):
  """create a BlankFilterBox

  """

  gtk.HBox.__init__(self,False)
  self.__combo_store = gtk.ListStore(gobject.TYPE_STRING,gobject.TYPE_PYOBJECT)
  self.combo = gtk.ComboBox(self.__combo_store)
  cell = gtk.CellRendererText()
  self.combo.pack_start(cell, True)
  self.combo.add_attribute(cell, 'text', 0)
  self.combo.show()
  self.combo.connect("changed",self.__changed)
  self.entry = gtk.Entry()
  self.entry.show()
  self.entry.connect("changed",self.__changed)
  self.pack_start(self.combo, False, False)
  self.pack_start(self.entry)

 def filter(self, orig_val):
  if self.combo.get_active() == -1:
   return True
  filt_iter = self.combo.get_model().get_iter(self.combo.get_active())
  filt_func = self.combo.get_model().get_value(filt_iter,1)
  target_val = self.entry.get_text()
  if target_val is None or target_val == "":
   return False
  else:     
   return filt_func(orig_val, self.entry.get_text())

 def __changed(self, widget, data=None):
    self.emit("changed",data)

 def append(self, text, func):
    """append: adds a row to the FilterCombo that includes a
    string to display in the combo, and a function to determine
    if a row should displayed or hidden by the filter. 

    func should take a value indicated by text, and a value entered by
    the user in the supplied gtk.TextEntry, and return True if the
    row should be displayed or False if it should be hidden.

    """

    self.__combo_store.append([text, func])

class StringFilterBox( BlankFilterBox ):
 """StringFilterBox: A default string filter class for use in a FilterRow.

    Lets the user specify if the row should be displayed based on
    containing, not containing, starting with, or ending with a user specified
    string.


 """
 def __init__(self):
  """create a StringFilterBox.

  """

  BlankFilterBox.__init__(self)
  self.append(_("contains"),self.contains)
  self.append(_("does not contain"),self.not_contains)
  self.append(_("starts with"),self.starts_with)
  self.append(_("ends with"),self.ends_with)

 def contains(self, orig_val, target_val):
  if len(self.entry.get_text()) == 0:
   return True
  return orig_val.find(target_val) > -1

 def not_contains(self, orig_val, target_val):
  if len(target_val) == 0:
   return True
  return orig_val.find(target_val) == -1

 def starts_with(self, orig_val, target_val):
  if len(target_val) == 0:
   return True
  return orig_val.startswith(target_val)

 def ends_with(self, orig_val, target_val):
  if len(target_val) == 0:
   return True
  return orig_val.endswith(target_val)


class TagsFilterBox( BlankFilterBox ):
 """TagsFilterBox: A default tag filter class for use in a FilterRow.

    Lets the user specify if the row should be displayed based on
    containing a one tag or all tags. Assumes tags are seperated by
    spaces.

 """

 def __init__(self):
  BlankFilterBox.__init__(self)
  self.append(_("has any of these tags"), self._filter_any)
  self.append(_("has all of these tags"), self._filter_all)
  self.append(_("does not have one of these tags"), self._filter_not)
  self.append(_("does not have any of these tags"), self._filter_not_all)

 def _filter_any(self, orig_val, target_val):
  """
  _filter_any: filter function that hides rows
  if none of the tags supplied in "bugs_tags_s" are found
  in the gtk.TextEntry.

  Do not call directly

  """

  if len(target_val) == 0:
   return True

  tags_on_bug = orig_val.split()
  tags_in_filter = target_val.split()

  for tag in tags_in_filter:
   if tag in tags_on_bug:
    return True
  return False

 def _filter_all(self, orig_val, target_val):
  """
  _filter_any: filter function that hides rows
  if not all of the tags supplied in "bugs_tags_s" are found
  in the gtk.TextEntry.

  Do not call directly

  """
  if len(target_val) == 0:
   return True

  tags_on_bug = orig_val.split()
  tags_in_filter = self.entry.get_text().split()

  for tag in tags_in_filter:
   if tag not in tags_on_bug:
    return False
  return True

 def _filter_not(self, orig_val, target_val):
  """
  _filter_not: filter function that hides rows
  if one of the tags supplied in "bugs_tags_s" are found
  in the gtk.TextEntry.

  Do not call directly

  """
  if len(target_val) == 0:
   return True

  tags_on_bug = orig_val.split()
  tags_in_filter = target_val.split()
              
  for tag in tags_in_filter:
   if tag not in tags_on_bug:
    return True
  return False

 def _filter_not_all(self, orig_val, target_val):
  """
  _filter_not all: filter function that hides rows
  if all of the tags supplied in "bugs_tags_s" are found
  in the gtk.TextEntry.

  Do not call directly

  """
  if len(self.entry.get_text()) == 0:
   return True

  tags_on_bug = orig_val.split()
  tags_in_filter = target_val.split()

  for tag in tags_in_filter:
   if tag in tags_on_bug:
    return False
   return True
  
class IntegerFilterBox( gtk.HBox ):
 """

 """
 __gsignals__ = {'changed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
		(gobject.TYPE_PYOBJECT,)),
		}

 def __init__(self):
  gtk.HBox.__init__(self, False, 10)
  self.__combo_store = gtk.ListStore(gobject.TYPE_STRING,gobject.TYPE_PYOBJECT)
  self.combo = gtk.ComboBox(self.__combo_store)
  cell = gtk.CellRendererText()
  self.combo.pack_start(cell, True)
  self.combo.add_attribute(cell, 'text', 0)
  self.combo.show()
  self.combo.connect("changed",self.__changed)
  adj = gtk.Adjustment(0,-1000000000,1000000000,1)
  
  self.spinner = gtk.SpinButton(adj,1,0)
  self.spinner.set_activates_default(True)
  self.spinner.show()
  self.spinner.set_numeric(True)

  self.spinner.connect("value-changed",self.__changed)
  self.pack_start(self.combo, False, False)
  self.pack_start(self.spinner)

  self.__combo_store.append(["=",self._equals])
  self.__combo_store.append(["<",self._less_than])
  self.__combo_store.append([">",self._greater_than])
  self.__combo_store.append(["<=",self._less_than_equals])
  self.__combo_store.append([">=",self._greater_than_equals])

 def __changed(self, widget, data=None):
    self.emit("changed",data)

 def filter(self, orig_val):
  if self.combo.get_active() == -1:
       return True

  filt_iter = self.combo.get_model().get_iter(self.combo.get_active())
  filt_func = self.combo.get_model().get_value(filt_iter,1)

  try:
   target_val = int(self.spinner.get_value_as_int())


  except Exception, inst:
   print inst
   return False

  return filt_func(orig_val, target_val)

 def _equals(self, orig_val, target_val):
  return int(orig_val) == target_val

 def _less_than(self, orig_val, target_val):
  return int(orig_val) < target_val

 def _greater_than(self, orig_val, target_val):
  return int(orig_val) > target_val

 def _less_than_equals(self, orig_val, target_val):
  return int(orig_val) <= target_val

 def _greater_than_equals(self, orig_val, target_val):
  return int(orig_val) >= target_val

class DateFilterBox( gtk.HBox ):
 """DateFilterCombo: A default date filter class for use in a FilterRow.

    Lets the user specify if the row should be displayed based on
    the settings in a date widget.

 """
 __gsignals__ = {'changed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
		(gobject.TYPE_PYOBJECT,)),
		}

 def __init__(self):
  """create a CheckFilterCombo
  
  """
  gtk.HBox.__init__(self, False, 10)

  self.__combo_store = gtk.ListStore(gobject.TYPE_STRING,gobject.TYPE_PYOBJECT)
  self.combo = gtk.ComboBox(self.__combo_store)
  cell = gtk.CellRendererText()
  self.combo.pack_start(cell, False)
  self.combo.add_attribute(cell, 'text', 0)
  self.combo.show()
  self.combo.connect("changed",self.__changed)

  self.__combo_store.append([ _("before"),self.before ])
  self.__combo_store.append([ _("on or before"),self.on_before ])
  self.__combo_store.append([ _("on"), self.on_date ])
  self.__combo_store.append([ _("on or after"),self.on_after ])
  self.__combo_store.append([ _("after"),self.after ])

  self.calendar = gtk.Calendar()
  self.calendar.show()
  self.calendar.connect("day-selected", self.__changed)
  vb = gtk.VBox(False, 5)
  vb.show()
  vb.pack_start(self.combo, True, False)
  self.pack_start(vb, False, False)
  self.pack_start(self.calendar, False, False)

 def before(self, orig_val):
   stored_date, target_date = self.__get_dates(orig_val, self.calendar.get_date())
   return stored_date < target_date

 def on_before(self, orig_val):
   stored_date, target_date = self.__get_dates(orig_val, self.calendar.get_date())
   return stored_date <= target_date

 def on_date(self, orig_val):
   stored_date, target_date = self.__get_dates(orig_val, self.calendar.get_date())
   return stored_date == target_date

 def on_after(self, orig_val):
   stored_date, target_date = self.__get_dates(orig_val, self.calendar.get_date())
   return stored_date >= target_date

 def after(self, orig_val):
   stored_date, target_date = self.__get_dates(orig_val, self.calendar.get_date())
   return stored_date > target_date

 def __get_dates(self, orig_val, target_date):
   target_date = self.calendar.get_date()
   target_date = datetime.date(int(target_date[0]),int(target_date[1] + 1),int(target_date[2]))
   p = orig_val.split("-")
   stored_date = datetime.date(int(p[0]),int(p[1]),int(p[2]))   
   return (stored_date, target_date)

 def filter(self, orig_val):
  if self.combo.get_active() == -1:
   return True

  filt_iter = self.combo.get_model().get_iter(self.combo.get_active())
  filt_func = self.combo.get_model().get_value(filt_iter,1)
  return filt_func(orig_val)

 def __changed(self, widget, data=None):
  self.emit("changed",data)


class CheckFilterBox( gtk.HBox ):
 """CheckFilterCombo: A default checkbox filter class for use in a FilterRow.

    Lets the user specify if the row should be displayed based on
    whether a Checkbox is active, inactive, or not set.

 """
 __gsignals__ = {'changed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
		(gobject.TYPE_PYOBJECT,)),
		}

 def __init__(self):
  """create a CheckFilterCombo
  
  """
  gtk.HBox.__init__(self, False, 10)

  self.__combo_store = gtk.ListStore(gobject.TYPE_STRING,gobject.TYPE_PYOBJECT)
  self.combo = gtk.ComboBox(self.__combo_store)
  cell = gtk.CellRendererText()
  self.combo.pack_start(cell, True)
  self.combo.add_attribute(cell, 'text', 0)
  self.combo.show()
  self.combo.connect("changed",self.__changed)

  self.__combo_store.append([ _("checked"),self.filter_checked ])
  self.__combo_store.append([ _("not Checked"),self.filter_not_checked ])
  self.__combo_store.append([ _("unset"), self.filter_unset ])

  self.pack_start(self.combo, False, False)

 def filter(self, orig_val):
  if self.combo.get_active() == -1:
   return True

  filt_iter = self.combo.get_model().get_iter(self.combo.get_active())
  filt_func = self.combo.get_model().get_value(filt_iter,1)
  return filt_func(orig_val)

 def filter_checked(self, orig_val):
  return orig_val == 1

 def filter_not_checked(self, orig_val):
  return orig_val == 0

 def filter_unset(self, orig_val):
  return orig_val == -1

 def __changed(self, widget, data=None):
  self.emit("changed",data)


class NumericFilterBox( BlankFilterBox ):
 """NumericFilterCombo: A default number filter class for use in a FilterRow.

    Lets the user specify if the row should be displayed based on numeric
    relationships to a number specified by the user.

 """


 def __init__(self):
  """create a NumericFilterCombo

  """
  BlankFilterBox.__init__( self )
  self.append("=",self._equals )
  self.append("<",self._less_than )
  self.append(">",self._greater_than )
  self.append("<=",self._less_than_equals)
  self.append(">=",self._greater_than_equals )

 def _equals(self, orig_val):
  try:
   return float(orig_val) == float(self.entry.get_text())
  except:
   return True

 def _less_than(self, orig_val):
  try:
   return float(orig_val) < float(self.entry.get_text())
  except:
   return True

 def _greater_than(self, orig_val):
  try:
   return float(orig_val) > float(self.entry.get_text())
  except:
   return True

 def _less_than_equals(self, orig_val):
  try:
   return float(orig_val) <= float(self.entry.get_text())
  except:
   return True

 def _greater_than_equals(self, orig_val):
  try:
   return float(orig_val) >= float(self.entry.get_text())
  except:
   return True

def __delete_test(button, grid):
    grid.remove_selected_rows(delete=True)

if __name__ == "__main__":
    """creates a test CouchGrid if called directly"""
    from couch_grid import CouchGrid

    #create and show a test window
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.set_title("DictionaryGrid Test Window")
    win.connect("destroy",gtk.main_quit)
    win.show()

    #create a top level container
    vbox = gtk.VBox(False, 10)
    vbox.show()
    win.add(vbox)

    #create a test widget with test database values
    dicts = [{"ID": 0, "key?": True, "tags": "aaa bbb ccc", "string":"aaaaaaa","date":"2010-08-01"},
                 {"ID": 1, "key?": False, "tags": "bbb ccc ddd", "string":"bbbbbbb","date":"2010-08-01"},
                 {"ID": 2, "key?": True, "tags": "ccc ddd eee", "string":"cccccccc","date":"2010-09-01"},
                 {"ID": 3, "key?": False, "tags": "ddd eee fff", "string":"dddddddd","date":"2010-10-01"},
                 {"ID": 4, "key?": True, "tags": "eee fff ggg", "string":"eeeeeeee","date":"2010-11-01"}]

    database_name = "couch_widget_test"
    record_type = "couch_grid_filter_test"
    grid = CouchGrid(database_name, record_type=record_type, dictionaries=dicts, editable=True)
    grid.columns["tags"].set_title("modified title")
    grid.show()


    hints = {}
    filt = GridFilter(grid,hints)
    filt.show()
    vbox.pack_start(filt, False, False)
    vbox.pack_end(grid, True, True)

    delete_button = gtk.Button("Delete Selected")
    delete_button.connect("clicked",__delete_test,grid)
    delete_button.show()


    vbox.pack_start(delete_button,False, False)
    gtk.main()


