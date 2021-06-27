#!/usr/local/bin/python3.4
 
import os, sys, logging, json, argparse, time, datetime, requests, uuid
from web3 import Web3

from config_files import settings

###################################### BLOCKCHAIN MAPPER FOR NETWORK SLICES #######################################
# NOTE: adds slice-subnet (NST) information into the blockchain
def slice_to_blockchain(nst_json):
    settings.logger.info('BLOCKCHAIN_MAPPER: Distributes local slice-subnet template information with Blockchain peers.')
    # Add a slice template to make it available for other domains
    tx_hash = settings.slice_contract.functions.addSliceTemplate(str(nst_json["id"]), nst_json["name"], nst_json["version"], nst_json["vendor"], nst_json["price"], nst_json["unit"]).transact()
    
    # Wait for transaction to be mined and check it's in the blockchain (get)
    settings.web3.eth.waitForTransactionReceipt(tx_hash)
    
    response = settings.slice_contract.functions.getSliceTemplate(str(nst_json["id"])).call()
    
    nst_json['blockchain_owner'] = response[5]
    return nst_json, 200

#TODO: returns all slice-subnets (NSTs) information from other domains
def slices_from_blockchain():
    settings.logger.info('BLOCKCHAIN_MAPPER: Requests all Blockchain slice-subnet template information.')
    pass 

# NOTE: returns a specific slice-subnet (NST) information from another domain
def slice_from_blockchain(slice_ID):
    # TODO: IMPROVE this function when solidity will allow to return an array of strings (or multidimensional elements like json).
    settings.logger.info('BLOCKCHAIN_MAPPER: Requests Blockchain slice-subnet template information. ID: ' + str(slice_ID))
    response = settings.slice_contract.functions.getSliceTemplate(slice_ID).call()
    nst_json = {}
    nst_json['id'] = slice_ID
    nst_json['name'] = response[0]
    nst_json['version'] = response[1]
    nst_json['vendor'] = response[2]
    nst_json['price'] = response[3]
    nst_json['unit'] = response[4]
    nst_json['blockchain_owner'] = response[5]
    return nst_json, 200

# NOTE: returns the number of slice-subnets (NSTs) in the blockchain db
def get_slices_counter():
    response = settings.slice_contract.functions.getSliceTemplateCount().call()
    return response

# NOTE: returns the slice-subnet (NST) ID based on the index position within the slice_subnets list in the blockchain
def get_slice_id(index):
    response = settings.slice_contract.functions.getSliceTemplateId(index).call()
    return response

# NOTE: requests the deployment of a slice-subnet template (NST) from another domain
def deploy_blockchain_slice(ref_slice_subnet):
    settings.logger.info('BLOCKCHAIN_MAPPER: Starts Blockchain deployment (TIME 3): ' + str(time.time_ns()))
    settings.logger.info('BLOCKCHAIN_MAPPER: Distributes request to deploy slice-subnet in the Blockchain: ' + str(ref_slice_subnet))
    # instantiate slice-subnet
    tx_hash = settings.slice_contract.functions.instantiateSlice(str(ref_slice_subnet["id"]), ref_slice_subnet["nst_ref"]).transact()
    
    # Wait for transaction to be added and check it's in the blockchain (get)
    tx_receipt = settings.web3.eth.waitForTransactionReceipt(tx_hash)
    
    #listen the event associated to the transaction receipt
    rich_logs = settings.slice_contract.events.slice_response().processReceipt(tx_receipt)
    
    #create json to send back to the user the initial instantiation request info.
    deployment_response = {}
    deployment_response["log"] = rich_logs[0]['args']['log']
    deployment_response["status"] = rich_logs[0]['args']['status']
    
    return deployment_response, 200

# NOTE: requests the termination of a slice-subnet instance (NSI) from another domain
def terminate_blockchain_slice(ref_slice_subnet):
    settings.logger.info('BLOCKCHAIN_MAPPER: Distributes request to terminate slice-subnet in the Blockchain: ' + str(ref_slice_subnet))
    # terminate slice-subnet
    tx_hash = settings.slice_contract.functions.terminateSlice(ref_slice_subnet['id']).transact()
    
    # Wait for transaction to be added and check it's in the blockchain (get)
    tx_receipt = settings.web3.eth.waitForTransactionReceipt(tx_hash)
    
    #listen the event associated to the transaction receipt
    rich_logs = settings.slice_contract.events.slice_response().processReceipt(tx_receipt)
    
    #create json to send back to the user the initial instantiation request info.
    deployment_response = {}
    deployment_response["log"] = rich_logs[0]['args']['log']
    deployment_response["status"] = rich_logs[0]['args']['status']
    
    return deployment_response, 200

