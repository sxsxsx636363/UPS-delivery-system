import world_ups_pb2 
import amazon_ups_pb2 
from db import *
def create_truck(truck_num):
    uconnect = world_ups_pb2.UConnect()
    for i in range(truck_num):
        new_truck = uconnect.trucks.add()
        new_truck.id = i
        new_truck.x = 0
        new_truck.y = 0
    print(uconnect.trucks)
    return uconnect.trucks 

def test_db_add_truck(truck_num):
    trucks = create_truck(truck_num)
    db_add_truck(trucks)

def test_db_add_whbindtruck(truck_id,wh_id):
    db_add_whbindtruck(truck_id,wh_id)

def createainitship(id, wid, item_num, packageid, _x, _y):
    acommand = amazon_ups_pb2.AmazonCommands()
    ainitship = acommand.initship.add()
    ainitship.id= id
    ainitship.wid = wid
    for i in range(item_num):
        new_item = ainitship.items.add()
        new_item.description= "test"
        new_item.quantity= i
    ainitship.packageid = packageid
    ainitship.x = _x
    ainitship.y = _y
    print(ainitship)
    return ainitship
def test_db_add_package(id, wid, item_num, packageid, _x, _y, truck_id):
    amazon_initship = createainitship(id, wid, item_num, packageid, _x, _y)
    db_add_package(amazon_initship,truck_id)


def test_user_add_package(id, wid, item_num, packageid, _x, _y, truck_id,u_id):
    amazon_initship = createainitship(id, wid, item_num, packageid, _x, _y)
    db_add_package_user(amazon_initship ,truck_id,u_id)   



def test_db_get_wh_bind_truck(wh_id,t_id):
   db_get_wh_bind_truck(wh_id,t_id) 
   

# def create_warehouse(id,xs,ys):
#     from register.models import Warehouse
#     assert len(xs)==len(ys)
#     if Warehouse.objects.all().count()==0:
#         for i in range(len(xs)):
#             Warehouse.objects.create(warehouse_id=id[i], address_x=xs[i],address_y=ys[i])

if __name__ == "__main__":
    db_yan_add_warehouse(1, 5, 3)
    db_yan_add_warehouse(2, 10, 20)
    db_yan_add_warehouse(3, 20, 20)
    # test_db_add_truck(3)
    # test_db_add_truck(5)
    # test_db_add_whbindtruck(1,1)
    # test_db_add_whbindtruck(3,3)
    # test_db_add_whbindtruck(4,4)
    # test_db_add_package(1, 2, 2, 2, 3, 4, 2)
    # test_db_add_package(3, 3, 3, 3, 4, 5, 2)
    # test_db_add_package(4, 2, 2, 10, 6, 5, 2)
    # test_db_add_package(5, 3, 3, 9, 4, 5, 3)
    # db_update_truck_status(0,"traveling")
    # db_update_truck_status(1,"arrive")
    # db_update_truck_status(2,"loading")
    # db_update_truck_status(3,"delivering")
    # db_update_truck_status(2,"arrive")
    # db_update_truck_status(4,"delivering")
    # db_update_truck_status(0,"delivering")
    # db_update_truck_packnum(1,10)
    # db_update_truck_packnum(2,20)
    # db_get_wh_bind_truck(1,1)
    # db_get_wh_bind_truck(None,1)
    # db_get_wh_bind_truck(None,None)
    # db_update_package_status(2, "p")
    # db_update_package_status(2, "wait_pick")
    # db_update_package_status(2, "delivering")
    # db_update_package_status(10, "delivering")
    # db_update_package_status(3, "wait_pick")
    # db_get_package(2, "delivering")
    # db_get_package(2, "d")
    # db_get_package(7, "delivering")
    # db_get_package(3, "unready")
    # db_get_package(2, "wait_pick")
    # db_get_package(3, "wait_pick")
    # db_update_truck_packnum(6, 3)
    # db_update_truck_packnum(0, 2)
    # db_update_truck_packnum(0, -1)
    # db_update_truck_packnum(1, 3)
    # db_update_truck_packnum(1, 9)
    # db_get_pack_truck(13)
    # db_get_pack_truck(1)
    # db_get_pack_truck(10)
    # db_remove_whbindtruck(1)
    # db_remove_whbindtruck(2)
    # db_remove_whbindtruck(3)
    # get_package_wh(13)
    # get_package_wh(10)
    # get_package_wh(1)
    # db_get_truck_status(2)
    # db_get_truck_status(0)
    # db_get_truck_status(7)
    # db_get_status_truck("arrive")
    # db_get_status_truck("delivering")
    # db_get_status_truck("arve")
    # db_get_status_truck("traveling")
    # test_user_add_package(id, wid, item_num, packageid, _x, _y, truck_id,u_id)
    # test_user_add_package(9, 2, 3, 18, 0, 0, 3,1)
    # test_user_add_package(10,3, 2, 38, 2, 9, 2,1)
    # test_user_add_package(10,3, 2, 28, 22, 9, 3,1)
    # db_update_package_status(18, "delivering")
    # db_update_package_status(28, "delivered")
    # db_update_package_status(88, "delivered")
    # db_add_whbindtruck(1,2)
    # db_get_truckbind_wh_id(1)
    # db_get_truckbind_wh_id(3)
    # db_get_truckbind_wh_id(0)

    # db_add_seqnum(1,"uquery",1,2)
    # db_add_seqnum(2,"ugodeliver",0,None)
    # db_get_msgtype_seqnum(0) #upsamazoninitship
    # db_get_msgtype_seqnum(1)#uquery
    # db_get_msgtype_seqnum(2)#ugodeliver
    # db_get_truck_seqnum(0)#-1
    # db_get_truck_seqnum(1)#1
    # db_get_truck_seqnum(2)#0
    # db_get_pack_seqnum(0)#-1
    # db_get_pack_seqnum(1)#2
    # db_get_pack_seqnum(2)#-1
    # db_update_truck_status(0,"arrive")
    # db_update_truck_location(0,1,0)
    # db_update_truck_status(0,"arrive")
   