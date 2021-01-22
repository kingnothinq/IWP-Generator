from collections import Counter
from configparser import ConfigParser
from copy import deepcopy
from csv import reader
from datetime import datetime
from geopy import point as gepoint
from geopy import distance as gedistance
from json import dumps
from logging import getLogger, StreamHandler, FileHandler, Formatter
from pathlib import Path
from random import randint
from re import compile
from tinydb import TinyDB, Query
from zipfile import ZipFile
from xml.etree import ElementTree


def read_csv(file_path):
    """Opens *.CSV file. Expects even amount of sites."""

    logger.info(f'Open CSV file: {file_path}')
    with open(file_path, mode='r') as file:
        csv_reader = list(reader(file, delimiter=','))
        csv_reader = list(filter(lambda x: len(x) != 0, csv_reader))
        if len(csv_reader) % 2 != 0:
            raise ValueError(f'{file_path} doesn\'t contains even number of rows.')
        else:
            return csv_reader


def create_links(sites):
    """Combine sites into links.
    Return a dictonary contains all links and their properties
    For example:
    {'Link name':
        {'Site A': {'Name': 'Home', 'Latitude': '59.6070142792', 'Longitude': '60.5717699289', 'Height': '60'},
         'Site B': {'Name': 'Damm', 'Latitude': '59.597915334', 'Longitude': '60.3832959195', 'Height': '60'},
         'Requirements':
             {'Frequency range': '5',
              'Bandwidth': '40',
              'Capacity': 1100,
              'Availability': '99.99',
              'Exclude':
                  {'xg1000': False, 'xg500': False, 'quanta': False,
                   'e5000': False, 'r5000_pro': False, 'r5000_lite': False}}}
    """

    def check_req_freq(req_freq):
        """Check what this frequency range is supported."""

        if req_freq in ['3', '4', '5', '6', '28', '70']:
            return req_freq
        else:
            raise ValueError(f'The requested frequency range cannot be {req_freq}. '
                             f'Appropriate values are 3, 4, 5, 6, 28, 70.')

    def check_req_bw(req_bw):
        """Check what this bandwidth is supported (cannot be zero)."""

        if int(req_bw) > 0:
            return req_bw
        else:
            raise ValueError(f'The requested bandwidth cannot be {req_bw}. '
                             f'Appropriate value must be greater than zero.')

    def check_req_cap(req_cap):
        """Check what this capacity is supported (cannot be zero)."""

        if int(req_cap) > 0:
            return int(req_cap)
        else:
            raise ValueError(f'The requested capacity  cannot be {req_cap}. '
                             f'Appropriate value must be greater than zero.')

    def check_req_avb(req_avb):
        """Check what this availability range is supported."""

        if req_avb in ['99.90', '99.99']:
            return req_avb
        else:
            raise ValueError(f'The requested availability cannot be {req_avb}. '
                             f'Appropriate value is either 99.90 or 99.99 %.')

    def check_req_exclude(req_exclude):
        """Parse excluded options."""

        result = {'XG 1000': False,
                  'XG 500': False,
                  'Quanta': False,
                  'E5000': False,
                  'R5000 Pro': False,
                  'R5000 Lite': False}
        pattern_xg1000 = compile(r'(xg1000)')
        pattern_xg500 = compile(r'(xg500)')
        pattern_quanta = compile(r'(quanta)')
        pattern_e5000 = compile(r'(e5000)')
        pattern_r5000_pro = compile(r'(r5000_pro)')
        pattern_r5000_lite = compile(r'(r5000_lite)')
        if pattern_xg1000.search(req_exclude.lower()) is not None:
            result['XG 1000'] = True
        if pattern_xg500.search(req_exclude.lower()) is not None:
            result['XG 500'] = True
        if pattern_quanta.search(req_exclude.lower()) is not None:
            result['Quanta '] = True
        if pattern_e5000.search(req_exclude.lower()) is not None:
            result['E5000'] = True
        if pattern_r5000_pro.search(req_exclude.lower()) is not None:
            result['R5000 Pro'] = True
        if pattern_r5000_lite.search(req_exclude.lower()) is not None:
            result['R5000 Lite'] = True
        return result

    links = {}
    link = {'Site A': {}, 'Site B': {}, 'Requirements': {}}
    # An even row is the first site, an odd row is the second site
    sites_even = sites[::2]
    sites_odd = sites[1::2]
    for link_id in range(len(sites_even)):
        name = f'From {sites_even[link_id][0]} to {sites_odd[link_id][0]}'
        links[name] = deepcopy(link)
        links[name]['Site A']['Name'] = sites_even[link_id][0]
        links[name]['Site A']['Latitude'] = sites_even[link_id][1]
        links[name]['Site A']['Longitude'] = sites_even[link_id][2]
        links[name]['Site A']['Height'] = sites_even[link_id][3]
        links[name]['Site B']['Name'] = sites_odd[link_id][0]
        links[name]['Site B']['Latitude'] = sites_odd[link_id][1]
        links[name]['Site B']['Longitude'] = sites_odd[link_id][2]
        links[name]['Site B']['Height'] = sites_odd[link_id][3]

        """
        If there are only 4 options in CSV, other values will be got from project defaults.
        Otherwise, parse them from CSV.
        """

        if len(sites_even[link_id]) == 4:
            links[name]['Requirements']['Frequency range'] = check_req_freq(config.get('Project', 'req_freq'))
            links[name]['Requirements']['Bandwidth'] = check_req_bw(config.get('Project', 'req_bw'))
            links[name]['Requirements']['Capacity'] = check_req_cap(config.get('Project', 'req_cap'))
            links[name]['Requirements']['Availability'] = check_req_avb(config.get('Project', 'req_avb'))
            links[name]['Requirements']['Exclude'] = check_req_exclude(config.get('Project', 'req_exclude'))
        elif len(sites_even[link_id]) == 9:
            if sites_even[link_id][4] == '':
                links[name]['Requirements']['Frequency range'] = check_req_freq(config.get('Project', 'req_freq'))
            else:
                links[name]['Requirements']['Frequency range'] = check_req_freq(sites_even[link_id][4])

            if sites_even[link_id][5] == '':
                links[name]['Requirements']['Bandwidth'] = check_req_bw(config.get('Project', 'req_bw'))
            else:
                links[name]['Requirements']['Bandwidth'] = check_req_bw(sites_even[link_id][5])

            if sites_even[link_id][6] == '':
                links[name]['Requirements']['Capacity'] = check_req_cap(config.get('Project', 'req_cap'))
            else:
                links[name]['Requirements']['Capacity'] = check_req_cap(sites_even[link_id][6])

            if sites_even[link_id][7] == '':
                links[name]['Requirements']['Availability'] = check_req_avb(config.get('Project', 'req_avb'))
            else:
                links[name]['Requirements']['Availability'] = check_req_avb(sites_even[link_id][7])

            if sites_even[link_id][8] == '':
                links[name]['Requirements']['Exclude'] = check_req_exclude(config.get('Project', 'req_exclude'))
            else:
                links[name]['Requirements']['Exclude'] = check_req_exclude(sites_even[link_id][8])
        else:
            raise ValueError(f'Site \'{sites_even[link_id][0]}\' must contain either 4 or 9 parameters.')

    return links


