
## Compute a gene correlation matrix from a gene expression matrix

The input is a csv, mtx, or tsv file that represents a gene expression matrix corresponding to a single-cell transcriptome data. 
The format of a gene expression matrix is as follows. 
Each row represents a gene, and each column represents a cell. 
Thus, the first row contains the names of cells, and the first column contains the names of genes. 

The following is an example of a part of a gene exprresion matrix

```
"","Og5-WTA_162","Og5-WTA_185","Og5-WTA_382"
"1700016K19Rik",0,0,0
"AA467197",0,0,0
"Abcg1",0,21,29
```

To generate a gene correlation matrix from the input, "compute_gcm.py" is used. 
By default, MAGIC is applied to the generation. 

The following an example of the usage of "compute_gcm.py", assuming that the input file is "data/SilicaCCR2KO1_Day21.csv".

```
python compute_gcm.py data/SilicaCCR2KO1_Day21.csv -g 1050
```

This outputs "data/corr_SilicaCCR2KO1_Day21.csv". 
The option and parameter "-g 1050" means that genes appeared on less than 1050 cells are ignored. 
For the details of parameters and options, use "-h" option. 

```
python compute_gcm.py -h
```










## Construct a gene correlation network from a gene correlation network

The input is a .csv file that is an output of the previous section (it represents a gene correlation network).
Here, "construct_gcn.py" is used. 


The following is an example of the usage of "construct_gcn.py", assuming that the input file is "data/corr_SilicaCCR2KO1_Day21.csv". 

```
python construct_gcn.py data/corr_SilicaCCR2KO1_Day21.csv dict_final.csv 0.8 1.1
```

Note that "dict_final.csv" is a file containing a dictionary whose key is the name of each gene and value is the chromosome and 

The first parameter "0.8" means that every pair of genes whose correlation coefficient is at most -0.8 has an edge in the output network. 
The second parameter "1.1" means that every pair of genes with a positive correlation coefficient has not an edge in the output network ("1.1" can be any value larger than 1.0). 

The code above outputs "data/corr_SilicaCCR2KO1_Day21.net". 
For the details of parameters and options, use "-h" option. 




## Plot a gene correlation network

A gene correlation correlation network can be plotted using "plot_gcn.py". 

The following is an example for plotting "data/corr_SilicaCCR2KO1_Day21.net" that represents the gene correlation network obtained above. 

```
python plot_gcn.py data/corr_SilicaCCR2KO1_Day21.net 
```

The result of plotting this network is stored as "data/corr_SilicaCCR2KO1_Day21.png". 
For the details of parameters and options, use "-h" option. 
For example, you can output an .eps file instead of a .png file.




## Compute a ranking of genes on a gene correlation network

PageRank is a method for ranking web pages on a web graph. 
This algorithm can be applied to several kinds of networks.
Especially, ranking of vertices on a gene correlation network would reveal important genes. 

The following is an example for computing a ranking of genes in the gene correlation network represented by the file "data/corr_SilicaCCR2KO1_Day21.net". 

```
python rank_genes.py data/corr_SilicaCCR2KO1_Day21.net
```

This outputs "data/corr_SilicaCCR2KO1_Day21_rank.csv". 
The first column of the result .csv file contains the names of genes. 
The second column shows the degree of the vertex corresponding to each gene. 
The third column shows the value of PageRank of each gene. 
The forth column shows the value of PageRank using edge weight. 

For the details of parameters and options, use "-h" option. 




## Find gene communities (clusters) on a gene correlation network

While various clustering methods are known, the Louvain method is specialized for network structure. It is a method that leverages the structure of a given network to discover communities (subgraphs with dense edges) similar to clusters.

The following is an example for finding gene clusters on the gene correlation network represented by the file "data/corr_SilicaCCR2KO1_Day21.net". 

```
python louvain_clustering.py data/corr_SilicaCCR2KO1_Day21.net
```

This outputs several .net files, including "data/louvain_corr_SilicaCCR2KO1_Day21_1.net" and "data/louvain_corr_SilicaCCR2KO1_Day21_2.net". 
The last "_1" and "_2" denote the indices of clusters. 

For the details of parameters and options, use "-h" option. 
For example, you can generate .png files that plot the network structure of each obtained cluster. Note that every cluster is a subgraph of the input gene correlation network. 
