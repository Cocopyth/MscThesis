import sys  
sys.path.insert(0, '/home/cbisot/pycode/MscThesis/')
sys.path.append( '/home/cbisot/pycode/MscThesis/sample/pipeline/functions')

from sample.notebooks.analysis.util import *
from sample.paths.directory import path_code, directory_scratch, directory_project
from sample.notebooks.analysis.data_info import *

for treatment in treatments.keys():
    insts = treatments[treatment]
    bas_frequs = estimate_bas_freq_mult(insts,1000,0,criter, directory_project)
    pickle.dump(bas_frequs, open(f'{path_code}/MscThesis/Results/bas_{treatment}.pick', "wb"))