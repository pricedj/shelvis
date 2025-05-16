# This file is part of SHELVIS.
#
# Copyright 2024 SHELVIS developers
#
# Use of this source code is governed by a BSD-style license 
# that can be found in the LICENSE.md file.

"""Slice plot widget
"""

from traitlets import HasTraits
import astropy.units

import shelvis.widgets.plot
from shelvis.vtk.filters import ImplicitCutter
from shelvis import internal


class SlicePlot(shelvis.widgets.plot.PlotWidget):
    """A widget for plotting values on a surface extracted from 3D data.
    
    Parameters
    ----------
    data : 
        The object containing the mesh and data
    surface:
        A widget providing the surface to extract and plot
    name: str
        Descriptive unique name for the plot
    variable: str
        The name of the variable in `data` to display on the surface
    unit : str or astropy.units.Unit, default: None
        The unit to use in the plot. If `None`, the same unit as in the data is used.
    """

    def __init__(self, data, surface, name, variable, unit=None):

        super().__init__(name=name)
        
        # Name of the variable to plot
        self._varname = variable

        # Unit of the data
        self._data_unit = astropy.units.Unit(data.unit(variable))

        # The unit of the plot
        self._unit = self._data_unit if unit is None else astropy.units.Unit(unit)
        
        # The coordinate frame of the plot
        self._coordinate_frame = data.coordinate_frame

        # Widget controlling the surface used to generate the slice
        self._widget = surface

        # Create the cutter
        self._cutter = ImplicitCutter(data, self._widget.surface)
            
    @property
    def variable(self):
        """Returns the name of the plotted variable
        """
        return self._varname

    @property
    def _scale(self):
        """Scaling constant from data length units to plot length units
        """
        return (internal.unit.length/self.unit_of_length).si.value

    def _set_menu_items(self):
        
        self._menu.children = [self._widget, self.cmap]
        self._menu.titles = ["Slice", "Colormap"]

    def _link_menu_items(self):

        HasTraits.observe(self._widget, self.update)
        self.update()
    
    def create_plot(self):
        
        self._cutter.update()
        poly_data = self._cutter.output

        return shelvis.renderers.plotly.polydata.PolyDataPlot.create_plot(poly_data, 
                                                                          name=self.variable,
                                                                          unit=self.unit, 
                                                                          scale=self._scale)
        
    def update(self, change=None):

        # Properties of the slicing surface have changed: update the cutter
        self._cutter.update()
         
        # Get the polygonal data
        poly_data = self._cutter.output

        # Update mesh plot data
        with self._plot.parent.batch_update():
            shelvis.renderers.plotly.polydata.PolyDataPlot.update(self._plot,
                                                                  poly_data, 
                                                                  name=self.variable,
                                                                  unit=self.unit, 
                                                                  scale=self._scale)