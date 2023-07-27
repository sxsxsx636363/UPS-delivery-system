import world_ups_pb2 
import amazon_ups_pb2 
from db import *
from django.db.models import Q
import socket
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint
amazon_port = 6666
amazon_host = "vcm-32866.vm.duke.edu"
world_port = 12345
# "vcm-32866.vm.duke.edu"
world_host = "vcm-32866.vm.duke.edu"
# world_host = "vcm-30735.vm.duke.edu"
executor = ThreadPoolExecutor(100)
world_id = None
world_soc = None
seqnum = 0
seqnumlock = threading.Lock()
amazon_acknum = []
world_acknum = []
amazon_seqnum = []
world_seqnum = []
query_flag = False
query_truck = -1
world_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# multithread reference:
# https://superfastpython.com/threadpoolexecutor-in-python/#What_Are_Python_Threads
# manualy create two thread, one for world listening and the other for amazon listening
# each thread will then put received msg into automatically thread pool to processing the received msg received by worker thread.
# reference_link:https://www.liaoxuefeng.com/wiki/1016959663602400/1017788916649408
# -------------------------------send msg --------------------------------
def send_amazon_finishship(package_id,amazon_soc):
    id_seqnum = get_seq_num()
    ups_command = amazon_ups_pb2.UPSCommands()
    ups_finishship = ups_command.finishship.add()
    ups_finishship.id = id_seqnum
    ups_finishship.packageid = package_id
    # add this msg into db
    db_add_seqnum(id_seqnum, "upsamazonfinishship", None, package_id)
    while True:
        send_msg(ups_command, amazon_soc)
        print("send_amazon_finishship \n",ups_command ,"\n" )
        # amazoncommand = recv_amazon_msg("AmazonCommands",amazon_soc)
        if id_seqnum in amazon_acknum: 
            print("successfully send amazon finiship")
            break
        else:
            time.sleep(2)
            continue
    return
#TODO: ups_initship.id and ups_initship.packageid may change
def send_amazon_initship(packageid,truck_id,amazon_soc):  
    id_seqnum = get_seq_num()
    ups_command = amazon_ups_pb2.UPSCommands()
    ups_initship = ups_command.initship.add()
    ups_initship.id = id_seqnum
    ups_initship.truckid = truck_id
    ups_initship.packageid = packageid
    print("start send amazon initship\n",ups_command)
    # add this msg into db
    db_add_seqnum(id_seqnum, "upsamazoninitship", truck_id, packageid)
    # print("finish build send amazon initship:\n",ups_command)
    while True:
        send_msg(ups_command, amazon_soc)
        print("send_amazon_initship \n")
        # print("send_amazon_initship received: \n",amazoncommand)
        if id_seqnum in amazon_acknum:
            print("successfully send amazon initship")
            break
        else:
            time.sleep(2)
            continue
    return
def send_amazon_startship(package_id, amazon_soc):
    id_seqnum = get_seq_num()
    print("startship send to amazon: ",id_seqnum)
    ups_command = amazon_ups_pb2.UPSCommands()
    ups_startship = ups_command.startship.add()
    ups_startship.id = id_seqnum
    ups_startship.packageid = package_id
    print("start send amazon startship\n",ups_command)
    # add this msg into db
    db_add_seqnum(id_seqnum, "upsamazonstartship", None, package_id)
    while True:
        print("sending amazon startship\n")
        send_msg(ups_command, amazon_soc)
        if id_seqnum in amazon_acknum:
            print("successfully send amazon startship",amazoncommand)
            break
        else:
            time.sleep(2)
            continue
    return

def send_amazon_error(error_msg, originseq_num):
    id_seqnum = get_seq_num()
    ups_command = amazon_ups_pb2.UPSCommands()
    ups_error = ups_command.error.add()
    ups_error.err = error_msg
    ups_error.originseqnum = originseq_num
    ups_error.seqnum = id_seqnum
    print("start send amazon error\n",ups_command)
    # add this msg into db
    db_add_seqnum(id_seqnum, "amazomerror", None, None)
    # print("sending amazon error\n")
    # send_msg(ups_command, amazon_soc)
    while True:
        print("sending amazon error\n")
        send_msg(ups_command, amazon_soc)
        if id_seqnum in amazon_acknum:
            print("successfully send amazon error",ups_command)
            break
        else:
            time.sleep(2)
            continue
    return

