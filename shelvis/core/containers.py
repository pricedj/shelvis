# This file is part of SHELVIS.
#
# Copyright 2024 SHELVIS developers
#
# Use of this source code is governed by a BSD-style license 
# that can be found in the LICENSE.md file.

"""Miscellaneous containers
"""

from traitlets import HasTraits, TraitType
from astropy.coordinates import SkyCoord
import astropy.units as u


class SkyCoordDict(TraitType):
    """A trait type of a dictionary that contains astropy SkyCoord objects.
    """
    default_value = {}
    info_text = 'a dictionary of SkyCoord objects'

    def validate(self, obj, value):

        if not isinstance(value, dict):
            self.error(obj, value)

        for k, v in value.items():
            if not isinstance(k, str) or not isinstance(v, SkyCoord):
                self.error(obj, value)
        
        return value


class SkyCoordContainer(HasTraits):
    """A container for named astropy SkyCoord objects with update tracking.
    
    Supports dict-like interaction via item access:
        container["point_name"] = SkyCoord(...)
        coord = container["point_name"]
    
    Automatically emits change information on additions, removals,
    and updates via traitlets observation mechanism.

    Attributes:
    -----------
    points : SkyCoordDict
        A dictionary mapping keys to astropy.coordinates.SkyCoord objects.
    """
    points = SkyCoordDict()

    def __setitem__(self, key, value):
        """Add or update a SkyCoord.

        Parameters
        ----------
        key : str 
            The identifier for the coordinate point.
        value : SkyCoord
            The coordinate to associate with the name.

        Raises:
            TypeError: If value is not a SkyCoord instance.
        """
        if not isinstance(value, SkyCoord):
            raise TypeError("value must be a SkyCoord instance")
        
        new_points = dict(self.points)
        new_points[key] = value

        # Reassigning the dictionary triggers the event
        self.points = new_points

    def __delitem__(self, key):
        """Remove a point by name.

        Parameters
        ----------
        key :str 
            The name of the point to remove.
        """
        self.remove(key)

    def __getitem__(self, key):
        """Retrieve a SkyCoord by name.

        Parameters
        ----------
        key : str
            The name of the SkyCoord.

        Returns:
            SkyCoord: The associated coordinate.
        """
        return self.points[key]

    def remove(self, key):
        """Remove a point by name.

        Parameters
        ----------
        key :str 
            The name of the point to remove.
        """
        if key in self.points:
            new_points = dict(self.points)
            del new_points[key]

            self.points = new_points

    @staticmethod
    def changes_to_points(old, new, tolerance_arcsec=1e-6):
        """Determines the added, removed, and updated keys between two dicts 
        that contain SkyCoords.

        Arguments:
        ---------
        old : dict 
            Previous dict of SkyCoord values.
        new : dict 
            New dict of SkyCoord values.
        tolerance_arcsec : float 
            Separation threshold when coordinates are considered to have changed.
             
        Returns:
        -------
        tuple: (added, removed, updated) where:
            - added is a dict of new keys
            - removed is a dict of removed keys
            - updated is a dict of {key: (old_value, new_value)} for changed entries
        """
        added = {}
        removed = {}
        updated = {}

        old_keys = set(old)
        new_keys = set(new)

        for k in new_keys - old_keys:
            added[k] = new[k]
        for k in old_keys - new_keys:
            removed[k] = old[k]
        for k in old_keys & new_keys:
            old_coord = old[k]
            new_coord = new[k]
            if old_coord.shape != new_coord.shape:
                updated[k] = (old_coord, new_coord)
            else:
                sep = new_coord.separation(old_coord).arcsecond
                if not (sep < tolerance_arcsec).all():
                    updated[k] = (old_coord, new_coord)

        return added, removed, updated
