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

import gtk
import gobject
from grid_column import StringColumn, CurrencyColumn, CheckColumn
from grid_column import IntegerColumn, TagsColumn, DateColumn

def get_column(key, index, dictionary_index, editable):
    if key.lower() == "id":
        return IntegerColumn(key, index, dictionary_index, editable)
    elif key.endswith("?"):
        return CheckColumn(key, index, dictionary_index, editable)
    elif key.lower().endswith(" price") or key.lower() == "price":
        return CurrencyColumn(key, index, dictionary_index, editable)
    elif key.lower() == "tags":
        return TagsColumn(key, index, dictionary_index, editable)
    elif key.lower().endswith(" count") or key.lower() == "count":
        return IntegerColumn(key, index, dictionary_index, editable)
    elif key.lower().endswith(" date") or key.lower() == "date":
        return DateColumn(key, index, dictionary_index, editable)

    else:
        return StringColumn(key, index, dictionary_index, editable)




