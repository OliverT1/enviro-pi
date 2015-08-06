# Written by Oliver Turnbull for EnviroPi project, part of the AstroPi competition
import sqlite3 as lite
import urllib.request
import json
import time

global db

# Opens DB and creates the temperatures table
def getDatabase():
    global db
    db = None
    try:
        # Connects to DB, creates it if it doesn't exist
        db = lite.connect('enviroPiHome.db')
        cur = db.cursor()
        # Creates the table if it doesn't exist
        cur.execute('''CREATE TABLE IF NOT EXISTS
                        temperatureChange(id INTEGER PRIMARY KEY AUTOINCREMENT, country TEXT NOT NULL,
                        code TEXT NOT NULL, avgChange REAL NOT NULL, totalChange REAL NOT NULL);''')
        db.commit()
    except Exception as e:
        # Roll back any changes if something goes wrong
        db.rollback()
        raise e
    # Returns cursor object to be used to later add entries
    return cur

# Used to insert the data into the table
def insertIntoDatabase(country, code, avgChange, totalChange, cur):
    global db
    cur.execute('''INSERT INTO temperatureChange
                    (country, code, avgChange, totalChange)
                    VALUES(?, ?, ?, ?)''', (country, code, avgChange, totalChange))
    db.commit()

# String of all countries and their ISO3 country code, split into countries and their codes
countries = '''ABW Aruba
AFG Afghanistan
AGO Angola
AIA Anguilla
ALA Åland Islands
ALB Albania
AND Andorra
ANT Netherlands Antilles
ARE United Arab Emirates
ARG Argentina
ARM Armenia
ASM American Samoa
ATA Antarctica
ATF French Southern Territories
ATG Antigua and Barbuda
AUS Australia
AUT Austria
AZE Azerbaijan
BDI Burundi
BEL Belgium
BEN Benin
BFA Burkina Faso
BGD Bangladesh
BGR Bulgaria
BHR Bahrain
BHS Bahamas
BIH Bosnia and Herzegovina
BLM Saint Barthélemy
BLR Belarus
BLZ Belize
BMU Bermuda
BOL Bolivia, Plurinational State of
BRA Brazil
BRB Barbados
BRN Brunei Darussalam
BTN Bhutan
BVT Bouvet Island
BWA Botswana
CAF Central African Republic
CAN Canada
CCK Cocos (Keeling) Islands
CHE Switzerland
CHL Chile
CHN China
CIV Côte d'Ivoire
CMR Cameroon
COD Congo, the Democratic Republic of the
COG Congo
COK Cook Islands
COL Colombia
COM Comoros
CPV Cape Verde
CRI Costa Rica
CUB Cuba
CXR Christmas Island
CYM Cayman Islands
CYP Cyprus
CZE Czech Republic
DEU Germany
DJI Djibouti
DMA Dominica
DNK Denmark
DOM Dominican Republic
DZA Algeria
ECU Ecuador
EGY Egypt
ERI Eritrea
ESH Western Sahara
ESP Spain
EST Estonia
ETH Ethiopia
FIN Finland
FJI Fiji
FLK Falkland Islands (Malvinas)
FRA France
FRO Faroe Islands
FSM Micronesia, Federated States of
GAB Gabon
GBR United Kingdom
GEO Georgia
GGY Guernsey
GHA Ghana
GIB Gibraltar
GIN Guinea
GLP Guadeloupe
GMB Gambia
GNB Guinea-Bissau
GNQ Equatorial Guinea
GRC Greece
GRD Grenada
GRL Greenland
GTM Guatemala
GUF French Guiana
GUM Guam
GUY Guyana
HKG Hong Kong
HMD Heard Island and McDonald Islands
HND Honduras
HRV Croatia
HTI Haiti
HUN Hungary
IDN Indonesia
IMN Isle of Man
IND India
IOT British Indian Ocean Territory
IRL Ireland
IRN Iran, Islamic Republic of
IRQ Iraq
ISL Iceland
ISR Israel
ITA Italy
JAM Jamaica
JEY Jersey
JOR Jordan
JPN Japan
KAZ Kazakhstan
KEN Kenya
KGZ Kyrgyzstan
KHM Cambodia
KIR Kiribati
KNA Saint Kitts and Nevis
KOR Korea, Republic of
KWT Kuwait
LAO Lao People's Democratic Republic
LBN Lebanon
LBR Liberia
LBY Libyan Arab Jamahiriya
LCA Saint Lucia
LIE Liechtenstein
LKA Sri Lanka
LSO Lesotho
LTU Lithuania
LUX Luxembourg
LVA Latvia
MAC Macao
MAF Saint Martin (French part)
MAR Morocco
MCO Monaco
MDA Moldova, Republic of
MDG Madagascar
MDV Maldives
MEX Mexico
MHL Marshall Islands
MKD Macedonia, the former Yugoslav Republic of
MLI Mali
MLT Malta
MMR Myanmar
MNE Montenegro
MNG Mongolia
MNP Northern Mariana Islands
MOZ Mozambique
MRT Mauritania
MSR Montserrat
MTQ Martinique
MUS Mauritius
MWI Malawi
MYS Malaysia
MYT Mayotte
NAM Namibia
NCL New Caledonia
NER Niger
NFK Norfolk Island
NGA Nigeria
NIC Nicaragua
NIU Niue
NLD Netherlands
NOR Norway
NPL Nepal
NRU Nauru
NZL New Zealand
OMN Oman
PAK Pakistan
PAN Panama
PCN Pitcairn
PER Peru
PHL Philippines
PLW Palau
PNG Papua New Guinea
POL Poland
PRI Puerto Rico
PRK Korea, Democratic People's Republic of
PRT Portugal
PRY Paraguay
PSE Palestinian Territory, Occupied
PYF French Polynesia
QAT Qatar
REU Réunion
ROU Romania
RUS Russian Federation
RWA Rwanda
SAU Saudi Arabia
SDN Sudan
SEN Senegal
SGP Singapore
SGS South Georgia and the South Sandwich Islands
SHN Saint Helena, Ascension and Tristan da Cunha
SJM Svalbard and Jan Mayen
SLB Solomon Islands
SLE Sierra Leone
SLV El Salvador
SMR San Marino
SOM Somalia
SPM Saint Pierre and Miquelon
SRB Serbia
STP Sao Tome and Principe
SUR Suriname
SVK Slovakia
SVN Slovenia
SWE Sweden
SWZ Swaziland
SYC Seychelles
SYR Syrian Arab Republic
TCA Turks and Caicos Islands
TCD Chad
TGO Togo
THA Thailand
TJK Tajikistan
TKL Tokelau
TKM Turkmenistan
TLS Timor-Leste
TON Tonga
TTO Trinidad and Tobago
TUN Tunisia
TUR Turkey
TUV Tuvalu
TWN Taiwan, Province of China
TZA Tanzania, United Republic of
UGA Uganda
UKR Ukraine
UMI United States Minor Outlying Islands
URY Uruguay
USA United States
UZB Uzbekistan
VAT Holy See (Vatican City State)
VCT Saint Vincent and the Grenadines
VEN Venezuela, Bolivarian Republic of
VGB Virgin Islands, British
VIR Virgin Islands, U.S.
VNM Viet Nam
VUT Vanuatu
WLF Wallis and Futuna
WSM Samoa
YEM Yemen
ZAF South Africa
ZMB Zambia
ZWE Zimbabwe'''.split('\n')

