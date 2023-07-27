import os
import world_ups_pb2 
import amazon_ups_pb2 
from django.db.models import Q
import threading
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
if django.VERSION >= (1, 7):
    django.setup()

from register.models import *

def db_check_user_exist(u_id):
    if not User.objects.filter(id=u_id).exists():
        print("No User found for is as", u_id)
        return False
    return True

def db_add_package_user(amazon_initship ,t_id,u_id):
    package_id = amazon_initship.packageid
    user_id = u_id # temp set as -1
    truck_id = t_id
    deliver_x = amazon_initship.x
    deliver_y = amazon_initship.y
    warehouse_id = amazon_initship.wid
    descript = ""
    ct=0
    for i in amazon_initship.items:
        descript+=i.description
        descript+= "*"
        descript+=str( i.quantity) 
        descript+= " "    
        ct=ct+1
    try:
        Package.objects.get_or_create(tracking_id=package_id, status="unready", user_id=user_id, truck_id=truck_id, deliver_x=deliver_x, deliver_y=deliver_y, warehouse_id= warehouse_id,description=descript, count=ct)
    except Exception as e:
        print(e)
        return
    print("Add Package successfully")
    return
    
def db_get_status_truck(status):
    valid_status = [status[0] for status in Truck.status_options]
    if status not in valid_status:
        print("Error: truckStatus is not valid")
        return None
    trucks= Truck.objects.filter(status=status).order_by('truck_id')
    if trucks:
        trucks_ids = [truck.truck_id for truck in trucks]
        print(trucks_ids)
        return trucks_ids
    else:
        print("No truck found for status as", status)
        return None

# 
def db_add_truck(trucks):
    try:
        for newtruck in trucks:
            truck_id = newtruck.id
            x = newtruck.x
            y = newtruck.y
            Truck.objects.get_or_create(truck_id=truck_id,x=x,y=y,status="idle",package_number=0)
    except Exception as e:
        print(e)   
    return
# 
def db_add_whbindtruck(truck_id,wh_id):
    if not Truck.objects.filter(truck_id=truck_id).exists():
        print("Error: truck with id", truck_id, "does not exist")
        return
    exist_truck = Truck.objects.all().filter(truck_id = truck_id).first()
    new_whbindtruck = WareBindTruck.objects.get_or_create(warehouse_id=wh_id,truck_id=exist_truck.truck_id)
    # new_whbindtruck.save()
    print("Bind truck with warehouse successfully")
    return new_whbindtruck[0]

def db_add_seqnum(seq_num, msg_type, truckid, packageid):
    valid_type = [msg_type for massege_type in Seqnum.massege_type_options]
    if msg_type not in valid_type:
        print("Error: msg_type is not valid")
        return None
    if Seqnum.objects.filter(seqnum=seq_num).exists():
        print("Error: ", seq_num, "msg already exist")
        return None
    try:
        if truckid is not None and packageid is not None:
            new_seq = Seqnum.objects.get_or_create(seqnum=seq_num,massege_type=msg_type, truck_id = truckid, package_id = packageid)
        elif truckid is not None and packageid is None:
            new_seq = Seqnum.objects.get_or_create(seqnum=seq_num,massege_type=msg_type, truck_id = truckid, package_id = -1)
        elif truckid is None and packageid is not None:
            new_seq = Seqnum.objects.get_or_create(seqnum=seq_num,massege_type=msg_type, truck_id = -1, package_id = packageid)
        else:
            new_seq = Seqnum.objects.get_or_create(seqnum=seq_num,massege_type=msg_type, truck_id = -1, package_id = -1)
        print("Add Seqnum successfully")
    except Exception as e:
        print(e)   
    return

def db_get_msgtype_seqnum(seq_num):
    if not Seqnum.objects.filter(seqnum=seq_num).exists():
        print("Error: ", seqnum, "msg not exist")
        return None
    msg = Seqnum.objects.all().filter(seqnum=seq_num).first()
    if msg:
        print("get msg type: ", msg.massege_type)
        return msg.massege_type
    else:
        None
def db_get_truck_seqnum(seq_num):
    if not Seqnum.objects.filter(seqnum=seq_num).exists():
        print("Error: db_get_truck_seqnum", seqnum, "msg not exist")
        return None
    msg = Seqnum.objects.all().filter(seqnum=seq_num).first()
    if msg:
        print("db_get_truck_seqnum get truck_id: ", msg.truck_id)
        if msg.truck_id == -1:
            return None
        else:
            return msg.truck_id
    else:
        print("db_get_truck_seqnum: msg didn't find\n")
        return None

