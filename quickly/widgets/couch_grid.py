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

"""A Treeview for Desktop CouchDB
Displays and persists data in desktopcouch, handles presentation
of the UI in a Gtk.TreeView, as well handles persistence to a backend
desktopcouch database.

Using
#define the database and record type
database = "couch_widget_test"
record_type="test_record_type"

#create a dictionary if you don't already have one
dicts = [{"test?":True,"price":100,"foo count":100,"Key4":"1004"},
    {"test?":True,"price":100,"foo count":100,"Key4":"1004"},
    {"test?":True,"price":100,"foo count":100,"Key4":"1004"}]

#create the CouchGrid
cg = CouchGrid(database, record_type=record_type, dictionaries=dicts)

Configuring
#Define columns to display
keys=["price","test?"]
cg = CouchGrid(database, record_type=record_type, dictionaries=dicts,keys=keys)

#Define column types to use
hints = {"price": StringColumn}
cg = CouchGrid(database, record_type=record_type, dictionaries=dicts,keys=keys, type_hints = hints)

#A CouchGrid is a Dictionary Grid whcih is a TreeView,
#so you can use DicationaryGrid and TreeView members
cg.editable = True
cg.get_column(0).set_title("Price")

Extending
To change the way CouchGrid persists data, change _refresh_treeview to
handle persistence of data if needed, calling DictionaryGrid._populate_treeivew
to handle the UI. You should do the same with append_row.
 
You may also want to override _edited and _edited_toggled to handle persistence 
when the UI is changed.

It is only useful to extend CouchGrid if you are using desktopcouch for
persistence. Otherwise, derive from DictionaryGrid.

"""

import gtk
import gobject
from desktopcouch.records.server import CouchDatabase
from desktopcouch.records.record import Record
from quickly.widgets.dictionary_grid import DictionaryGrid
from quickly.widgets.grid_column import CheckColumn

#TODO: a delete_selected_rows function would be nice and not too hard

