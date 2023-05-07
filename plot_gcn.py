__doc__ = (
""" 
  Plot a gene correlation graph. 
  Default output: "data_dir"/"data_prefix".png
  ('data_dir' is the directory of <data_file>, 'data_prefix' is the prefix of <data_file>)
  Setting_file: each row should contain "gene_name, size, color"
  (if size is 0, the gene is removed)
  
usage:
{f} <data_file> [-s <setting_file>] [-e] [-o <output_file>]
{f} -h | --help

options:
  -h, --help               show this help message and exit.
  <data_file>              specify the graph file (.net).
  -e                       output eps file.
  -s <setting_file>        use a setting CSV file.
  -o <output_file>         specify the output file.
""").format(f=__file__)

import numpy as np
import pandas as pd
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
from mypajek import my_read_pajek
import os
import sys
from docopt import docopt
from schema import Schema, SchemaError, And, Or, Use, Optional

# define the schema for args.
schema = Schema({
  '--help': bool,
  '<data_file>': Use(str),
  '-e': bool,
  Optional('-s'): Use(str),
  Optional('-o'): Use(str),
})

def plot_gcn(g, plot_filename, node_color='green', map_node_edge=True):
    edge_width = [ abs(d["weight"])*0.5 for (u,v,d) in g.edges(data=True)]
    cm = plt.get_cmap('Blues')
    cm_interval = [ i+1 / 10 for i in range(10)]
    cm = cm(cm_interval)
    #print(cm)
    cmr = plt.get_cmap('Reds')
    cmr = cmr(cm_interval)
    edge_color = [ 'blue' if d["weight"] > 0 else 'red' for (u,v,d) in g.edges(data=True)]
    #edge_color = [ cm[int((d["weight"] - 0.9)/0.01)] if d["weight"] > 0 else cmr[int((-0.8 - d["weight"])/0.02)] for (u,v,d) in g.edges(data=True)]
    #edge_alpha = [ 1.0 if d["weight"] > 0 else 0.0 for (u,v,d) in g.edges(data=True)]
    node_pos = {k: (d['x'], d['y']) for k, d in g.nodes(data=True)}
    node_color = [ g.nodes[v]['color'] for v in g.nodes() ]
    node_size = [ g.nodes[v]['size'] for v in g.nodes() ]
    
    plt.figure(figsize=(12, 12))
    #plt.text(0.5, 1.1, r'1')
    nx.draw(g,
            pos = node_pos,
            node_color=node_color,
            node_size=node_size,
            #edge_cmap=plt.cm.Greys,
            edge_color=edge_color,
            #edge_alpha=edge_alpha,
            edge_vmin=-3e4,
            width=edge_width,
            with_labels=False,
            font_size=16,
            font_color='black')
    
    plt.savefig(plot_filename, dpi=300)


def default_setting(g, nodesize = 200, color = 'green'):
  for v in g.nodes():
    g.nodes[v]['color'] = 'green'
    g.nodes[v]['size'] = nodesize



def custom_setting(g, setting_df):
  genes = set(g.nodes.keys())
  print(len(genes))
  default_size = 100
  try:
    for index, row in setting_df.iterrows():
      gene = row['gene']
      #print(gene)
      if gene == 'default':
        default_size = row['size']
        default_setting(g, default_size, row['color'])
      else:
        size = int(row['size'])
        v = g.nodes[gene]

        if size == 0:
          g.remove_node(gene)
        else:
          genes.remove(gene)
          v['size'] = size
          v['color'] = row['color']
          #print(v)
  except Exception as error:
      print('setting file error at row {0}:{1}'.format(index, row))
      raise error
  print(len(genes))
  if default_size == 0:
    edges = []
    for v in genes:
      #print(g.edges(v))
      edges.extend(list(g.edges(v)))
    #print(edges)
    g.remove_edges_from(edges)



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
  data_file_without_ext, data_type = os.path.splitext(data_filename)
  result_file = args['-o']
  if result_file == 'None' or result_file == '':
    ext = '.png'
    if args['-e']:
      ext = '.eps'
    result_file = data_dir + '/' + data_file_without_ext + ext 
  
  
  g = nx.Graph(my_read_pajek(data_file))
  default_setting(g)
  if args['-s'] != 'None':
    df = pd.read_csv(args['-s'])
    custom_setting(g, df)
  
  plot_gcn(g, result_file)

  


