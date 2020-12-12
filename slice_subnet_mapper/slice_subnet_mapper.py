#!/usr/local/bin/python3.4

import os, sys, logging, json, argparse, time, datetime, requests, uuid


#### NETWORK SLICE MANAGER/NFVO URL
JSON_CONTENT_HEADER = {'Content-Type':'application/json'}
def get_nsm_url():
    nsm_ip = os.environ.get("NSM_IP")
    nsm_port = os.environ.get("NSM_PORT")
    nfvo_url = "http://"+ str(nsm_ip) +":"+ str(nsm_port) +"/api/v3"
    return nfvo_url


#### REQUESTS
# returns all the slice-subnets templates in the NSM
def get_all_slice_subnet_templates():
    url = get_nsm_url() + "/slices"
    response = requests.get(url, headers=JSON_CONTENT_HEADER)
    return response.text, response.status_code

# returns a specific slice-subnet template in the NSM
def get_slice_subnet_template(slice_ID):
    url = get_nsm_url() + "/slices/" + str(slice_ID)
    response = requests.get(url, headers=JSON_CONTENT_HEADER)
    return response.text, response.status_code

# returns all slice-subnet instances in the NSM
def get_all_slice_subnet_instances():
    url = get_nsm_url() + "/slice-instances"
    response = requests.get(url, headers=JSON_CONTENT_HEADER)
    return response.text, response.status_code

# returns specific slice-subnet instance in the NSM
def get_slice_subnet_instance(instance_ID):
    url = get_nsm_url() + "/slice-instances/" + str(instance_ID)
    response = requests.get(url, headers=JSON_CONTENT_HEADER)
    return response.text, response.status_code

# sends request to deploy a slice-subnet template (NST) to the NSM
def instantiate_slice_subnet(data_json):  
    data_dumps = json.dumps(data_json)  
    url = get_nsm_url() + "/requests"
    response = requests.post(url, headers=JSON_CONTENT_HEADER, data=data_dumps)
    return response.text, response.status_code

#TODO: sends request to terminate a slice-subnet template (NST) to the NSM
def terminate_slice_subnet(data_json):
    pass