def get_recommendations(link, table):
    """Select the best option for the requested throughput among all products.
    Return the most suitable device option.
    """

    link_req_bw = link['Requirements']['Bandwidth']
    link_req_cap = int(link['Requirements']['Capacity'])
    link_req_avb = link['Requirements']['Availability']
    link_excl_xg1000 = link['Requirements']['Exclude']['XG 1000']
    link_excl_xg500 = link['Requirements']['Exclude']['XG 500']
    link_excl_quanta = link['Requirements']['Exclude']['Quanta']
    link_excl_e5000 = link['Requirements']['Exclude']['E5000']
    link_excl_r5000_pro = link['Requirements']['Exclude']['R5000 Pro']
    link_excl_r5000_lite = link['Requirements']['Exclude']['R5000 Lite']

    point_a = gepoint.Point(latitude=link['Site A']['Latitude'], longitude=link['Site A']['Longitude'])
    point_b = gepoint.Point(latitude=link['Site B']['Latitude'], longitude=link['Site B']['Longitude'])
    link_dist = round(gedistance.distance(point_a, point_b).km, 2)

    candidates = []
    for device in table:
        # Find relations between MCS and Throughput for the particular bandwidth and packs them to dev_modulations
        dev_cap = device['Capacity'].get(link_req_bw)
        if dev_cap is None:
            logger.debug(f'Link \'From {link["Site A"]["Name"]} to {link["Site B"]["Name"]}\'. '
                         f'{device["Model"]} doesn\'t support the requested bandwidth ({link_req_bw}).')
            continue
        dev_modulations = list(dev_cap.items())
        """
        If MCS doesn't satisfy the requested capacity need to filter it 
        but if there are no suitable MCSes at all 
        then it is needed to save the highest MCS in case no devices will be suitable.
        """
        dev_modulations = list(filter(lambda x: x[1] >= link_req_cap, dev_modulations[:-1])) + [dev_modulations[-1]]
        """
        Find the closest MCS to the requested capacity. 
        It will be the highest MCS if the device doesn't satisfy the requirements.
        """
        dev_mcs_clst = min(dev_modulations, key=lambda x: abs(x[1] - link_req_cap))
        # Find relations between MCS and Distance for the particular availability
        dev_avb = device['Availability'].get(link_req_avb).get(link_req_bw)
        dev_mcs_dist = dev_avb.get(dev_mcs_clst[0])

        """
        Calculate weights (the less the better).
        
        Default weight_cost:
        XG 1000 = -1000
        XG 500 = -2000
        Quanta 5, 6, 70 = -3000
        Evolution (E5000) = -4000
        R5000 Pro = -5000
        R5000 Lite = -6000
        
        If a family must be excluded, its weight becomes +100000.
        Therefore, it will be presented in the list of candidates but it always loses.
        
        After that, it is needed to choose a device from these families.
        If a device satisfies the requested capacity, its weight equals the family weight (weight_cost) but
        if the devices doesn't satisfy, its weight will be reversed.
        
        reversed weight_cost:
        XG 1000 = +1000
        XG 500 = +2000
        Quanta 5, 6, 70 = +3000
        Evolution (E5000) = +4000
        R5000 Pro = +5000
        R5000 Lite = +6000
        
        Therefore, if all families satisfy the requirements, the algorithm will offer the cheapest device 
        from suitable options, otherwise it will offer the most productive device.
        
        Afterward, it is needed to choose the most suitable antenna option. 
        If the device can reach the MCS that satisfies the requested capacity, weight_dist will be equal
        the difference between the MCS's distance and the link distance. 
        In the opposite case, the device is not suitable (cannot establish MCS) and 
        it loses and its weight_cost will be reversed.
        
        As a result, it is calculated how the final weight.
        """
        if device['Family'] == 'InfiLINK XG 1000':
            weight_cost = int(config.get('Settings', 'weight_xg1000'))
            weight_excl = int(config.get('Settings', 'weight_exclude')) if link_excl_xg1000 else 0
        elif device['Family'] == 'InfiLINK XG 500':
            weight_cost = int(config.get('Settings', 'weight_xg500'))
            weight_excl = int(config.get('Settings', 'weight_exclude')) if link_excl_xg500 else 0
        elif device['Family'] == 'Quanta 5' or device['Family'] == 'Quanta 6':
            weight_cost = int(config.get('Settings', 'weight_quanta'))
            weight_excl = int(config.get('Settings', 'weight_exclude')) if link_excl_quanta else 0
        elif device['Family'] == 'Quanta 70':
            weight_cost = int(config.get('Settings', 'weight_quanta_70'))
            weight_excl = int(config.get('Settings', 'weight_exclude')) if link_excl_quanta else 0
        elif device['Family'] == 'InfiLINK Evolution':
            weight_cost = int(config.get('Settings', 'weight_e5000'))
            weight_excl = int(config.get('Settings', 'weight_exclude')) if link_excl_e5000 else 0
        elif device['Family'] == 'InfiLINK 2x2 PRO':
            weight_cost = int(config.get('Settings', 'weight_r5000_pro'))
            weight_excl = int(config.get('Settings', 'weight_exclude')) if link_excl_r5000_pro else 0
        elif device['Family'] == 'InfiLINK 2x2 LITE':
            weight_cost = int(config.get('Settings', 'weight_r5000_lite'))
            weight_excl = int(config.get('Settings', 'weight_exclude')) if link_excl_r5000_lite else 0

        if link_req_cap > dev_mcs_clst[1]:
            weight_cap = weight_cost * -1
        else:
            weight_cap = weight_cost

        if (link_dist - dev_mcs_dist) > 0:
            weight_cap = weight_cost * -1
            weight_dist = link_dist - dev_mcs_dist
        #elif (link_dist - dev_mcs_dist) < 0 and weight_cap > 0:
            #weight_dist = (link_dist - dev_mcs_dist) * -1
        else:
            weight_dist = (link_dist - dev_mcs_dist) * -1

        weight = weight_cap + weight_dist + weight_excl

        candidates.append((weight, device['Name']))

    print(link)
    print(candidates)

    if len(candidates) == 0:
        raise ValueError(f'Link \'From {link["Site A"]["Name"]} to {link["Site B"]["Name"]}\'. '
                         f'There is no suitable equipment. Please check the requirements.')

    return min(candidates)[1]


