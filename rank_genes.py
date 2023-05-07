__doc__ = (
""" 
  Rank genes (the nodes) of a gene correlation graph.
  Default output: "data_dir"/"data_prefix"_rank.csv 
  ('data_dir' is the directory of <data_file>, 'data_prefix' is the prefix of <data_file>)
usage:
{f} <data_file> [-p <gene>] [-o <output_file>]
{f} -h | --help

options:
  -h, --help               show this help message and exit.
  <data_file>              specify the graph file (.net).
  -p <gene>                (work in progress) 
  -o <output_file>         specify the output file.
""").format(f=__file__)

import numpy as np
import pandas as pd
import networkx as nx
from mypajek import my_read_pajek
import os
import sys
from docopt import docopt
from schema import Schema, SchemaError, And, Or, Use, Optional


# define the schema for args.
schema = Schema({
  '--help': bool,
  '<data_file>': Use(str),
  Optional('-p'): Use(str),
  Optional('-o'): Use(str),
})

def negative_pagerank(g):
  g1 = g.copy()
  for u, v in g1.edges:
    g1.edges[u, v]['weight'] = abs(g1.edges[u, v]['weight'])
  return nx.pagerank(g1, weight='weight')

def ranking(g, filename, gene=''):
  """Rank the nodes of a graph.
  Currently, this computes
  (1) Simple degree
  (2) PageRank, banilla
  (3) PageRank, using weight 
      (warning: this might not work well if the graph has both positive and negative edges)
  Parameters
  ----------
  g: the graph.
  filename: csv file for storing the result
  gene: for personalized PageRank
  """
  degs = [g.degree(i) for i in g.nodes ]
  pr_noweight = nx.pagerank(g, weight=None)
  pr_weight = negative_pagerank(g)
  if gene != '': 
    ppr_weight = nx.pagerank(g, weight='weight', personalization={gene:1})
  df = pd.DataFrame([], columns=['Gene', 'Degree', 'PageRank w/o weight', 'PageRank w/ weight'])
  df['Gene'] = g.nodes
  df['Degree'] = degs
  df['PageRank w/o weight'] = list(pr_noweight.values())
  df['PageRank w/ weight'] = list(pr_weight.values())
  df.to_csv(filename, index=False)

if __name__ == '__main__':
  args = docopt(__doc__)
  
  try:
    args = schema.validate(args)
  except SchemaError as error:
    print(error)
    sys.exit(1)
  print(args)
  
  data_file = args['<data_file>']
  data_dir, data_filename = os.path.split(os.path.abspath(data_file))
  data_file_without_ext = os.path.splitext(data_filename)[0]
  print(data_dir)
  print(data_filename)
  
  gene = args['-p']
  result_file = args['-o']
  if result_file == 'None' or result_file == '':
    gene_prefix = ''
    if gene != 'None' and gene != '':
      gene_prefix = gene + '_'
    result_file = data_dir + '/' + gene_prefix + data_file_without_ext + "_rank.csv"
  print(result_file)
  g = nx.Graph(my_read_pajek(data_file))
  ranking(g, result_file, gene)
  
  
