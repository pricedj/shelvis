# This file is part of SHELVIS.
#
# Copyright 2024 SHELVIS developers
#
# Use of this source code is governed by a BSD-style license 
# that can be found in the LICENSE.md file.

"""Plot widget 
"""

import ipywidgets
import astropy.units as u

from shelvis.widgets.colormap import ColormapWidget


class PlotWidget(ipywidgets.HBox):
    """A plot widget is a custom widget consisting of a plotting window 
    and a widget for interactively controlling properties of the plot.

    Parameters
    ----------
    name : str
        A unique string describing the plot. The name appears in the menu, 
        and is used to distinguish plots. 
    """
    
    def __init__(self, name):

        super().__init__()

        # The rendered plot
        self._plot = None

        # The colorbar of the plot
        self._cmap = None

        # The unit of the plot
        self._unit = None

        # The unit of length in the plot
        # By default, si is used
        self._unit_of_length = u.m

        # The coordinate frame of the plot
        self._coordinate_frame = None

        # Name of the plot that identifies it
        self._name = name

        # The menu widget
        self._menu = ipywidgets.Tab(
            layout=ipywidgets.Layout(
                margin='0px 0px 0px -15px', padding='0px'))

    def _set_menu_items(self):
        pass

    def _link_menu_items(self):
        pass
    
    @property
    def plot(self):
        return self._plot

    @plot.setter
    def plot(self, _plot):
        """Links the given plot with this widget
        """        
        
        # Set the plot
        self._plot = _plot

        # Create the colorbar
        self._cmap = ColormapWidget(
            plot=self._plot,
            unit=self._unit
        )

        # Create the menu items and link them
        self._set_menu_items()
        self._link_menu_items()
        
    @property
    def menu(self):
        return self._menu

    @property
    def cmap(self):
        return self._cmap

    @property
    def name(self):
        return self._name
    
    @property
    def unit(self):
        return self._unit
    
    @property
    def unit_of_length(self):
        return self._unit_of_length

    @unit_of_length.setter
    def unit_of_length(self, value):
        self._unit_of_length = u.Unit(value)

    @property
    def coordinate_frame(self):
        return self._coordinate_frame