def send_world_UGoPickUp(truck_id, wh_id, world_soc):
    seq_num = get_seq_num()
    ucommand = world_ups_pb2.UCommands()
    ugopickup_cmd = ucommand.pickups.add()
    # ugopickup_cmd = world_ups_pb2.UGoPickup()
    ugopickup_cmd.truckid = truck_id
    ugopickup_cmd.whid = wh_id
    ugopickup_cmd.seqnum = seq_num
    # ucommand.pickups.append(ugopickup_cmd)
    # add this msg into db
    db_add_seqnum(seq_num, "ugopickup", truck_id, None)
    # print("finish add send_world_UGoPickUp into seqnumdb")
    while True:
        # print("start send send_world_UGoPickUp to world", ucommand)
        send_msg(ucommand, world_soc)  
        # print("send_world_UGoPickUp():send:\n",ucommand)
        if seq_num in world_acknum:
            print("send_world_UGoPickUp():received:\n",uresponse)  
            break
        else:
            time.sleep(2)
            continue
    
def send_world_UGoDeliver(truck_id, package_id, world_soc):
    print("start send_world_UGoDeliver()\n")
    seq_num = get_seq_num()
    ucommand = world_ups_pb2.UCommands()
    ugodeliver_cmd = ucommand.deliveries.add()
    ugodeliver_cmd.truckid = truck_id
    packages_cmd = ugodeliver_cmd.packages.add()
    packages_cmd.packageid = package_id
    packages_cmd.x = db_get_x_destlocation(package_id)
    packages_cmd.y = db_get_y_destlocation(package_id)
    ugodeliver_cmd.seqnum = seq_num
    print("start send world godeliver\n",ucommand)
    # add this msg into db
    db_add_seqnum(seq_num, "ugodeliver", truck_id, package_id)
    while True:
        print("send_world_UGoDeliver():send:\n",ucommand)
        send_msg(ucommand, world_soc)       
        if seq_num in world_acknum:
            print("send_world_UGoDeliver():received ack:\n")  
            break 
        # uresponse = recv_amazon_msg("UResponses",world_soc)
        # if uresponse.seqnum == seq_num:
        #     return Ture
        #     break
        else:
            time.sleep(2)
            continue
def send_world_UQuery(truck_id, world_soc):
    seq_num = get_seq_num()
    ucommand = world_ups_pb2.UCommands()
    uquery_cmd = ucommand.queries.add()
    uquery_cmd.truckid = truck_id
    uquery_cmd.seqnum = seq_num
    # add this msg into db
    db_add_seqnum(seq_num, "uquery", truck_id, None)
    while True:
        send_msg(ucommand, world_soc)    
        print("send_world_UQuery():send:\n",ucommand)
        if seq_num in world_acknum:
            print("send_world_UQuery():received:\n",uresponse)  
            break   
        else:
            time.sleep(2)
            continue
#---------------listening & processing received msg-----------------------
# TODO: acks_resp, truckstatus_resp, error_resp
def process_query(world_soc,amazon_soc):
    while True:   
        # print("process_query: true\n")
        global query_flag
        if query_flag is True:
            executor.submit(start_send_world_UQuery, world_soc)
            query_flag = False
        
def process_world_msg(world_soc,amazon_soc):
    while True:
        while True:    
            uresponse = recv_world_msg("UResponses",world_soc)
            if uresponse is None:
                continue
            else:
                print("---------------------process_world_msg() received msg: \n") 
                print(uresponse)
                break        
        for completions_resp in uresponse.completions:
            if completions_resp.seqnum not in world_seqnum:
                # print('\completions_resp: ')
                # print(completions_resp)         
                executor.submit(ack_to_world, completions_resp.seqnum, world_soc)
                executor.submit(handle_world_finished, completions_resp, world_soc,amazon_soc)
        for delivered_resp in uresponse.delivered:
            if delivered_resp.seqnum not in world_seqnum:
                # print('\delivered_resp: ')
                # print(delivered_resp)         
                executor.submit(ack_to_world, delivered_resp.seqnum, world_soc)
                executor.submit(handle_world_delivered, delivered_resp, world_soc,amazon_soc)
        for acks_resp in uresponse.acks:
            if acks_resp not in world_acknum:
                # print("\nworld_acks: ", acks_resp)           
                executor.submit(handle_world_acks, acks_resp)
        for truckstatus_resp in uresponse.truckstatus:
            if truckstatus_resp.seqnum not in world_seqnum:
                # print("\ntruckstatus_resp: ",truckstatus_resp)
                executor.submit(ack_to_world, truckstatus_resp.seqnum, world_soc)           
                executor.submit(handle_world_TruckStatus, truckstatus_resp)
        for error_resp in uresponse.error:
            if error_resp.seqnum not in world_seqnum:
                # print('\nerror_resp: ')
                # print(error_resp)
                executor.submit(ack_to_world, error_resp.seqnum, world_soc)           
                executor.submit(handle_world_error, error_resp, world_soc, amazon_soc)
        if uresponse.HasField("finished"):
            if uresponse.finished == True:
                # print('\n Receivedfinished: ')
                # print(uresponse.finished)
                executor.submit(close_world_socket, world_soc)
            else:
                print('\nfinished exist but not finished')   

