__doc__ = (
""" 
  Find the top 10 largest clusters in the graph specified by <data_file>) by Louvain method.
  Default output: 
  "data_dir"/louvain_"data_prefix"_"idx".net,
  "data_dir"/louvain_"data_prefix"_"idx".png, and
  "data_dir"/louvain_"data_prefix"_rank".csv 
  where "idx" denotes the index of the cluster.
  ('data_dir' is the directory of <data_file>, 'data_prefix' is the prefix of <data_file>) 
usage:
{f} <data_file> [-r] [-p] [-o <output_prefix>]
{f} -h | --help

options:
  -h, --help               show this help message and exit.
  <data_file>              specify the graph file (.net).
  -r                       generate the ranking for each cluster.
  -p                       generate the plot (.png) for each cluster.
  -o <output_prefix>       specify the prefix of output file.
""").format(f=__file__)


import community as community_louvain
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import os
import sys
import collections
from mypajek import my_read_pajek
import plot_gcn
from docopt import docopt
from schema import Schema, SchemaError, And, Or, Use, Optional

# define the schema for args.
schema = Schema({
  '--help': bool,
  '<data_file>': Use(str),
  Optional('-r'): bool,
  Optional('-p'): bool,
  Optional('-o'): Use(str),
})



def louvain(G, output_prefix, ranking=False, plot=True):
    G_temp = G.copy()
    
    for (u,v,d) in G_temp.edges(data=True):
      d["weight"] = abs(d["weight"])
    
    partition = community_louvain.best_partition(G_temp, random_state=0)
    
    part_values = list(partition.values())
    part_size = collections.Counter(part_values).most_common()
    
    print(len(part_size), "communites found")
    print("modularity =", community_louvain.modularity(partition, G_temp))
    #print(part_size)

    part_dict = dict() # for ranking data

    idx_max = 10 if len(part_size) > 10 else len(part_size)
    for i in range(idx_max):
      part_num = part_size[i][0]
      part_nodes = [v for v, p in partition.items() if p == part_num]
      if len(part_nodes) > 1:
        H_origin = nx.subgraph(G, part_nodes)
        output_file = output_prefix + str(i+1) + '.net'
        print('output', output_file)
        nx.write_pajek(H_origin, output_file)

        if plot:
          plot_file = output_prefix + str(i+1) + '.png'
          plot_gcn.default_setting(H_origin)
          print('plot', plot_file)
          plot_gcn.plot_gcn(H_origin, plot_file)
        
        if ranking:
          H_temp = nx.subgraph(G_temp, part_nodes)
          pr = nx.pagerank(H_temp, weight='weight')
          pr = sorted(pr.items(), key=lambda x:x[1], reverse=True)
          pr_nodes = [v for v,r in pr]
          pr_rank = [r for v,r in pr]
          part_dict["part"+str(i+1)] = pr_nodes
          part_dict["part"+str(i+1)+" PageRank"] = pr_rank
    
    if ranking:
      df = pd.DataFrame(part_dict.values(), index=part_dict.keys()).T
      ranking_file = output_prefix + 'rank.csv'
      print('ranking', ranking_file)
      df.to_csv(ranking_file)


    return partition
    


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
  output_prefix = args['-o']
  if output_prefix == 'None' or output_prefix == '':
    output_prefix = data_dir + '/louvain_' + data_file_without_ext + '_'
  
  G = nx.Graph(my_read_pajek(data_file))
  print(nx.number_of_nodes(G), 'nodes')
  partition = louvain(G, output_prefix, ranking=args['-r'], plot=args['-p'])

  