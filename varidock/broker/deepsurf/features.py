#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""Created on Mon Oct 21 11:46:54 2019.

@author: smylonas
"""


from .tfbio_data import Featurizer,make_grid
from .utils import rotation
import numpy as np
     

class KalasantyFeaturizer:
    """Featurizer for generating 3D grid-based molecular features.

    This class creates voxelized representations of molecular structures
    centered on specific points, using rotation to align with surface normals.

    Attributes:
        neigh_radius: Radius for neighbor atom search.
        featurizer: Underlying Featurizer for extracting atom features.
        grid_resolution: Voxel size in Angstroms.
        max_dist: Maximum distance from grid center to edge.

    """

    def __init__(self,gridSize,voxelSize):
        """Initialize the KalasantyFeaturizer with grid parameters.

        Args:
            gridSize: Number of voxels along each grid dimension.
            voxelSize: Size of each voxel in Angstroms.

        """
        grid_limit = (gridSize/2-0.5)*voxelSize
        grid_radius = grid_limit*np.sqrt(3)             
        self.neigh_radius = 4 + grid_radius   # 4 > 2*R_vdw
        self.featurizer = Featurizer(save_molecule_codes=False)
        self.grid_resolution = voxelSize
        self.max_dist = (gridSize-1)*voxelSize/2 
    
    def get_channels(self,mol):
        """Extract feature channels from a molecular structure.

        Args:
            mol: Molecular structure to extract features from.

        Note:
            Sets self.channels as a side effect containing per-atom feature vectors.

        """
        _, self.channels = self.featurizer.get_features(mol)  # returns only heavy atoms
    
    def grid_feats(self,point,normal,mol_coords):
        """Generate a 3D feature grid centered on a point aligned to a surface normal.

        Args:
            point: Center point coordinates (x, y, z) for the grid.
            normal: Surface normal vector for rotation alignment.
            mol_coords: Array of atomic coordinates from the molecule.

        Returns:
            3D numpy array containing voxelized molecular features.

        """
        neigh_atoms = np.sqrt(np.sum((mol_coords-point)**2,axis=1))<self.neigh_radius
        Q = rotation(normal)
        Q_inv = np.linalg.inv(Q)
        transf_coords = np.transpose(mol_coords[neigh_atoms]-point)
        rotated_mol_coords = np.matmul(Q_inv,transf_coords)
        features = make_grid(np.transpose(rotated_mol_coords),self.channels[neigh_atoms],self.grid_resolution,self.max_dist)[0]
        
        return features
        
        
