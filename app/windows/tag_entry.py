# encoding: utf-8

import gi
import sqlite3
import time
import datetime

from windows.database.queries import SQL_Entry

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

class Tag_Entry(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Area de transferencia")

        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        self.text = self.clipboard.wait_for_text()

        self.conn = sqlite3.connect('clipboard.db')
        self.conn.text_factory = str
        self.cursor = self.conn.cursor()

        self.box = Gtk.Box(spacing=6)
        self.add(self.box)

        self.label = Gtk.Label("Digite quantas tags achar necessario, separadas por virgula. Depois, tecle ENTER: ")
        self.box.pack_start(self.label, True, True, 0)

        self.entry = Gtk.Entry()
        self.entry.connect('key-press-event', self.on_key_press)
        self.box.pack_start(self.entry, True, True, 0)

    def on_key_press(self, widget, ev):
        if ev.keyval == 65421:
            try:
                SQL_Entry.SQL_TEXT_CREATE(self.cursor)
                SQL_Entry.SQL_TAG_CREATE(self.cursor)
                SQL_Entry.SQL_TAG_INSERT(
                    self.cursor,
                    SQL_Entry.SQL_TEXT_INSERT(self.cursor, self.clipboard.wait_for_text()), 
                    self.entry.get_text()
                )
            except sqlite3.Error as err:
                print(err.args[0])
            finally:
                self.conn.commit()
                self.destroy()

def tag_entry():
    win = Tag_Entry()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
