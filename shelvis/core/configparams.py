# This file is part of SHELVIS.
#
# Copyright 2024 SHELVIS developers
#
# Use of this source code is governed by a BSD-style license 
# that can be found in the LICENSE.md file.

"""Configuration parameters container
"""

import astropy.units


class ConfigParams:
    """Configuration parameter container base class.
    """
    
    def __setattr__(self, key, value):
        raise AttributeError(f"Cannot set '{key}' directly. Use the `set()` method instead.")

    def set(self, key, value):
        """Set the value of a configuration parameter.

        Parameters
        ----------
        key : str
            The name of the parameter
        value
            The value of the parameter. The type must match the original type.
        """
        
        # The allowed parameters are defined as annotations
        annotations = self.__class__.__annotations__

        if key in annotations:
            
            # The type must remain unchanged
            original_type = annotations[key]
            original_value = getattr(self, key)
            
            if not isinstance(value, original_type):
                raise TypeError(
                    f"Invalid type for '{key}': expected {original_type.__name__}, got {type(value).__name__}"
                    )
            
            if isinstance(value, astropy.units.Quantity):
                if not value.unit.is_equivalent(original_value.unit):
                    raise TypeError(
                        f"The unit '{value.unit}' of the given Quantity not compatible with '{original_value.unit}'"
                    )
                
            super().__setattr__(key, value)
        else:
            raise AttributeError(f"Key {key} not defined as a configurable parameter")

    def __repr__(self):
        
        keys = self.__class__.__annotations__.keys()
        items = {k: getattr(self, k) for k in keys}
        
        return f"{type(self).__name__}({items})"
