from django.urls import path, re_path
from toys import views

urlpatterns = [
    re_path(r'^toys/$', views.ToyListView.as_view(), name='toys_list'),
    re_path(r'^toys/(?P<pk>[0-9]+)$', views.ToyDetailView.as_view(), name='toy_detail'),
]