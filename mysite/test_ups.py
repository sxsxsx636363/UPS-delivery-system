import world_ups_pb2 
import amazon_ups_pb2 
from db import *
# from upssocket import *
from test_db import *
import socket
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint
ups_port = 6666
ups_host = "vcm-32866.vm.duke.edu"
executor = ThreadPoolExecutor(50)
world_id = None
seqnum = 0
ack_num = []

def get_seq_num():
    # seqnum_lock.acquire()
    global seqnum
    seqnum = seqnum + 1
    temp_num = seqnum
    # seqnum_lock.release()
    return temp_num

def create_world_uconnect(connected):
    connected.result = True

def createainitship(acommand,id_seqnum, wid, item_num, packageid, _x, _y):
    ainitship = acommand.initship.add()
    ainitship.id= id_seqnum
    ainitship.wid = wid
    for i in range(item_num):
        new_item = ainitship.items.add()
        new_item.description= "test"
        new_item.quantity= i
    ainitship.packageid = packageid
    ainitship.x = _x
    ainitship.y = _y
    print(ainitship)
def send_world_error(error,oldseqnum,ups_soc):
    id_seqnum = get_seq_num()
    uresponse = world_ups_pb2.UResponses()
    uerror = uresponse.error.add()
    uerror.err= error
    uerror.originseqnum = oldseqnum
    uerror.seqnum = id_seqnum
    print("send_world_error(): ",uresponse)
    while True:
        send_msg(uresponse, ups_soc)
        print("send_world_error(): start receive\n")
        ucommand = recv_msg("UCommands",ups_soc)
        if id_seqnum in ack_num:
            print("successfully send ups startship",ucommand)
            break

def send_world_disconnect(ups_soc):
    print("start send send_world_disconnect(): ")
    id_seqnum = get_seq_num()
    uresponse = world_ups_pb2.UResponses()
    uresponse.finished = True
    print("send_world_disconnect(): ",uresponse)
    while True:
        send_msg(uresponse, ups_soc)
        time.sleep(2)
        continue
    return

def send_ups_startship(packageid):
    id_seqnum = get_seq_num()
    acommand = amazon_ups_pb2.AmazonCommands()
    astartship = acommand.startship.add()
    astartship.id= id_seqnum
    astartship.packageid = packageid
    print("send_ups_startship(): ",acommand)
    while True:
        send_msg(acommand, ups_soc)
        amazoncommand = recv_msg("UpsCommands",ups_soc)
        if id_seqnum in ack_num:
            print("successfully send ups startship",amazoncommand)
            break
def send_ups_finishship(packageid):
    id_seqnum = get_seq_num()
    acommand = amazon_ups_pb2.AmazonCommands()
    afinishship = acommand.finishship.add()
    afinishship.id= id_seqnum
    afinishship.packageid = packageid
    print("send_ups_finishship(): ",acommand)
    while True:
        send_msg(acommand, ups_soc)
        amazoncommand = recv_msg("UpsCommands",ups_soc)
        if id_seqnum in ack_num:
            print("successfully send ups finishship",amazoncommand)
            break

def send_ups_initship(wid, item_num, packageid, _x, _y, ups_soc):
    id_seqnum = get_seq_num()
    acommand = amazon_ups_pb2.AmazonCommands()
    createainitship(acommand, id_seqnum, wid, item_num, packageid, _x, _y)
    # print("send_ups_initship(): ",acommand)
    while True:
        send_msg(acommand, ups_soc)
        amazoncommand = recv_msg("UpsCommands",ups_soc)
        if id_seqnum in ack_num:
            print("successfully send ups initship",amazoncommand)
            break
    return


def send_world_UTruck(truck_id, cur_status, _x, _y, ups_soc):
    id_seqnum = get_seq_num()
    uresponse = world_ups_pb2.UResponses()
    utruck = uresponse.truckstatus.add()
    utruck.truckid = truck_id
    utruck.status = cur_status
    utruck.x = _x
    utruck.y = _y
    utruck.seqnum = id_seqnum
    print("send_world_UTruck(): ",uresponse)
    while True:
        send_msg(uresponse, ups_soc)
        ucommand = recv_msg("UCommands",ups_soc)
        if id_seqnum in ack_num:
            print("successfully send ups startship",ucommand)
            break
    return

def send_world_delivered(truck_id,package_id,ups_soc):
    uresponse = world_ups_pb2.UResponses()
    id_seqnum = get_seq_num()
    udelivered = uresponse.delivered.add()
    udelivered.truckid = truck_id
    udelivered.packageid = package_id
    udelivered.seqnum = id_seqnum
    print("send_world_delivered(): ",uresponse)
    while True:
        send_msg(uresponse, ups_soc)
        ucommand = recv_msg("UCommands",ups_soc)
        if id_seqnum in ack_num:
            print("successfully send ups send_world_delivered",ucommand)
            break
    
def send_world_finished(truck_id,_x,_y,_status,ups_soc):
    uresponse = world_ups_pb2.UResponses()
    id_seqnum = get_seq_num()
    ufinished = uresponse.completions.add()
    ufinished.truckid = truck_id
    ufinished.x = _x
    ufinished.y = _y
    ufinished.status = _status
    ufinished.seqnum = id_seqnum
    print("send_world_finished(): ",uresponse)
    while True:
        send_msg(uresponse, ups_soc)
        ucommand = recv_msg("UCommands",ups_soc)
        if id_seqnum in ack_num:
            print("successfully send ups send_world_finished",ucommand)
            break
# ---------------------send/rec msg------------------------------------
def send_msg(msg, ups_soc):
    # str1 = "---------------------start send msg: \n "
    # print(str1,msg)
    msg_str = msg.SerializeToString()
    _EncodeVarint(ups_soc.send, len(msg_str), None)
    ups_soc.send(msg_str)

