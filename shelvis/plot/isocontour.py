# This file is part of SHELVIS.
#
# Copyright 2024 SHELVIS developers
#
# Use of this source code is governed by a BSD-style license 
# that can be found in the LICENSE.md file.

"""Isocontour plot widget
"""

import astropy.units
from traitlets import HasTraits

from shelvis import internal
import shelvis.widgets.contour
import shelvis.widgets.plot
from shelvis.renderers.plotly.polydata import PolyDataPlot


class IsocontourPlot(shelvis.widgets.plot.PlotWidget):
    """A widget for plotting an isocontour of a scalar.
    
    Extracts the surface defined by the coordinates at which 
    a scalar field attains a given set value.

    Parameters
    ----------
    data : 
        The object containing the mesh and data
    surface:
        A widget providing the surface to extract and plot
    name: str
        Descriptive unique name for the plot
    variable: str
        The name of the scalar in `data` to use to extract the surface
    color: str, default: None
        Name of the scalar in `data` used to color the surface
    unit : str or astropy.units.Unit, default: None
        The unit to use in the plot. If `None`, the same unit as in the data is used.
    """

    def __init__(self, data, name, variable, value=None, unit=None, color=None):

        super().__init__(name=name)

        # This plot requires a reference to the data
        self._data = data

        # Name of the variable in the dataset that is contoured
        self._contour_varname = variable

        # Name of the variable in the dataset that is used to paint the contour
        self._paint_varname = color

        # The unit of the plot
        self._unit = self._data_unit if unit is None else astropy.units.Unit(unit)

        # Create the contour value selection widget
        self._widget = shelvis.widgets.contour.Contour(value=value, unit=self.unit)
        self._widget.contour.SetInputData(data)

    @property
    def variable(self):
        """Returns the name of the variable used to define the isocontour
        """
        return self._contour_varname

    @property
    def _scale(self):
        """Scaling constant from data length units to plot length units
        """
        return (internal.unit.length/self.unit_of_length).si.value

    def _set_menu_items(self):
        self._menu.children = [self._widget, self.cmap]
        self._menu.titles = ["Contour", "Colormap"]

    def _link_menu_items(self):

        HasTraits.observe(self._widget, self.update)
        self.update()
        
    def create_plot(self):

        # Ensure contouring variable is active
        self._data.GetPointData().SetActiveScalars(self._contour_varname)

        # Make sure widget is up to date
        self._widget.contour.Update()

        # Get the polydata of the contour surface
        poly_data = self._widget.contour.output

        # Ensure painting variable is active
        if self._paint_varname is not None:
            self._data.GetPointData().SetActiveScalars(self._paint_varname)

        # If no coloring variable has been provided, use the same variable
        # as for constructing the surface. 
        paint_var = self.variable if self._paint_varname is None else self._paint_varname
        
        return PolyDataPlot.create_plot(poly_data, 
                                        name=paint_var,
                                        unit=self.unit,
                                        scale=self._scale)
    
    def update(self, change=None):


        self._data.GetPointData().SetActiveScalars(self.variable)
        self._widget.contour.Update()
        
        poly_data = self._widget.contour.output

        # Ensure painting variable is active
        if self._paint_varname is not None:
            self._data.GetPointData().SetActiveScalars(self._paint_varname)

        paint_var = self.variable if self._paint_varname is None else self._paint_varname
        
        with self._plot.parent.batch_update():
            PolyDataPlot.update(self._plot, 
                                poly_data, 
                                name=paint_var,
                                unit=self.unit,
                                scale=self._scale)
      