# TODO: amazon_error, amazon_acks
def process_amazon_msg(world_soc, amazon_soc):
    while True:    
        amazon_command = recv_amazon_msg("AmazonCommands",amazon_soc)
        if amazon_command is None:
            continue
        else:
            print("---------------------process_amazon_msg() received msg: \n") 
            print(amazon_command)
            for amazon_initship in amazon_command.initship:
                if amazon_initship.id not in amazon_seqnum:
                    print('\namazon_initship: ')
                    print(amazon_initship)
                    executor.submit(ack_to_amazon, amazon_initship.id, amazon_soc)
                    executor.submit(handle_amazon_initship, amazon_initship, world_soc, amazon_soc)
            for amazon_startship in amazon_command.startship:
                if amazon_startship.id not in amazon_seqnum:
                    print('\nreceived amazon_startship: ')
                    print(amazon_startship)            
                    executor.submit(ack_to_amazon, amazon_startship.id, amazon_soc)
                    executor.submit(handle_amazon_startship, amazon_startship, world_soc, amazon_soc)
            for amazon_finishship in amazon_command.finishship:
                if amazon_finishship.id not in amazon_seqnum:
                    print('\namazon_finishship: ')
                    print(amazon_finishship)         
                    executor.submit(ack_to_amazon, amazon_finishship.id, amazon_soc)
                    executor.submit(handle_amazon_finishship, amazon_finishship, world_soc)
            for amazon_error in amazon_command.error:
                print("\namazon_error: ",amazon_error.err," with packageid: ",amazon_error.packageid,"\n")   
                # executor.submit(handle_amazon_error, uresponse.error[error_resp]) 
            for amazon_acks in amazon_command.acks:
                if amazon_acks not in amazon_acknum:
                    print('\namazon_acks: ',amazon_acks)
                    executor.submit(handle_amazon_acks, amazon_acks)      
#TODO: do we need finish flag to finish connection between ups and amazon?
  
# ------------------------send/rec msg------------------------------------
def send_msg(msg, world_soc):
    str1 = "---------------------start send msg: \n "
    print(str1,msg)
    msg_str = msg.SerializeToString()
    _EncodeVarint(world_soc.send, len(msg_str), None)
    world_soc.send(msg_str)
    return

def send_world_msg(msg, world_soc):
    print("---------------------start send msg: \n ",msg)
    msg_str = msg.SerializeToString()
    print("finish SerializeToString\n")
    _EncodeVarint(world_soc.send, len(msg_str), None)
    print("send_world_msg finish encoding")
    world_soc.send(msg_str)
    print("send_world_msg finish sending")
    return

def recv_world_msg(msgtype,world_soc):
    print("---------------------receive msg from world: \n") 
    var_int_buff = []
    try:
        while True:
            # try:
            buf = world_soc.recv(1)
            # if len(buf) <= 0: 
            #     # print("buf length <0\n") 
            var_int_buff += buf
            msg_len, new_pos = _DecodeVarint32(var_int_buff, 0)
            if new_pos != 0:
                break
            # except IndexError as ex:
            #     continue

        buf_message = world_soc.recv(msg_len)
        if msgtype == "UConnected":
            uconnected = world_ups_pb2.UConnected()
            try:
                uconnected.ParseFromString(buf_message)
                print(uconnected)
                return uconnected 
            except:
                print("Error: recv_world_msg() failed parsing the uconnected msg")
                return None
        elif msgtype == "UResponses":
            uresponse = world_ups_pb2.UResponses()
            try:
                uresponse.ParseFromString(buf_message)
                print(uresponse)
                return uresponse 
            except:
                print("Error: recv_world_msg() failed parsing the uresponses msg")
                return None
        else:
            print("Error: the msg type didn't exist!\n")
    except Exception as error:
        print("Error:recv_world_msg()", error)
        return
