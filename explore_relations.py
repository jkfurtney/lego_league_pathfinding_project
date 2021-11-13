from xml.dom import minidom
from collections import defaultdict

# parse an xml file by name
mydoc = minidom.parse('map.osm')

relations = mydoc.getElementsByTagName('way')
house_nodes = []
node_hash = {}
for relation in relations:
    print(relation.attributes["id"].value)
    for cn in relation.childNodes:
        if cn.nodeName == "tag":
            k,v = cn.attributes["k"].value, cn.attributes["v"].value
            print(k,v)
    print()
