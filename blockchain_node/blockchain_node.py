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
    print("idl_string: " + str(len(idl_string)))
    print("e2e_topology_string: " + str(len(e2e_topology_string)))
    
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
    def divide_string_in_3(sentence):
        parts = 3
        segmented_list = []
        initial_pos = 0
        ending_pos = 0
        chunk_size = len(sentence)/parts
        rounded_up_size = round(chunk_size)
        rounded_down_size = int(chunk_size)

        for i in range(parts):
            if i==(parts-1):
                ending_pos = ending_pos + (rounded_down_size)
                segmented_string = sentence[initial_pos:ending_pos]
                segmented_list.append(segmented_string)
            else:
                ending_pos = ending_pos + (rounded_up_size)
                segmented_string = sentence[initial_pos:ending_pos]
                segmented_list.append(segmented_string)
            
            initial_pos = ending_pos
        return segmented_list
    
    settings.logger.info('BLOCKCHAIN_MAPPER: Distributes local contextconnectivity service template information with Blockchain peers.')
    id_string = context_json["id"]
    name_context = context_json["name_context"]
    sip = context_json["sip"]
    #segmented_sip = divide_string_in_3(sip)
    nw_topo_serv = context_json["nw_topo_serv"]
    topo_metadata = context_json["topo_metadata"]
    node_topo = context_json["node_topo"]
    link_topo = context_json["link_topo"]

    sip_uuid_list = []
    node_uuid_list = []
    link_uuid_list = []
    settings.logger.info('BLOCKCHAIN_MAPPER: Distributing SIPs.')
    for sip_item in json.loads(context_json["sip"]):        
        bl_sip_uuid = context_json["id"]+":"+sip_item["uuid"]
        tx_hash = settings.transport_contract.functions.addSip(bl_sip_uuid, json.dumps(sip_item)).transact()
        # Wait for transaction to be mined
        tx_receipt = settings.web3.eth.waitForTransactionReceipt(tx_hash)
        sip_uuid_list.append(sip_item["uuid"])
    
    settings.logger.info('BLOCKCHAIN_MAPPER: Distributing Nodes.')
    for node_item in json.loads(context_json["node_topo"]):
        bl_node_uuid = context_json["id"]+":"+node_item["uuid"]
        tx_hash = settings.transport_contract.functions.addNode(bl_node_uuid, json.dumps(node_item)).transact()
        # Wait for transaction to be mined and check it's in the blockchain (get)
        tx_receipt = settings.web3.eth.waitForTransactionReceipt(tx_hash)
        node_uuid_list.append(node_item["uuid"])
    
    if context_json["link_topo"]:
        settings.logger.info('BLOCKCHAIN_MAPPER: Distributing Links.')
        for link_item in json.loads(context_json["link_topo"]):
            bl_link_uuid = context_json["id"]+":"+link_item["uuid"]
            tx_hash = settings.transport_contract.functions.addLink(bl_link_uuid, json.dumps(link_item)).transact()
            # Wait for transaction to be mined and check it's in the blockchain (get)
            tx_receipt = settings.web3.eth.waitForTransactionReceipt(tx_hash)
            link_uuid_list.append(link_item["uuid"])
    else:
        settings.logger.info('BLOCKCHAIN_MAPPER: There are NO Links to distribute.')
    
    print("sip_uuid_list: " + str(len(sip_uuid_list)))
    print("node_uuid_list: " + str(len(node_uuid_list)))
    print(link_uuid_list)
    print("link_uuid_list: " + str(len(link_uuid_list)))
    
    # Add a connectivity service template to make it available for other domains
    settings.logger.info('BLOCKCHAIN_MAPPER: Triggering transaction for new context.')    
    tx_hash = settings.transport_contract.functions.addContextTemplate(id_string, name_context, json.dumps(sip_uuid_list), nw_topo_serv, topo_metadata, json.dumps(node_uuid_list), json.dumps(link_uuid_list)).transact()
    
    # Wait for transaction to be mined and check it's in the blockchain (get)
    tx_receipt = settings.web3.eth.waitForTransactionReceipt(tx_hash)
    settings.logger.info('BLOCKCHAIN_MAPPER: Transaction for new context done.')

    response = settings.transport_contract.functions.getNodeCount().call()
    print(str(response[0]))

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

# TODO: need to be updated with what it really returns (context with list of sips, ndoes, links)
def get_context_from_blockchain(context_ID):
    # TODO: IMPROVE this function when solidity will allow to return an array of strings (or multidimensional elements like json).
    settings.logger.info('BLOCKCHAIN_MAPPER: Requests Blockchain context information (sips, ndoes and links).' )
    
    #response = settings.transport_contract.functions.getContextTemplate(context_ID).call()   
    response = {}
    #contstruct the context information as a single json.
    context_json = {}
    """
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
    """

    response_json = {}
    response_json["context"] = context_json
    response_json["blockchain_owner"] = response[6]
    return response_json, 200

# return all the sips, nodes and links belonging to a specific context to build the json with the complete TAPI format
def get_context_sips_ndoes_links_from_blockchain(context_json):
    print("BL_NODE:GETTING Nodes")
    nodes_list_json = []
    for node_item in json.loads(context_json["node_topo"]):
        print("BL_NODE:GET NODE with ID: " + str(node_item))
        print(type(node_item))
        response = settings.transport_contract.functions.getNode(node_item).call() 
        node_json = json.loads(response[0])
        print(node_json)
        print(type(node_json))
        nodes_list_json.append(node_json)
    print(nodes_list_json)
    context_json["node_topo"] = nodes_list_json

    sips_list_json = []
    print("BL_NODE:GETTING SIPs")
    for sip_item in json.loads(context_json["sip"]):
        print("BL_NODE:GET SIP with ID: " + str(sip_item))
        print(type(sip_item))
        response = settings.transport_contract.functions.getSIP(sip_item).call() 
        sip_json = json.loads(response[0])
        sips_list_json.append(sip_json)
    context_json["sip"] = sips_list_json


    links_list_json = []
    print("BL_NODE:GETTING Links")
    linklist = json.loads(context_json["link_topo"])
    if linklist:
        for link_item in linklist:
            print("BL_NODE:GET LINK with ID: " + str(link_item))
            print(type(link_item))
            response = settings.transport_contract.functions.getLink(link_item).call() 
            link_json = json.loads(response[0])
            links_list_json.append(link_json)
    context_json["link_topo"] = links_list_json
    
    return context_json

# returns the number of slice-subnets (NSTs) in the blockchain db
def get_context_counter():
    response = settings.transport_contract.functions.getContextTemplateCount().call()
    return response

# returns the slice-subnet (NST) ID based on the index position within the slice_subnets list in the blockchain
def get_context_id(index):
    response = settings.transport_contract.functions.getContextTemplateId(index).call()
    return response

# returns IDLs information from blockchain
def get_e2etopology_from_blockchain():
    # TODO: IMPROVE this function when solidity will allow to return an array of strings (or multidimensional elements like json).
    settings.logger.info('BLOCKCHAIN_MAPPER: Requests Blockchain IDL information.')
    response = settings.transport_contract.functions.getE2EContext().call()
    if (not response):
        context_json = "empty"
    else:
        converted_response = response.replace("'", "\"")
        context_json = json.loads(converted_response)
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