def recv_amazon_msg(msgtype,world_soc):
    # print("---------------------receive msg from world: \n") 
    var_int_buff = []
    try:
        while True:
            # try:
            buf = world_soc.recv(1)
            # if len(buf) <= 0: 
            #     print("buf length <0\n") 
            var_int_buff += buf
            msg_len, new_pos = _DecodeVarint32(var_int_buff, 0)
            if new_pos != 0:
                break
            # except IndexError as ex:
            #     continue

        buf_message = world_soc.recv(msg_len)
        if msgtype == "AConnected":
            connected = amazon_ups_pb2.Connected()
            try:
                connected.ParseFromString(buf_message)
                print(connected)
                return connected 
            except:
                print("Error: recv_amazon_msg() failed parsing the amazon connected msg")
                return None
        elif msgtype == "AmazonCommands":
            amazoncommand = amazon_ups_pb2.AmazonCommands()
            try:
                amazoncommand.ParseFromString(buf_message)
                print(amazoncommand)
                return amazoncommand
            except:
                print("Error: recv_amazon_msg() failed parsing the amazoncommand msg")
                return None
        else:
            print("Error: the msg type didn't exist!\n")
    except Exception as error:
        print("Error:recv_amazon_msg()", error)
        return
    return
#--------------------create world connnection socket--------------------------------
# get socket to world server as client
def get_world_socket():
    # global world_soc
    world_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            world_soc.connect((world_host, world_port))
        except Exception:
            print("Error: get_world_socket() failed connect to world")
            continue
        else:
            break
    return world_soc

#set up connection with world by sending & receiving Uconnect
def setup_world_connect(world_id,truck_num):
    world_soc = get_world_socket()
    uconnect = world_ups_pb2.UConnect()
    if world_id is None:
        create_world_uconnect(uconnect, None, truck_num)
        while True:
            send_msg(uconnect, world_soc)
            uconnected = recv_world_msg("UConnected",world_soc)
            if uconnected.result == "connected!":
                world_id = uconnected.worldid

                print("setup_world_connect():successfully connect to world: ",world_id)
                break
            # TODO: add new world and truck into db
            # do we need to check it the created world id is exist?
    else:
        # TODO: check is world is exst in database
        # if db_world_exit(world_id):
        print(" world if exist ",world_id)
        create_world_uconnect(uconnect, world_id, 0)
        while True:
            send_msg(uconnect, world_soc)
            uconnected = recv_world_msg("UConnected",world_soc)
            if uconnected.result == "connected!":
                world_id = uconnected.worldid
                print("successfully connect to world: ",world_id)
                break
        # else:
        #     print("World didn't find in database")
        
    return world_soc,world_id
# close world socket
# TODO: Need a while loop to continuely send?
def close_world_socket(world_soc):
    print("start close_world_socket\n")
    ucommand = world_ups_pb2.UCommands()
    ucommand.disconnect = True
    send_msg(ucommand, world_soc)
#--------------------create amazon connnection socket--------------------------------
# get socket to amazon as server
def setup_amazon_connect(world_id):
    amazon_listen_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            amazon_listen_soc.bind((amazon_host, amazon_port))
            amazon_listen_soc.listen()
            amazon_soc, amazon_addr = amazon_listen_soc.accept()  
            connect = amazon_ups_pb2.Connect()       
        except Exception as err:
            print("Error: setup_amazon_connect() failed connect to amazon",err)
            continue
        else:       
            print("connected with amazon socket!\n")
            break
    
    if world_id is None:
        print("Error: get_amazon_socket() world id can't be None\n")
    else:
        connect.worldid = world_id        
        while True:
            send_msg(connect, amazon_soc)
            connected = recv_amazon_msg("AConnected",amazon_soc)
            if connected.result == True:
                executor.submit(handle_amazon_connected, connected)
                print("setup_amazon_connect():successfully connect to amazon!\n")
                break
    return amazon_soc
def handle_amazon_connected(amazon_command):
    print("start handle_amazon_connected()")
    for warehouse in amazon_command.initwh:
        print("Save warehouse: wh_id: ",warehouse.id," x: ", warehouse.x, " y: ", warehouse.y)
        #save the warehouse detail into db
        db_add_warehouse(warehouse)
    return

#--------------------create data structure--------------------------------
# create uconnect to world simulator
def create_world_uconnect(uconnect,world_id,truck_num):
    if world_id is not None:
        uconnect.worldid = world_id
    while True:
        try:
            truck_num = int(input("Enter the number of trucks: "))
            print(truck_num)
        except ValueError:
            truck_num = int(truck_number)
            print('plase enter the right format!')
            continue
        else:
            if truck_num > 0:
                for i in range(truck_num):
                    new_truck = uconnect.trucks.add()
                    # TODO: dose truck x, y need to be defined?
                    # new_truck = Truck.objects.create(truck_package_number=0, status='idle')
                    # truck.id = int(cur_truck.truck_id)
                    new_truck.id = i
                    new_truck.x = 0
                    new_truck.y = 0
                db_add_truck(uconnect.trucks)
                break
            else:
                print('truck number need larger than 0')
                continue     
    uconnect.isAmazon = False
    return uconnect

