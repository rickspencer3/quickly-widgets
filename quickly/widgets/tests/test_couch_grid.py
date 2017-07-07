# Copyright 2009 Canonical Ltd.
#
# This file is part of desktopcouch.
#
#  desktopcouch is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation.
#
# desktopcouch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with desktopcouch.  If not, see <http://www.gnu.org/licenses/>.
#
# Authors: Rick Spencer <rick.spencer@canonical.com>

"""Tests for the CouchGrid object"""

from testtools import TestCase

from desktopcouch.records.record import Record
from desktopcouch.records.server import CouchDatabase
from quickly.widgets.couch_grid import CouchGrid


class TestCouchGrid(TestCase):
    """Test the CouchGrid functionality"""

    def setUp(self):
        TestCase.setUp(self)
        self.dbname = self._testMethodName
        self.db = CouchDatabase(self.dbname, create=True)
        self.record_type = "test_record_type"

    def tearDown(self):
        """tear down each test"""
        TestCase.tearDown(self)
        #delete the database
        del self.db._server[self.dbname]

    def test_constructor_guarded(self):
        """Ensure that CouchGrid cannot be constructed without a
        database name.
        """
        try:
            cw = CouchGrid(None)
        except TypeError, inst:
            self.assertEqual(
                inst.args[0],"database_name is required and must be a string")

    def test_new_rows_with_headings(self):
        """Test a simple creating a CouchGrid """

        #create a test widget with test database values
        cw = CouchGrid(self.dbname)

        #allow editing
        cw.editable = True

        #create headers/keys
        cw.keys = ["Key1", "Key2", "Key3", "Key4"]

        #set the record_type for the TreeView
        #it will not populate without this value being set
        cw.record_type = self.record_type

        #create a row with all four columns set
        cw.append_row({"Key1":"val1", "Key2":"val2", "Key2":"val3", "Key4":"val4"})

        #create a row with only the second column set
        cw.append_row({"Key1":"", "Key2":"val2"})

        #create an empty row (which will not be saved until the user edits it)
        cw.append_row({})

        #if this all worked, there should be three rows in the model
        model = cw.get_model()
        self.assertEqual(len(model), 3)

    def test_headings_no_stored_records(self):
        record_type = "a_new_record_type"
        dicts = [{"key1":"val1"},{"key1":"val2"}]
        cw = CouchGrid(self.dbname, record_type=record_type,dictionaries=dicts)
        self.assertEqual(len(cw.get_model()),2)
        self.assertEqual(cw.get_model().get_n_columns(),2)

    def test_no_headings_or_stored_records(self):
        """test when there is no defined headings and no stored records
        to infer headings from. Should raise a proper exception.
        """

        try:
            #create a test widget with test database values
            cw = CouchGrid(self.dbname)

            #set the record_type for the TreeView
            #it will not populate without this value being set
            cw.record_type = self.record_type

            #create a row with all four columns set
            cw.append_row(["val1", "val2", "val3", "val4"])

            #create a row with only the second column set
            cw.append_row(["", "val2"])

            #create an empty row (which will not be saved until the
            #user edits it)
            cw.append_row([])

            #if this all worked, there should be three rows in the model
            model = cw.get_model()

        #should be catching the following exception
        except RuntimeError, inst:
            self.assertEquals(
                inst.args[0].find("Cannot infer columns for CouchGrid"),0)


    def test_all_from_database(self):
        #create some records
        db = CouchDatabase(self.dbname, create=True)
        db.put_record(Record({
            "key1_1": "val1_1", "key1_2": "val1_2", "key1_3": "val1_3",
            "record_type": self.record_type}))
        db.put_record(Record({
            "key1_1": "val2_1", "key1_2": "val2_2", "key1_3": "val2_3",
            "record_type": self.record_type}))

        #build the CouchGrid
        cw = CouchGrid(self.dbname)
        cw.record_type = self.record_type
        #make sure there are three columns and two rows
        self.assertEqual(cw.get_model().get_n_columns(),4)
        self.assertEqual(len(cw.get_model()),2)

    def test_delete_selected_rows(self):
        #create some records
        db = CouchDatabase(self.dbname, create=True)
        ids = []
        for i in xrange(0,10):
            ids.append( db.put_record(Record({
            "key1_1": "val1_%s" % str(i), "iter_count": i,
            "record_type": self.record_type})))

        #build the CouchGrid
        cw = CouchGrid(self.dbname, record_type = self.record_type)
        cw.selected_record_ids = [ids[0],ids[5],ids[9]]
        cw.remove_selected_rows(delete=True)
        self.assertEqual(self.db.get_record(ids[0]) is None,True)     
        self.assertEqual(self.db.get_record(ids[5]) is None,True)     
        self.assertEqual(self.db.get_record(ids[9]) is None,True)     

        self.assertEqual(self.db.get_record(ids[1]) is not None,True)     
        self.assertEqual(self.db.get_record(ids[2]) is not None,True)     
        self.assertEqual(self.db.get_record(ids[3]) is not None,True)     
        self.assertEqual(self.db.get_record(ids[4]) is not None,True)     
        self.assertEqual(self.db.get_record(ids[6]) is not None,True)     
        self.assertEqual(self.db.get_record(ids[7]) is not None,True)     
        self.assertEqual(self.db.get_record(ids[8]) is not None,True)     

    def test_dont_delete_selected_rows(self):
        #create some records
        db = CouchDatabase(self.dbname, create=True)
        ids = []
        for i in xrange(0,10):
            ids.append( db.put_record(Record({
            "key1_1": "val1_%s" % str(i), "iter_count": i,
            "record_type": self.record_type})))

        #build the CouchGrid
        cw = CouchGrid(self.dbname, record_type = self.record_type)
        cw.selected_record_ids = [ids[0],ids[5],ids[9]]
        cw.remove_selected_rows(delete=False)
        cw.selected_record_ids = [ids[1],ids[4],ids[8]]
        cw.remove_selected_rows()
        self.assertEqual(self.db.get_record(ids[0]) is not None,True)     
        self.assertEqual(self.db.get_record(ids[5]) is not None,True)     
        self.assertEqual(self.db.get_record(ids[9]) is not None,True)     

        self.assertEqual(self.db.get_record(ids[1]) is not None,True)     
        self.assertEqual(self.db.get_record(ids[2]) is not None,True)     
        self.assertEqual(self.db.get_record(ids[3]) is not None,True)     
        self.assertEqual(self.db.get_record(ids[4]) is not None,True)     
        self.assertEqual(self.db.get_record(ids[6]) is not None,True)     
        self.assertEqual(self.db.get_record(ids[7]) is not None,True)     
        self.assertEqual(self.db.get_record(ids[8]) is not None,True)     


       
    def test_selected_id_property(self):
        #create some records
        db = CouchDatabase(self.dbname, create=True)
        id1 = db.put_record(Record({
            "key1_1": "val1_1", "key1_2": "val1_2", "key1_3": "val1_3",
            "record_type": self.record_type}))
        id2 = db.put_record(Record({
            "key1_1": "val2_1", "key1_2": "val2_2", "key1_3": "val2_3",
            "record_type": self.record_type}))

        #build the CouchGrid
        cw = CouchGrid(self.dbname)
        cw.record_type = self.record_type

        #make sure the record ids are selected properly
        cw.selected_record_ids = [id1]
        self.assertEqual(cw.selected_record_ids[0], id1)
        cw.selected_record_ids = [id2]
        self.assertEqual(cw.selected_record_ids[0], id2)

    def test_single_col_from_database(self):
        #create some records
        self.db.put_record(Record({
            "key1_1": "val1_1", "key1_2": "val1_2", "key1_3": "val1_3",
            "record_type": self.record_type}))
        self.db.put_record(Record({
            "key1_1": "val2_1", "key1_2": "val2_2", "key1_3": "val2_3",
            "record_type": self.record_type}))
        #build the CouchGrid
        cw = CouchGrid(self.dbname)
        cw.keys = ["key1_1"]
        cw.record_type = self.record_type
        #make sure there are three columns and two rows
        self.assertEqual(cw.get_model().get_n_columns(),2)
        self.assertEqual(len(cw.get_model()),2)

    def test_optional_record_type_arg(self):
        """Test a simple creating a CouchGrid """
        #create some records
        self.db.put_record(Record({
            "key1_1": "val1_1", "key1_2": "val1_2", "key1_3": "val1_3",
            "record_type": self.record_type}))
        self.db.put_record(Record({
            "key1_1": "val1_1", "key1_2": "val2_2", "key1_3": "val2_3",
            "record_type": self.record_type}))

        #create a test widget with test database values
        cw = CouchGrid(self.dbname, record_type=self.record_type)

        #make sure there are three columns and two rows
        self.assertEqual(cw.get_model().get_n_columns(),4)
        self.assertEqual(len(cw.get_model()),2)

    def test_optional_args_no_stored_records(self):
        """Test a simple creating a CouchGrid """

        #create a test widget with test database values
        cw = CouchGrid(
            self.dbname, record_type=self.record_type,
            keys=["Key1", "Key2", "Key3", "Key4"])

        #create a row with all four columns set
        cw.append_row({"Key1":"val1", "Key2":"val2", "Key2":"val3", "Key4":"val4"})

        #create a row with only the second column set
        cw.append_row({"Key1":"", "Key2":"val2"})

        #create an empty row (which will not be saved until the user edits it)
        cw.append_row({})

        #if this all worked, there should be three rows in the model
        model = cw.get_model()
        self.assertEqual(len(model), 3)

    def test_programatically_add_row(self):
        """test appending different sized rows programatically"""
        #create some records
        self.db.put_record(Record({
            "key1_1": "val1_1", "key1_2": "val1_2", "key1_3": "val1_3",
            "record_type": self.record_type}))
        self.db.put_record(Record({
            "key1_1": "val2_1", "key1_2": "val2_2", "key1_3": "val2_3",
            "record_type": self.record_type}))

        #create a test widget with test database values
        cw = CouchGrid(self.dbname, record_type=self.record_type)

        #allow editing
        cw.append_row({"key1_1":"boo", "key1_2":"ray"})

        #make sure there are three columns and two rows
        self.assertEqual(cw.get_model().get_n_columns(),4)
        self.assertEqual(len(cw.get_model()),3)
