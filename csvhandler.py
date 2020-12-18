from copy import deepcopy
from csv import reader
from datetime import datetime
from geopy import point as gepoint
from geopy import distance as gedistance
from json import dumps
from pathlib import Path
from random import randint
from re import compile
from tinydb import TinyDB, Query
from zipfile import ZipFile
from xml.etree import ElementTree


def read_csv(file_path):
    """Opens *.CSV file. Expects even amount of sites"""
    with open(file_path, mode='r') as file:
        csv_reader = list(reader(file, delimiter=','))
        csv_reader = list(filter(lambda x: len(x) != 0, csv_reader))
        if len(csv_reader) % 2 != 0:
            print('ERROR. The number of sites must be even')
        else:
            print(f'The total amount of links: {len(csv_reader) // 2}')
            return csv_reader


def create_links(sites):
    """Combines sites to links"""
    links = {}
    link = {'Site A': {}, 'Site B': {}, 'Requirements': {}}
    sites_even = sites[::2]
    sites_odd = sites[1::2]
    for id in range(len(sites_even)):
        key = f'From {sites_even[id][0]} to {sites_odd[id][0]}'
        links[key] = deepcopy(link)
        links[key]['Site A']['Name'] = sites_even[id][0]
        links[key]['Site A']['Latitude'] = sites_even[id][1]
        links[key]['Site A']['Longitude'] = sites_even[id][2]
        links[key]['Site A']['Height'] = sites_even[id][3]
        links[key]['Site B']['Name'] = sites_odd[id][0]
        links[key]['Site B']['Latitude'] = sites_odd[id][1]
        links[key]['Site B']['Longitude'] = sites_odd[id][2]
        links[key]['Site B']['Height'] = sites_odd[id][3]
        links[key]['Requirements']['Frequency range'] = '5'
        links[key]['Requirements']['Bandwidth'] = '40'
        links[key]['Requirements']['Capacity'] = '1'
        links[key]['Requirements']['Availability'] = '99.99'
    return links


def get_recommendations(link, table):
    """Selects the best option for the requested throughput among all products"""

    req_band = link['Requirements']['Bandwidth']
    req_cap = int(link['Requirements']['Capacity'])
    req_avail = link['Requirements']['Availability']

    exlcude_quanta = False
    exlcude_xg = False
    exlcude_e5000 = False
    exclude_r5000_pro = False
    exclude_r5000_lite = False

    point_a = gepoint.Point(latitude=link['Site A']['Latitude'], longitude=link['Site A']['Longitude'])
    point_b = gepoint.Point(latitude=link['Site B']['Latitude'], longitude=link['Site B']['Longitude'])
    link_distance = round(gedistance.distance(point_a, point_b).km, 2)

    candidates = []
    for device in table:
        device_capacity = device['Capacity'].get(req_band)
        if device_capacity is None:
            print(f'Запрашиваемая ширина канала не поддерживается {device["Name"]}')
            continue
        modulations = list(device_capacity.items())
        modulations = list(filter(lambda x: x[1] >= req_cap, modulations[:-1])) + [modulations[-1]]
        modulation_closest = min(modulations, key=lambda x: abs(x[1] - req_cap))
        device_availability = device['Availability'].get(req_avail).get(req_band)
        modulation_distance = device_availability.get(modulation_closest[0])

        if device['Family'] == 'InfiLINK XG':
            weight_cost = -1000
            weight_exclude = 10000 if exlcude_xg else 0
        elif 'Quanta' in device['Family']:
            weight_cost = -2000
            weight_exclude = 10000 if exlcude_quanta else 0
        elif device['Family'] == 'InfiLINK Evolution':
            weight_cost = -3000
            weight_exclude = 10000 if exlcude_e5000 else 0
        elif device['Family'] == 'InfiLINK 2x2 PRO':
            weight_cost = -4000
            weight_exclude = 10000 if exclude_r5000_pro else 0
        elif device['Family'] == 'InfiLINK 2x2 LITE':
            weight_cost = -5000
            weight_exclude = 10000 if exclude_r5000_lite else 0

        if req_cap > modulation_closest[1]:
            weight_capacity = weight_cost * -1
        else:
            weight_capacity = weight_cost

        if (link_distance - modulation_distance) > 0:
            weight_capacity = weight_cost * -1
            weight_distance = link_distance - modulation_distance
        else:
            weight_distance = (link_distance - modulation_distance) * -1

        weight = weight_capacity + weight_distance + weight_exclude

        candidates.append((weight, device['Name']))

    return min(candidates)[1]


