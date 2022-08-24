from asyncio.windows_events import NULL
from warnings import filters
from event_log import EventLog
from logs_graph import Graph
from filter_class import FilterOut


class Control():

    def __init__(self):
        self.currentEventLog = EventLog() #Maybe this is not needed
        self.graph = NULL
        self.filters = self.initFilters()

    def loadRawfile(self, json):
        self.currentEventLog.populateTracesFromCSV(json["content"]["data"], json["timestampformat"], json["timestampcolumn"], json["activitycolumn"], json["tracecolumn"])
        self.graph = Graph(self.currentEventLog)
        print(self.currentEventLog)

    def initFilters(self):
        return [FilterOut()]

    def applyFilter(self, json): # maybe the filter is going to be json format, the idea of the code should still hold
        id = json["id"] # something else  json with id: , filtertype:, parater:,
        for filter in self.filters:
            if filter.getName() == json["filterName"]: #is not going to be just like this couse filter most probably holds also the parameters
                self.graph.createNewEdge(
                                        self.graph.getNodefromId(id), 
                                        filter.getName() + json["parameters"], 
                                        filter.filter(self.graph.getNodefromId(id).eventLog.copy(), json["parameters"])
                                        )
                break

    def getEdgesAsJson(self):
        return str({"edges":self.graph.getEdges()})
