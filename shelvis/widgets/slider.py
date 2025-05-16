# This file is part of SHELVIS.
#
# Copyright 2024 SHELVIS developers
#
# Use of this source code is governed by a BSD-style license 
# that can be found in the LICENSE.md file.

"""Slider widgets 
"""

import astropy.constants
import numpy as np
import ipywidgets
import traitlets
import astropy
import astropy.units as u


class QuantityTrait(traitlets.TraitType):
    info_text = 'an astropy Quantity'

    def validate(self, obj, value):

        if isinstance(value, u.Quantity):
            return value
        
        self.error(obj, value)


class SliderBase(ipywidgets.VBox):
    """Base class for slider widgets for setting values with physical units.
    """

    value = QuantityTrait()

    def __init__(self, unit, **kwargs):

        super().__init__()

        # Set widget layout if given
        if kwargs.get("layout") is not None:
            self.layout = kwargs.get("layout")

        # Set the unit of this slider
        self._unit = u.Unit(unit)
        
        # Label showing the name of the unit
        #self.unit_label = ipywidgets.HTMLMath(value=self._label_str)
        self.unit_label = ipywidgets.Label(value=self._label_str)

    def _on_slider_value_change(self, change):
        """Updates the value trait when the slider changes
        """
        self.value = change['new'] * self.unit

    @property
    def _label_str(self):
        """Returns the string representation of the unit
        """
        unit_str = self._unit.to_string()

        # Change string in special cases
        if self.unit.is_equivalent(u.m):
            if np.isclose(self.unit.scale, astropy.constants.R_sun.value):
                unit_str = r'Rsun'
            elif np.isclose(self.unit.scale, astropy.constants.au.value):
                unit_str = r'au'
            return unit_str
        
        return "" if unit_str == "" else r'[{}]'.format(unit_str)

    def _to_float(self, val) -> float:
        """Returns the value as a float in the current units
        """
        if isinstance(val, u.Quantity):
            value = val.to(self._unit).value
        else:
            value = float(val)

        return value

    @property
    def unit(self) -> astropy.units.Unit:
        """Returns the physical unit associated with the slider value.
        """
        return self._unit
   
    @property
    def max(self) -> astropy.units.Quantity:
        """Returns the slider range maximum.
        """
        return self.slider.max * self._unit
 
    @max.setter
    def max(self, val):
        """Set the slider range maximum value.

        Parameters
        ----------
        val : float, astropy.units.Quantity
        """
        self.slider.max = self._to_float(val)
 
    @property
    def min(self) -> astropy.units.Quantity:
        """Returns the slider range minimum.
        """
        return self.slider.min * self._unit

    @min.setter
    def min(self, val):
        """Set the slider range minimum value.

        Parameters
        ----------
        val : float, astropy.units.Quantity
        """
        self.slider.min = self._to_float(val)
 
    @property
    def minmax(self) -> astropy.units.Quantity:
        return (self.min.to_value(self.unit), self.max.to_value(self.unit))*self.unit

    @minmax.setter
    def minmax(self, val):
        self.min = min(val)
        self.max = max(val)

    @property
    def step(self) -> astropy.units.Quantity:
        """Returns the slider step.
        """
        return self.slider.step * self._unit

    @step.setter
    def step(self, val):
        """Set the slider step value.

        Parameters
        ----------
        val : float, astropy.units.Quantity
        """
        self.slider.step = self._to_float(val)


class FloatSliderWithUnit(SliderBase):
    """A slider widget for setting values with physical units.

    A slider widget similar to ipywidgets.FloatSlider supporting 
    values with physical units using AstroPy.

    Parameters
    ----------
    unit : str or astropy.units.Unit
        The physical unit associated with the slider value.
    **kwargs:
        Arguments to the slider can be passed using keyword arguments.
        The arguments are identical to those of ipywidgets.FloatSlider,
        with the unit of the values given by ``unit``.
    
    Attributes
    ----------
    value : astropy.units.Quantity
        The current value of the slider including the unit.   
    """

    def __init__(self, unit, **kwargs):

        super().__init__(unit=unit, **kwargs)

        # The slider holding the value
        self.slider = ipywidgets.FloatSlider(            
            readout_format='.3g',
            **kwargs
        )
        
        # The label is wrapped inside a Box for correct alignment
        label_box = ipywidgets.Box([self.unit_label], 
                                   layout=ipywidgets.Layout(display='flex', 
                                                            align_items='center'))

        # Set the children of the base VBox
        self.children = [ipywidgets.HBox([self.slider, label_box])]
        

        # Set initial value for the trait
        self.value = self.slider.value*self.unit

        # Observe changes to the slider value
        self.slider.observe(self._on_slider_value_change, names='value')

    @traitlets.observe('value')
    def _on_value_trait_change(self, change):
        """Updates the slider when value changes
        """
        self.slider.value = self._to_float(change['new'])

    @property
    def unit(self) -> astropy.units.Unit:
        """Returns the physical unit associated with the slider value.
        """
        return self._unit

    @unit.setter
    def unit(self, val):
        """Set the unit for the slider value.

        Parameters
        ----------
        val : str or astropy.units.Unit
        """

        # The current (old) unit
        old_unit = self._unit 

        # The new unit
        new_unit = u.Unit(val)

        # Set the new unit
        self._unit = new_unit

        # Update label
        self.unit_label.value = self._label_str
        
        # Set
        old_value = u.Quantity(self.slider.value, old_unit)

        self.slider.value = old_value.to(new_unit).value
    
        # Update slider properties
        self.slider.min = u.Quantity(self.slider.min, old_unit).to(new_unit).value
        self.slider.max = u.Quantity(self.slider.max, old_unit).to(new_unit).value
        self.slider.step = u.Quantity(self.slider.step, old_unit).to(new_unit).value
    
        # Update quantity without calling its observer
        self.set_trait('value', old_value.to(new_unit))



class FloatRangeSliderWithUnit(SliderBase):

    def __init__(self, unit, **kwargs):

        super().__init__(unit=unit, **kwargs)
        
        # The slider holding the value
        self.slider = ipywidgets.FloatRangeSlider(            
            readout_format='.3g',
            **kwargs
        )
        
        # Set the children of the VBox
        self.children = [ipywidgets.HBox([self.slider, self.unit_label])]

        # Set initial value for the trait
        self.value = self.slider.value*self.unit

        # Observe changes to the slider value
        self.slider.observe(self._on_slider_value_change, names='value')

    @traitlets.observe('value')
    def _on_value_trait_change(self, change):
        """Updates the slider when value changes
        """
        self.slider.value = tuple(self._to_float(change['new']))

    @property
    def unit(self):
        return self._unit

    @unit.setter
    def unit(self, val):
        """Set the unit for the slider value.

        Parameters
        ----------
        val : str or astropy.units.Unit
        """

        # The current (old) unit
        old_unit = self._unit 

        # The new unit
        new_unit = u.Unit(val)

        # Set the new unit
        self._unit = new_unit

        # Update label
        self.unit_label.value = self._label_str
        
        # Update the slider value
        old_value = u.Quantity(self.slider.value, old_unit)
        self.slider.value = tuple(old_value.to(new_unit).value)
            
        # Update slider properties
        self.slider.min = u.Quantity(self.slider.min, old_unit).to(new_unit).value
        self.slider.max = u.Quantity(self.slider.max, old_unit).to(new_unit).value
        self.slider.step = u.Quantity(self.slider.step, old_unit).to(new_unit).value
    
        # Update quantity without calling its observer
        self.set_trait('value', old_value.to(new_unit))
        