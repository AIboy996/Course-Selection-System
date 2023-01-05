from django.contrib import admin
from django.urls import path, re_path
from . import views



urlpatterns = [
    # 通用
    re_path(r'^$', views.login),
    path('login/', views.login),
    path('logout/', views.logout),
    path('admin/', admin.site.urls),
    path("message/", views.message),
    path("message/message_delete/", views.message_delete),
    # 未完成的页面
    path('find_password/', lambda x:views.error(x, 404)),
    path('chang_password/', lambda x:views.error(x, 404)),

    # 学生有关网页
    path('index/', views.index),
    path('me/', views.me),
    path('classinfo/', views.classinfo),
    path('classinfo/detail/', views.classinfo_detail),
    path('classchoice/', views.classchoice),
    path('classchoice/drop_class/', views.drop_class),
    path('classchoice/add_class/', views.add_class),
    path('program/', views.program),
    path('classtable/', views.class_table),
    path("score/", views.score),
    re_path(r"^evaluation/(.*)/?$", views.evaluation),
    path('student_note/', views.student_note),

    #### 老师有关网页 ###
    path("teacher_index/", views.teacher_index),
    path("teacher_me/", views.teacher_me),
    path("evaluation_view/", views.evaluation_view),
    path("evaluation_view/evaluation_detail/", views.evaluation_detail),
    path("teach_table/", views.teach_table),
    path("teach_table/student_list/", views.student_list),
    path("grade_mission/", views.grade_mission),
    re_path(
        r"^grade_mission/grade_set/(?P<classid>[A-Z]{4}[0-9]{6}\.[0-9]{2})/?(?P<stu_id>[0-9]*)/$", views.grade_set),
    re_path(
        r"^grade_mission/grade_set/(?P<classid>[A-Z]{4}[0-9]{6}\.[0-9]{2})/?(?P<stu_id>[0-9]*)/grade_delete/$", views.grade_delete),
    re_path(
        r"^grade_mission/grade_set/(?P<classid>[A-Z]{4}[0-9]{6}\.[0-9]{2})/grade_message", views.grade_message),
    path("grade_mission/grade_views/", views.grade_views),
    path("class_open/", views.class_open),
    path("class_open/class_delete/", views.class_delete),
    path("class_adj/", views.class_adj),
    re_path(
        "class_adj/adjust_views/(?P<classid>[A-Z]{4}[0-9]{6}\.[0-9]{2})/?$", views.adjust_views),
    path("adjust/", views.adjust),

    #### 教务老师有关网页 ###
    path("admin_index/", views.admin_index),
    path("admin_me/", views.admin_me),
    path("grade_audit/", views.grade_audit),
    re_path(
        "grade_audit/grade_detail/(?P<classid>[A-Z]{4}[0-9]{6}\.[0-9]{2})/?$", views.grade_detail),
    path("grade_audit/grade_confirm/", views.grade_confirm),
    path("class_view/", views.class_view),
    path("class_view/student_list/", views.admin_student_list),
    path("program_update/", views.program_update),
    re_path(
        "program_update/program_set/(?P<classid>[A-Z]{4}[0-9]{6}\.[0-9]{2})/?$", views.program_set),
    path("class_audit/", views.class_audit),
    re_path("class_audit/class_set/(?P<id>[0-9]*)/?$", views.class_set),
    path("settle/", views.settle)
]