cur = getDatabase()

# Multi dimensional string to store countries and their ISO3 code
countriesList = []
for country in countries:
    countriesList.append(country.split())

# Cycles through each country in the list
for country in countriesList:
    # Prevents zero error if there is no data for a country
    try:
        
        # Gets temperature data for the country from the Wold Bank Climate Data API
        req = urllib.request.Request\
            ("http://climatedataapi.worldbank.org/climateweb/rest/v1/country/cru/tas/year/%s.json" % country[0])
        response = urllib.request.urlopen(req)

        # Decodes url into string data for json to read
        encoding = response.headers.get_content_charset('utf8')
        # Reads data into obj
        obj = json.loads(response.read().decode(encoding))

        temps = []
        tempDiff = []
        x=1
        # Extracts the temperature data from the request
        for data in obj:
            temps.append(data['data'])

        # Calculates yearly temp change and puts it in tempdiff list
        while x < len(temps):
            tempDiff.append(abs(temps[x]-temps[x-1]))
            x +=1

        # Inserts the country name, code and average yearly temp change and total change (1901 to 2012) into DB
        insertIntoDatabase(country[1], country[0], (sum(tempDiff)/len(tempDiff)), abs(tempDiff[0] - tempDiff[-1]), cur)
    except ZeroDivisionError:
        print('no country data')
        print (country[1])

db.commit()