def get_seq_num():
    seqnumlock.acquire()
    global seqnum
    seqnum = seqnum + 1
    temp_num = seqnum
    seqnumlock.release()
    print("\nnew seqnum:------------", temp_num)
    return temp_num
# --------------------------Handle world msg------------------------------
def handle_world_TruckStatus(truckstatus_resp):
    #update truck status
    print("handle_world_TruckStatus",truckstatus_resp)
    if truckstatus_resp.status == "IDLE":
        db_update_truck_status(truckstatus_resp.truckid,"idle")
    elif truckstatus_resp.status == "TRAVELING":
        db_update_truck_status(truckstatus_resp.truckid,"traveling")
    elif truckstatus_resp.status == "ARRIVE":
        db_update_truck_status(truckstatus_resp.truckid,"arrive")
    elif truckstatus_resp.status == "LOADING":
        db_update_truck_status(truckstatus_resp.truckid,"loading")
    elif truckstatus_resp.status == "DELIVERING":
        db_update_truck_status(truckstatus_resp.truckid,"delivering")
    else:
        db_update_truck_status(truckstatus_resp.truckid, truckstatus_resp.status)
    #update truck x y
    db_update_truck_location(truckstatus_resp.truckid, truckstatus_resp.x, truckstatus_resp.y)
    print("handle_world_TruckStatus(): finish udpate the truck status")
def handle_world_error(world_error, world_soc, amazon_soc):
    print("Received world error: ", world_error.err, "\n")
    oldseq = world_error.originseqnum
    msgtype = db_get_msgtype_seqnum(oldseq)
    if msgtype is None:
        print("Error: handle_world_error() Didn't find the msg")
    elif msgtype == "ugopickup":
        truck_id = db_get_truck_seqnum(oldseq)
        # find if truck_id exist or not, it exist, go to WareBindTruck table to find the wh_id
        if truck_id is None:
            print("Error: handle_world_error() truck_id is not exist\n")
        else:
            wh_id = db_get_truckbind_wh_id(truck_id)
            if wh_id is None:
                print("Error: handle_world_error() truck_id didn't bind to any wh\n")
            else:
                send_world_UGoPickUp(truck_id, wh_id, world_soc)
                # resend_world_UGoPickUp(truck_id, wh_id, world_soc,oldseq)
                return
        return
    elif msgtype == "ugodeliver":
        package_id = db_get_pack_seqnum(oldseq)
        truck_id = db_get_truck_seqnum(oldseq)
        # find if truck_id exist or not, it exist, go to WareBindTruck table to find the wh_id
        if package_id is None or truck_id is None:
            print("Error: handle_world_error() truck_id and package_id are both not exist\n")
        else:
            send_world_UGoDeliver(truck_id, package_id, world_soc)
        return
    elif msgtype == "uquery":
        truck_id = db_get_truck_seqnum(oldseq)
        # find if truck_id exist or not, it exist, go to WareBindTruck table to find the wh_id
        if  truck_id is None:
            print("Error: handxle_world_error() truck_id is not exist\n")
        else:
            send_world_UQuery(truck_id,world_soc)
        return
    else:
        print("Error: message type is not exist\n")

    # TODO
    # else:
    #     handle_world_acks(amazon_error.originseqnum)
def handle_world_delivered(delivered, world_soc, amazon_soc):
    print("start handle_world_delivered()\n")
    package_id = delivered.packageid
    # update truck status in db to delivered
    db_update_package_status(package_id,"delivered")
    # send UPSAmazonFinishShip to amazon
    send_amazon_finishship(package_id, amazon_soc)
    # update the package number in the truck in db
    current_packnum = db_update_truck_packnum(delivered.truckid,-1)
    print("handle_world_delivered packnum update to: ", current_packnum,"/n")
    if current_packnum == 0:
        # update the truck status to loading in db
        db_update_truck_status(delivered.truckid,"idle")
