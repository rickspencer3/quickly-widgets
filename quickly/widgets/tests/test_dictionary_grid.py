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

"""Tests for the DictionaryGrid"""

from testtools import TestCase
from quickly.widgets.dictionary_grid import DictionaryGrid
import gobject
from quickly.widgets.grid_column import StringColumn, IntegerColumn, CurrencyColumn,CheckColumn, DateColumn

class TestDictionaryGrid(TestCase):
    """Test the CouchGrid functionality"""

    def setUp(self):
        TestCase.setUp(self)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_empty_construction(self):
        """Test a simple creating An AsynchTaskProgressBox 
        and then adding keys and dictionaries after creation

        """
        grid = DictionaryGrid()
        self.assertEqual((grid != None), True)
        grid.keys = ["key1","key2"]
        self.assertEqual(grid.get_model().get_n_columns(),3)
        grid.append_row({"key1":"val11","key2":"val12"})
        self.assertEqual(len(grid.get_model()),1)


    def test_constructor_with_dicts(self):
        """test creating a grid with dictionaries in the contructor"""
        dicts = [{"key1_1": "val1_1", "key1_2": "val1_2", "key1_3": "val1_3"},
                 {"key1_1": "val2_1", "key1_2": "val2_2", "key1_3": "val2_3"}]

        #build the CouchGrid
        grid = DictionaryGrid(dicts)
        self.assertEqual(grid.get_model().get_n_columns(),4)
        self.assertEqual(len(grid.get_model()),2)

    def test_constructor_with_dicts_and_keys(self):
        """test creating a grid with dictionaries in the contructor
        as well as keys in the contructor, with fewer keys than
        items in the dictionary

        """
        dicts = [{"key1_1": "val1_1", "key1_2": "val1_2", "key1_3": "val1_3"},
                 {"key1_1": "val2_1", "key1_2": "val2_2", "key1_3": "val2_3"}]
        keys = ["key1_1", "key1_3"]

        #build the CouchGrid
        grid = DictionaryGrid(dicts,keys)
        self.assertEqual(grid.get_model().get_n_columns(),4)
        self.assertEqual(len(grid.get_model()),2)

    def test_extra_data_from_selected(self):
        """Ensure that keys starting with _ are not displayed,
        but the valuesa retrievable.

        """

        dicts = [{"key1_1": "val1_1", "key1_2": "val1_2", "__extra": ["boo","biz","baz"]},
                 {"key1_1": "val2_1", "key1_2": "val2_2", "__extra": self}]
        grid = DictionaryGrid(dicts)

        #make sure there are 2 columns
        self.assertEqual(len(grid.get_model()),2)

        #ensure that none of the columns are named _extra
        cols = grid.get_columns()
        for c in cols:
            self.assertEqual(c.get_title().startswith("key"), True)

        #select the first row
        selection = grid.get_selection()
        selection.select_path((0,))
        selected_dict = grid.selected_rows[0]
        self.assertEqual(selected_dict["__extra"],["boo","biz","baz"])

    def test_dicts_with_different_keys(self):
        dicts = [{"key1_1": "val1_1", "key1_2": "val1_2", "__extra": ["boo","biz","baz"]},
                 {"key2_1": "val2_1", "key2_2": "val2_2", "__extra": self}]
        grid = DictionaryGrid(dicts)

        #make sure there are 5 columns
        self.assertEqual(grid.get_model().get_n_columns(),5)

    def test_remove_selected_rows(self):
        dicts = [{"key1_1": "val1_1", "key1_2": "val1_2", "key1_3": "val1_3"},
                 {"key1_1": "val2_1", "key1_2": "val2_2", "key1_3": "val2_3"},
                 {"key1_1": "val3_1", "key1_2": "val3_2", "key1_3": "val3_3"},
                 {"key1_1": "val4_1", "key1_2": "val4_2", "key1_3": "val4_3"},
                 {"key1_1": "val5_1", "key1_2": "val5_2", "key1_3": "val5_3"}]

        grid = DictionaryGrid(dicts)
        selection = grid.get_selection()
        grid.remove_selected_rows()

        #select the last row and remove it
        selection.select_path((4,))
        grid.remove_selected_rows()

        #the last row should then be selected and there should be 4 rows now
        self.assertEqual(len(grid.get_model()),4)
        self.assertEqual(len(grid.selected_rows),1)
        self.assertEqual(grid.selected_rows[0]["key1_1"],"val4_1") 

        #select the first and third rows and remove them
        selection = grid.get_selection()
        selection.unselect_all()        
        selection.select_path((0,))
        selection.select_path((2,))
        grid.remove_selected_rows()

        #make sure the now last row is selected, and there are 2 rows left
        self.assertEqual(len(grid.get_model()),2)
        self.assertEqual(len(grid.selected_rows),1)
        self.assertEqual(grid.selected_rows[0]["key1_2"],"val4_2") 

    def test_auto_set_col_types(self):
        """Ensure that collumn types are set properly"""

        data = [{"id":0,"price":1.00,"bool?":True,
                "sale price":.50, "count":50, "full count":100,
                "date":"2010-05-05","sale date":"2010-05-06"}]
        grid = DictionaryGrid(data)
        c_type = type(grid.columns["id"])
        self.assertEqual(c_type,IntegerColumn)

        c_type = type(grid.columns["price"])
        self.assertEqual(c_type,CurrencyColumn)

        c_type = type(grid.columns["bool?"])
        self.assertEqual(c_type,CheckColumn)

        c_type = type(grid.columns["sale price"])
        self.assertEqual(c_type,CurrencyColumn)

        c_type = type(grid.columns["count"])
        self.assertEqual(c_type,IntegerColumn)

        c_type = type(grid.columns["full count"])
        self.assertEqual(c_type,IntegerColumn)

        c_type = type(grid.columns["date"])
        self.assertEqual(c_type,DateColumn)

        c_type = type(grid.columns["sale date"])
        self.assertEqual(c_type,DateColumn)

    def test_NONE_values(self):
        keys = ["id","price","bool?","foo"]
        dicts = [{"price":None,"id":None,"bool?":None,"foo":None}]
        grid = DictionaryGrid(dicts)
        self.assertEqual(len(grid.get_model()),1)

    def test_use_custom_columns(self):
        """Ensure that type hins work so inferred types can be
        overridden and non-inferred type can be set.

        """

        keys = ["id","price","bool?","foo"]
        hints = {"id":StringColumn, "price":IntegerColumn,
                 "bool?":CurrencyColumn,"foo":CheckColumn}
        dicts = [{"price":100,"id":"asdfas","bool?":10.01,"foo":True}]
        grid = DictionaryGrid(dicts, keys=keys, type_hints=hints)
        for c in grid.get_columns():
            key = c.key
            col_type = c.column_type
            if key == "id":
                self.assertEqual(col_type,gobject.TYPE_STRING)
            elif key == "price":
                self.assertEqual(col_type,gobject.TYPE_STRING)
            elif key == "bool?":
                self.assertEqual(col_type,gobject.TYPE_STRING)
            elif key == "foo":
                self.assertEqual(col_type,gobject.TYPE_INT)
            else:
                self.assertEqual("Extra key Found",False) 

    def test_infer_boolean_values(self):
        """Ensure that inferring boolean values from strings works"""
        keys = ["a?","b?","c?","d?","e?","f?"]
        dicts = [{"a?":True,"b?":False,"c?":"Yes","d?":"No","e?":1.5,"f?":0}]
        grid = DictionaryGrid(dicts, keys)
        test_dict = grid.get_dictionaries_copy()[0]
        self.assertEqual(test_dict["a?"],True)
        self.assertEqual(test_dict["b?"],False)
        self.assertEqual(test_dict["c?"],True)
        self.assertEqual(test_dict["d?"],False)
        self.assertEqual(test_dict["e?"],True)
        self.assertEqual(test_dict["f?"],False)
        

    def test_mismatched_col_and_val_types(self):
        """Ensure robustness for strings passed in for non-str
        column types

        """

        keys = ["id","price","bool?"]
        dicts = [{"price":"100.00","id":"50","bool?":"Yes"}]
        grid = DictionaryGrid(dicts, keys)
        test_dict = grid.get_dictionaries_copy()[0]
        self.assertEqual(test_dict["id"],50)
        self.assertEqual(test_dict["price"],100.00)
        self.assertEqual(test_dict["bool?"],True)
        
    def test_copy_dictionaries(self):
        """Testcase for LP: #497664"""
        dicts = [{"key1_1": "val1_1", "key1_2": "val1_2", "key1_3": "val1_3"},
                 {"key1_1": "val2_1", "key1_2": "val2_2", "key1_3": "val2_3"}]

        #build the CouchGrid
        grid1 = DictionaryGrid(dicts)
        # added two dicts, so length should be 2
        self.assertEqual(len(grid1.get_dictionaries_copy()), 2)

        #no dicts, so it should be 0
        grid2 = DictionaryGrid()
        self.assertEqual(len(grid2.get_dictionaries_copy()), 0)
        
    def test_columns_property(self):
        dicts = [{"key1_1": "val1_1", "key1_2": "val1_2", "key1_3": "val1_3"},
                 {"key1_1": "val2_1", "key1_2": "val2_2", "key1_3": "val2_3"},
                 {"key1_1": "val3_1", "key1_2": "val3_2", "key1_3": "val3_3"},
                 {"key1_1": "val4_1", "key1_2": "val4_2", "key1_3": "val4_3"},
                 {"key1_1": "val5_1", "key1_2": "val5_2", "key1_3": "val5_3"}]

        grid = DictionaryGrid(dicts)
        self.assertTrue("key1_1" in grid.columns)
        self.assertTrue("key1_2" in grid.columns)
        self.assertTrue("key1_3" in grid.columns)

    def test_set_a_column_title(self):
        dicts = [{"key1_1": "val1_1", "key1_2": "val1_2", "key1_3": "val1_3"},
                 {"key1_1": "val2_1", "key1_2": "val2_2", "key1_3": "val2_3"},
                 {"key1_1": "val3_1", "key1_2": "val3_2", "key1_3": "val3_3"},
                 {"key1_1": "val4_1", "key1_2": "val4_2", "key1_3": "val4_3"},
                 {"key1_1": "val5_1", "key1_2": "val5_2", "key1_3": "val5_3"}]

        grid = DictionaryGrid(dicts)
        grid.columns["key1_1"].set_title("KEY")
        for c in grid.get_columns():
            if c.key == "key1_1":
                self.assertEqual(c.get_title(),"KEY")

    def test_set_multiple_column_titles(self):
        dicts = [{"key1_1": "val1_1", "key1_2": "val1_2", "key1_3": "val1_3"},
                 {"key1_1": "val2_1", "key1_2": "val2_2", "key1_3": "val2_3"},
                 {"key1_1": "val3_1", "key1_2": "val3_2", "key1_3": "val3_3"},
                 {"key1_1": "val4_1", "key1_2": "val4_2", "key1_3": "val4_3"},
                 {"key1_1": "val5_1", "key1_2": "val5_2", "key1_3": "val5_3"}]

        grid = DictionaryGrid(dicts)
        titles = {"key1_1":"KEY1","key1_2":"KEY2","key1_3":"KEY3"}
        grid.set_column_titles(titles)
        for c in grid.columns:
            self.assertTrue(grid.columns[c].get_title() in ("KEY1","KEY2","KEY3"))

