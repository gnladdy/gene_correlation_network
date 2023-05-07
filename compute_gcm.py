__doc__ = (
""" 
  Compute the correlation matrix of genes from .mtx|.tsv|.csv file.
  Default output: "data_dir"/[corr_|wom_corr_]"data_prefix".csv
  ('data_dir' is the directory of <data_file>, 'data_prefix' is the prefix of <data_file>)
  ('corr_' is default, 'wom_corr' is used by '-n' option.)
  
usage:
{f} <data_file> [-c <threshold_cell>] [-g <threshold_gene>] [-n] [-m] [-o <output_file>]
{f} -h | --help

options:
  -h, --help              show this help message and exit.
  <data_file>             specify the data file containing the expression data (row: gene, column: cell).
  -c <threshold_cell>     specify the threshold of cells [default: 0].
  -g <threshold_gene>     specify the threshold of genes [default: 0].
  -n                      run without MAGIC.
  -m                      output multiple files. 
  -o <output_file>        specify the output file.
""").format(f=__file__)

import magic
import scprep

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import os
import sys
from docopt import docopt
from schema import Schema, SchemaError, And, Or, Use, Optional

# define the schema for args.
schema = Schema({
  '--help': bool,
  '<data_file>': Use(str),
  '-c': And(Use(int), lambda n: 0 <= n),
  '-g': And(Use(int), lambda n: 0 <= n),
  '-n': bool,
  '-m': bool,
  Optional('-o'): Use(str),
})

def load_emt(data_file, result_file, is_magic):
  data_dir, data_filename = os.path.split(os.path.abspath(data_file))
  data_file_without_ext, data_type = os.path.splitext(data_filename)
  
  if result_file == 'None' or result_file == '':
    pre = '/corr_'
    if not is_magic:
      pre = '/wom_corr_'
    result_file = data_dir + pre + data_file_without_ext + '.csv'
  else:
    result_file = os.path.abspath(result_file) 
  print(result_file)

  sparse_flag = False
  if data_type == '.mtx':
    cell_filename = data_dir + '/cells_' + data_file_without_ext + '.tsv'
    gene_filename = data_dir + '/genes_' + data_file_without_ext + '.tsv'
    emt_data = scprep.io.load_mtx(data_file, gene_names=gene_filename, cell_names=cell_filename, sparse=True)
  elif data_type == '.tsv':
    emt_data = scprep.io.load_csv(data_file, cell_axis='column', delimiter='\t', sparse=sparse_flag)
  else: # csv
    emt_data = scprep.io.load_csv(data_file, cell_axis='column', delimiter=',', sparse=sparse_flag)
  return (emt_data, result_file)  
 

def preprocessed_data(emt_data, thres_cell, thres_gene):
  print('preprocess start')
  print(emt_data.shape)
  emt_data = scprep.filter.remove_empty_cells(emt_data)
  emt_data = scprep.filter.remove_empty_genes(emt_data)
  print(emt_data.shape)
  if thres_cell > 0:
    emt_data = scprep.filter.filter_library_size(emt_data, cutoff=thres_cell)
  print(emt_data.shape)
  if thres_gene > 0:
    emt_data = scprep.filter.remove_rare_genes(emt_data, cutoff=0, min_cells=thres_gene)
  print('preprocess done')
  print(emt_data.shape)
  emt_data = scprep.normalize.library_size_normalize(emt_data)
  return emt_data


def compute_gene_corr(data_file, corr_file, thres_cell, thres_gene, is_magic=True, is_multi=False):
  (emt_data, corr_file) = load_emt(data_file, corr_file, is_magic)
  emt_data = preprocessed_data(emt_data, thres_cell, thres_gene)
  allgenes = emt_data.columns
  #print(allgenes)
  
  magic_op = magic.MAGIC()
  if is_magic:
    magic_op.set_params(t=10) #'auto')
    magic_op.set_params(decay=15)
    magic_op.set_params(knn=10)
    emt_magic = magic_op.fit_transform(emt_data, genes=allgenes)
    corrdata = emt_magic.corr()
  else:
    corrdata = emt_data.corr()
  ## single file mode
  if not is_multi:
    corrdata.to_csv(corr_file)
  ## multi files mode
  else:
    corr_dir, corr_filename = os.path.split(corr_file)
    n = len(corrdata)
    x = n//100
    y = n%100
    for i in range(x):
      corrdata[i*100:(i+1)*100].to_csv(corr_dir + '/' + str(i) + '_' + corr_filename)
    if y > 0:
      corrdata[x*100:(x*100+y)].to_csv(corr_dir + '/' + str(x) + '_' + corr_filename)
  

if __name__ == '__main__':
  args = docopt(__doc__)
  
  try:
    args = schema.validate(args)
  except SchemaError as error:
    print(error)
    sys.exit(1)
  print(args)
  
  is_magic = True
  if args['-n']:
    is_magic = False
  
  compute_gene_corr(args['<data_file>'], args['-o'], args['-c'], args['-g'], is_magic, args['-m'])
  