class CouchGrid(DictionaryGrid):
    def __init__(
            self, database_name, record_type=None, dictionaries=None, editable=False, keys=None, type_hints=None, uri=None):
        """Create a new Couchwidget
        arguments:
        database_name - specify the name of the database in the desktop
        couchdb to use. If the specified database does not exist, it
        will be created.

        optional arguments:
        record_type - a string to specify the record_type to use in
        retrieving and creating records. Note that if no records exist
        in the CouchDB then the keys argument must also be used or
        a RuntimeError will result.

        dictionaries - a list of dictionaries to initialize in the 
        grid. If these haven't been added to desktopcouch, the will
        be automatically persisted and updated using the recored_type
        specified. Any previously saved data of the same record_type will
        also be displayed. 

        keys - a list of strings specifying keys to use in
        the columns of the CouchGrid. The keys will also be used for the
        column titles and keys in desktop couch.

        If a record does not contain a value for a specified key
        the CouchGrid will simply display an empty cell of the 
        appropriate type. If the widget is set to editable, 
        the user will be able to add values to the database.

        The types for the columns will be inferred by the key based on
        some conventions. the key "id" is assumed to be an integer, as
        is any key ending in " count". A key ending in "?" is assumed
        to be a Boolean displayed with a checkbox. The key "price" is
        assumed to be currency, as is any key ending in "count". There
        may be others. Defaults can be overridden using type-hints. All
        other keys will be assumed to be strings.
        
        type-hints - a dictionary containing keys specificed for the
        TreeView and GridColumns. Used to override types inferred
        by convention, or for changing the type of a column from
        the default of a string to something else.

        uri - A uri for the DesktopCouch. This is only used to 
        choose a Couch database running remotely. The default is
        to use the local desktopcouch database.

        """

        if type(database_name) is not type(str()):
            raise TypeError("database_name is required and must be a string")

        #set up the database before trying to use it
        self.uri = uri
        self._record_type = None
        self._db = None
        if record_type is not None:
            self._record_type = record_type

        if dictionaries is not None and keys is None:
            DictionaryGrid.__init__(self, None, editable, keys, type_hints)
        else:
            DictionaryGrid.__init__(self, None, editable, keys, type_hints)

        if self.uri:
            self._db = CouchDatabase(database_name, create=True, uri=self.uri)
        else:
            self._db = CouchDatabase(database_name, create=True)

        if dictionaries is not None:
            for d in dictionaries:
                self._persist_dict_to_couch(d)

        self._refresh_treeview()

    @property
    def database(self):
        """database - gets an instance to the CouchDB.
        Set to a string to change the database.

        """
        return self._db

    @database.setter
    def database(self, db_name):
        if self.uri:
            self._db = CouchDatabase(db_name, create=True, uri=self.uri)
        else:
            self._db = CouchDatabase(db_name, create=True)
        if self.record_type != None:
            self._refresh_treeview()#first time treeview is reset

    @property
    def record_type(self):
        """record_type - a string specifying the record type of
        the documents to retrieve from the CouchDB.

        Will cause the TreeView to refresh when set.
        """
        return self._record_type

    @record_type.setter
    def record_type(self, record_type):

        #store the record type string
        self._record_type = record_type
        self._refresh_treeview()

    @property
    def selected_record_ids(self):
        """ selected_record_ids - a list of document ids that are
        selected in the CouchGrid. Throws an IndexError if
        a specified id is not found in the list when setting
        this property.

        This property is read/write

        """
        ids = []
        for row in self.selected_rows:
            id_ = None
            
            if "__desktopcouch_id" in row:
                id_ = row["__desktopcouch_id"]
            ids.append(id_)
        return ids

    @selected_record_ids.setter
    def selected_record_ids(self, indexes):
        rows = [] #a list of rows to select
        for id in indexes:
            id_found = False #track if the id was found

            for i,r in enumerate(self.list_store):
                dictionary = r[len(self.keys)] #this dictionary always last column
                if "__desktopcouch_id" in dictionary:
                    if dictionary["__desktopcouch_id"] == id:
                        id_found = True #id was good
                        if r not in rows: #don't have duplicates to select
                            rows.append(i)
            if not id_found: #stop if a requested id was not in the list
                raise IndexError("id %s not found" %id)

        #select the requested ids
        selection = self.get_selection()
        selection.unselect_all()
        for r in rows:
            selection.select_path(r)

    def remove_selected_rows(self, delete=False):
        rows_to_delete = self.selected_rows
        if delete:
            for r in rows_to_delete:
                self.database.delete_record(r["__desktopcouch_id"])
        DictionaryGrid.remove_selected_rows(self)

    def _refresh_treeview(self):
        """
        _refresh_treeview: internal function to handle rebuilding
        the gtk.TreeView along with columns and cell renderers. extends
        DictionaryGrid._refresh_treeview by retrieving stored desktopcouch
        records before calling DictionaryGrid._refresh_treeview. 

        _refresh_treeview is not typically called directly,
        but may be useful to override in subclasses.

        """

        #if the database is not set up, just return
        if self._db is None or self._record_type is None:
            return

        #if keys aren't set, infer them from the collection
        if len(self._dictionaries) > 0 and self.keys is None:
            self._infer_keys_from_dictionaries()        

        #retrieve the docs for the record_type, if any
        results = self._db.get_records(
            record_type=self._record_type,create_view=True)


        #if there are no rows and no keys set, there is no
        #way to build the grid, just raise an error
        if len(results) == 0 and self._keys is None:
            raise RuntimeError("Cannot infer columns for CouchGrid")

        dicts = []
        for r in results:
            d = r.value

            #hmmm, maybe make these so they get hidden rather than delete them
            #hide the desktopcouch variabls
            for key in d:
                if key.startswith("_") and not key.startswith("__desktopcouch"):
                    d["__desktopcouch" + key] = d[key]
                    del(d[key])

            d["__record_type"] = d["record_type"]
            del(d["record_type"])
            dicts.append(d)

        self._dictionaries = dicts
        DictionaryGrid._refresh_treeview(self)

        for c in self.get_columns():
            if type(c) == CheckColumn:
                c.renderer.connect("toggled",self._edited_toggled, c)
            else:
                c.renderer.connect("edited",self._edited, c)

    def append_row(self, dictionary):
        """append_row: add a row to the TreeView and to DesktopCouch. 
        If keys are already set up only the the keys in the dictionary 
        matching the keys used for columns will be displayed, though 
        all the key value pairs will be saved to the DesktopCouch. 
        If no keys are set up, and this is the first row, keys will be
        inferred from the dictionary keys.

        arguments:
        dictionary - a dictionary to add to the Treeview and to DesktopCouch

        """

        if dictionary is None:
            dictionary = {}

        #Here we add rows to desktopcouch if needed
        if "__desktopcouch_id" not in dictionary:
            self._persist_dict_to_couch(dictionary)
        DictionaryGrid.append_row(self,dictionary)

    def _persist_dict_to_couch(self,dictionary):
        """ _persist_dict_to_couch - internal implementation. may be useful
        a subclass of CouchGrid, but not normally called directly.

        """

        dictionary["record_type"] = self.record_type
        rec = Record(dictionary)
        #meh, best not to save an empty row
        if len(dictionary) > 1:
            doc_id = self._db.put_record(rec)
            dictionary["__desktopcouch_id"] = doc_id
            dictionary["__record_type"] = self.record_type
            del(dictionary["record_type"])
                
    def _edited_toggled(self, cell, path, col):
        """ _edited_toggled - internal signal handler.
        Updates the database if a cell in the Treeview
        has been edited special cased for CheckColumns.

        """

        iter = self.list_store.get_iter(path)
        key = col.key
        active = not cell.get_active()
        self._edited(cell, path, active, col)

    def _edited(self, cell, path, new_val, col):
        """ _edited - internal signal handler.
        Updates the database if a cell in the Treeview
        has been edited.

        """
        iter = self.list_store.get_iter(path)
        key = col.key
        dictionary = self.list_store.get_value(iter,len(self.keys))

        if "__desktopcouch_id" not in dictionary: #the row has not been stored
            #create a document
            dictionary["record_type"] = self.record_type
            rec = Record(dictionary)
            doc_id = self._db.put_record(rec)
            dictionary["__desktopcouch_id"] = doc_id
            self.list_store.set_value(iter, len(self.keys), dictionary)

        else: #it has been saved
            #get the record id from the dictionary
            #then update the datbase with the change
            id = dictionary["__desktopcouch_id"]
            key = col.key
            self._db.update_fields(id,{key:new_val})