def recv_msg(msgtype,world_soc):
    print("---------------------receive msg from world: \n") 
    var_int_buff = []
    try:
        while True:
            # try:
            buf = world_soc.recv(1)
            if len(buf) <= 0: 
                print("buf length <0\n") 
            var_int_buff += buf
            msg_len, new_pos = _DecodeVarint32(var_int_buff, 0)
            if new_pos != 0:
                break
            # except IndexError as ex:
            #     continue

        buf_message = world_soc.recv(msg_len)
        if msgtype == "Connect":
            connect = amazon_ups_pb2.Connect()
            try:
                connect.ParseFromString(buf_message)
                print(connect)
                return connect 
            except:
                print("Error: recv_msg() failed parsing the connected msg")
                return None
        if msgtype == "UCommands":
            uconmmand = world_ups_pb2.UCommands()
            try:
                uconmmand.ParseFromString(buf_message)
                print(uconmmand)
                return uconmmand 
            except:
                print("Error: recv_msg() failed parsing the uconmmand msg")
                return None
        elif msgtype == "UpsCommands":
            upscommand = amazon_ups_pb2.UPSCommands()
            try:
                upscommand.ParseFromString(buf_message)
                print("recv_msg():received upscommand:",upscommand)
                return upscommand
            except:
                # print("Error: recv_msg() failed parsing the upscommand msg")
                return None
        else:
            print("Error: the msg type didn't exist!\n")
    except Exception as error:
        print("Error:recv_msg()", error)
        return
def ack_to_world(ack, world_soc):
    # print("---------------------ack_to_world() acknowledged: \n") 
    ucommand = world_ups_pb2.UCommands()
    ucommand.acks.append(ack)
    # print(ucommand)
    for i in range(0,5):
        send_msg(ucommand, world_soc)
    
def ack_to_ups(ack,ups_soc):  
    acommand = amazon_ups_pb2.AmazonCommands() 
    acommand.acks.append(ack)
    print("---------------------ack_to_ups() acknowledged:",acommand)
    for i in range(0,5):
        send_msg(acommand, ups_soc)

def handle_ups_acks(ups_acks):
    ack_num.append(ups_acks)
    return
#--------------------create ups connnection socket--------------------------------
# get socket to ups server as client
def get_ups_socket():
    ups_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            ups_soc.connect((ups_host, ups_port))
        except Exception:
            print("Error: get_ups_socket() failed connect to world")
            continue
        else:
            break
    return ups_soc

#set up connection with world by sending & receiving Uconnect
def setup_ups_connect():
    ups_soc = get_ups_socket()
    connected = amazon_ups_pb2.Connected()
    create_world_uconnect(connected)
    while True: 
        if (uconnected := recv_msg("Connect",ups_soc)) is not None:
            send_msg(connected, ups_soc)  
            world_id = uconnected.worldid    
            print("setup_ups_connect():successfully connect to ups: ",world_id)           
            return ups_soc


def process_ups_msg(ups_soc,world_soc):
    while True:
        while True:    
            ups_command = recv_msg("UpsCommands",ups_soc)
            if ups_command is None:
                print("process_amazon_ms(): ups_command is None\n")
                continue
            else:
                print("---------------------process_amazon_msg() received msg: \n") 
                print(ups_command)
                break
        # for ups_initship in ups_command.initship:
        #     print("\nprocess ups_initship: ")
        #     print(ups_initship)
        #     executor.submit(ack_to_ups, ups_initship.id, ups_soc)
            # executor.submit(ups_initship, ups_initship, world_soc, amazon_soc)
        for ups_initship in range(0, len(ups_command.initship)):
            print("\nprocess ups_initship: ")
            print(ups_initship)
            executor.submit(ack_to_ups, ups_command.initship[ups_initship].id, ups_soc)
        for ups_startship in range(0, len(ups_command.startship)):
            print("\nprocess ups_startship: ")
            print(ups_command.startship[ups_startship])
            executor.submit(ack_to_ups, ups_command.startship[ups_startship].id, ups_soc)
        for ups_finishship in range(0, len(ups_command.finishship)):
            print("\nprocess ups_finishship: ")
            print(ups_finishship)
            executor.submit(ack_to_ups, ups_command.finishship[ups_finishship].id, ups_soc)
        # for ups_startship in ups_command.startship:
        #     print("\nprocess ups_startship: ")
        #     print(ups_startship)
        #     executor.submit(ack_to_ups, ups_startship.id, ups_soc)
        for ups_acks in ups_command.acks:
            print('\nups_command acks: ',ups_acks)
            executor.submit(handle_ups_acks, ups_acks) 

if __name__ == "__main__":
    ups_soc = setup_ups_connect()
    amazon_thread = Thread(target=process_ups_msg, args=(ups_soc,1))
    amazon_thread.start()
    # send_world_disconnect(ups_soc)
    # send_ups_initship(10, 20, 1, 12, 12, ups_soc)
    # db_update_package_status(0, "wait_pick")
    # db_update_truck_status(0,"delivering")
    # # db_remove_whbindtruck(0)
    send_ups_startship(0)
    # send_world_finished(0,1,1,"shabiyan")
    # db_update_truck_status(0,"arrive")
    # db_add_whbindtruck(0,0)
    # send_ups_finishship(0)
    # db_update_package_status(1, "delivering")
    # db_update_truck_status(1, "delivering")
    # # db_remove_whbindtruck(0)
    # send_world_delivered(1,1,ups_soc)
    # send_world_error("yanshishabi",1,ups_soc)
    # send_world_UTruck(2, "arrive", 23, 14, ups_soc)

