# quickly-widgets
A library of PyGtk widget to dramatically simplify PyGtk app development. The code is from 2010, so is unlikely to work unmodified, but should be useful to someone developing with PyGtk today.

This code base was used to simplify and accelerate application development on many applications for the Ubuntu Desktop around 2010 - 2013, before we started working on Ubuntu Touch.

The overriding ethos of the quickly project was to make programming apps "easy and fun." Therefore, each widget was designed to always do something useful with just a line or two of code. Documentation was included with each widget that showed how to use the widget, how to customize the widget, and how to extend the widget. 

For example, creating a treeview in Gtk, instead of involving multiple objects and likely dozens of lines of code, becomes simply:

```
#create a dictionary if you don't already have one
dicts = [{"test?":True,"price":100,"foo count":100,"Key4":"1004"},
    {"test?":True,"price":100,"foo count":100,"Key4":"1004"},
    {"test?":True,"price":100,"foo count":100,"Key4":"1004"}]
#create the DictionaryGrid
dg = DictionaryGrid(dictionaries=dicts)
```
The code base includes prompts, grids, media widgets, a downloader widget, and others.