def __show_selected(widget, row, widgets):
    """Test function for selection properties of CouchGrid"""
    tv, cg = widgets
    disp = "Rows:\n"
    for r in cg.selected_rows:
        disp += str(r) + "\n"

    disp += "\n\n_Ids:\n"
    for r in cg.selected_record_ids:
        disp += str(r) + "\n"

    tv.get_buffer().set_text(disp)
    
def __select_ids(widget, widgets):
    """Test function for selecting ids."""
    entry, cg, lbl = widgets
    cg.selected_record_ids = entry.get_text().split(",")

if __name__ == "__main__":
    """creates a test CouchGrid if called directly"""

    from quickly.widgets.grid_column import StringColumn

    #create and show a test window and container
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.set_title("CouchGrid Test Window")
    win.connect("destroy",gtk.main_quit)
    win.show()
    vbox = gtk.VBox(False, False)
    vbox.show()
    win.add(vbox)

    #create a test widget with test database values
    dicts = [{"test?":True,"price":100,"foo count":100,"Key4":"1004"},
             {"test?":True,"price":100,"foo count":100,"Key4":"1004"},
             {"test?":True,"price":100,"foo count":100,"Key4":"1004"}]

    #create some settings
    database = "couch_widget_test"
    record_type="test_record_type"
    keys=["price","test?"]
    hints = {"price": StringColumn}
    
    #create it and part a bit
    cg = CouchGrid(database, record_type=record_type, dictionaries=dicts,keys=keys, type_hints = hints)
    cg.editable = True
    cg.get_column(0).set_title("Price")

    #finish out and run the test UI
    cg.show()
    vbox.pack_start(cg, False, True)
    hbox = gtk.HBox(False, 5)
    hbox.show()
    tv = gtk.TextView()
    tv.show()
    tv.set_wrap_mode(gtk.WRAP_CHAR)
    tv.set_size_request(300,-1)
    cg.connect("selection-changed",__show_selected, (tv,cg))

    id_vbox = gtk.VBox(False, 5)
    id_vbox.show()

    fb_lbl = gtk.Label("paste ids into the edit box to select them")
    fb_lbl.show()

    entry = gtk.Entry()
    entry.show()

    btn = gtk.Button("select ids")
    btn.show()
    btn.connect("clicked", __select_ids, (entry,cg, fb_lbl))

    id_vbox.pack_start(fb_lbl, False, False)
    id_vbox.pack_start(entry, False, False)
    id_vbox.pack_end(btn, False, False)

    hbox.pack_start(tv, False, False)
    vbox.pack_end(hbox, False, False)
    hbox.pack_end(id_vbox, False, False)

    #run the test app
    gtk.main()