# NOTE: requests to update a slice-subnet element in the Blockchain
def update_blockchain_slice(subnet_json):
    settings.logger.info("BLOCKCHAIN_MAPPER: Updating information about local deployment (TIME 3): " + str(time.time_ns()))
    settings.logger.info('BLOCKCHAIN_MAPPER: Updates slice-subnet element inside Blockchain. Element ID: ' + str(subnet_json))
    # Add a service
    tx_hash = settings.slice_contract.functions.updateInstance(subnet_json['id'], subnet_json['status'], subnet_json['log']).transact()

    # Wait for transaction to be mined and check it's in the blockchain (get)
    tx_receipt = settings.web3.eth.waitForTransactionReceipt(tx_hash)
    
    #listen the event associated to the transaction receipt
    rich_logs = settings.slice_contract.events.slice_response().processReceipt(tx_receipt)

    deployment_response = {}
    deployment_response["log"] = rich_logs[0]['args']['log']
    deployment_response["status"] = rich_logs[0]['args']['status']
    
    return deployment_response, 200

###################################### BLOCKCHAIN MAPPER FOR IDLs, SDN CONTEXT & CSs #######################################
# distributes the domain associated inter-domain links (IDL) with the other peers
def interdomainlinks_to_blockchain(idl_json, e2e_topology):
    settings.logger.info('BLOCKCHAIN_MAPPER: Distributes local IDLs & e2e topology Blockchain peers.')
    #response = settings.transport_contract.functions.getE2EContext(settings.web3.eth.defaultAccount).call()
    idl_string = json.dumps(idl_json)
    e2e_topology_string = json.dumps(e2e_topology)
    
    # Add a connectivity service template to make it available for other domains
    tx_hash = settings.transport_contract.functions.addIDLContext(idl_string, e2e_topology_string).transact()
    settings.logger.info('BLOCKCHAIN_MAPPER: Transaction for new IDL done.')
    
    # Wait for transaction to be mined and check it's in the blockchain (get)
    tx_receipt = settings.web3.eth.waitForTransactionReceipt(tx_hash)
    settings.logger.info('BLOCKCHAIN_MAPPER: Transaction receipt.')

    msg = {}
    msg["msg"] = "Everything OK"
        
    return msg, 200

# returns the number of slice-subnets (NSTs) in the blockchain db
def get_idl_counter():
    response = settings.transport_contract.functions.getIDLContextCount().call()
    return response

# returns the slice-subnet (NST) ID based on the index position within the slice_subnets list in the blockchain
def get_idl_id(index):
    response = settings.transport_contract.functions.getIDLContextId(index).call()
    return response