def prepare_project(link, site_id):
    """Prepare link for importing to a KMZ project.
    It must follow InfiPLANNER KML template.
    KML contains JSON with linksArray and sitesArray,
    need to fill this structure to match the InfiPLANNER requirements.
    Return link for linksArray (linksArray contains sites for sitesArray)."""

    project_site_template = {'id': None,
                             'name': None,
                             'location': {'latitude': None, 'longitude': None},
                             'antennaHeight': None,
                             'deviceProductKey': None,
                             'antennaPartNumber': None,
                             'rfCablePartNumber': None,
                             'relocationLocked': True,
                             'interference': '-Infinity',
                             'temperature': 293
                             }
    project_site_a = deepcopy(project_site_template)
    project_site_b = deepcopy(project_site_template)
    project_link_template = {'terrainType': 'AVERAGE',
                             'climateType': 'NORMAL',
                             'frequencies': {'start': None, 'end': None},
                             'band': None,
                             'transmissionType': 'SINGLE_CARRIER',
                             'bandwidth': None,
                             'goal': {'type': 'DISTANCE', 'value': 30000},
                             'txPowerLimit': 'Infinity',
                             'eirpLimit': None,
                             'temperature': 293,
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

    if equipment['Family'] == 'InfiLINK 2x2 PRO' or equipment['Family'] == 'InfiLINK 2x2 LITE':
        equipment['Family'] = 'InfiLINK 2x2'
    if equipment['Family'] == 'InfiLINK XG 500':
        equipment['Family'] = 'InfiLINK XG'
    if config.get('Settings', 'region') == 'rus' and 'Quanta' in equipment['Family']:
        equipment['Family'] = equipment['Family'].replace('Quanta', 'Vector')
        equipment['Model'] = equipment['Model'].replace('Q', 'V')

    if equipment['Type'] == 'external':
        project_site_a['antennaPartNumber'] = equipment['Antenna']
        project_site_b['antennaPartNumber'] = equipment['Antenna']
        project_site_a['rfCablePartNumber'] = equipment['RF Cable']
        project_site_b['rfCablePartNumber'] = equipment['RF Cable']

    project_site_a['deviceProductKey'] = f'{equipment["Family"]}#{equipment["Model"]}'
    project_site_b['deviceProductKey'] = f'{equipment["Family"]}#{equipment["Model"]}'

    if link['Requirements']['Frequency range'] == '3':
        project_link['frequencies'] = {'start': 2990, 'end': 4010}
        project_link['band'] = 3000
    elif link['Requirements']['Frequency range'] == '4':
        project_link['frequencies'] = {'start': 3990, 'end': 5010}
        project_link['band'] = 4000
    elif link['Requirements']['Frequency range'] == '5':
        project_link['frequencies'] = {'start': 4850, 'end': 6050}
        project_link['band'] = 5000
    elif link['Requirements']['Frequency range'] == '6':
        project_link['frequencies'] = {'start': 6000, 'end': 6425}
        project_link['band'] = 6000
    elif link['Requirements']['Frequency range'] == '28':
        project_link['frequencies'] = {'start': 28000, 'end': 29000}
        project_link['band'] = 28000
    elif link['Requirements']['Frequency range'] == '70':
        project_link['frequencies'] = {'start': 70500, 'end': 76000}
        project_link['band'] = 70500

    project_link['bandwidth'] = link['Requirements']['Bandwidth']
    project_link['startSite'] = project_site_a
    project_link['endSite'] = project_site_b

    if equipment['Family'] == 'InfiLINK XG 1000':
        project_link['transmissionType'] = 'DUAL_CARRIER'

    return project_link


def create_project(pr_name, pr_links, pr_sites):
    """Create KMZ for InfiPLANNER and BOM."""

    if config.get('Output', 'output_folder') == 'default':
        if Path.is_dir(Path.cwd() / 'Output') is False:
            Path.mkdir(Path.cwd() / 'Output')
        output = Path.cwd() / 'Output'
    else:
        if Path.is_dir(Path(config.get('Output', 'output_folder'))) is False:
            Path.mkdir(Path(config.get('Output', 'output_folder')), parents=True, exist_ok=True)
        output = Path(config.get('Output', 'output_folder'))

    if config.get('Output', 'kmz_name') == 'default':
        kmz_name = f'{pr_name}'
    else:
        kmz_name = config.get('Output', 'kmz_name')
    kmz_path = output / f'{kmz_name}.kmz'
    kmz_counter = 0
    while True:
        if kmz_path.is_file() is True:
            kmz_counter += 1
            kmz_path = output / f'{kmz_name}_{kmz_counter}.kmz'
        else:
            break

    if config.get('Output', 'bom_name') == 'default':
        bom_name = f'{pr_name}'
    else:
        bom_name = config.get('Output', 'kmz_name')
    bom_path = output / f'{bom_name}.txt'
    bom_counter = 0
    while True:
        if bom_path.is_file() is True:
            bom_counter += 1
            bom_path = output / f'{bom_name}_{bom_counter}.txt'
        else:
            break

    # Prepare KMZ (doc.kml in an archive)
    project = {'appVersion': '609ef5b',
               'appVersionFull': '609ef5b',
               'linksArray': pr_links,
               'sitesArray': pr_sites,
               'obstaclesArray': [],
               'project': {'id': f'{randint(45000, 99999)}',
                           'name': f'{pr_name}',
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
    with ZipFile(kmz_path, 'w') as kmz:
        kmz.write('doc.kml')
    file_kml = Path('doc.kml')
    file_kml.unlink()

    # Prepare BOM
    bom = []
    for site in pr_sites:
        bom.append(site['deviceProductKey'].replace('#', ' '))
        if site['antennaPartNumber'] is not None:
            bom.append(site['antennaPartNumber'])
        if site['rfCablePartNumber'] is not None:
            bom.append(site['antennaPartNumber'])
    bom = Counter(bom)

    with open(bom_path, 'w') as bom_text:
        text = []
        for partnumber, counter in bom.items():
            text.append(f'InfiNet {partnumber}:  {counter} pc.')
        bom_text.write('\n'.join(text))


def handle(input_file):
    """Waits for a CSV file and returns a KMZ project + a TXT bill of materials"""

    if config.get('Database', 'db_path') == 'default':
        db_path = Path('devices.db')
    else:
        db_path = Path(config.get('Database', 'db_path'))

    db = TinyDB(db_path)
    equipment = Query()

    # Parse the CSV file and create a links array for future needs
    file_csv = read_csv(input_file)
    links = create_links(file_csv)

    project_name = Path(input_file).stem
    # linksArray
    project_links = []
    # sitesArray
    project_sites = []
    # site id
    project_counter = 400000
    for link_name, link in links.items():
        try:
            link_freq = link['Requirements']['Frequency range']
            table = db.table(link_freq)
            link_rec = get_recommendations(link, table)
            links[link_name]['Equipment'] = dict(table.search(equipment.Name == link_rec)[0])
            # They won't be needed else
            del links[link_name]['Equipment']['Capacity']
            del links[link_name]['Equipment']['Availability']
            # Prepare all information about the link for importing to InfiPLANNER
            project_link = prepare_project(link, project_counter)
            project_counter += 2
            project_links.append(project_link)
            project_sites.append(project_link['startSite'])
            project_sites.append(project_link['endSite'])
        except ValueError as error_msg:
            logger.exception(f'{error_msg}', exc_info=False)
        finally:
            continue
    # Create KMZ + BOM
    try:
        if len(project_links) == 0:
            raise ValueError(f'Something goes wrong. Please check the logs.')
        else:
            logger.info('Project has been successfully created.')
            create_project(project_name, project_links, project_sites)
    except ValueError as error_msg:
        logger.exception(f'{error_msg}', exc_info=False)


# Import config
config = ConfigParser(comment_prefixes='/', allow_no_value=True)
config_path = Path('config.ini')
config.read(config_path)

# Create logger
logger = getLogger(__name__)
logger.setLevel(level='DEBUG')

# Create path and filenames
log_path = Path.cwd() / 'Logs'
if Path.is_dir(log_path) is False:
    Path.mkdir(log_path)
log = log_path / f'{datetime.today().strftime("%Y_%m_%d")}.log'

# Create handlers
console_handler = StreamHandler()
file_handler = FileHandler(log)
console_handler.setLevel(level='DEBUG')
file_handler.setLevel(level='INFO')

# Create formatter and add it to handlers
form = '%(asctime)s - %(levelname)s - %(pathname)s - %(message)s'
formatter = Formatter(fmt=form, datefmt='%d-%b-%y %H:%M:%S')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

if __name__ == '__main__':
    # Work with files
    file_input = Path('example.csv')
    handle(file_input)
