from path import path_code_dir
import sys  
sys.path.insert(0, path_code_dir)
import numpy as np
from scipy import sparse
import cv2
from pymatreader import read_mat

# from extract_graph import dic_to_sparse
from sample.pipeline.functions.extract_graph import (
    generate_skeleton,
)
from sample.pipeline.functions.extract_graph import (
    from_sparse_to_graph,
    generate_nx_graph,
    prune_graph,
    clean_degree_4,
)
from sample.util import get_dates_datetime, get_dirname
import scipy.sparse
import scipy.io as sio

plate = int(sys.argv[1])
i = int(sys.argv[-1])
threshold = float(sys.argv[2])
directory = str(sys.argv[3])

dates_datetime = get_dates_datetime(directory,plate)
dates_datetime.sort()
date_datetime = dates_datetime[i]
date = date_datetime
directory_name = get_dirname(date, plate)
path_snap = directory + directory_name
skel = read_mat(path_snap + "/Analysis/skeleton_masked.mat")["skeleton"]
skeleton = scipy.sparse.dok_matrix(skel)

# nx_graph_poss=[generate_nx_graph(from_sparse_to_graph(skeleton)) for skeleton in skels_aligned]
# nx_graphs_aligned=[nx_graph_pos[0] for nx_graph_pos in nx_graph_poss]
# poss_aligned=[nx_graph_pos[1] for nx_graph_pos in nx_graph_poss]
# nx_graph_pruned=[clean_degree_4(prune_graph(nx_graph),poss_aligned[i])[0] for i,nx_graph in enumerate(nx_graphs_aligned)]
nx_graph, pos = generate_nx_graph(from_sparse_to_graph(skeleton))
nx_graph_pruned = clean_degree_4(prune_graph(nx_graph, threshold), pos)[0]
directory_name = get_dirname(date, plate)
path_snap = directory + directory_name
skeleton = generate_skeleton(nx_graph_pruned, (30000, 60000))
skel = scipy.sparse.csc_matrix(skeleton, dtype=np.uint8)
sio.savemat(path_snap + "/Analysis/skeleton_pruned.mat", {"skeleton": skel})
dim = skel.shape
kernel = np.ones((5, 5), np.uint8)
itera = 1
sio.savemat(
    path_snap + "/Analysis/skeleton_pruned_compressed.mat",
    {
        "skeleton": cv2.resize(
            cv2.dilate(skel.todense(), kernel, iterations=itera),
            (dim[1] // 5, dim[0] // 5),
        )
    },
)
