#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""Created on Thu Jan 30 16:00:46 2020.

@author: smylonas

Modified on Sat Feb 6 14:30:00 2026 by abdollahegazy
to include TF2 compatibility.
"""

import numpy as np
from sklearn.cluster import MeanShift


class Bsite_extractor():
    """Extract binding sites from protein surface using clustering.

    This class uses MeanShift clustering to identify potential binding sites
    from ligandability scores computed on protein surface points.

    Attributes:
        T: Ligandability score threshold for filtering surface points.
        ms: MeanShift clustering instance.

    """

    def __init__(self,lig_thres,bw=15):
        """Initialize the binding site extractor.

        Args:
            lig_thres: Ligandability score threshold for filtering surface points.
            bw: Bandwidth parameter for MeanShift clustering. Defaults to 15.

        """
        self.T = lig_thres
        self.ms = MeanShift(bandwidth=bw,bin_seeding=True,cluster_all=False,n_jobs=4)
    
    def _cluster_points(self,prot,lig_scores):
        T_new = self.T
        while sum(lig_scores>=T_new) < 10 and T_new>0.3001:    # at least 10 points with prob>P  and P>=0.3
            T_new -= 0.1 

        filtered_points = prot.surf_points[lig_scores>T_new]
        filtered_scores = lig_scores[lig_scores>T_new]
        if len(filtered_points)<5:
            return () 

        clustering = self.ms.fit(filtered_points)
        labels = clustering.labels_
        
        unique_l,freq = np.unique(labels,return_counts=True)
    
        if len(unique_l[freq>=5])!=0:
            unique_l = unique_l[freq>=5]    # keep clusters with 5 points and more
        else:
            return ()
        
        if unique_l[0]==-1:                 # discard the "unclustered" cluster
            unique_l = unique_l[1:]    
        
        clusters = [(filtered_points[labels==l],filtered_scores[labels==l]) for l in unique_l]  # noqa: E741
        
        return clusters
        
    def extract_bsites(self,prot,lig_scores):
        """Extract binding sites from protein surface and store them.

        Clusters high-ligandability surface points and adds identified
        binding sites to the protein object.

        Args:
            prot: Protein object with surface points and bsite storage methods.
            lig_scores: Array of ligandability scores for each surface point.

        Returns:
            None. Modifies prot in place by adding and writing binding sites.

        """
        clusters = self._cluster_points(prot,lig_scores)
        if len(clusters)==0:
            print('No binding site found')
            return
        for cluster in clusters:
            prot.add_bsite(cluster)
        prot.sort_bsites()
        prot.write_bsites()
        
        
