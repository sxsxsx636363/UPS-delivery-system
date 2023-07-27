from django.urls import path
from . import views

app_name = "register"

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("register/", views.register_request, name="register"),
    path("login/", views.login_request, name="login"),
    path("logout/", views.logout_request, name= "logout"),
    path("user_view_profile", views.user_view_profile, name="user_view_profile"),
    path("user_edit_profile", views.user_edit_profile, name="user_edit_profile"),
    path("track_package/", views.track_request, name="track_package"),
    path("package_list/", views.package_list_show, name="package_list"),
    path('package_detail/<int:tracking_id>/', views.package_detail_request, name = "package_detail"),
    path('change_dest/<int:tracking_id>/', views.change_dest_request, name = "change_dest"),
    path('report_issue/<int:tracking_id>', views.report_issue_request, name = "report_issue"),
    path('map_truck/<int:tracking_id>', views.map_truck_request, name = "map_truck"),
    
]
