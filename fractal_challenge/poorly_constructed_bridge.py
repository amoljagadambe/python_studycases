def convert_to_adjacency_graph(pillars_connections: list):
    adjacency_graph_dictionary = {}
    for index, adjacency_list in enumerate(pillars_connections):
        connection_list = []
        for value_index, values in enumerate(adjacency_list):
            if values == 1 and value_index != index:
                connection_list.append(value_index)
        adjacency_graph_dictionary[index] = connection_list
    return adjacency_graph_dictionary


def dfs_for_cycle(u, color, parent):
    color[u] = 'G'
    for v in adj_list[u]:
        if color[v] == 'W':
            parent[v] = u
            cycle = dfs_for_cycle(v, color, parent)
            if cycle:
                return True
        elif color[v] == "G" and parent[u] != v:
            return True
    color[u] = "B"
    return False


if __name__ == "__main__":
    """
    P.S : (IMPORTANT) this solution will only work if there is only one cycle present in graph
    and that cycle will end on start node like shown in below fig E.G
                
             -->(1)-----(2)---(3)
                 |       |
                 |       |
                (5)-----(4)---(6)
                
    """
    pillars_connection_list_test = [[1, 1, 0, 0, 0, 0, 0],
                                    [1, 1, 1, 1, 0, 0, 0],
                                    [0, 1, 1, 0, 0, 0, 0],
                                    [0, 1, 0, 1, 1, 0, 0],
                                    [0, 0, 0, 0, 1, 1, 0],
                                    [0, 0, 0, 1, 1, 1, 1],
                                    [1, 0, 0, 0, 0, 1, 1]]

    num_of_pillars = int(input())  # Input the number of pillars
    pillars_connection_list = []
    for _ in range(num_of_pillars):
        list_of_numbers = list(map(int, input().split()))  # Input for the connections
        pillars_connection_list.append(list_of_numbers)

    color = {}
    parent = {}
    adj_list = convert_to_adjacency_graph(pillars_connection_list)

    for u in adj_list.keys():
        color[u] = 'W'
        parent[u] = None

    is_cyclic = False
    for u in adj_list.keys():
        if color[u] == 'W':
            is_cyclic = dfs_for_cycle(u, color, parent)
            if is_cyclic:
                break
    if is_cyclic:
        print(1)
    else:
        print(0)

