from django.shortcuts import render, redirect
from .forms import NewUserForm, UserModificationForm, TrackForm, DestForm, ReportForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .models import Package, Truck, Issue, WareBindTruck, Warehouse
from django.contrib.auth.decorators import login_required
import datetime
from django.core.mail import send_mail
from upssocket import *

# Create your views here.
def homepage(request):
    print(request.user.id)
    if request.method == 'POST':
        form = TrackForm(request.POST)
        if form.is_valid():
            tracknum = form.cleaned_data.get('tracknum')
            searchlist = Package.objects.filter(tracking_id=tracknum)
            if(searchlist):
                searchres = searchlist[0]
            else:
                messages.error(request,"Tracking number is wrong.")
                return render(request, 'register/home.html', locals())
            return redirect('register:package_detail', tracking_id=tracknum)
        else:
            messages.error(request,"Error in input format!")
            return render(request, 'register/home.html', locals())
    else:
        form = TrackForm()
        return render(request, 'register/home.html',{'form': form})

def register_request(request):
 if request.method == "POST":
  form = NewUserForm(request.POST)
  if form.is_valid():
   user = form.save()
   login(request, user)
   messages.success(request, "Registration successful." )
   return redirect("register:homepage")
  messages.error(request, "Unsuccessful registration. Invalid information.")
 form = NewUserForm()
 return render(request=request, template_name="register/register.html", context={"register_form":form})

def login_request(request):
 if request.method == "POST":
  form = AuthenticationForm(request, data=request.POST)
  if form.is_valid():
   username = form.cleaned_data.get('username')
   password = form.cleaned_data.get('password')
   user = authenticate(username=username, password=password)
   if user is not None:
    login(request, user)
    return redirect("register:homepage")
   else:
    messages.error(request,"Invalid username or password.")
  else:
   messages.error(request,"Invalid username or password.")
 form = AuthenticationForm()
 return render(request=request, template_name="register/login.html", context={"login_form":form})

def logout_request(request):
 logout(request)
 messages.info(request, "You have successfully logged out.") 
 return redirect("register:homepage")

def user_view_profile(request):
    try:
        user = User.objects.get(id=request.user.id)
    except:
        return redirect('register:homepage')
    return render(request, "register/user_profile.html", {'user': user})

def user_edit_profile(request):
    try:
        user = User.objects.get(id=request.user.id)
    except:
        return redirect('register:homepage')
    if request.method == 'POST':
        form = UserModificationForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['email']:
                user.email = form.cleaned_data['email']
            if form.cleaned_data['password']:
                user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect("register:user_view_profile")
    else:
        form = UserModificationForm()
    return render(request, 'register/user_modification_form.html', {'form': form})


def track_request(request):
    if request.method == 'POST':
        form = TrackForm(request.POST)
        if form.is_valid():
            tracknum = form.cleaned_data.get('tracknum')
            searchlist = Package.objects.filter(tracking_id=tracknum)
            if(searchlist):
                searchres = searchlist[0]
            else:
                message = 'tracking number is wrong'
                return render(request, 'register/track_package.html', locals())
            return redirect('register:package_detail', tracking_id=tracknum)
        else:
            message = 'Error in input format!'
            return render(request, 'register/track_package.html', locals())
    form = TrackForm()
    return render(request, 'register/track_package.html',{'form': form})


@login_required(login_url='login')
def package_list_show(request):
    orders = Package.objects.filter(user_id=request.user.id)
    # completed = orders.filter(status='delivered')
    completed_pack = orders.filter(status='delivered')
    pending_pack = orders.exclude(status='delivered')

    context = {'orders': orders, 'pending_package': pending_pack, 'completed_package': completed_pack}
    return render(request, 'register/package_list.html', context)


# @login_required(login_url='login')
def package_detail_request(request, tracking_id):
    flag=0
    seeDes=0
    seeLocation=1
    u_id=request.user.id
    p = Package.objects.get(tracking_id=tracking_id)   
    if p.user_id==u_id:
        flag=1
        seeDes=1
    if p.status == 'delivering' or p.status == 'delivered':
        flag=0
    if p.status == 'unready' or p.status == 'wait_pick':
        seeLocation=1
    description=p.description
    status =p.status
    truck_id = p.truck_id
    deliver_x = p.deliver_x
    deliver_y = p.deliver_y 
    count=p.count
    return render(request, 'register/package_detail.html', {'package':p, 'tracking_id':tracking_id, 'description':description, 'status':status, 'truck_id':truck_id,'deliver_x': deliver_x, 'deliver_y':deliver_y, 'count':count, 'flag':flag, 'seeLocation': seeLocation, 'seeDes': seeDes})