# distributes the domain SDN context with the other peers
def context_to_blockchain(context_json):
    settings.logger.info('BLOCKCHAIN_MAPPER: Distributes local contextconnectivity service template information with Blockchain peers.')
    id_string = str(context_json["id"])
    name_context = str(context_json["name_context"])
    sip = str(context_json["sip"])
    nw_topo_serv = str(context_json["nw_topo_serv"])
    topo_metadata = str(context_json["topo_metadata"])
    node_topo = str(context_json["node_topo"])
    link_topo = str(context_json["link_topo"])
    print("id_string length: " + str(len(id_string)))
    print("name_context length: " + str(len(name_context)))
    print("sip length: " + str(len(sip)))
    print("nw_topo_serv length: " + str(len(nw_topo_serv)))
    print("topo_metadata length: " + str(len(topo_metadata)))
    print("node_topo length: " + str(len(node_topo)))
    node_topo1 = node_topo[0:len(node_topo)//2]
    node_topo2 = node_topo[len(node_topo)//2 if len(node_topo)%2 == 0 else ((len(node_topo)//2)+1):]
    print("node_topo1 length: " + str(len(node_topo1)))
    print("node_topo2 length: " + str(len(node_topo2)))
    print("link_topo length: " + str(len(link_topo)))
    
    # Add a connectivity service template to make it available for other domains
    settings.logger.info('BLOCKCHAIN_MAPPER: Tirggering transaction for new context.')
    tx_hash = settings.transport_contract.functions.addContextTemplate_part1(id_string, name_context, sip).transact()
    settings.logger.info('BLOCKCHAIN_MAPPER: PART_1 done.')
    
    # Wait for transaction to be mined and check it's in the blockchain (get)
    tx_receipt = settings.web3.eth.waitForTransactionReceipt(tx_hash)

    settings.logger.info('BLOCKCHAIN_MAPPER: Tirggering transaction part 2.')
    tx_hash = settings.transport_contract.functions.addContextTemplate_part2(id_string, nw_topo_serv, topo_metadata, node_topo1).transact()
    settings.logger.info('BLOCKCHAIN_MAPPER: Part_2 done.')
    
    # Wait for transaction to be mined and check it's in the blockchain (get)
    tx_receipt = settings.web3.eth.waitForTransactionReceipt(tx_hash)

    settings.logger.info('BLOCKCHAIN_MAPPER: Tirggering transaction part 3.')
    tx_hash = settings.transport_contract.functions.addContextTemplate_part3(id_string, node_topo2, link_topo).transact()
    settings.logger.info('BLOCKCHAIN_MAPPER: Part_3 done.')
    
    # Wait for transaction to be mined and check it's in the blockchain (get)
    tx_receipt = settings.web3.eth.waitForTransactionReceipt(tx_hash)
    settings.logger.info('BLOCKCHAIN_MAPPER: Transaction for new context done.')

    #rich_logs = settings.transport_contract.events.topology_response().processReceipt(tx_receipt)
    #settings.logger.info('BLOCKCHAIN_MAPPER: topology_event.' + str(rich_logs))

    #response = settings.transport_contract.functions.getContextTemplate(str(context_json["id"])).call()
    #create json to send back to the user the initial instantiation request info.
    #deployment_response = {}
    #deployment_response["log"] = rich_logs[0]['args']['log']
    #deployment_response["status"] = rich_logs[0]['args']['status']
    #deployment_response["owner"] = rich_logs[0]['args']['requester']
    #print(str(deployment_response))

    msg = {}
    msg["msg"] = "Everything OK"
    
    return msg, 200

# returns topology saved in the blockchain
def get_context_from_blockchain(context_ID):
    # TODO: IMPROVE this function when solidity will allow to return an array of strings (or multidimensional elements like json).
    settings.logger.info('BLOCKCHAIN_MAPPER: Requests Blockchain context template information. ID: ' + str(context_ID))
    response = settings.transport_contract.functions.getContextTemplate(context_ID).call()
    
    #contstruct the context information as a single json.
    context_json = {}
    topology_list = []
    topology_json = {}
    tapi_topo_topo_context_json = {}
    context_json["uuid"] = context_ID
    context_json["name"] = json.loads(response[0])
    context_json["service-interface-point"] = json.loads(response[1])
    tapi_topo_topo_context_json["nw-topology-service"] = json.loads(response[2])
    topology_json = json.loads(response[3])
    topology_json["node"] = json.loads(response[4])
    topology_json["link"] = json.loads(response[5])
    topology_list.append(topology_json)
    tapi_topo_topo_context_json["topology"] = topology_list
    context_json["tapi-topology:topology-context"] = tapi_topo_topo_context_json

    response_json = {}
    response_json["context"] = context_json
    response_json["blockchain_owner"] = response[6]
    return response_json, 200

# returns the number of slice-subnets (NSTs) in the blockchain db
def get_context_counter():
    response = settings.transport_contract.functions.getContextTemplateCount().call()
    return response

# returns the slice-subnet (NST) ID based on the index position within the slice_subnets list in the blockchain
def get_context_id(index):
    response = settings.transport_contract.functions.getContextTemplateId(index).call()
    return response

# returns E2E Topology information from blockchain
def get_e2etopology_from_blockchain():
    # TODO: IMPROVE this function when solidity will allow to return an array of strings (or multidimensional elements like json).
    settings.logger.info('BLOCKCHAIN_MAPPER: Requests Blockchain IDL information.')
    response = settings.transport_contract.functions.getE2EContext().call()
    if (not response):
        context_json = "empty"
    else:
        converted_response = response.replace("'", "\"")
    return context_json, 200

# requests the deployment of a CS between domains
def instantiate_blockchain_cs(address, cs_json, cs_uuid):
    settings.logger.info('BLOCKCHAIN_MAPPER: Distributes request to configure connectivity service in the Blockchain')
    cs_dumps = json.dumps(cs_json)
    
    # instantiate slice-subnet
    tx_hash = settings.transport_contract.functions.instantiateConnectivityService(address,cs_dumps, cs_uuid).transact()
    
    # Wait for transaction to be added and check it's in the blockchain (get)
    tx_receipt = settings.web3.eth.waitForTransactionReceipt(tx_hash)
    
    #listen the event associated to the transaction receipt
    rich_logs = settings.transport_contract.events.topology_response().processReceipt(tx_receipt)
    
    #create json to send back to the user the initial instantiation request info.
    deployment_response = {}
    deployment_response["log"] = rich_logs[0]['args']['log']
    deployment_response["status"] = rich_logs[0]['args']['status']
    
    return deployment_response, 200

# TODO: requests the termination of a CS between domains
def terminate_blockchain_cs(ref_cs):
    pass

# NOTE: requests to update a connectivity service element in the Blockchain
def update_blockchain_cs(cs_json):
    settings.logger.info('BLOCKCHAIN_MAPPER: Updates connectivity service element within the Blockchain.')
    # Add a service
    tx_hash = settings.transport_contract.functions.updateConnectivityService(cs_json['uuid'], cs_json, cs_json['status']).transact()

    # Wait for transaction to be mined and check it's in the blockchain (get)
    tx_receipt = settings.web3.eth.waitForTransactionReceipt(tx_hash)
    
    #listen the event associated to the transaction receipt
    rich_logs = settings.transport_contract.events.topology_response().processReceipt(tx_receipt)

    deployment_response = {}
    deployment_response["log"] = rich_logs[0]['args']['log']
    deployment_response["status"] = rich_logs[0]['args']['status']
    
    return deployment_response, 200