1. Settings and options

Settings are stored in /config.ini

1.1 Setting partition

Region:
eng - Quanta and Q in partnumbers
rus - Vector and V in partnumbers

Weights:
The script uses weight to rank all devices in the database. The less weight they have, the better option this device is.
The algorithm:
1) Can a device satisfy the throughput requirement (is there a modulation that suits)? 
If yes:
It weight is chosen from the table below (default):
XG 1000 = -1000
XG 500 = -2000
Quanta 5, 6, 70 = -3000
Evolution (E5000) = -4000
R5000 Pro = -5000
R5000 Lite = -6000

If no:
It weight is chosen from the table below (reversed):
XG 1000 = +1000
XG 500 = +2000
Quanta 5, 6, 70 = +3000
Evolution (E5000) = +4000
R5000 Pro = +5000
R5000 Lite = +6000

So, the cheapest device will be recommended from all options that satisfy the throughput requirement. The most productive device will be recommended if no device satisfies the throughput requirement.

The result weight is weight_cost.

2) Can a device establish a link at the requested distance and with the suitable modulation? 
If yes: 
Need to sort devices by antenna gain: Link distance - MCS distance = weight_dist
weight_dist cannot be positive because this means that the modulation cannot be set at this distance.
For example:
Link distance is 10.69 km, MCS distance is 23.65 km
10.69 - 23.65 = -12.96
Therefore, -12.96 is this is a margin. Need to reverse it for further calculations.

If no:
Need to reverse weight_cost due to this device doesn't suit anymore. 
Need to sort devices by antenna gain: Link distance - MCS distance = weight_dist
The main idea is the same but there is no need to reverse the value.

3) Must this family be excluded? 
If yes:
weight_excl = 100000

If no:
weight_excl = 0

Then, this device is still an option but it will never win till other options are presented.

4) What is the final weight?
weight = weight_cap + weight_dist + weight_excl

Examples:

All yes:
Q5-23
weight = -3000 + 12.959999999999999 + 0 = -2987.04
R5000-Mmx/5.300.2x500.2x23
weight = -6000 + 10.88 + 0 = -5989.12
R5000-Mmx/5.300.2x500.2x26
weight = -6000 + 15.194 + 0 = -5984.806
Result:
R5000-Mmx/5.300.2x500.2x23 < R5000-Mmx/5.300.2x500.2x26 < Q5-23 = R5000-Mmx/5.300.2x500.2x23 wins

One no:
Q5-23
weight = 3000 + 5.850000000000001 + 0 = 3005.85
R5000-Mmx/5.300.2x500.2x23
weight = 6000 + 7.93 + 0 = 6007.93
R5000-Mmx/5.300.2x500.2x26
weight = 6000 + 3.6159999999999997 + 0 = 6003.616
Result:
Q5-23 < R5000-Mmx/5.300.2x500.2x26 < R5000-Mmx/5.300.2x500.2x23 = Q5-23 wins

1.2 Project partition

If the input CSV file doesn't contain any parameters, then they are taken from here.

req_freq:
[3, 4, 5, 6, 28, 70]

req_bw:
Any but must be greater than 0. If devices don't support this bandwidth, they will be excluded.

req_cap: 
Any but must be greater than 0

req_avb: 
[99.90, 99.99]

req_exclude:
None - nothing to excluded
xg1000 - exclude XG 1000
xg500 - exclude XG
quanta - exclude Quanta
e5000 - exclude Evolution
r5000_pro - exclude R5000 Pro
r5000_lite - exclude R5000 Lite
if need to exclude several options, then write them separated by any sign (space, comma, dot, etc.).
For example:
req_exclude = xg1000 xg500 r5000_lite

1.3 Database partition

db_path:
Points out where the database is stored
default - /devices.db

1.4 Output partition

output_folder:
Points out where results must be saved
default - /Output

kmz_name:
default - csv file name

bom_name:
default - csv file name

2. Update database

/dbupdater.py takes information from devices.xlsx by default and fills in /devices.db.
Actually, devices.db is JSON.

Device's structure:
{'Family': family, 'Name': name, 'Model': model, 'Type': device_type, 'RF Cable': cable, 'Capacity': capacity, 'Availability': availability}
Capacity contains MCS to Throughput table for all bandwidth options that the device supports.
Availability contains MCS to Distance table for all bandwidth options that the device supports and for two availabilities (99.90% and 99.99%).

3. Input

3.1 CSV Structure

3.1.1 Initial data format

CSV must contain an even amount of sites!

Automatically detects the mode (Simple or Advanced) for each link.
If not complete data, then the simple mode. If full, then the advanced mode.

---Compatible coordinates types---
Degrees, minutes, and seconds (DMS): 41°24'12.2"N 2°10'26.5"E
Degrees and decimal minutes (DMM): 41 24.2028, 2 10.4418
Decimal degrees (DD): 41.40338, 2.17403

---Elevation---
Elevation - <int> meters

3.1.2 Simple mode

Takes missing parameters from /config.ini (the project partition).
4 Parameters! - An empty string " , , , "

---Template (Simple mode)---
Link #1
Site A (Even string):
Name, Latitude, Longitude, Elevation
Site B (Odd string):
Name, Latitude, Longitude, Elevation
Link #2
...

---Example (Simple Mode)---
Home,59.6070142792,60.5717699289,60
Damm,59.597915334,60.3832959195,60
Serov,59.6058984265,60.571072097,100
Krasnoturinks,59.7756608567,60.169184831,100
Link #1 - From Home to Damm
Link #2 - From Serov to Krasnoturinks

3.1.3 Advanced mode

Takes all parameters from strings. Even strings must contain common parameters for the link. Optional parameters can be missed.
9 Parameters! - An empty string " , , , , , , , , "

---Template (Advanced mode)---
Link #1
Site A (Even string):
Name <Str>, Latitude <Str>, Longitude <Str>, Elevation <Number>, -Optional- Requirement frequency range [3|4|5|6|28|70] , -Optional- Requirement bandwidth [5|10|20|40|50|56], -Optional- Requirement capacity <Number>, -Optional- Requirement availability [99.90|99.99], -Optional- Exclude [XG|Quanta|E5000|R5000Pro|R5000Lite]
Site B (Odd string):
Name, Latitude, Longitude, Elevation
Link #2
...

---Example (Advanced Mode)---
Home,59.6070142792,60.5717699289,60,5,20,200,99.90,XG Quanta
Damm,59.597915334,60.3832959195,60
Serov,59.6058984265,60.571072097,100,3,40,1000,99.99,
Krasnoturinks,59.7756608567,60.169184831,100
Link #1 - From Home to Damm
Link #2 - From Serov to Krasnoturinks

4. Output

The files will be saved in the folder specified in the configuration.
Default path:
/Output

4.1 KMZ

KMZ is an archive (zip) that includes doc.kml. KML is a modified XML that contains JSON. InfiPLANNER looks into this JSON to create a project.

4.2 Bill of materials

BOM is a simple text file that contains partnumbers and quantity.