@login_required(login_url='login')
def change_dest_request(request, tracking_id):
    flag=1
    u_id=request.user.id
    p = Package.objects.get(tracking_id=tracking_id)   
    if p.user_id!=u_id:
        flag=0  
        return render(request, 'register/change_dest.html', locals())
    if request.method == 'POST':
        form = DestForm(request.POST)
        if form.is_valid():
            x = form.cleaned_data.get('x')
            y = form.cleaned_data.get('y')
            cur_package = Package.objects.get(tracking_id=tracking_id)   
            if cur_package.status == 'delivering' or cur_package.status == 'delivered':
                messages.error(request, "The package is on delivering or delivered so cannot change address.")
                return render(request, 'register/change_dest.html', locals())
            cur_package.deliver_x = x
            cur_package.deliver_y = y
            cur_package.save()
            subject = "[Mini-UPS] Your package delivered address has been changed!"
            body= "Dear Customer,\n\nYour address for package with tracking_id "  + str(tracking_id)+" has been successfully changed to ("+ str(x)+ "," +str(y) +"). Thank you for reaching out to us and try our service.\n\nBest regards,\nThe Mini-UPS Team"
            sender = "yyan0916@outlook.com"
            receiver = []
            receiver.append(request.user.email)
            send_mail(
                    subject,
                    body,
                    sender,
                    receiver,
                    fail_silently=False
                    )   
            messages.success(request, 'Address changed successfully, notification have been sent to your linked email')
            return render(request, 'register/change_dest.html', locals())
        else:
            messages.error(request, "Please check your input format.")
            return render(request, 'register/change_dest.html', locals())
    form = DestForm()
    return render(request, 'register/change_dest.html', locals())

def report_issue_request(request, tracking_id):
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['email']:
                email = form.cleaned_data['email']
            if form.cleaned_data['content']:
                content=(form.cleaned_data['content'])
            
            subject = "[Mini-UPS] Your problem has been reported!"
            body= "Dear Customer,\n\nYour problem related to package which tracking_id is "  + str(tracking_id)+" has been successfully reported. Thank you for reaching out to us. We will get back to you as soon as possible.\n\nBest regards,\nThe Mini-UPS Team"
            sender = "yyan0916@outlook.com"
            receiver = []
            receiver.append(email)
            new=Issue.objects.get_or_create(tracking_id=tracking_id,content=content,email=email)
            send_mail(
                    subject,
                    body,
                    sender,
                    receiver,
                    fail_silently=False
                    )   
            messages.success(request, 'Your message have been uploaded.')
        else:
            messages.error(request, 'Please check your format.')
    form = ReportForm()
    return render(request, 'register/report_issue.html', locals())

     

def map_truck_request(request, tracking_id):
    
    cur_package = Package.objects.filter(tracking_id=tracking_id).first()
    pack_truck=cur_package.truck_id
    if cur_package.status == 'delivering':
            status="delivering"
            front_world_UQuery(True, pack_truck)
            cur_truck = Truck.objects.get(truck_id=pack_truck)
            x=cur_truck.x
            y=cur_truck.y
            return render(request, 'register/map_truck.html', locals())
    if cur_package.status == 'delivered':
            status="delivered"
            front_world_UQuery(False, pack_truck)
            x=cur_package.deliver_x
            y=cur_package.deliver_y
            return render(request, 'register/map_truck.html', locals())
    if cur_package.status == 'unready' or cur_package.status == 'wait_pick':
            status="at warehouse"
            front_world_UQuery(True, pack_truck)
            ware_id=cur_package.warehouse_id
            cur_ware = Warehouse.objects.get(warehouse_id=ware_id)
            x=cur_ware.x
            y=cur_ware.y
            return render(request, 'register/map_truck.html', locals())
    return render(request, 'register/map_truck.html', locals())