def handle_world_finished(completions, world_soc, amazon_soc):
    print("start handle_world_finished\n")
    truck_status = completions.status
    # print("handle_world_finished truck_status:\n",truck_status)
    if truck_status == "ARRIVE WAREHOUSE":
    # if truck_status == "shabiyan":
        print("handle_world_finished is arrive at warehouse\n")
        # update truck status in db to arrive
        db_update_truck_status(completions.truckid, "arrive")
        # sort out corresponding wait_pick package_id set corresponding to the truck
        packageid_set = db_get_package(completions.truckid, "wait_pick")
        if packageid_set:
            #update correesponding package status to loading
            db_update_truck_status(completions.truckid, "loading")
            # print("\nfind some ready to pick up item")
            for package_id in packageid_set:
                # send start pickup to amazon
                print("handle_world_finished send amazon\n")
                send_amazon_startship(package_id, amazon_soc)
        else:
            print("\nError: handle_world_finished() didn't find any ready to pick up item")
#--------------------------Handle amazon msg------------------------------
# TODO: this function don't need to send back to amazon?
def handle_amazon_finishship(amazon_finishship, world_soc):
    print("start handle_amazon_finishship()\n")
    package_id = amazon_finishship.packageid
    print("handle_amazon_finishship() package_id: ",package_id,"\n")
    # Get the truck id correponding to the package_id
    truck_id = db_get_pack_truck(package_id)
    print("start handle_amazon_finishship() truck_id:", truck_id,"\n")
    # increase the loaded pack num of the truck
    db_update_truck_packnum(truck_id,1)
    # TODO:do we need this?
    # # reduce the binded pack number of the truck            
    # db_update_truck_bindpacknum(truck_id, -1) 
    #update package status to delivering
    db_update_package_status(package_id, "delivering")
    # db_update_package_status(package_id, "delivering")
    wh_id = db_get_package_wh(package_id)
    if wh_id is not None:
        #check if there is other package in the same warehouse and be assigned to this truck
        packageid_set = db_get_package_truck_status_wh(truck_id, "wait_pick", wh_id)
        if packageid_set is None:
            db_remove_whbindtruck(truck_id)
            package_delivery_set = db_get_package_truck_status_wh(truck_id, "delivering", wh_id)
            for de_package in package_delivery_set:
                print("send ugodliver for package_id:  ",de_package, " truck: ",truck_id)
                # send world to let truck start delievery
                send_world_UGoDeliver(truck_id, de_package, world_soc)
            #update truck status to delivering
            db_update_truck_status(truck_id, "delivering")
        else:
            print("handle_amazon_finishship(): Truck still loading")
# TODO: add get_truck_package(package_id), db_get_package_wh(package_id) function 
def handle_amazon_startship(amazon_startship, world_soc, amazon_soc):
    package_id = amazon_startship.packageid
    # Get the truck id correponding to the package_id
    truck_id = db_get_pack_truck(package_id)
    wh_id = db_get_package_wh(package_id)
     #update package status to delivering
    db_update_package_status(package_id, "wait_pick")
    #check truck state
    truck_status = db_get_truck_status(truck_id)
    print("start handle handle_amazon_startship() ","truck_id: ",truck_id," wh_id: ",wh_id)
    if truck_status == "idle":
        print("truck_status detected handle idle\n")
        # while True:
        #     print("truck_status start send send_world_UGoPickUp\n")
        send_world_UGoPickUp(truck_id, wh_id, world_soc)
        # print("truck_status finish send send_world_UGoPickUp\n")
        # if (truck_status := db_get_truck_status(truck_id))!= "traveling":
        #     break
        # # add truck to the bindwhtruck
        # db_add_whbindtruck(truck_id,wh_id)
        print("handle_amazon_startship(): truck in on the way to wh: ",truck_id)
        return
    elif truck_status == "traveling":
        # print("truck_status detected traveling\n")
        # do nothing?
        return
    elif truck_status == "arrive" or truck_status == "loading":
        print("truck_status detected arrive\n")
        send_amazon_startship(package_id, amazon_soc)
        print("\nhandle_amazon_startship(): truck is already arrived at the wh")
        return
    elif truck_status == "delivering":
        # print("truck_status detected delivering\n")
        if send_world_UGoPickUp(truck_id, wh_id, world_soc) == True:
            db_add_whbindtruck(truck_id,wh_id)
            # print("\nhandle_amazon_startship(): truck in on the way to wh: ",truck_id)
        else:  #error
            print("\nError: handle_amazon_startship() failed send world_UGoPickUp")
        return
    else:
        print("truck status didn't exist\n")
    return 