def db_get_pack_seqnum(seq_num):
    if not Seqnum.objects.filter(seqnum=seq_num).exists():
        print("Error: db_get_truck_seqnum", seqnum, "msg not exist")
        return None
    msg = Seqnum.objects.all().filter(seqnum=seq_num).first()
    if msg:
        print("db_get_truck_seqnum get package_id: ", msg.package_id)
        if msg.package_id == -1:
            return None
        else:
            return msg.package_id
    else:
        print("db_get_truck_seqnum:msg didn't find\n")
        return None
# 
def db_get_wh_bind_truck(wh_id,t_id):
    if wh_id is not None: 
        truck_=WareBindTruck.objects.all().filter(warehouse_id=wh_id).first()
        if truck_:
                print(truck_.truck_id)
                return truck_.truck_id
        else:
            return None
    elif t_id is not None:
        exist_truck=WareBindTruck.objects.all().filter(truck_id=t_id)
        if exist_truck:
            return exist_truck
        else:
            return None
    return None

# 
def db_get_truckbind_wh_id(t_id):
    if t_id is None:
        return None
    else:
        if not WareBindTruck.objects.filter(truck_id=t_id).exists():
            print("truck didn't bind to any wh")
            return None
        else:
            truck = WareBindTruck.objects.all().filter(truck_id=t_id).first()
            print("Find the wh_if of the bind truck: ", truck.warehouse_id, "\n")
            return truck.warehouse_id



def db_add_package(amazon_initship ,t_id):
    print("start db_add_package()")
    package_id = amazon_initship.packageid
    u_id = amazon_initship.username # temp set as -1
    # u_id = 1
    if not User.objects.filter(id=u_id).exists():
        db_add_package_user(amazon_initship ,t_id,-1)
        print("Add package ",package_id, " with user_id=-1" )
        return
    deliver_x = amazon_initship.x
    deliver_y = amazon_initship.y
    warehouseid = amazon_initship.wid
    descript = " "
    ct=0

    try:
        for item in amazon_initship.items:
            descript+=item.description
            descript+= "*"
            descript+=str(item.quantity) 
            descript+= "  "    
            ct=ct+1
        Package.objects.get_or_create(tracking_id=package_id, status="unready",  user_id=u_id, truck_id=t_id, deliver_x=deliver_x, deliver_y=deliver_y, warehouse_id= warehouseid,description=descript, count=ct)
    except Exception as e:
        print(e)
        return
    print("Add Package successfully")
    return

# 
def db_update_truck_status(truckid,truckstatus):
    if not Truck.objects.filter(truck_id=truckid).exists():
       print("Error: truck with id", truckid, "does not exist")
       return
    valid_status = [status[0] for status in Truck.status_options]
    if truckstatus not in valid_status:
       print("Error: truckstatus is not valid")
       return
    num_updated = Truck.objects.filter(truck_id=truckid).update(status=str(truckstatus))
    if num_updated > 0:
       print("Truck", truckid, "status updated to", truckstatus)
       return
    else:
       print("Error: failed to update truck", truckid, "status")
       return

def db_update_truck_location(truckid,_x,_y):
    if not Truck.objects.filter(truck_id = truckid).exists():
       print("Error: truck with id", truckid, "does not exist")
       return
    num_updated = Truck.objects.filter(truck_id=truckid).update(x = int(_x), y = int(_y))
    if num_updated > 0:
       print("Truck", truckid, "locarion updated to x:", _x, " and y: ", _y)
       return
    else:
       print("Error: failed to update truck", truckid, "location")
       return

# 
def db_update_package_status(package_id, packageStatus):
    valid_status = [status[0] for status in Package.status_options]
    if packageStatus not in valid_status:
       print("Error: packageStatus is not valid")
       return
    if not Package.objects.filter(tracking_id=package_id).exists():
       print("Error: package with id", package_id, "does not exist")
       return
    num_updated = Package.objects.filter(tracking_id=package_id).update(status=str(packageStatus))
    if num_updated > 0:
      print("Package", package_id, "status updated to", packageStatus)
      return
    else:
      print("Error: failed to update package", package_id, "status")
      return
# 
def db_get_package_truck_status_wh(truckid, packageStatus, wh_id):
    valid_status = [status[0] for status in Package.status_options]
    if packageStatus not in valid_status:
        print("Error: packageStatus is not valid")
        return None
    
    if not Truck.objects.filter(truck_id=truckid).exists():
        print("Error: truck with id", truckid, "does not exist")
        return None
    
    packages = Package.objects.filter(truck_id=truckid, status=packageStatus, warehouse_id = wh_id).order_by('tracking_id')
    if packages:
        package_ids = [package.tracking_id for package in packages]
        print(package_ids)
        return package_ids
    else:
        print("No packages found for truck", truckid, "with status", packageStatus)
        return None


