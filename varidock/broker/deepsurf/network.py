#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""Created on Thu Jan 30 15:13:37 2020.

@author: smylonas

Modified on Sat Feb 6 14:30:00 2026 by abdollahegazy
to include TF2 compatibility.
"""

import os
import numpy as np
import tensorflow as tf
import tf_slim as slim
from .features import KalasantyFeaturizer
from tensorflow.compat.v1 import ( # type: ignore
    reset_default_graph,
    placeholder,
    disable_v2_behavior,
    ConfigProto,
    Session,
    global_variables_initializer,
)
from tensorflow.compat.v1.train import Saver # type: ignore
disable_v2_behavior()

class Network:

    def __init__(self,model_path,model,voxelSize):
        """Initialize the neural network for binding site prediction.

        Args:
            model_path: Path to the directory containing saved model weights.
            model: Model architecture type, either 'orig' or 'lds'.
            voxelSize: Size of voxels in Angstroms for grid featurization.

        """
        gridSize = 16
        reset_default_graph()
        
        self.inputs = placeholder(tf.float32,shape=(None,gridSize,gridSize,gridSize,18))
        
        if model=='orig':
            from .net.resnet_3d import resnet_arg_scope, resnet_v1_18
        elif model=='lds':
            from .net.resnet_lds_3d_bottleneck import resnet_arg_scope, resnet_v1_18
        
        with slim.arg_scope(resnet_arg_scope()):  
            self.net, self.end_points = resnet_v1_18(self.inputs, 1, is_training=False)
        
        config = ConfigProto()
        config.gpu_options.allow_growth = True
        self.sess = Session(config=config)
        
        self.sess.run(global_variables_initializer()) 
        saver = Saver()
        if model=='orig':
            saver.restore(self.sess,os.path.join(model_path,'resnet18'))
        elif model=='lds':
            saver.restore(self.sess,os.path.join(model_path,'bot_lds_resnet18'))
        
        self.featurizer = KalasantyFeaturizer(gridSize,voxelSize)
        
    def get_lig_scores(self, prot, batch_size):
        """Calculate ligandability scores for protein surface points.

        Args:
            prot: Protein object containing surface points, normals, heavy atom
            coordinates, and molecular structure.
            batch_size: Number of surface points to process in each batch.

        Returns:
            np.ndarray: Array of ligandability scores for each surface point.

        """
        self.featurizer.get_channels(prot.mol)

        gridSize = 16
        lig_scores = []
        input_data = np.zeros((batch_size,gridSize,gridSize,gridSize,18))  
        batch_cnt = 0
        for p,n in zip(prot.surf_points,prot.surf_normals):
            input_data[batch_cnt,:,:,:,:] = self.featurizer.grid_feats(p,n,prot.heavy_atom_coords)  
            batch_cnt += 1
            if batch_cnt==batch_size:
                output = self.sess.run(self.end_points,feed_dict={self.inputs:input_data}) 
                lig_scores += list(output['probs'])
                batch_cnt = 0
        
        if batch_cnt>0:
            output = self.sess.run(self.end_points,feed_dict={self.inputs:input_data[:batch_cnt,:,:,:,:]}) 
            if batch_cnt==1:
                lig_scores.append(output['probs'])
            else:
                lig_scores += list(output['probs'])
        
        return np.array(lig_scores)
        
