# cg-list-site-policy-csv

CloudGenix script to Create a CSV listing of all Sites and their associated Policies
---------------------------------------

usage: cg-list-site-policy-csv.py [-h] [--token "MYTOKEN"]
                                  [--authtokenfile "MYTOKENFILE.TXT"]
                                  [--csvfile csvfile]

By default we write to the file 'site-policy-mapping.csv' if none is specified

Example:

cg-list-site-policy-csv.py --csvfile site-report.csv
    Uses either the ENV variable or interactive login and prints the report to site-report.csv

cg-list-site-policy-csv.py --csvfile site-report.csv
    Uses either the ENV variable or interactive login and prints the report to site-report.csv
