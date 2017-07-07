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

"""Tests for the AsyncTaskProgressBox"""

from testtools import TestCase
from quickly.widgets.asynch_task_progressbox import AsynchTaskProgressBox

class TestAsynchTaskProgessBox(TestCase):
    """Test the CouchGrid functionality"""

    def setUp(self):
        TestCase.setUp(self)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_constructions(self):
        """Test a simple creating An AsynchTaskProgressBox """
        box = AsynchTaskProgressBox(self.asynch_function)
        self.assertEqual((box != None), True)

    #A function to run asynchronously
    def asynch_function( self, params ):
        #pull values from the params that were set above
        for x in range(params["start"],params["stop"]):
        #check if to see if the user has told the task to stop
            if params["kill"] == True:
                #return a string if the user stopped the task
                return "stopped at " + str(x)
            else:
                #if the user did not try to stop the task, go ahead and do something
                print x
                #this is a processor intensive task, so
            #sleep the loop to keep the UI from bogging down
            time.sleep(.5)
        #if the loop completes, return a string
        return "counted all"