# TODO：Add db_add_package, db_add_whbindtruck function
def handle_amazon_initship(amazon_initship, world_soc, amazon_soc):
    wh_id = amazon_initship.wid
    if db_check_user_exist(amazon_initship.username) == False:
        send_amazon_error("username not exist!\n", amazon_initship.id)
    while True:
        try:
            # # for test
            # send_amazon_initship(amazon_initship.packageid,0,amazon_soc)
            # return
            # first check if there is truck bind with the same ware house(idle,travling,arrive,loading) 
            if (truck_id := db_get_wh_bind_truck(wh_id,None)) is not None:
                print("find bind truck to same wh: ",truck_id)
                #add the initship into database package

                db_add_package(amazon_initship, truck_id) 
                # TODO: do we need this?
                # #add the bind package number to the truck in db
                # db_update_truck_bindpacknum(truck_id, 1) 
                #send initship msg back to amazon    
                send_amazon_initship(amazon_initship.packageid,truck_id,amazon_soc) 
                return
            # secondly check if there is truck is idle and not bind with any wh
            if(truck_id := db_get_status_truck("idle")) is not None:
                for truck_index in range(0, len(truck_id)):
                    if db_get_wh_bind_truck(None, truck_id[truck_index]) is None: 
                        print("find idle truck: ",truck_id[truck_index], truck_index )
                        #add the initship into database package
                        db_add_package(amazon_initship,truck_id[truck_index])  
                        #bind the truck to wh                  
                        db_add_whbindtruck(truck_id[truck_index],amazon_initship.wid)
                        # TODO: do we need this?
                        # #add the bind package number to the truck in db
                        # db_update_truck_bindpacknum(truck_id[truck_index], 1) 
                        #send initship msg back to amazon   
                        send_amazon_initship(amazon_initship.packageid,truck_id[truck_index],amazon_soc) 
                        # # Send new truck to the warehouse
                        # send_world_UGoPickUp(truck_id, wh_id, world_soc)
                        return 
            if(truck_id := db_get_status_truck("delivering")) is not None:
                for truck_index in range(0, len(truck_id)):
                    print("find delivering truck1: ",truck_id[truck_index])
                    #add the initship into database package
                    db_add_package(amazon_initship,truck_id[truck_index])  
                    #bind the truck to wh                  
                    db_add_whbindtruck(truck_id[truck_index],amazon_initship.wid)
                    # TODO: do we need this?
                    # #add the bind package number to the truck in db
                    # db_update_truck_bindpacknum(truck_id[truck_index], 1) 
                    #send initship msg back to amazon   
                    send_amazon_initship(amazon_initship.packageid,truck_id[truck_index],amazon_soc) 
                    # # Send new truck to the warehouse
                    # send_world_UGoPickUp(truck_id[truck_index], wh_id, world_soc)
                    return
            else:                   
                # wait for 2s to check again
                time.sleep(2)
                continue
        except Exception as error:
            print("Error:handle_amazon_initship()", error)
            return
    '''           
    # first check if there is truck on the arrive warehouse to the same warehouse
    # secondly check if there is truck idle
    # thirdly check if there is trucking on delivering
    truck = None
    wh_id = amazon_initship.wid
    while True:
        try:
            if (truck_id := db_get_wh_bind_truck(wh_id)) is not None:
                #add the initship into database package
                db_add_package(amazon_initship,truck_id) 
                #send initship msg back to amazon    
                send_amazon_initship(amazon_initship.packageid,truck_id,tracking_id,amazon_soc) 
                return
            elif(truck_id := get_idle_truck()) is not None: 
                # Send new truck to the warehouse
                send_world_UGoPickUp(truck_id, wh_id, world_soc)
                db_add_whbindtruck(amazon_initship,truck_id)
                #add the initship into database   
                db_add_package(amazon_initship,truck_id) 
                #send initship msg back to amazon   
                send_amazon_initship(amazon_initship.packageid,truck_id,tracking_id,amazon_soc) 
                return  
            elif(truck_id := get_delivering_truck()) is not None:
                send_world_UGoPickUp(truck_id, wh_id, world_soc) 
                db_add_whbindtruck(amazon_initship,truck_id)
                #add the initship into database 
                tracking_id = db_add_package(amazon_initship,truck_id)  
                #send initship msg back to amazon 
                send_amazon_initship(amazon_initship.packageid,truck_id,tracking_id,amazon_soc)  
                return     
            else:
                # wait for 2s to check again
                time.sleep(2)
                continue
    except Exception as error:
        print("Error:handle_amazon_initship()", error)
        return
    '''
 
