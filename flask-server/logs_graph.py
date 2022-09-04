from platform import node
from trie import Trie
# An eventLog has to be a set of all traces
import math


class Node:  # alias Log

    def __init__(self, eventLog, id):
        self.eventLog = eventLog
        self.hash = self.hashNode(eventLog)
        self.id = id

    def hashNode(self, eventLog):
        hash = ""
        # NOTE maybe since the order of the traces should not matter they should be ordered with respect to the alphabetical order of the ids
        traces = eventLog.traces
        for trace in traces:
            hash += trace.getHash()  # NOTE all equivalent event-log must have the same hash
        return hash

    def getEventLog(self):
        return self.eventLog.getAsList()


class Graph:

    def __init__(self, eventLog):
        self.root = Node(eventLog.copy(), 0)  # maybe it is not needed
        self.nodes = [self.root]

        self.trie = Trie()
        self.adjecency_graph = [[]]
        self.lastNode = 0

        self.nr_trie_nodes = 1
        self.map_trie_graph = {0: [0]}

    # Whenever a diff (filter) is created we need to generate a new node
    # [operation] or list of diff/filter that have been applied in the path
    def addOperation(self, currentNode, newEventLog, operations):
        id = self.trie.search(operations)
        if not id:
            # NOTE is going to be a problem if we delete nodes
            newNodeNotChecked = Node(newEventLog, len(self.nodes))

            # check if node already exists
            newNode = self.checkForMatch(newNodeNotChecked)
            self.trie.insert(operations, self.nr_trie_nodes)

            self.map_trie_graph[newNode.id].append(self.nr_trie_nodes)

            self.adjecency_graph[currentNode.id].append(
                (operations[-1], newNode.id))
            self.lastNode = self.nr_trie_nodes
            self.nr_trie_nodes += 1
        else:
            print("IDi", id)
            self.lastNode = id

    def getEventLogFromId(self, id):
        print(self.trie)
        node = self.getNodefromId(id)
        return node.getEventLog()

    # returns the new node or the equivalent old one

    def checkForMatch(self, newNode):
        for node in self.nodes:
            if node.hash == newNode.hash:
                if True:  # TODO here we need a further check, maybe done line by line in each trace between the two eventlogs

                    return node
        # if node does not match with any other node, add an entry to node list and adjacency graph
        self.nodes.append(newNode)
        self.adjecency_graph.append([])
        self.map_trie_graph[newNode.id] = []
        return newNode

    def getNodefromId(self, id):

        return self.nodes[self.cleanNodeFromTrieNode(id)]

    def getEdges(self):
        result = []
        for node_id, next_nodes in enumerate(self.adjecency_graph):
            for (operation, next_node_id) in next_nodes:
                result.append({"parentNode": node_id,
                              "childrenNode": next_node_id, "operation": operation.getName()})
        return result

    def getCleanGraph(self):
        result = [{"id": 0, "nodes": [0]}]
        self.getCleanGraphRecorsive(1, [0], [0], result)
        return result

    def getCleanGraphRecorsive(self, level, alradyScoutedNodes, nodesFromPreviousLayer, result):
        nodes = []
        nodesForNextLayer = []
        for previousNode in nodesFromPreviousLayer:
            for operation, node in self.adjecency_graph[previousNode]:
                if node not in alradyScoutedNodes:
                    nodes.append(node)
                    alradyScoutedNodes.append(node)
                    nodesForNextLayer.append(node)
        if len(nodes) > 0:
            result.append({"id": level, "nodes": nodes})
            self.getCleanGraphRecorsive(
                level + 1, alradyScoutedNodes, nodesForNextLayer, result)

    def getCleanGraphTrie(self):
        nodes = {"0": [0]}
        edges = []
        node_history = {0: []}
        self.getCleanGraphRecursiveTrie(
            0, edges, nodes, node_history, self.trie.child)
        return nodes, edges, node_history

    def getCleanGraphRecursiveTrie(self, level, edges, nodes, node_history, current):
        next = []
        for key in current.keys():
            if type(key) != str:
                print(current[key])
                next.append(current[key])
                if level+1 not in nodes:
                    nodes[level+1] = []
                nodes[level+1].append(current[key]["#"])
                history = node_history[current["#"]].copy()
                history.append(key.getDict())
                print("HISTORY AFTER COPY", history)
                node_history[current[key]["#"]] = history
                edges.append(
                    {"parentNode": current["#"], "childrenNode": current[key]["#"], "operation": key.getName()})

        for n in next:
            self.getCleanGraphRecursiveTrie(
                level+1, edges, nodes, node_history, n)

    def cleanNodeFromTrieNode(self, trieNodeId):

        for key in self.map_trie_graph.keys():

            if trieNodeId in self.map_trie_graph[key]:
                return key
