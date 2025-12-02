from django.urls import path
from . import views

urlpatterns = [

    path('', views.index, name='index'),
    path('error/', views.aud_lec, name='error'),
    path('mark/', views.mark_paper, name='mark'),
    path('upload/', views.upload, name='upload'),
    path('results/', views.results, name='results'),
    path('reports/', views.reports, name='reports'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('lecturer/', views.lecturer, name='lecturer'),
    path('auditor/', views.auditor, name='auditor'),
    path('write_report/<int:marking_task_id>/', views.write_report, name='write_report'),
    path('auditor/view_reports/', views.view_reports, name='view_reports'),
    path('create_report/', views.create_report_for_auditor, name='create_report_for_auditor'),

    
]