def create_project_link(link, site_id):
    project_site_template = {'id': None,
                             'name': None,
                             'location': {'latitude': None, 'longitude': None},
                             'antennaHeight': None,
                             'deviceProductKey': None,
                             'antennaPartNumber': None,
                             'rfCablePartNumber': None,
                             'relocationLocked': True,
                             'interference': '-Infinity',
                             'temperature': 293.15
                             }
    project_site_a = deepcopy(project_site_template)
    project_site_b = deepcopy(project_site_template)
    project_link_template = {'terrainType': 'AVERAGE',
                             'climateType': 'NORMAL',
                             'frequencies': {'start': 4900, 'end': 5010},
                             'band': 5000,
                             'transmissionType': 'SINGLE_CARRIER',
                             'bandwidth': 40,
                             'goal': {'type': 'DISTANCE', 'value': 30000},
                             'txPowerLimit': 'Infinity',
                             'eirpLimit': None,
                             'temperature': 293.15,
                             'totalAirPressure': 800,
                             'humidity': 60,
                             'startSite': project_site_a,
                             'endSite': project_site_b
                             }
    project_link = deepcopy(project_link_template)

    site_a = link['Site A']
    site_b = link['Site B']
    equipment = link['Equipment']

    project_site_a['id'] = site_id
    project_site_b['id'] = site_id + 1
    project_site_a['name'] = site_a['Name']
    project_site_b['name'] = site_b['Name']
    project_site_a['location']['latitude'] = site_a['Latitude']
    project_site_b['location']['latitude'] = site_b['Latitude']
    project_site_a['location']['longitude'] = site_a['Longitude']
    project_site_b['location']['longitude'] = site_b['Longitude']
    project_site_a['antennaHeight'] = site_a['Height']
    project_site_b['antennaHeight'] = site_b['Height']
    project_site_a['deviceProductKey'] = f'{equipment["Family"]}#{equipment["Model"]}'.replace(' PRO', '')
    project_site_b['deviceProductKey'] = f'{equipment["Family"]}#{equipment["Model"]}'.replace(' PRO', '')
    if equipment['Type'] == 'external':
        project_site_a['antennaPartNumber'] = equipment['Antenna']
        project_site_b['antennaPartNumber'] = equipment['Antenna']
        project_site_a['rfCablePartNumber'] = equipment['RF Cable']
        project_site_b['rfCablePartNumber'] = equipment['RF Cable']

    project_link['bandwidth'] = link['Requirements']['Bandwidth']
    project_link['startSite'] = project_site_a
    project_link['endSite'] = project_site_b

    return project_link


def create_project(project_name, project_links, project_sites):
    project = {'appVersion': '609ef5b',
               'appVersionFull': '609ef5b',
               'linksArray': project_links,
               'sitesArray': project_sites,
               'obstaclesArray': [],
               'project': {'id': f'{randint(45000, 99999)}',
                           'name': f'{project_name}',
                           'type': 'PTP',
                           'regulation': 'WORLDWIDE',
                           'unitSystem': 'METRIC',
                           'settings': {'ptmp': {'visible': True}},
                           'updatedDatetime': f'{datetime.now()}',
                           'createNew': 0
                           }
               }

    kml_attributes = {'xmlns': 'http://www.opengis.net/kml/2.2',
                      'xmlns:gs': 'http://earth.google.com/kml/2.1',
                      'xmlns:kml': 'http://www.opengis.net/kml/2.2',
                      'xmlns:atom': 'http://www.w3.org/2005/Atom',
                      'xmlns:infidata': 'http://infinet.ru/kml'}

    root = ElementTree.Element('kml', kml_attributes)
    document = ElementTree.SubElement(root, 'Document')
    extended_data = ElementTree.SubElement(document, 'ExtendedData')
    ElementTree.SubElement(extended_data, 'infidata:json').text = dumps(project)

    tree = ElementTree.ElementTree(root)
    tree.write('doc.kml', encoding='UTF-8', xml_declaration=True)
    with ZipFile(f'{project_name}.kmz', 'w') as kmz:
        kmz.write('doc.kml')
    file_kml = Path('doc.kml')
    file_kml.unlink()


def start():
    file_csv = read_csv('example.csv')
    db = TinyDB('devices.db')
    equipment = Query()
    bom = {}
    project_name = 'DESK-11111'
    project_links = []
    project_sites = []
    project_counter = 400000

    links = create_links(file_csv)
    for link_name, link in links.items():
        req_freq = link['Requirements']['Frequency range']
        table = db.table(req_freq)
        recommendation = get_recommendations(link, table)
        links[link_name]['Equipment'] = dict(table.search(equipment.Name == recommendation)[0])
        del links[link_name]['Equipment']['Capacity']
        del links[link_name]['Equipment']['Availability']
        project_link = create_project_link(link, project_counter)
        project_counter += 2
        project_links.append(project_link)
        project_sites.append(project_link['startSite'])
        project_sites.append(project_link['endSite'])

    create_project(project_name, project_links, project_sites)
