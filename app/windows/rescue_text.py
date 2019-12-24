#!/usr/bin/env python3
# encoding: utf-8

import gi
import sqlite3

from database.queries import SQL_Rescue

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

class Rescue_Text(Gtk.Window):
    
    
    def __init__(self):
        Gtk.Window.__init__(self, title="Area de transferencia")
        self.set_border_width(15)

        # all tags typed
        self.tags = set()

        self.current_filter_topic = None
        
        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(True)
        self.add(self.grid)

        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        self.conn = sqlite3.connect('clipboard.db')
        self.conn.text_factory = str
        self.cursor = self.conn.cursor()

        self.clipboard_liststore = Gtk.ListStore(str, str, str)

        self.topic_filter = self.clipboard_liststore.filter_new()
        self.topic_filter.set_visible_func(self.topic_filter_func)

        self.treeview = Gtk.TreeView.new_with_model(self.topic_filter)
        for i, column_title in enumerate(
            ["Text", "Created At", "Tags"]
        ):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.treeview.append_column(column)

        self.select = self.treeview.get_selection()
        self.select.connect("changed", self.on_tree_selection_changed)

        self.botton_view = Gtk.Grid()
        self.botton_view.set_column_homogeneous(True)
        self.botton_view.set_row_homogeneous(True)

        # text that explains what should be done
        self.label = Gtk.Label("Digite as TAGS ")
        self.botton_view.attach(self.label, 0, 0, 1, 1)

        self.entry = Gtk.Entry()
        self.entry.connect('key-press-event', self.on_key_press)
        self.botton_view.attach(self.entry, 1, 0, 4, 1)

        # setting up the layout, putting the treeview in a scrollwindow, and the box in a row
        self.scrollable_treelist = Gtk.ScrolledWindow()
        self.scrollable_treelist.set_vexpand(True)
        self.grid.attach(self.scrollable_treelist, 0, 0, 1, 5)
        self.grid.attach_next_to(
            self.botton_view, self.scrollable_treelist, Gtk.PositionType.BOTTOM, 1, 1 
        )

        self.scrollable_treelist.add(self.treeview)

        self.show_all()

    def on_tree_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter is not None:
             self.clipboard.set_text("".join(model[treeiter][0].split("\n")), -1)

    def topic_filter_func(self, model, iter, data):
        if (
            self.current_filter_topic is None
            or self.current_filter_topic == "None"
        ):
            return True
        else:
            return model[iter][2] == self.current_filter_topic

    def on_key_press(self, widget, ev):
        
        # if you type comma
        if ev.keyval == 44:
            # get the last tag typed. Do union operation
            tag = self._return_last_tag_typed()
            
            # indentify all texts that identify this tag
            list_of_tuple_of_text_table = self._return_list_of_text_tuple(tag)

            # if don't have texts matching the tag passed
            if list_of_tuple_of_text_table is None:
                return

            # if the liststore is empty
            self._update_if_liststore_is_empty(list_of_tuple_of_text_table)

            # if the liststore is not empty
            self._update_liststore(list_of_tuple_of_text_table)

        # if you type backspace or delete
        elif ev.keyval == 65288 or ev.keyval == 65535:
            # delete last tag
            self._delete_last_tag()
            
            # update the set of tags with the new tags in entry. Do intersection operation
            self._compare_input_tags_with_registered_tags()

            # for each tag in set of tags, execute the function to return texts match
            # and update liststore with these texts tuple
            def send_to_update(tag):
                list_of_tuple_of_text_table = self._return_list_of_text_tuple(tag)
                if not list_of_tuple_of_text_table is None:
                    self._update_liststore(list_of_tuple_of_text_table)

            map(send_to_update, list(self.tags))
        
        # if type you type enter this window is destroyed
        elif ev.keyval == 65421:
            self.destroy()
            
    def _delete_last_tag(self):
        new_entry = ''
        this_entry = list(map(lambda tag: tag.lstrip(' ').rstrip(' '), self.entry.get_text().split(',')))
        if len(this_entry[-1]) == 0:
            this_entry.pop()
        if len(this_entry) > 0:
            this_entry.pop()
        for i in range(len(this_entry)):
            new_entry += this_entry[i] + ', '
        self.entry.set_text(new_entry)
        self.entry.set_position(len(new_entry))
        
    def _is_a_valid_tag(self, tag):
        if len(SQL_Rescue.SQL_TAG_QUERY(self.cursor, tag)) == 0:
            return False
        return True

    def _compare_input_tags_with_registered_tags(self):
        different_values = self.tags - set(map(lambda tag: tag.lstrip(' ').rstrip(' '), self.entry.get_text().split(',')))
        excluded_value = []
        for tag in list(different_values):
            if self._is_a_valid_tag(tag):
                excluded_value.append(tag)
        for tag in excluded_value:
            self.tags.discard(tag)
        for p in range(len(self.clipboard_liststore)):
            try:
                row_tags = list(map(
                    lambda tag: tag.lstrip(' ').rstrip(' '),
                    self.clipboard_liststore.get(self.clipboard_liststore.get_iter(p), 2)[0].split(','))
                )
            except ValueError as ve:
                print(ve)
            for tag in excluded_value:
                for i in range(len(row_tags)):
                    if tag == row_tags[i]:
                        row_tags.pop(i)
                        break
                self.clipboard_liststore[p][2] = ', '.join(row_tags)
                        
                # delete tuple
                if len(self.clipboard_liststore[p][2]) == 0:
                    iter =  self.clipboard_liststore.get_iter(p)
                    self.clipboard_liststore.remove(iter)
                    self.clipboard_liststore.unref_node(iter)
            
    def _return_last_tag_typed(self):
        # separate words of entry with comma, ignoring spaces
        _tags = self.entry.get_text().split(',')
        _tags = map(lambda tag: tag.lstrip(' ').rstrip(' '), _tags)
        # get last tag typed
        tag = list(set(_tags).difference(self.tags))[0]
        # adding tag to tag set
        if self._is_a_valid_tag(tag):
            self.tags.add(tag)
        return tag
    
    def _return_list_of_text_tuple(self, tag):
        tuple_of_text_ids = SQL_Rescue.SQL_TAG_QUERY(self.cursor, tag)
        
        # managed to get more than one ids match
        if len(tuple_of_text_ids) > 0:
            # get all lines matching the passed tag
            return SQL_Rescue.SQL_TEXT_QUERY(self.cursor, tuple_of_text_ids, tag)
        else:
            return None

    def _update_liststore(self, list_of_tuple_of_text_table):
        # get all text in liststore
        texts_liststore = list(map(lambda reg: reg[0].replace('\n', ''), self.clipboard_liststore))
        # get all text in param
        texts_from_list_of_tuple_of_text_table = list(map(lambda reg: reg[0], list_of_tuple_of_text_table))
        # get all occurrences that are not contained in liststore
        text_not_in_liststore = list(set(texts_from_list_of_tuple_of_text_table) - set(texts_liststore))
        # append tuple in liststore if not repeated
        for text_tuple in list_of_tuple_of_text_table:
            if text_tuple[0] in text_not_in_liststore:
                text_formatted = text_tuple[0].split(' ')
                count = 1
                for i in range(len(text_formatted)):
                    if count % 3 == 0:
                        text_formatted[i] += '\n'
                        count = 0
                    count += 1
                self.clipboard_liststore.append((' '.join(text_formatted), text_tuple[1], text_tuple[2]))
            else:
                # search the position of current text in liststore
                text_index = texts_liststore.index(text_tuple[0])
                tags_of_this_text = list(map(lambda tag: tag.lstrip(' ').rstrip(' '), self.clipboard_liststore[text_index][2].split(',')))
                self.clipboard_liststore[text_index][2] = ', '.join(list(set(tags_of_this_text).union(list(map(lambda tag: tag.lstrip(' ').rstrip(' '), text_tuple[2].split(','))))))
                
                # classifier
                p = text_index
                sentinel_len = None
                sentinel_tuple = None
                piter = self.clipboard_liststore.get_iter(text_index)
                if text_index % 2 == 0:
                    while not piter is None:
                        len_tags = len(self.clipboard_liststore[piter][2].split(','))
                        if not sentinel_len is None and len_tags < sentinel_len:
                            sentinel_tuple = self.clipboard_liststore.get(
                                self.clipboard_liststore.iter_next(piter),
                                0, 1, 2
                            )
                            self.clipboard_liststore.set_row(
                                self.clipboard_liststore.iter_next(piter),
                                self.clipboard_liststore.get(piter, 0, 1, 2)
                            )
                            self.clipboard_liststore.set_row(piter, sentinel_tuple)
                        if p % 2 == 0:
                            sentinel_len = len_tags
                        if not self.clipboard_liststore.iter_previous(piter) is None:
                            piter = self.clipboard_liststore.iter_previous(piter)
                        else:
                            self.clipboard_liststore.unref_node(piter)
                            piter = None
                        p -= 1
                else:
                    while not piter is None:
                        len_tags = len(self.clipboard_liststore[p][2].split(','))
                        if not sentinel_len is None and len_tags < sentinel_len:
                            sentinel_tuple = self.clipboard_liststore.get(
                                    self.clipboard_liststore.iter_next(piter),
                                    0, 1, 2
                            )
                            self.clipboard_liststore.set_row(
                                    self.clipboard_liststore.iter_next(piter),
                                    self.clipboard_liststore.get(piter, 0, 1, 2)
                            )
                            self.clipboard_liststore.set_row(piter, sentinel_tuple)
                            
                            self.clipboard_liststore[p] = sentinel_tuple
                        if p % 2 != 0:
                            sentinel_len = len_tags
                        if not self.clipboard_liststore.iter_previous(piter) is None:
                            piter = self.clipboard_liststore.iter_previous(piter)
                        else:
                            self.clipboard_liststore.unref_node(piter)
                            piter = None
                        p -= 1
    
    def _update_if_liststore_is_empty(self, list_of_tuple_of_text_table):
        if len(self.clipboard_liststore) != 0:
            return
        
        # for each line of text found adds to the liststore
        for tuple_of_text_table in list_of_tuple_of_text_table:
            liststore_row_to_add = [tuple_of_text_table[0], tuple_of_text_table[1], tuple_of_text_table[2]]
            words_list = liststore_row_to_add[0].split(" ")
            count = 1
            for i in range(len(words_list)):
                if count % 3 == 0:
                    words_list[i] += '\n'
                    count = 0
                count += 1
            words_list = " ".join(words_list)
            self.clipboard_liststore.append((words_list, tuple_of_text_table[1], tuple_of_text_table[2]))


def rescue_text():
    
    win = Rescue_Text()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

rescue_text()
