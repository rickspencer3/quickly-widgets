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
from quickly.widgets.grid_filter import GridFilter

class TestGridFilter(TestCase):
    """Test the CouchGrid functionality"""

    def setUp(self):
        TestCase.setUp(self)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_create_a_grid(self):
        dicts = [{"key1_1": "val1_1", "key1_2": "val1_2", "key1_3": "val1_3"},
                 {"key1_1": "val2_1", "key1_2": "val2_2", "key1_3": "val2_3"},
                 {"key1_1": "val3_1", "key1_2": "val3_2", "key1_3": "val3_3"},
                 {"key1_1": "val4_1", "key1_2": "val4_2", "key1_3": "val4_3"},
                 {"key1_1": "val5_1", "key1_2": "val5_2", "key1_3": "val5_3"}]
        grid = DictionaryGrid(dicts)
        grid_filter = GridFilter(grid)
        self.assertEqual(len(grid.get_model()),5)

    def test_filter_a_row(self):
        dicts = [{"key1_1": "val1_1", "key1_2": "val1_2", "key1_3": "val1_3"},
                 {"key1_1": "val2_1", "key1_2": "val2_2", "key1_3": "val2_3"},
                 {"key1_1": "val3_1", "key1_2": "val3_2", "key1_3": "val3_3"},
                 {"key1_1": "val4_1", "key1_2": "val4_2", "key1_3": "val4_3"},
                 {"key1_1": "val5_1", "key1_2": "val5_2", "key1_3": "val5_3"}]
        grid = DictionaryGrid(dicts)
        grid_filter = GridFilter(grid)
        filter_row = grid_filter.rows[0]
        filter_combo = filter_row.get_children()[1].get_children()[0].get_children()[0]
        filter_combo.set_active(1)
        entry = filter_row.get_children()[1].get_children()[0].get_children()[1]
        entry.set_text("val5_1")
        self.assertEqual(len(grid.get_model()),4)

    def test_remove_selected_with_filter(self):
        dicts = [{"key1_1": "val1_1", "key1_2": "val1_2", "key1_3": "val1_3"},
                 {"key1_1": "val2_1", "key1_2": "val2_2", "key1_3": "val2_3"},
                 {"key1_1": "val3_1", "key1_2": "val3_2", "key1_3": "val3_3"},
                 {"key1_1": "val4_1", "key1_2": "val4_2", "key1_3": "val4_3"},
                 {"key1_1": "val5_1", "key1_2": "val5_2", "key1_3": "val5_3"}]
        grid = DictionaryGrid(dicts)
        grid_filter = GridFilter(grid)
        filter_row = grid_filter.rows[0]
        filter_combo = filter_row.get_children()[1].get_children()[0].get_children()[0]
        filter_combo.set_active(1)
        entry = filter_row.get_children()[1].get_children()[0].get_children()[1]
        entry.set_text("val5_1")
                
        selection = grid.get_selection()
        selection.select_path((1,))
        selection.select_path((2,))

        grid.remove_selected_rows()

        self.assertEqual(len(grid.get_model()),2)

    def test_with_set_column_titles(self):
        dicts = [{"key1_1": "val1_1", "key1_2": "val1_2", "key1_3": "val1_3"},
                 {"key1_1": "val2_1", "key1_2": "val2_2", "key1_3": "val2_3"},
                 {"key1_1": "val3_1", "key1_2": "val3_2", "key1_3": "val3_3"},
                 {"key1_1": "val4_1", "key1_2": "val4_2", "key1_3": "val4_3"},
                 {"key1_1": "val5_1", "key1_2": "val5_2", "key1_3": "val5_3"}]

        grid = DictionaryGrid(dictionaries = dicts, keys=["key1_1","key1_2","key1_3"])
        titles = {"key1_1":"KEY1","key1_2":"KEY2","key1_3":"KEY3"}
        grid.set_column_titles(titles)
        grid_filter = GridFilter(grid)

        filter_row = grid_filter.rows[0]
        column_combo = filter_row.get_children()[0].get_children()[0]
        #make sure the correct titles are appearing
        itr = column_combo.get_model().get_iter(0)
        self.assertEqual(column_combo.get_model().get_value(itr,0),"KEY1")

        itr = column_combo.get_model().get_iter(1)
        self.assertEqual(column_combo.get_model().get_value(itr,0),"KEY2")

        itr = column_combo.get_model().get_iter(2)
        self.assertEqual(column_combo.get_model().get_value(itr,0),"KEY3")

        #make sure filtering still works
        filter_combo = filter_row.get_children()[1].get_children()[0].get_children()[0]
        filter_combo.set_active(1)
        entry = filter_row.get_children()[1].get_children()[0].get_children()[1]
        entry.set_text("val5_1")
        self.assertEqual(len(grid.get_model()),4)


