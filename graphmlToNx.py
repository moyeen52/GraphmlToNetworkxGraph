__author__= "M A MOYEEN"
__license__ = "GNU General Public License v2.0"
__credits__=['sjas','M A MOYEEN']
__version__ = "1.0.1"
__maintainer__ = "M A MOYEEN"
__email__ = "moyeen.kuet@gmail.com"
import xml.etree.ElementTree as ET
import networkx as nx
import os,re,math
class GraphmlToNx:
    """
	 Generates graphml(like zoo topology) to networkx graph
	 @arguments:
               inputFile: input file

    """
    def __init__(self,*args,**kwargs):
        """
    	"""
        self.graphmlFile=kwargs['inputFile']
        #self.genNx()
    def genNx(self):
    	"""
    	 reads graphml and generates Networkx graph
    	"""
    	graph=nx.DiGraph()
    	xml_tree    = ET.parse(self.graphmlFile)
        ns   = "{http://graphml.graphdrawing.org/xmlns}"
        root_element    = xml_tree.getroot()
        graph_element   = root_element.find(ns + 'graph')
        index_values_set    = root_element.findall(ns + 'key')
        node_set            = graph_element.findall(ns + 'node')
        edge_set            = graph_element.findall(ns + 'edge')
        node_label_name_in_graphml = ''
        node_latitude_name_in_graphml = ''
        node_longitude_name_in_graphml = ''
	node_index_value     = ''
	node_name_value      = ''
	node_longitude_value = ''
	node_latitude_value  = ''
	# id:value dictionaries
	id_node_name_dict   = {}     # to hold all 'id: node_name_value' pairs
	id_longitude_dict   = {}     # to hold all 'id: node_longitude_value' pairs
	id_latitude_dict    = {}     # to hold all 'id: node_latitude_value' pairs
	# FIND OUT WHAT KEYS ARE TO BE USED, SINCE THIS DIFFERS IN DIFFERENT GRAPHML TOPOLOGIES
	for i in index_values_set:

	    if i.attrib['attr.name'] == 'label' and i.attrib['for'] == 'node':
		node_label_name_in_graphml = i.attrib['id']
	    if i.attrib['attr.name'] == 'Longitude':
		node_longitude_name_in_graphml = i.attrib['id']
	    if i.attrib['attr.name'] == 'Latitude':
		node_latitude_name_in_graphml = i.attrib['id']
	for n in node_set:

	    node_index_value = n.attrib['id']

	    #get all data elements residing under all node elements
	    data_set = n.findall(ns + 'data')

	    #finally get all needed values
	    for d in data_set:

		#node name
		if d.attrib['key'] == node_label_name_in_graphml:
		    #strip all whitespace from names so they can be used as id's
		    node_name_value = re.sub(r'\s+', '', d.text)
		#longitude data
		if d.attrib['key'] == node_longitude_name_in_graphml:
		    node_longitude_value = d.text
		#latitude data
		if d.attrib['key'] == node_latitude_name_in_graphml:
		    node_latitude_value = d.text

		#save id:data couple
		id_node_name_dict[node_index_value] = node_name_value
		id_longitude_dict[node_index_value] = node_longitude_value
		id_latitude_dict[node_index_value]  = node_latitude_value
		graph.add_node(node_index_value,label=node_name_value)
	distance = 0.0
	latency = 0.0
        edge_list=[]
	for e in edge_set:

	    # GET IDS FOR EASIER HANDLING
	    src_id = e.attrib['source']
	    dst_id = e.attrib['target']

	    # CALCULATE DELAYS

	    #    CALCULATION EXPLANATION
	    #
	    #    formula: (for distance)
	    #    dist(SP,EP) = arccos{ sin(La[EP]) * sin(La[SP]) + cos(La[EP]) * cos(La[SP]) * cos(Lo[EP] - Lo[SP])} * r
	    #    r = 6378.137 km
	    #
	    #    formula: (speed of light, not within a vacuumed box)
	    #     v = 1.97 * 10**8 m/s
	    #
	    #    formula: (latency being calculated from distance and light speed)
	    #    t = distance / speed of light
	    #    t (in ms) = ( distance in km * 1000 (for meters) ) / ( speed of light / 1000 (for ms))

	    #    ACTUAL CALCULATION: implementing this was no fun.

	    first_product               = math.sin(float(id_latitude_dict[dst_id])) * math.sin(float(id_latitude_dict[src_id]))
	    second_product_first_part   = math.cos(float(id_latitude_dict[dst_id])) * math.cos(float(id_latitude_dict[src_id]))
	    second_product_second_part  = math.cos((float(id_longitude_dict[dst_id])) - (float(id_longitude_dict[src_id])))

	    distance = math.radians(math.acos(first_product + (second_product_first_part * second_product_second_part))) * 6378.137

	    # t (in ms) = ( distance in km * 1000 (for meters) ) / ( speed of light / 1000 (for ms))
	    # t         = ( distance       * 1000              ) / ( 1.97 * 10**8   / 1000         )
	    latency = ( distance * 1000 ) / ( 197000 )
            edge_list.append((src_id,dst_id,{'delay':latency}))
        graph.add_edges_from(edge_list)
        return graph

graphmlNxObj=GraphmlToNx(inputFile='graphmlfiles/Abilene.graphml')
nxGraph=graphmlNxObj.genNx()