# 
def db_get_package(truckid, packageStatus):
    valid_status = [status[0] for status in Package.status_options]
    if packageStatus not in valid_status:
        print("Error: packageStatus is not valid")
        return None
    
    if not Truck.objects.filter(truck_id=truckid).exists():
        print("Error: truck with id", truckid, "does not exist")
        return None
    
    packages = Package.objects.filter(truck_id=truckid, status=packageStatus).order_by('tracking_id')
    if packages:
        package_ids = [package.tracking_id for package in packages]
        print(package_ids)
        return package_ids
    else:
        print("No packages found for truck", truckid, "with status", packageStatus)
        return None
    
# 
def db_get_x_destlocation(package_id):
    if not Package.objects.filter(tracking_id=package_id).exists():
        print("Error: package with id", package_id, "does not exist")
        return None
    else:
        
        package = Package.objects.filter(tracking_id=package_id).first()
        print("db_get_x_destlocation() exist:",package.deliver_x,"\n")
        return package.deliver_x

def db_get_y_destlocation(package_id):
    if not Package.objects.filter(tracking_id=package_id).exists():
        print("Error: package with id", package_id, "does not exist")
        return None
    else:
        package = Package.objects.filter(tracking_id=package_id).first()
        print("db_get_y_destlocation() exist:",package.deliver_y,"\n")
        return package.deliver_y

def db_update_truck_packnum(truckid, edit_value):
    try:
        truck = Truck.objects.get(truck_id=truckid)
    except Truck.DoesNotExist:
        print(f"Error: Truck with id {truckid} does not exist")
        return None
    try:
        new_packnum = int(edit_value)
    except ValueError:
        print(f"Error: {edit_value} is not a valid integer value for packnum")
        return None
    new_package_number = truck.package_number+new_packnum
    num_updated = Truck.objects.filter(truck_id=truckid).update(package_number=new_package_number)   
    return new_package_number
def db_get_package_wh(package_id):
    if not Package.objects.filter(tracking_id=package_id).exists():
       print("Error: package with id", package_id, "does not exist")
       return None
    else:
       package = Package.objects.filter(tracking_id=package_id).first()
       print(package.warehouse_id)
       return package.warehouse_id
# 
def db_get_pack_truck(package_id):
    if not Package.objects.filter(tracking_id=package_id).exists():
        print("Error: package with id", package_id, "does not exist")
        return None
    else:
        print("db_get_pack_truck() exist\n")
        package = Package.objects.filter(tracking_id=package_id).first()
        return package.truck_id
    
# 
def db_remove_whbindtruck(tr_id):
    if not WareBindTruck.objects.filter(truck_id=tr_id).exists():
        print("Error: truck with id", tr_id, "does not exist in warehouse table")
        return
    else:
        whbindtruck = WareBindTruck.objects.get(truck_id=tr_id)
        whbindtruck.delete()
        print("Truck", tr_id, "successfully removed from WareBindTruck table")
        return  
    
# 
def get_package_wh(package_id):
    if not Package.objects.filter(tracking_id=package_id).exists():
       print("Error: package with id", package_id, "does not exist")
       return None
    else:
        package = Package.objects.get(tracking_id=package_id)
        print(package.warehouse_id)
        return package.warehouse_id 
    
# 
def db_get_truck_status(truck_id):
    if not Truck.objects.filter(truck_id=truck_id).exists():
        print("Error: truck with id", truck_id, "does not exist")
        return None
    else:
        truck = Truck.objects.get(truck_id=truck_id)
        print(truck.status)
        return truck.status

# TODO: test
def query_user_pack(u_id):
    if not User.objects.filter(user_id=u_id).exists():
        print("Error: user with id", u_id, "does not exist")
        return None
    try:
        user_pack = Package.objects.all().filter(user_id=u_id)
        package_ids = [package.tracking_id for package in user_pack]
        if user_pack:
            return package_ids
        else:
            return None
    except Exception as e:
        print(e)

# 
def query_pack(track_id):
    if not Package.objects.filter(tracking_id=track_id).exists():
        print("Error: package with id", track_id, "does not exist")
        return None
    try:
        user_pack = Package.objects.all().filter(tracking_id=track_id)
        if user_pack:
            return user_pack
        else:
            return None
    except Exception as e:
        print(e)

def db_add_warehouse(warehouse):
    print("start add wh in db")
    try: 
        warehouse = Warehouse.objects.get_or_create(warehouse_id=warehouse.id, x=warehouse.x, y=warehouse.y)
    except Exception as e:
        print(e)
    print("finish add wh in db")
    return

def db_yan_add_warehouse(warehouse_id, x, y):
    warehouse = Warehouse(warehouse_id=warehouse_id, x=x, y=y)
    warehouse.save()
