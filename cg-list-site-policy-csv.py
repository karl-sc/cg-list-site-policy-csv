#!/usr/bin/env python
PROGRAM_NAME = "cg-list-site-policy-csv.py"
PROGRAM_DESCRIPTION = """
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

"""
from cloudgenix import API, jd
import cloudgenix_idname 
import os
import sys
import argparse
import csv

CLIARGS = {}
cgx_session = API()              #Instantiate a new CG API Session for AUTH

def parse_arguments():
    parser = argparse.ArgumentParser(
        prog=PROGRAM_NAME,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=PROGRAM_DESCRIPTION
            )
    parser.add_argument('--token', '-t', metavar='"MYTOKEN"', type=str, 
                    help='specify an authtoken to use for CloudGenix authentication')
    parser.add_argument('--authtokenfile', '-f', metavar='"MYTOKENFILE.TXT"', type=str, 
                    help='a file containing the authtoken')
    parser.add_argument('--csvfile', '-c', metavar='csvfile', type=str, 
                    help='the CSV Filename to write', default="site-policy-mapping.csv", required=False)
    args = parser.parse_args()
    CLIARGS.update(vars(args)) ##ASSIGN ARGUMENTS to our DICT
    print(CLIARGS)

def authenticate():
    print("AUTHENTICATING...")
    user_email = None
    user_password = None
    
    ##First attempt to use an AuthTOKEN if defined
    if CLIARGS['token']:                    #Check if AuthToken is in the CLI ARG
        CLOUDGENIX_AUTH_TOKEN = CLIARGS['token']
        print("    ","Authenticating using Auth-Token in from CLI ARGS")
    elif CLIARGS['authtokenfile']:          #Next: Check if an AuthToken file is used
        tokenfile = open(CLIARGS['authtokenfile'])
        CLOUDGENIX_AUTH_TOKEN = tokenfile.read().strip()
        print("    ","Authenticating using Auth-token from file",CLIARGS['authtokenfile'])
    elif "X_AUTH_TOKEN" in os.environ:              #Next: Check if an AuthToken is defined in the OS as X_AUTH_TOKEN
        CLOUDGENIX_AUTH_TOKEN = os.environ.get('X_AUTH_TOKEN')
        print("    ","Authenticating using environment variable X_AUTH_TOKEN")
    elif "AUTH_TOKEN" in os.environ:                #Next: Check if an AuthToken is defined in the OS as AUTH_TOKEN
        CLOUDGENIX_AUTH_TOKEN = os.environ.get('AUTH_TOKEN')
        print("    ","Authenticating using environment variable AUTH_TOKEN")
    else:                                           #Next: If we are not using an AUTH TOKEN, set it to NULL        
        CLOUDGENIX_AUTH_TOKEN = None
        print("    ","Authenticating using interactive login")
    ##ATTEMPT AUTHENTICATION
    if CLOUDGENIX_AUTH_TOKEN:
        cgx_session.interactive.use_token(CLOUDGENIX_AUTH_TOKEN)
        if cgx_session.tenant_id is None:
            print("    ","ERROR: AUTH_TOKEN login failure, please check token.")
            sys.exit()
    else:
        while cgx_session.tenant_id is None:
            cgx_session.interactive.login(user_email, user_password)
            # clear after one failed login, force relogin.
            if not cgx_session.tenant_id:
                user_email = None
                user_password = None            
    print("    ","SUCCESS: Authentication Complete")

def go():
    name_to_id = cloudgenix_idname.generate_id_name_map(cgx_session)

    ####CODE GOES BELOW HERE#########
    resp = cgx_session.get.tenants()
    if resp.cgx_status:
        tenant_name = resp.cgx_content.get("name", None)
        print("======== TENANT NAME",tenant_name,"========")
    else:
        logout()
        print("ERROR: API Call failure when enumerating TENANT Name! Exiting!")
        print(resp.cgx_status)
        sys.exit((vars(resp)))

    csvfilename = CLIARGS['csvfile']
    
    counter = 0
    with open(csvfilename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        resp = cgx_session.get.sites()
        if resp.cgx_status:
            site_list = resp.cgx_content.get("items", None)    #EVENT_LIST contains an list of all returned events
            csvwriter.writerow( [ "Site-Name", "Path-Policy", "QoS-Policy", "NAT-Policy"])
            for site in site_list:       
                

                site_name = name_to_id[site['id']]
                if (site['element_cluster_role'] == "SPOKE"): ###ONLY do this for SPOKE's
                    if (site['policy_set_id']): ###Are we using Classic Policies? If so, there is no separate "QoS" Policy
                        path_name = name_to_id[site['policy_set_id']]
                        qos_name = name_to_id[site['policy_set_id']]
                        nat_name = name_to_id[site['policy_set_id']]
                    elif (site['network_policysetstack_id']): ### Using Stacked policy instead!
                        path_name = name_to_id[site['network_policysetstack_id']]
                        qos_name = name_to_id[site['priority_policysetstack_id']]
                        nat_name = name_to_id[site['nat_policysetstack_id']]
                    else:
                        path_name = "None"
                        qos_name = "None"
                        nat_name = "None"
                    
                    counter += 1
                    csvwriter.writerow( [ 
                        site_name, path_name, qos_name, nat_name
                        ] ) 
        else:
            logout()
            print("ERROR: API Call failure when enumerating SITES in tenant! Exiting!")
            sys.exit((jd(resp)))

    print("Wrote to CSV File:", csvfilename, " - ", counter, 'rows')
    ####CODE GOES ABOVE HERE#########
  
def logout():
    print("Logging out")
    cgx_session.get.logout()

if __name__ == "__main__":
    parse_arguments()
    authenticate()
    go()
    logout()
