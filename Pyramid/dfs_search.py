def conflict(cu1_ind, cu2_ind,cu_table):
    #print "cu 1 index: ", cu1_ind, " cu 2 index: ", cu2_ind
    flag = False 
    if cu1_ind == cu2_ind:
        flag = True
        return flag
    else:
        pair = (cu1_ind,cu2_ind)
        if cu_table.has_key(pair):
            flag = cu_table[pair]
        else:
            #swap the index
            pair = (cu2_ind,cu1_ind)
            flag = cu_table[pair]       
    return flag 
    
def pull_WAS(path,graphlist,start):
    #print "path : ", path
    was = 0
    count = {}
    a_s = {}
    #print path
    for item in path:
        # k: current layer index 
        k = len(graphlist[item].members)
        if count.has_key(k):
            count[k] += 1 
        else:
            count[k] = 1 
        if a_s.has_key(k):
            a_s[k] += float(graphlist[item].WAS)/k 
        else:
            a_s[k] = float(graphlist[item].WAS)/k
    for key, value in count.items():
        was += a_s[key] / value 
    #was += graphlist[start].WAS
    return was 

#def CheckWAS(node_path, interpath, count, )
"""
Bugs:
longest_path, max_was, interpath, node_path = dfs_search(adj_matrix, 30,nodelist, cand_graphs,cu_table)

return [24, 27, 36, 39, 42]
but adj_matrix[24] = [25, 27, 40, 43]
36, 39 is not compatible with 24
"""
def Modified_dfs(graph, start,graphlist,cu_table):
    path = []
    interpath = {}
    count = 0 
    longest_path = []
    max_was = 0 
    scope = graph[start]
    for index in range(0,len(scope)-1):
        item = scope[index]
        current_scope = graph[item]
        path = [start,item]
        flag = False
        for iind in range(index+1,len(scope)):
            curr_item = scope[iind]
            for thing in path:
                if cu_table[(thing,curr_item)]:
                    flag = True
                else:
                    pass
            if flag:
                pass
            else:
                path.append(curr_item)
        interpath[count] = path
        count += 1    

    for k,v in interpath.items():
        path = v[:]
        new_was = pull_WAS(path,graphlist,start)
        #print "Update WAS", new_was
        if new_was > max_was:
            longest_path = path[:]
            max_was = new_was
        else:
            pass

    return longest_path, max_was