# ---------handle ack-----------------------------------
def ack_to_amazon(ack,amazon_soc):
    add_amazon_seqnum(ack)
    upscommand = amazon_ups_pb2.UPSCommands()
    upscommand.acks.append(ack)
    print("---------------------ack_to_amazon() acknowledged:",upscommand,"\n") 
    send_msg(upscommand, amazon_soc)

def ack_to_world(seq,world_soc):
    print("start sending ack to world\n")
    add_world_seqnum(seq)
    print("ack to world finished append\n")
    ucommand = world_ups_pb2.UCommands()
    ucommand.acks.append(seq)
    print("---------------------ack_to_world() acknowledged:",ucommand) 
    send_msg(ucommand, world_soc)
    
def handle_amazon_acks(amazon_acks):
    print("start handle_world_acks",amazon_acks)  
    amazon_acknum.append(amazon_acks)
    print("finish handle_world_acks", amazon_acks)  
    return
def handle_world_acks(world_acks):
    print("start handle_world_acks",world_acknum)  
    world_acknum.append(world_acks)
    print("finish handle_world_acks", world_acknum)  
    return
def add_amazon_seqnum(amazon_acks):
    amazon_seqnum.append(amazon_acks)
    return
def add_world_seqnum(world_acks):
    world_seqnum.append(world_acks)
    return

def start_send_world_UQuery(world_soc):
    global query_truck
    seq_num = get_seq_num()
    ucommand = world_ups_pb2.UCommands()
    uquery_cmd = ucommand.queries.add()
    uquery_cmd.truckid = query_truck
    uquery_cmd.seqnum = seq_num
    # add this msg into db
    db_add_seqnum(seq_num, "uquery", query_truck, None)
    while True:
        send_msg(ucommand, world_soc)    
        print("send_world_UQuery():send:\n",ucommand)
        if seq_num in world_acknum:
            
            print("send_world_UQuery():received:\n",uresponse)  

            break   
        else:
            time.sleep(2)
            continue 

def resend_world_UGoPickUp(truck_id, wh_id, world_soc,seq_num):
    seq_num = get_seq_num()
    ucommand = world_ups_pb2.UCommands()
    ugopickup_cmd = ucommand.pickups.add()
    # ugopickup_cmd = world_ups_pb2.UGoPickup()
    ugopickup_cmd.truckid = truck_id
    ugopickup_cmd.whid = wh_id
    ugopickup_cmd.seqnum = seq_num
    # ucommand.pickups.append(ugopickup_cmd)
    # add this msg into db
    db_add_seqnum(seq_num, "ugopickup", truck_id, None)
    # print("finish add send_world_UGoPickUp into seqnumdb")
    while True:
        # print("start send send_world_UGoPickUp to world", ucommand)
        send_msg(ucommand, world_soc)  
        # print("send_world_UGoPickUp():send:\n",ucommand)
        if seq_num in world_acknum:
            print("send_world_UGoPickUp():received:\n",uresponse)  
            break
        else:
            time.sleep(2)
            continue

def front_world_UQuery(flag_status, truck_id):
    # global world_soc
    # start_send_world_UQuery(world_soc)
    print("send_world_UQuery() is been called")
    global query_flag
    global query_truck
    query_flag = flag_status
    query_truck = truck_id
    return

if __name__ == "__main__":
    world_soc,world_id = setup_world_connect(world_id,1)
    print("worldid is: ",world_id)
    amazon_soc = setup_amazon_connect(world_id)
    world_thread = Thread(target=process_world_msg, args=(world_soc,amazon_soc))
    world_thread.start()
    amazon_thread = Thread(target=process_amazon_msg, args=(world_soc,amazon_soc))
    amazon_thread.start()
    query_thread = Thread(target=process_query, args=(world_soc,amazon_soc))
    query_thread.start()
    # # world_id = 13
    # world_soc,world_id = setup_world_connect(None,1)
    # print("worldid is: ",world_id)
    # # amazon_soc = setup_amazon_connect(world_id)
    # amazon_soc = 0
    # world_thread = Thread(target=process_world_msg, args=(world_soc,amazon_soc))
    # world_thread.start()
    # amazon_thread = Thread(target=process_amazon_msg, args=(world_soc,amazon_soc))
    # amazon_thread.start()
    # send_world_UGoPickUp(1,1,world_soc)
    # world_id =0 
    # amazon_soc = setup_amazon_connect(world_id)
    # world_thread = Thread(target=process_world_msg, args=(amazon_soc,amazon_soc))
    # world_thread.start()
    # amazon_thread = Thread(target=process_amazon_msg, args=(amazon_soc,amazon_soc))
    # amazon_thread.start()

