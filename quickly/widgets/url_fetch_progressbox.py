### BEGIN LICENSE
# Copyright (C) 2010 Stuart Langridge stuart.langridge@canonical.com
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
    import gtk, gobject, gio
    import gettext
    from gettext import gettext as _
    gettext.textdomain('quickly-widgets')

except:
    print "couldn't load dependencies"


class UrlFetchProgressBox(gtk.HBox):
    """UrlFetchProgressBox: encapsulates a pulsating progressbar, a cancel
    button, and a URL that needs fetching. Use a UrlFetchProgressBox when you 
    need to fetch a URL; the box will show while the URL is being fetched 
    without blocking the UI for the user.
    By default, the box will automatically destroy itself once the URL is
    fetched; suppress this by passing destroy_after_fetching=False.
    Fires a "downloaded" signal once download is complete, passing the contents
    of the URL.
    Cancelling fires the "downloaded" signal with a value of None.
    """

    __gsignals__ = {
        'downloaded' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, 
            (gobject.TYPE_PYOBJECT,))
    }

    def __init__(self, url, destroy_after_fetching=True, cancelable=True):
        """Create an UrlFetchProgressBox

        Keyword arguments:
        url -- the URL to fetch
        destroy_after_fetching -- should this widget destroy itself once the URL
          is fetched? Defaults to True.
        cancelable -- whether to show cancel button. Defaults to True.
        """
        gtk.HBox.__init__( self, False, 2)
        self.progressbar = gtk.ProgressBar()
        gobject.timeout_add(100, self.__tick)
        parts = [x for x in url.split("/") if x]
        self.progressbar.set_text(_("Downloading %s") % parts[-1])
        self.running = True
        self.progressbar.show()
        self.pack_start(self.progressbar, True)
        self.destroy_after_fetching = destroy_after_fetching
        self.cancel_button = gtk.Button(stock=gtk.STOCK_CANCEL)
        if cancelable:
            self.cancel_button.show()
        self.cancel_button.set_sensitive(False)
        self.cancel_button.connect("clicked",self.__cancel)
        self.pack_end(self.cancel_button, False)
        self.cancel_button.set_sensitive(True)
        self.__canceller = gio.Cancellable()
        self.stream = gio.File(url)
        self.stream.load_contents_async(self.__download_finished, cancellable=self.__canceller)
    
    def __tick(self):
        self.progressbar.pulse()
        return self.running
    
    def __download_finished(self, gdaemonfile, result):
        try:
            content = self.stream.load_contents_finish(result)[0]
        except gio.Error, e:
            if e.code == 19:
                # user cancelled
                self.emit("downloaded", None)
        else:
            self.emit("downloaded", content)
        self.__maybe_destroy()
    
    def __cancel(self, btn):
        self.__canceller.cancel()
        self.__maybe_destroy()
    
    def __maybe_destroy(self):
        self.running = False
        if self.destroy_after_fetching: self.destroy()

class TestWindow(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.set_title("UrlFetchProgressBox test")
        self.vbox = gtk.VBox()
        btn = gtk.Button(stock=gtk.STOCK_EXECUTE)
        btn.connect("clicked", self.start_download)
        self.vbox.pack_end(btn)
        self.add(self.vbox)
        self.set_size_request(300,200)
        self.connect("destroy", gtk.main_quit)
    
    def start_download(self, btn):
        prog = UrlFetchProgressBox("http://www.ubuntu.com/desktop/get-ubuntu/download")
        prog.connect("downloaded", self.downloaded)
        self.vbox.pack_start(prog, expand=False)
        prog.show()
    
    def downloaded(self, widget, content):
        print "downloaded %s bytes of content" % len(content)

if __name__ == "__main__":
    w = TestWindow()
    w.show_all()
    gtk.main()

