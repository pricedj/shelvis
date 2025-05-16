# This file is part of SHELVIS.
#
# Copyright 2024 SHELVIS developers
#
# Use of this source code is governed by a BSD-style license 
# that can be found in the LICENSE.md file.

"""Widget for setting colormap and scale properties
"""

import numpy as np
import ipywidgets
from shelvis.widgets.slider import FloatRangeSliderWithUnit

class ColormapUIWidgets:

    @staticmethod
    def colorscale_dropdown():
        """Create a dropdown for selecting the color scale
        """

        # The supported colormaps are given in 
        import plotly
        named_colormaps = sorted(plotly.colors.named_colorscales())

        return ipywidgets.Dropdown(
            options=named_colormaps,
            value='rdbu',
            description='Color map',
            layout=ipywidgets.Layout(width='250px')
        )

    @staticmethod
    def checkbox(description, width, **kwargs):
        """Create a checkbox
        """
        return ipywidgets.Checkbox(
                description=description, 
                indent=False, 
                layout=ipywidgets.Layout(width=width),
                **kwargs)

    @staticmethod
    def value_range_slider(unit):
        """Create a float range slider with units for setting the value range
        """
        return FloatRangeSliderWithUnit(
                description='Range',
                layout=ipywidgets.Layout(width='450px'), #margin='0px 0px 0px -10px'),
                unit=unit)
        
    @staticmethod
    def opacity_slider():
        """Create a slider for setting the plot opacity
        """
        return ipywidgets.FloatSlider(
            value=1.0,
            min=0.0,
            max=1.0,
            step=0.01,
            description='Opacity',
            layout=ipywidgets.Layout(width='393px')
        )
    
    @staticmethod
    def button(description):
        """Create a clickable button
        """
        return ipywidgets.Button(description=description, 
                                 layout=ipywidgets.Layout(width='75px'))


class ColormapWidget(ipywidgets.GridBox):

    def __init__(self, plot=None, unit=None):

        super().__init__()

        # If all information provided to constructor, initialize immediately
        if (plot is not None) and (unit is not None):
            self.initialize(plot, unit)

    def _create_ui_widgets(self, unit):
        """Create the widgets comprising the UI
        """
        
        # Create the dropdown selection
        self.colorscale = ColormapUIWidgets.colorscale_dropdown()
        
        # Create checkboxes        
        self.reverse = ColormapUIWidgets.checkbox(description='Reverse', width='125px')
        self.visible = ColormapUIWidgets.checkbox(description='Visible', width='125px', value=True)

        #self.dynamic = ColormapUIWidgets.checkbox(description='Dynamic', width='125px')        
        self.logarithmic = ColormapUIWidgets.checkbox(description='Log', width='80px')
        self.range_50percent = ColormapUIWidgets.button(description="50 %")

        # Create the sliders
        self.range = ColormapUIWidgets.value_range_slider(unit)
        self.opacity = ColormapUIWidgets.opacity_slider()

        # Group checkboxes
        checkboxes = ipywidgets.HBox(
            children=[self.reverse, self.visible],
            layout=ipywidgets.Layout(
                margin='0px 0px 0px 20px')
            )

        # Construct the widget
        self.children = [self.colorscale, 
                         ipywidgets.HBox(children=[self.range, self.range_50percent], 
                                         layout=ipywidgets.Layout(#margin='0px 0px 0px 0px', 
                                                                  width='650px')), 
                         checkboxes, self.opacity]
        
        self.layout = ipywidgets.Layout(
            grid_template_columns="250px 350px",
            grid_gap="10px 10px")

    def _update_colorscale(self, change):

        new_cmap = change["new"]
        
        if self.reverse.value == True:
            new_cmap += "_r"

        self._plot.colorscale = new_cmap

    def _update_range(self, change):

        # The new value
        value = change["new"].value

        with self._plot.parent.batch_update():
            
            self._plot.cmin = np.min(value)
            self._plot.cmax = np.max(value)
            
    def _update_reverse(self, change):
        
        # Get the value of the checkbox
        is_checked = change["new"]

        if is_checked:
            self._plot.colorscale = self.colorscale.value + "_r" 
        else:
            self._plot.colorscale = self.colorscale.value

    def _update_visible(self, change):
        
        # Get the value of the checkbox
        is_checked = change["new"]

        if is_checked:
            self._plot.showscale = True
        else:
            self._plot.showscale = False
            
    def _update_opacity(self, change):
        self._plot.opacity = change["new"]
    
    def _update_range50percent(self, b):
        self._set_default_range()

    def _set_default_range(self, fraction=0.5):
        
        # Min and max of current plot
        if self._plot.intensity is not None:
            _min = self._plot.intensity.min()
            _max = self._plot.intensity.max()
        else:
            _min = self._plot.cmin
            _max = self._plot.cmax

        _mid = 0.5*(_min + _max)
        _dis = fraction*np.abs(_max - _min)
        
        if np.isclose(_min, 0.0) and np.isclose(_max, 0.0):
            _min, _max, _dis = -0.5, 0.5, 1.0

        # Set reasonable defaults
        with self._plot.parent.batch_update():
            with self.range.slider.hold_sync():
                self.range.min = _min
                self.range.max = _max
                self.range.value = (_mid - 0.5*_dis, _mid + 0.5*_dis)*self.range.unit

    def _set_defaults(self):
        """Set default values
        """
        self._plot.colorscale = self.colorscale.value

        self._set_default_range()

    def _set_widget_observers(self, plot):
        """Set observer callbacks to the widgets
        """
        
        # Store a reference to the plot
        self._plot = plot

        # Initialize with default values
        self._set_defaults()

        # Attach the update functions
        self.colorscale.observe(self._update_colorscale, names="value")

        # Attach value range
        self.range.observe(self._update_range, names="value")

        # Attach reverse checkbox
        self.reverse.observe(self._update_reverse, names="value")

        # Attach visible checkbox
        self.visible.observe(self._update_visible, names="value")

        # Attach opacity slider
        self.opacity.observe(self._update_opacity, names="value")

        self.range_50percent.on_click(self._update_range50percent)

    def initialize(self, plot, unit):
        """Initialize the colormap widget
        """
        self._create_ui_widgets(unit)
        self._set_widget_observers(plot)

    @property
    def value(self):
        return self.range.value
    
    @property
    def min(self):
        return self.range.min


