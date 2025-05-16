# This file is part of SHELVIS.
#
# Copyright 2024 SHELVIS developers
#
# Use of this source code is governed by a BSD-style license 
# that can be found in the LICENSE.md file.

"""VTK methods for transforming and modifying the grid and data
"""

from vtkmodules.vtkFiltersCore import vtkCutter

class ImplicitCutter:
    
    def __init__(self, data=None, cut_function=None):
        
        self._cutter = vtkCutter()

        if data is not None:
            self._cutter.input_data = data

        if cut_function is not None:
            self._cutter.cut_function = cut_function

        # Finalize initialization if all information given
        if data is not None and cut_function is not None:
            self.update()
    
    def update(self):
        self._cutter.Update()

    @property
    def output(self):
        return self._cutter.output
