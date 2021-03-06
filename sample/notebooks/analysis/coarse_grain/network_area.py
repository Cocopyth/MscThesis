
import sys  
sys.path.insert(0, '/home/cbisot/pycode/MscThesis/')
import pandas as pd
from sample.util import get_dates_datetime, get_dirname, get_plate_number, get_postion_number,get_begin_index
import ast
from sample.plotutil import plot_t_tp1
from scipy import sparse
from datetime import datetime
from sample.pipeline.functions.node_id import orient
import pickle
import scipy.io as sio
from pymatreader import read_mat
from matplotlib import colors
import cv2
import imageio
import matplotlib.pyplot as plt
import numpy as np
from skimage.filters import frangi
from skimage import filters
from random import choice
import scipy.sparse
import os
from sample.pipeline.functions.extract_graph import from_sparse_to_graph, generate_nx_graph, sparse_to_doc
from skimage.feature import hessian_matrix_det
from sample.pipeline.functions.experiment_class_surf import Experiment, Edge, Node, Hyphae, plot_raw_plus, get_hyphae
from sample.paths.directory import run_parallel, find_state, directory_scratch, directory_project
from sample.notebooks.analysis.util import *
from scipy import stats
from scipy.ndimage.filters import uniform_filter1d
from statsmodels.stats import weightstats as stests
from sample.pipeline.functions.hyphae_id_surf import get_pixel_growth_and_new_children, resolve_ambiguity, relabel_nodes_after_amb
from collections import Counter
from IPython.display import clear_output
from sample.notebooks.analysis.data_info import *
from sample.pipeline.functions.node_id import reconnect_degree_2
from sample.pipeline.functions.extract_graph import (
    generate_skeleton,
    from_nx_to_tab,
    prune_graph
)

from sample.pipeline.functions.hyphae_id_surf import (
    clean_and_relabel,
    get_mother,
    save_hyphaes,
    resolve_ambiguity_two_ends,
    clean_obvious_fake_tips,
    width_based_cleaning
)
from sample.pipeline.functions.experiment_class_surf import clean_exp_with_hyphaes
from scipy.ndimage import gaussian_filter
from scipy import ndimage
import matplotlib.pyplot as plt

directory = directory_project
plate_number = 59
plate = get_postion_number(plate_number)
begin = 7
end = 42
dates_datetime = get_dates_datetime(directory,plate)
dates = dates_datetime[begin:end+1]
exp = Experiment(plate,directory)
exp.load(dates) #for method 2
exp.load_compressed_skel()

def get_density_maps(exp,t,compress,kern_sizes):
    skeletons = [sparse.csr_matrix(skel) for skel in exp.skeletons]
    window=compress
    densities=np.zeros((skeletons[t].shape[0]//compress,skeletons[t].shape[1]//compress),dtype=np.float)
    for xx in range(skeletons[t].shape[0]//compress):
        for yy in range(skeletons[t].shape[1]//compress):
            x = xx*compress
            y = yy*compress
            skeleton=skeletons[t][x-window:x+window,y-window:y+window]
            density = skeleton.count_nonzero()/((window*1.725)**2)
            densities[xx,yy]=density
    results = {}
    for kern_size in kern_sizes:
        density_filtered = gaussian_filter(densities,kern_size)
        sx = ndimage.sobel(density_filtered ,axis=0,mode='constant')
        sy = ndimage.sobel(density_filtered ,axis=1,mode='constant')
        sobel=np.hypot(sx,sy)
        results[kern_size] = density_filtered,sx,sy,sobel
    return(results)

kern_size=20
density_maps = [get_density_maps(exp,t,100,[kern_size]) for t in range(exp.ts)]
for index,density_map in enumerate(density_maps):
    plt.close('all')
    clear_output(wait=True)
    fig=plt.figure(figsize=(14,12))
    ax = fig.add_subplot(111)
    im= density_map[kern_size][0]
    figure = ax.imshow(im>=0.001,vmax = 0.01)
    plt.colorbar(figure,orientation = 'horizontal')
    save = f'/home/cbisot/pycode/MscThesis/sample/notebooks/plotting/Figure/im*{index}.png'
    plt.savefig(save)
img_array = []
for index in range(len(density_maps)):
    img = cv2.imread(f'/home/cbisot/pycode/MscThesis/sample/notebooks/plotting/Figure/im*{index}.png')
    img_array.append(img)
imageio.mimsave(f'/home/cbisot/pycode/MscThesis/sample/notebooks/plotting/Figure/movie_dense_{kern_size}_{plate_number}thresh.gif', img_array,duration = 1)
sizes = []
for index,density_map in enumerate(density_maps):
    im= density_map[kern_size][0]
    size = np.sum(im>=0.0005)*100**2
    sizes.append(size)
np.save(f'/home/cbisot/pycode/MscThesis/Results/sizes_{plate_number}_{begin}_{end}',sizes)