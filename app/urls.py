from . import views 
from django.urls import path

app_name = "app"

urlpatterns = [
    path("",views.QueryView.as_view(),name="query"),
    path("new_chat/", views.NewChatView.as_view(), name="new_chat"),
    path("memory/",views.Memory.as_view(),name="memory")
]