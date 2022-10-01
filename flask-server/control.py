from event_log import EventLog
from logs_graph import Graph
from filter_class import FilterOut, FlowSelection, ThroughPut, RemoveBehavior


class Control():

    def __init__(self):
        self.currentEventLog = EventLog()  # Maybe this is not needed
        self.graph = None
        #self.filters = self.initFilters()
        self.filtersdict = {"filterOut": FilterOut, "flowSelection": FlowSelection, "throughPut": ThroughPut, "removeBehavior": RemoveBehavior}

    def loadRawfile(self, json):
        self.currentEventLog.populateTracesFromCSV(
            json["content"]["data"], json["timestampformat"], json["timestampcolumn"], json["activitycolumn"], json["tracecolumn"])
        self.graph = Graph(self.currentEventLog)

        self.graph.logdetails = json
        print(self.currentEventLog)

    def parse_parameters(self, parameters_string):
        print(parameters_string)
        p = parameters_string.split(";")
        return p

    def filterFromJson(self, json):  # TODO: this method could probably be written more agile
        return self.filtersdict[json["filterName"]].generateFilter(self.parse_parameters(json["activityName"]))

    def filterFromJson_no_parsing(self, json):  # TODO: this method could probably be written more agile
        return self.filtersdict[json["filterName"]].generateFilter(json["activityName"])

    # maybe the filter is going to be json format, the idea of the code should still hold
    def applyFilter(self, json):
        print(json)
        # something else  json with id: , filtertype:, parater:,
        # get id of node to be filtered
        id = json["id"]
        # create filter to be applied
        filter = self.filterFromJson(json)

        allOperations = list(
            map(self.filterFromJson_no_parsing, json["previousOperations"]))

        allOperations.append(filter)

        self.graph.addOperation(
            currentNode=self.graph.getNodefromId(id),
            operations=allOperations,
            newEventLog=filter.filter(self.graph.getNodefromId(
                id).eventLog.copy())
        )

    def getEdgesAsJson(self):
        map = self.reverseGraphTrieMap()
        print(str({"levels": self.graph.getCleanGraph(),
              "edges": self.graph.getEdges()}).replace("\'", "\""))
        return str({"levels": self.graph.getCleanGraph(), "edges": self.graph.getEdges(), "map": map}).replace("\'", "\"")

    def reverseGraphTrieMap(self):
        reverse = {}
        for key in self.graph.map_trie_graph.keys():
            for elemnt in self.graph.map_trie_graph[key]:
                st_elem = str(elemnt)
                reverse[st_elem] = key
        return reverse

    def getEdgesAsJsonHistory(self):
        nod, ed, hist = self.graph.getCleanGraphTrie(False)
        levels = []
        for key in nod.keys():
            levels.append({"id": int(key), "nodes": nod[key]})
        print(str({"levels": levels,
              "edges": ed}).replace("\'", "\""))
        print(self.graph.map_trie_graph)
        print("historys:", hist)
        map = self.reverseGraphTrieMap()
        print(map)
        return str({"levels": levels, "edges": ed, "map": map}).replace("\'", "\"")

    def getEventLog(self):
        log = self.graph.lastNode
        nod, ed, history = self.graph.getCleanGraphTrie(False)
        print("LASTNODEID", self.graph.lastNode)
        return str({"logId": self.graph.lastNode, "eventLog": self.graph.getEventLogFromId(log), "history": history[self.graph.lastNode]}).replace("\'", "\"")

    def changeLastNode(self, json):
        print(json)
        self.graph.lastNode = json["id"]

    def create_snapshot(self, json):
        fname = '../snapshot/snapshot.py'
        rawlogname = '../snapshot/rawLog.py'
        nod, ed, history = self.graph.getCleanGraphTrie(True)

        dependencies = 'event_log.py'

        with open(dependencies, 'r') as d:
            dep_str = d.read()
            d.close()

        script = "\n\n\n\n #DEPENDENCIES:  \nfrom rawLog import rawlog\n\n " + dep_str
        script = script + \
            "\n\n\neventlog = EventLog()\nif (path_to_file == \"\"):\n    eventlog.populateTracesFromCSV(\nrawlog, \"{0}\", {1}, {2}, {3})\nelse:\n    eventlog.actuallyPopulateTracesFromCSV(path_to_file, timestring, timeColumn, activityColumn, traceColumn, seperator)".format(
                self.graph.logdetails["timestampformat"], self.graph.logdetails["timestampcolumn"], self.graph.logdetails["activitycolumn"], self.graph.logdetails["tracecolumn"])

        var_string = "#VARIABLES: \nSEED = 10\n"
        for i, filter in enumerate(history[json["id"]]):
            cmt = filter.get_comment()
            fct, vars, vals = filter.get_function(i)
            for j, var in enumerate(vars):
                var_string += "\n" + var + " = " + vals[j]

            script = script + "\n" + cmt + "\n" + \
                fct
        print(script)
        script = var_string + "\n" + "# For using different eventlog (leave path_to_file empty to use original eventlog): \npath_to_file = \"\" \ntimestring = \"\"\ntimeColumn = 0\nactivityColumn = 0\ntraceColumn = 0\nseperator = \",\" \n\n\n" + script + \
            "\neventlog.export(\"final.csv\")"

        rawlog = "rawlog ={}".format(self.graph.logdetails["content"]["data"])
        with open(rawlogname, 'w') as r:
            r.write(rawlog)
            r.close()

        with open(fname, 'w') as f:
            f.write(script)
            f.close()
