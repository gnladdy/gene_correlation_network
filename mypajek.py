import networkx as nx

def my_parse_pajek(lines, encoding):
    """Parse Pajek format graph from string or iterable.

    Parameters
    ----------
    lines : string or iterable
       Data in Pajek format.

    Returns
    -------
    G : NetworkX graph

    See Also
    --------
    read_pajek()

    """
    import shlex

    # multigraph=False
    if isinstance(lines, str):
        lines = iter(lines.split("\n"))
    lines = iter([line.rstrip("\n") for line in lines])
    G = nx.MultiDiGraph()  # are multiedges allowed in Pajek? assume yes
    labels = []  # in the order of the file, needed for matrix
    while lines:
        try:
            l = next(lines)
        except:  # EOF
            break
        if l.lower().startswith("*network"):
            try:
                label, name = l.split(None, 1)
            except ValueError:
                # Line was not of the form:  *network NAME
                pass
            else:
                G.graph["name"] = name
        elif l.lower().startswith("*vertices"):
            nodelabels = {}
            l, nnodes = l.split()
            #print("number of nodes: {0}".format(nnodes))
            for i in range(int(nnodes)):
                l = next(lines)
                try:
                    splitline = [
                        x.decode("utf-8") for x in shlex.split(str(l).encode("utf-8"))
                    ]
                except AttributeError:
                    splitline = shlex.split(str(l))
                #print(splitline)
                id, label = splitline[0:2]
                labels.append(label)
                G.add_node(label)
                nodelabels[id] = label
                G.nodes[label]["id"] = id
                try:
                    #x, y, shape = splitline[2:5]
                    x, y = splitline[2:4]
                    #G.nodes[label].update(
                    #    {"x": float(x), "y": float(y), "shape": shape}
                    #)
                    G.nodes[label].update(
                        {"x": float(x), "y": float(y)}
                    )
                except:
                    pass
                try:
                    shape = splitline[4]
                    G.nodes[label].update(
                        {"shape": shape}
                    )
                except:
                    pass
                extra_attr = zip(splitline[5::2], splitline[6::2])
                G.nodes[label].update(extra_attr)
        elif l.lower().startswith("*edges") or l.lower().startswith("*arcs"):
            if l.lower().startswith("*edge"):
                # switch from multidigraph to multigraph
                G = nx.MultiGraph(G)
            if l.lower().startswith("*arcs"):
                # switch to directed with multiple arcs for each existing edge
                G = G.to_directed()
            for l in lines:
                try:
                    splitline = [
                        x.decode("utf-8") for x in shlex.split(str(l).encode("utf-8"))
                    ]
                except AttributeError:
                    splitline = shlex.split(str(l))

                if len(splitline) < 2:
                    continue
                ui, vi = splitline[0:2]
                u = nodelabels.get(ui, ui)
                v = nodelabels.get(vi, vi)
                # parse the data attached to this edge and put in a dictionary
                edge_data = {}
                try:
                    # there should always be a single value on the edge?
                    w = splitline[2:3]
                    edge_data.update({"weight": float(w[0])})
                except:
                    pass
                    # if there isn't, just assign a 1
                #                    edge_data.update({'value':1})
                extra_attr = zip(splitline[3::2], splitline[4::2])
                edge_data.update(extra_attr)
                # if G.has_edge(u,v):
                #     multigraph=True
                G.add_edge(u, v, **edge_data)
        elif l.lower().startswith("*matrix"):
            G = nx.DiGraph(G)
            adj_list = (
                (labels[row], labels[col], {"weight": int(data)})
                for (row, line) in enumerate(lines)
                for (col, data) in enumerate(line.split())
                if int(data) != 0
            )
            G.add_edges_from(adj_list)

    return G

def my_read_pajek(path, encoding="UTF-8"):
    """Read graph in Pajek format from path.

    Parameters
    ----------
    path : file or string
       File or filename to write.
       Filenames ending in .gz or .bz2 will be uncompressed.
    encoding : encoding of the file or string designated by the path
    Returns
    -------
    G : NetworkX MultiGraph or MultiDiGraph.

    Examples
    --------
    >>> G = nx.path_graph(4)
    >>> nx.write_pajek(G, "test.net")
    >>> G = nx.read_pajek("test.net")

    To create a Graph instead of a MultiGraph use

    >>> G1 = nx.Graph(G)

    References
    ----------
    See http://vlado.fmf.uni-lj.si/pub/networks/pajek/doc/draweps.htm
    for format information.
    """
    with open(path, 'r', encoding=encoding) as lines:
      #lines = (line.decode(encoding) for line in path)
      return my_parse_pajek(lines, encoding)




if __name__ == '__main__':
  #G = my_read_pajek("D:/dropbox/2013_lecture_1st/japangraph_pajek_xy2_eng.net")
  #G = my_read_pajek("pajektest.net")
  G = my_read_pajek("../../Shimano/red08/corr_betacell_6w.net")
  print(G.nodes(data=True))
  #xs = nx.get_node_attributes(G, 'y')
  nx.write_pajek(G, "../../Shimano/test_write.net")
  #print(xs)