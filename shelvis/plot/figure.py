# This file is part of SHELVIS.
#
# Copyright 2024 SHELVIS developers
#
# Use of this source code is governed by a BSD-style license 
# that can be found in the LICENSE.md file.

"""The visualization figure widget
"""

import plotly
import plotly.graph_objects
import ipywidgets
import astropy.units

import shelvis.widgets.plot


class Visualization(ipywidgets.VBox):
    """Main visualization widget

    Parameters
    ----------
    coordinate_frame : astropy.coordinates.BaseCoordinateFrame - derived type
        The coordinate frame of the plots in the figure
    unit_of_length : str or astropy.units.Unit
        The unit of length used in constructing the plot
    """
    
    def __init__(self, coordinate_frame, unit_of_length, theme="plotly_dark"):

        super().__init__()

        # Store figure options
        self._coordinate_frame = coordinate_frame
        self._unit_of_length = astropy.units.Unit(unit_of_length)

        # The main figure object
        self.fig = plotly.graph_objects.FigureWidget()

        if self.coordinate_frame is not None:
            title_text = "frame: {}  t: {}".format(self.coordinate_frame.name, 
                                                   self.coordinate_frame.obstime.strftime("%Y-%m-%d %H:%M:%S"))
                                                   
            self.fig.update_layout(title=dict(text=title_text, font=dict(size=12)));

        # Set default properties for the plot appearance
        self.fig.update_layout(
            template=theme,
            width=800, height=500,
            autosize=False, #True,
            margin=dict(t=30, b=5, l=5, r=50),
            scene=dict(xaxis=dict(range=(-5, 5)),
                       yaxis=dict(range=(-5, 5)),
                       zaxis=dict(range=(-5, 5)),
                       aspectmode="cube"));

        # The menu bar of figure widget
        self.menu = ipywidgets.Tab(
            layout=ipywidgets.Layout(
                margin='0px left')
                )
        
        # The UI window consists of the plot window and a menu
        self.children = [self.fig, self.menu]
        self.layout = ipywidgets.Layout()
        
        # Container of references to plot objects
        self.plots = dict()

    @property
    def coordinate_frame(self):
        return self._coordinate_frame
    
    @property
    def unit_of_length(self):
        return self._unit_of_length

    def add_widget(self, widget):
        """Add a plot widget to the figure

        Parameters
        ----------
        widget : shelvis.widgets.plot.PlotWidget
        """

        if widget.name in self.plots:
            raise Warning(f"Name '{widget.name}' already in used. Please change the plot name.")

        else:
            
            if widget.coordinate_frame is not None:
                if not widget.coordinate_frame.is_equivalent_frame(self.coordinate_frame):
                    raise ValueError("Coordinate frame in data not equivalent to the frame of the figure.")

            # Set the unit of length in the plot
            widget.unit_of_length = self.unit_of_length

            # Create the plot
            self.fig.add_trace(widget.create_plot())

            # Register the plot to the plot widget
            widget.plot = self.fig.data[-1]

            # Maintain a reference to the widget
            self.plots[widget.name] = widget
        
            # Update the menu
            self.menu.children = [plot.menu for plot in self.plots.values()]
            self.menu.titles = [key for key in self.plots.keys()]

    def add(self, plot):
        """Add a plot or plot widget to the figure
        """

        if not isinstance(plot, shelvis.widgets.plot.PlotWidget):
            # Assume the given data is a plotly trace, so add it to the figure
            self.fig.add_traces(plot)
        else:
            self.add_widget(plot)
