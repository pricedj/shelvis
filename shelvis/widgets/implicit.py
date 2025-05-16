# This file is part of SHELVIS.
#
# Copyright 2024 SHELVIS developers
#
# Use of this source code is governed by a BSD-style license 
# that can be found in the LICENSE.md file.

"""Widgets for handling various implicit functions
"""

import numpy as np
import astropy.units as u
import ipywidgets
import traitlets

from vtkmodules.vtkCommonDataModel import vtkSphere
from vtkmodules.vtkCommonDataModel import vtkPlane

from shelvis import internal
from shelvis.widgets.slider import FloatSliderWithUnit


class Sphere(FloatSliderWithUnit):
    """Widget for managing a VTK sphere
    """
    
    def __init__(self, radius=1.0, unit=u.m, **kwargs):
        
        super().__init__(description="Radius:", value=radius, unit=unit, **kwargs)

        # Set the implicit surface
        self.surface = vtkSphere(radius=(radius*unit).to(internal.unit.length).value)

    @traitlets.observe('value')
    def _on_radius_change(self, change):
        """Updates the slicer radius
        """
        if hasattr(self, 'surface'):

            new_radius = change['new'].to(internal.unit.length).value
        
            self.surface.radius = new_radius


class Plane(ipywidgets.VBox, traitlets.HasTraits):
    """
    Widget for managing a VTK plane using spherical angles (theta, phi).

    Parameters
    ----------
    theta, phi : float
        Initial values for the polar and azimuthal angles (in degrees).
    """
    normal = traitlets.Tuple(trait=float)

    def __init__(self, lat=0.0, lon=0.0, **kwargs):
        super().__init__()

        # Use FloatSliderWithUnit for angle sliders
        self.lat_slider = FloatSliderWithUnit(
            description="Lat:", value=lat, unit=u.deg, min=-90.0, max=90.0, step=1.0, **kwargs
        )
        self.lon_slider = FloatSliderWithUnit(
            description="Lon:", value=lon, unit=u.deg, min=0.0, max=360.0, step=1.0, **kwargs
        )

        # Display widget for layout
        self.children = [self.lat_slider, self.lon_slider]

        # Internal VTK plane
        self.surface = vtkPlane()

        # Initialize normal and observe
        self._update_plane_normal()

        self.lat_slider.observe(self._on_angle_change, names='value')
        self.lon_slider.observe(self._on_angle_change, names='value')

    def _on_angle_change(self, change):
        self._update_plane_normal()

    def _update_plane_normal(self):
        """Compute normal vector from spherical angles and update VTK plane."""

        if hasattr(self, "surface"):
            
            lat = self.lat_slider.value.to(u.rad).value
            lon = self.lon_slider.value.to(u.rad).value
    
            # sin(th) = sin(pi/2 - lat) = cos(lat)
            # cos(th) = cos(pi/2 - lat) = sin(lat)

            normal = (np.cos(lat)*np.cos(lon), np.cos(lat)*np.sin(lon), np.sin(lat))
            
            self.surface.normal = normal
            self.set_trait('normal', normal)

