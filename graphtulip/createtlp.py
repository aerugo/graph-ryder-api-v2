from tulip import *
from py2neo import *
import configparser

config = configparser.ConfigParser()
config.read("config.ini")


class CreateTlp(object):
    def __init__(self):
        super(CreateTlp, self).__init__()
        print('Initializing')

        self.neo4j_graph = Graph(host=config['neo4j']['url'], user=config['neo4j']['user'], password=config['neo4j']['password'])
        self.tulip_graph = tlp.newGraph()
        self.tulip_graph.setName('opencare')

        # Entities properties
        self.tmpIDNode = self.tulip_graph.getIntegerProperty("tmpIDNode")
        self.tmpIDEdge = self.tulip_graph.getIntegerProperty("tmpIDEdge")
        self.labelsNodeTlp = self.tulip_graph.getStringVectorProperty("labelsNodeTlp")
        self.labelEdgeTlp = self.tulip_graph.getStringProperty("labelEdgeTlp")
        self.nodeProperties = {}
        self.edgeProperties = {}
        self.indexNodes = {}

        # todo pass in parameters labels and colors
        self.labels = ["title", "subject", "name"]
        self.colors = {"uid": tlp.Color(51,122,183), "pid": tlp.Color(92,184,92), "cid": tlp.Color(240, 173, 78),  "edges": tlp.Color(204, 204, 204)}

    def managePropertiesEntity(self, entTlp, entN4J, entProperties):
        for i in entN4J.properties:
            tmpValue = str(entN4J.properties[i])
            if i in self.labels:
                word = tmpValue.split(' ')
                if len(word) > 3:
                    tmpValue = "%s %s %s ..." % (word[0], word[1], word[2])
                entProperties["viewLabel"] = self.tulip_graph.getStringProperty("viewLabel")
                entProperties["viewLabel"][entTlp] = tmpValue
            if i in self.colors.keys():
                entProperties["viewColor"] = self.tulip_graph.getColorProperty("viewColor")
                entProperties["viewColor"][entTlp] = self.colors.get(i)
            if i in entProperties:
                entProperties[i][entTlp] = tmpValue
            else:
                entProperties[i] = self.tulip_graph.getStringProperty(i)
                entProperties[i][entTlp] = tmpValue

    def manageLabelsNode(self, labelsNode, nodeTlp, nodeN4J):
        tmpArrayString = []
        for s in nodeN4J.properties:
            tmpArrayString.append(s)
        labelsNode[nodeTlp] = tmpArrayString

    def createNodes(self, req):
        # Expected Format :  RETURN ID(n),n
        result = self.neo4j_graph.run(req)
        for qr in result:
            if not qr[0] in self.indexNodes:
                n = self.tulip_graph.addNode()
                self.managePropertiesEntity(n, qr[1], self.nodeProperties)
                self.manageLabelsNode(self.labelsNodeTlp, n, qr[1])
                self.tmpIDNode[n] = qr[0]
                # keep the reference for edges creation
                self.indexNodes[qr[0]] = n

    def createEdges(self, req):
        # Expected Format : RETURN ID(e),ID(n1),ID(n2),n2,e
        # If n2 not exist it will be create
        result = self.neo4j_graph.run(req)
        for qr in result:
            # add new nodes
            if not qr[2] in self.indexNodes:
                n = self.tulip_graph.addNode()
                self.managePropertiesEntity(n, qr[3], self.nodeProperties)
                self.manageLabelsNode(self.labelsNodeTlp, n, qr[3])
                self.tmpIDNode[n] = qr[2]
                # keep the reference for edges creation
                self.indexNodes[qr[2]] = n

            # edge
            e = self.tulip_graph.addEdge(self.indexNodes[qr[1]], self.indexNodes[qr[2]])
            self.managePropertiesEntity(e, qr[4], self.edgeProperties)
            # manageLabelEdge(self.labelEdgeTlp,e,qr[3])
            self.edgeProperties["viewLabel"] = self.tulip_graph.getStringProperty("viewLabel")
            self.edgeProperties["viewLabel"][e] = qr[4].type()
            self.edgeProperties["viewColor"] = self.tulip_graph.getColorProperty("viewColor")
            self.edgeProperties["viewColor"][e] = self.colors['edges']
            self.edgeProperties["type"] = self.tulip_graph.getStringProperty("type")
            self.edgeProperties["type"][e] = "curvedArrow"
            self.labelEdgeTlp[e] = qr[4].type()
            self.tmpIDEdge[e] = qr[0]

    def createWithParams(self, params, private_gid):
        # create nodes pass in params
        for param in params:
            field, value = param
            # Prepare node request
            node_req = "MATCH (n { %s : %s}) RETURN ID(n),n" % (field, value)
            # Get the nodes of Neo4J
            self.createNodes(node_req)
            # Request neighboors of main nodes
            edges_req = "MATCH (n1 {%s : %s})-[e]-(n2) " % (field, value)
            edges_req += "WHERE NOT (n1)-[e:CREATED_ON]-(n2) "
            edges_req += "AND NOT (n1)-[e:POST_ON]-(n2) "
            edges_req += "AND NOT (n1)-[e:GROUP_IS]-(n2) "
            edges_req += "RETURN ID(e),ID(n1),ID(n2),n2,e"
            # Get the edges of Neo4J
            print("Read Edges")
            self.createEdges(edges_req)

            # GOOD RESULT BUT GREEDY
        # # Search for connection between nodes
        # if len(params) > 1:
        #     for nodeActual in self.indexNodes:
        #         for nodeOther in self.indexNodes:
        #             edges_req = "MATCH (n1)-[e]->(n2) "
        #             edges_req += "WHERE ID(n1) = %s " % nodeActual
        #             edges_req += "AND ID(n2) = %s " % nodeOther
        #             edges_req += "RETURN ID(e),ID(n1),ID(n2),n2,e"
        #             self.createEdges(edges_req)

        print("Export")
        tlp.saveGraph(self.tulip_graph, "%s%s.tlp" % (config['exporter']['tlp_path'], private_gid))
