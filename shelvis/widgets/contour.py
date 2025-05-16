# This file is part of SHELVIS.
#
# Copyright 2024 SHELVIS developers
#
# Use of this source code is governed by a BSD-style license 
# that can be found in the LICENSE.md file.

"""Widgets for handling various implicit functions
"""

import traitlets

from vtkmodules.vtkFiltersCore import vtkContourFilter
from shelvis.widgets.slider import FloatSliderWithUnit


class Contour(FloatSliderWithUnit):
    """Widget for managing an isocontour
    """
    
    def __init__(self, value, unit, **kwargs):
        
        super().__init__(description="Value:", value=value, unit=unit, **kwargs)

        # Set the contour
        self.contour = vtkContourFilter()
        
    @traitlets.observe('value')
    def _on_value_change(self, change):
        
        if hasattr(self, 'contour'):
            
            self.contour.SetValue(0, change['new'].si.value)