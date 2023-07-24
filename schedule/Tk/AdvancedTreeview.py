from __future__ import annotations
from tkinter import *
from tkinter import ttk
from typing import *


class AdvancedTreeview(ttk.Treeview):
    """
    A subclass of ttk.TreeView object that will keep track of which object belongs with
    which Treeview item.

    see: https://docs.python.org/3/library/tkinter.ttk.html#treeview
    """

    def __init__(self, root: Frame, **kwargs):
        self._item_to_obj_dict = dict()
        super().__init__(root, **kwargs)

    def open_branch(self, tree_id: str):
        """Opens all the leafs in this branch"""
        self.item(tree_id, open=True)
        for leaf in self.get_children(tree_id):
            self.open_branch(leaf)

    #
    def insert(self, parent_iid: str,
               any_object: Optional[Any],
               *,
               index: int | Literal['end'] = 'end', iid: str = None,
               **options) -> str:
        """
        override the ttk.treeview.insert command, adding 'any_object' as a new parameter

        Creates a new item and return the item identifier of the newly created item.

        see: https://docs.python.org/3/library/tkinter.ttk.html#treeview

        """

        iid = super().insert(parent_iid, index, iid, **options)
        self._item_to_obj_dict[iid] = any_object
        return iid

    def insert_sorted(self, parent_iid: str, any_object: Optional[Any], **options):
        """
        If the child objects support sorting, and if all siblings are of the
        same resource_type, then insert in sorted order, else put at end of siblings

        For allowed options, see: https://docs.python.org/3/library/tkinter.ttk.html#treeview
        """

        siblings = self.get_children(parent_iid)

        # are we sortable?
        sortable = True
        obj_type = None

        for kid_iid in siblings:
            if not sortable:
                break
            obj = self._item_to_obj_dict[kid_iid]
            if obj_type is None:
                sortable = hasattr(obj, "__lt__")
                obj_type = type(obj)
            else:
                sortable = obj_type == type(obj)

        # find index where to insert
        # NOTE: Assumes that 'get_children' returns items in row order
        options['index'] = 'end'
        if sortable:
            for index, kid_iid in enumerate(siblings):
                if any_object < self._item_to_obj_dict[kid_iid]:
                    options['index'] = index
                    break

        # insert
        return self.insert(parent_iid, any_object=any_object, **options)

    def get_obj_from_id(self, iid: str) -> Optional[Any]:
        """Gets and returns the object associated with the tree item, unless 'iid' is
        not valid, in which case it returns None"""
        if iid in self._item_to_obj_dict.keys():
            return self._item_to_obj_dict[iid]
        else:
            return None

    def delete(self, *item_iids):
        """Delete all specified items and all their descendants. The root item may not be deleted."""

        # remove item, and all its descendants from the dictionary of objects
        for iid in item_iids:
            if self.exists(iid):
                self._prune(iid)
                super().delete(iid)

    def expand_whole_branch(self, tree_id: str):
        """Opens all the twigs in this branch"""
        self.item(tree_id, open=True)
        for twig in self.get_children(tree_id):
            self.expand_whole_branch(twig)


    def _prune(self, iid: str):
        """Not only remove the tree branch, but remove the data from tree_objects as well"""
        if self.exists(iid):

            for twig in self.get_children(iid):
                self._prune(twig)
            self._item_to_obj_dict.pop(iid, None)


"""
# =================================================================
# footer
# =================================================================

=head1 AUTHOR

Sandy Bultena

=head1 COPYRIGHT

Copyright (c) 2023 Sandy Bultena 

All Rights Reserved.

This module is free software. It may be used, redistributed
and/or modified under the terms of the Perl Artistic License

     (see http://www.perl.com/perl/misc/Artistic.html)

=cut

1;
"""
