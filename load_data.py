from xml.dom import minidom
from collections import defaultdict
import joblib

mydoc = minidom.parse('big_map.osm')
nodes = mydoc.getElementsByTagName('node')

node_hash = {}
for node in nodes:
    nid = int(node.attributes["id"].value)
    lat = float(node.attributes["lat"].value)
    lon = float(node.attributes["lon"].value)
    node_hash[nid] = (lat, lon)



ways = mydoc.getElementsByTagName('way')
road_ways = {}
types = set()
house_ways = {}
for way in ways:
    wid = int(way.attributes["id"].value)
    way_nodes = []
    road=False
    name=""
    road_type=""
    house=False
    house_type=""
    for cn in way.childNodes:
        if cn.nodeName == "nd":
            way_nodes.append(int(cn.attributes["ref"].value))
        elif cn.nodeName == "tag":
            k,v = cn.attributes["k"].value, cn.attributes["v"].value
            if k=="highway":
                road=True
                road_type=v
                types.add(road_type)
            if k=="name":
                name=v
            if k=="addr:housenumber":
                house=True
            if k=="building":
                house=True
                house_type=v

    if road and not road_type in ("footway","pedestrian", "service", "cycleway", "steps"):
        road_ways[wid] = {"nodes": way_nodes,
                          "name": name,
                          "id": wid,
                          "type": road_type}

    if house and house_type not in ("garage", ):
        house_ways[wid] = {"nodes": way_nodes, "id": wid}

joblib.dump((node_hash,house_ways,road_ways), "parsed_data.pkl")
