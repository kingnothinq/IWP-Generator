1. Settings and options

1.1 Default settings

/config.ini

Database Path - /devices.db
Output Path - /Result
Mode - Simple
Project name - CSV filename
Requirement frequency range - 5 GHz
Requirement bandwidth - 40 MHz
Requirement capacity - 1000 Mbps
Requirement availability - 99.99 %
Exclude - None

1.2 Update database

Devices.db from devices.xlsx

2. Input

2.1 CSV Structure

2.1.1 Initial data format

---Compatible coordinates types---
Degrees, minutes, and seconds (DMS): 41°24'12.2"N 2°10'26.5"E
Degrees and decimal minutes (DMM): 41 24.2028, 2 10.4418
Decimal degrees (DD): 41.40338, 2.17403

---Elevation---
Elevation - <int> meters

2.1.2 Simple mode

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

2.1.3 Advanced mode

---Template (Advanced mode)---
Link #1
Site A (Even string):
Name <Str>, Latitude <Str>, Longitude <Str>, Elevation <Number>, -Optional- Requirement frequency range [3|4|5|6|28|70] , -Optional- Requirement bandwidth [5|10|20|40|50|56], -Optional- Requirement capacity <Number>, -Optional- Requirement availability [99.90|99.99] (Optional), -Optional- Exclude [XG|Quanta|E5000|R5000Pro|R5000Lite]
Site B (Odd string):
Name, Latitude, Longitude, Elevation
Link #2
...

---Example (Simple Mode)---
Home,59.6070142792,60.5717699289,60,5,20,200,99.90,XG Quanta
Damm,59.597915334,60.3832959195,60
Serov,59.6058984265,60.571072097,100,3,40,1000,99.99,
Krasnoturinks,59.7756608567,60.169184831,100
Link #1 - From Home to Damm
Link #2 - From Serov to Krasnoturinks

3. Output

3.1 KMZ

KMZ includes doc.kml

3.2 Bill of materials

BOM is a text file
