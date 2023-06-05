from typing import Any
from functools import partial
from tkinter import *
from tkinter import ttk
from os import path
import sys
from functools import partial

sys.path.append(path.dirname(path.dirname(__file__)))
from scrolled import Scrolled

sys.path.append(path.dirname(path.dirname(__file__)))


class DynamicTree(ttk.Treeview):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self._cget = dict()

        # ---------------------------------------------------------------
        # configuration and defaults
        # ---------------------------------------------------------------
        # this is a table of all the additional options available to
        # Dynamic tree and the methods used to set those options
        self.__config_specs = {
            'children': lambda selected: self.__default_callback('children', selected),
            'on_select': lambda selected: self.__default_callback('on_select', selected),
            'status_var': self.__define_status_variable,
            'right_click': lambda selected: self.__default_callback('right_click', selected),
        }

        # this is a table of all the additional options available to
        # Dynamic tree, and their default values
        self._defaults = {
            'children': None,
            'on_select': None,
            'status_var': StringVar(),
            'right_click': None,
        }

        # ---------------------------------------------------------------
        # configure & draw
        # ---------------------------------------------------------------
        to_configure = self._defaults.copy()
        to_configure.update(kwargs)
        self.__configure_save(**to_configure)

        # ---------------------------------------------------------------
        # setup bindings
        # ---------------------------------------------------------------
        self.bind('<<TreeviewOpen>>', self.open_branch)

    # ====================================================================================
    # run a callback routine
    # ====================================================================================
    def __run_callback(self, which_one, *args):
        callback: callable = self.cget(which_one)
        if callback:
            callback(*args)

    # ====================================================================================
    # define the StringVar for 'status_var'
    # ====================================================================================
    def __define_status_variable(self, variable: StringVar):
        self.__configure_save(status_var=variable)
        return self.cget("status_var")

    # ===================================================================
    # save the additional DynamicTree options in a list
    # ===================================================================
    def __configure_save(self, **kwargs):
        for k, v in kwargs.items():
            self._cget[k] = v

    # =================================================================================================
    # configure, cget, etc
    # =================================================================================================
    def cget(self, option: str) -> Any:
        if option in self._cget:
            return self._cget[option]
        else:
            return super().cget(option)

    def configure(self, **kwargs):
        for k, v in kwargs.items():
            if k in self._cget:
                self.__config_specs[k](v)
            else:
                super().configure(**{k: v})

    # =================================================================================================
    # sub open_branch -> callback for tree
    # -> dynamically updates the next level of grandchildren, using
    #    callback routine defined by '-children'
    # =================================================================================================
    def open_branch(self, event):
        item = self.focus()

'''

# ----------------------------------------------------------------------
# sub openbranch -> callback for tree
# -> dynamically updates the next level of grandchildren, using
#    callback routine defined by '-children'
# ----------------------------------------------------------------------
sub OpenCmd {
    
    # only continue on if callback is defined
    return unless $self->cget(-children);

    # get_by_id a list of children of this branch (should this be leaf instead of child?)
    my @children = $self->infoChildren($path);

    # loop through all the children
    my $i = 0;
    my $sep = $self->cget(-separator);
    foreach my $child (@children) {
        my @grandkids;
        

        # update status variable
        (my $node) = $child =~ /^.*?([^\Q$sep\E]*)$/;
        if (length($child) < 30) {
            $$status_ptr = "Scanning node $child";
        }
        else {
            $$status_ptr = "Scanning node ... ".substr($child,-30);
        }
        $i++;
        $$percent_ptr = ($i/@children)*100;
        $mw->update() if $mw;

        # have grandchildren already been defined?
        next if $self->infoChildren($child);

        # define grandchildren for this child
        ($node) = $child =~ /([^\Q$sep\E]*)$/;
        @grandkids = $self->Callback(-children=>$self,$child);

        # avoid infinite loop
        if ($child =~ /\Q$sep$node$sep\E/) {
            @grandkids = (['<etc>',{-state=>'disabled'}]);
        }


        foreach my $kid (@grandkids) {
            my $newkid;
            my %kidhash;
            $newkid = $kid;
            if (ref $kid eq 'ARRAY') {
                $newkid = $kid->[0];
                if (ref $kid->[1] eq 'HASH') {
                    %kidhash = %{$kid->[1]};
                }
            }
            $self->add ("$child$sep$newkid",-text=>$newkid, %kidhash)
                    unless $self->infoExists("$child$sep$newkid");
            $self->hide('entry', "$child$sep$newkid");
        }


    }

    # done, update status variable and progress bar
    $self->autosetmode;
    $$status_ptr = "Done";
    $$percent_ptr = 0;
}



sub selectionSet {
    my $self = shift;
    my $input = shift;
    return unless $self->infoExists($input);
    $self->SUPER::selectionSet($input);
    $self->Callback(-onSelect=>$self,$input);
}

# ======================================================================
# Expand Tree given a specific node to start from
# ======================================================================
{ my $goforit;
  my $treetext;
    sub ExpandTree {
        my $self     = shift;
        my $maxdepth = shift;
        my $keeptext = shift || 0;
        $treetext = '';

        my $selection = $self->selectionGet;
        my $select; $select = (ref $selection) ? $selection->[0] : $selection;
        return unless $select;

        $goforit = 1;
        return recursive_expand($self,$select,$maxdepth,$keeptext);
    }

    sub TreeText {
        return ExpandTree(@_,1);
    }

    sub recursive_expand {
        my $self = shift;
        my $path = shift;
        my $maxdepth = shift || 0;
        my $keeptext = shift || 0;
        my $curdepth = shift || 0;

        if ($self->getmode($path) ne 'none') {
            $self->open($path);
        }

        # bail out if curdepth exceeds max
        return if $maxdepth && $curdepth > $maxdepth;

        # keep text
        if ($keeptext) {
            my $sep = $self->cget(-separator);
            (my $ele = $path) =~ s/.*?([^$sep]*)$/$1/;
            $treetext = $treetext . "\n" . "  "x$curdepth . $ele;
        }

        # procreate
        $curdepth++;
        foreach my $child ($self->infoChildren($path)) {
            recursive_expand ($self,$child,
                              $maxdepth,$keeptext,$curdepth) if $goforit;
        }
        return $treetext;
    }

    sub CancelExpandTree {
        my $self = shift;
        $goforit = 0;
    }
}

# ======================================================================
# Collapse Tree given a specific node to start from
# ======================================================================
sub CollapseTree {
    my $self = shift;
    my $selection = $self->selectionGet;
    my $select; $select = (ref $selection) ? $selection->[0] : $selection;
    return unless $select;
    recursive_collapse($self,$select);
}
sub recursive_collapse {
    my $self = shift;
    my $path = shift;
    $self->close($path);
    foreach my $child($self->infoChildren($path)) {
        recursive_collapse($self,$child);
    }
}
1;
'''
