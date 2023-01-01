from django.shortcuts import render, HttpResponse, redirect
from xk_models.models import ClassInfo, Teacher, ClassDetail, User, Classchoice, Student, Program
from .forms import UserForm, TestModelForm
from django.db.models import Q
from django.template import RequestContext


def is_login(func):
    """装饰器，如果未登录则重定向到登录界面"""

    def wrapper(*args, **kw):
        ################################## 这里可能出问题，注意函数传递的第一个参数是不是request
        request = args[0]
        if request.session.get('is_login', False) == False:
            return redirect('/login')
        else:
            return func(*args, **kw)

    return wrapper


# Home页面
@is_login
def index(request):
    address = {}
    pagename = '欢迎来到选课系统'
    return render(request, 'index.html', locals())


def login(request):
    # 不允许重复登录
    if request.session.get('is_login', False):
        return redirect('/index')

    if request.method == "POST":
        login_form = UserForm(request.POST)
        message = "请检查填写的内容！"
        if login_form.is_valid():
            email = login_form.cleaned_data['email']
            password = login_form.cleaned_data['password']
            try:
                user = User.objects.get(email=email)
                if user.password == password:
                    request.session['is_login'] = True
                    request.session['user_id'] = user.user_id
                    request.session['user_name'] = user.name
                    request.session['user_email'] = user.email
                    request.session["identity"] = \
                        [user.is_student, user.is_teacher, user.is_roomadmin, user.is_classadmin].index(1)
                    request.session["grade"] = Student.objects.get(user_id_id=user.user_id).grade
                    request.session["major"] = Student.objects.get(user_id_id=user.user_id).major
                    return redirect('/index/')
                else:
                    message = "密码不正确！"
            except:
                message = "用户不存在！"
        return render(request, 'login.html', locals())

    login_form = UserForm()
    return render(request, 'login.html', locals())


# 只有登陆了才能访问这个页面
@is_login
def logout(request):
    request.session.flush()
    return redirect("/login/", locals())


@is_login
def me(request):
    address = {'/': 'Home'}
    pagename = '个人信息'
    id = request.session["user_id"]
    email = request.session["user_email"]
    name = request.session["user_name"]
    identity_dict = {0: "同学", 1: "老师", 3: "教务老师", 2: "教室管理老师"}
    grade_dict = {1:"大一上",2:"大一下",3:"大二上",4:"大二下",5:"大三上",6:"大三下",7:"大四上",8:"大四下"}
    identity = identity_dict[request.session["identity"]]
    major = Student.objects.get(user_id_id=id).major
    year = Student.objects.get(user_id_id=id).year
    grade = grade_dict[Student.objects.get(user_id_id=id).grade]

    return render(request, 'me.html', locals())


@is_login
def classinfo(request):
    address = {'/': 'Home'}
    pagename = '课程信息'
    objects = ClassInfo.objects.all()
    objects_values = list(objects.values())
    for obj in objects_values:
        obj['teacher'] = Teacher.objects.get(user_id_id=obj['teacher_id'])
        obj['detail'] = ClassDetail.objects.get(id=obj['detail_id'])

    class_lst = objects_values

    return render(request, 'classinfo.html', locals())


@is_login
def classinfo_detail(request):
    address = {'/': 'Home', '/classinfo/': '课程信息'}
    pagename = '课程详情'
    classid = request.GET['classid']
    classname = ClassInfo.objects.get(classid=classid).name
    teacherid = ClassInfo.objects.get(classid=classid).teacher_id
    teachername = Teacher.objects.get(user_id_id=teacherid).name
    teachertitle = Teacher.objects.get(user_id_id=teacherid).title

    detail = ClassDetail.objects.get(classid=classid).to_dict()
    return render(request, 'classinfo_detail.html', locals())


def test(request):
    form = TestModelForm()
    print("生成了form")
    if request.method == "POST":
        print(form)
        if form.is_valid():
            print('form is valid')
        else:
            print('form error')
    return render(request, 'test.html', locals())


@is_login
def classchoice(request):
    address = {'/': 'Home'}
    pagename = "选课列表"
    user_id = request.session["user_id"]
    cla = list(Classchoice.objects.filter(user_id_id=user_id))
    class_table = [["", "", "", "", "", "", ""] for i in range(14)]
    week_ref = {"周日": 0, "周一": 1, "周二": 2, "周三": 3, "周四": 4, "周五": 5, "周六": 6}
    cla_list = []
    for class_unit in cla:
        classid = class_unit.classid_id
        code = ClassInfo.objects.get(classid=classid).code
        department = ClassInfo.objects.get(classid=classid).department
        credit = ClassInfo.objects.get(classid=classid).credit
        teacher_id = ClassInfo.objects.get(classid=classid).teacher_id
        teacher = Teacher.objects.get(user_id_id=teacher_id).name
        hour = ClassDetail.objects.get(classid=classid).hours
        exam = ClassDetail.objects.get(classid=classid).exam
        name = ClassInfo.objects.get(classid=classid).name
        time = ClassDetail.objects.get(classid=classid).time
        time_list = time.split("，")
        row = time_list[1].split("-")
        col = week_ref[time_list[0]]
        for i in range(int(row[0]) - 1, int(row[1])):
            class_table[i][col] = name

        class_dict = {"classid": classid,
                      "code": code,
                      "department": department,
                      "credit": credit,
                      "teacher": teacher,
                      "hour": hour,
                      "exam": exam,
                      "name": name,
                      "time": time}
        cla_list.append(class_dict)
    request.session["class_table"] = class_table
    if request.method=="POST":


    return render(request, 'classchoice.html', locals())


@is_login
def drop_class(request):
    if request.method == "GET":
        classid = request.GET.get("classid")
        stu_id = request.session["user_id"]
        dropclass = Classchoice.objects.get(Q(classid_id=classid), Q(user_id_id=stu_id)).delete()

    return redirect("/classchoice/", locals())

@is_login
def program(request):
    address = {"/":"Home"}
    pagename = "培养方案推荐"
    major = request.session["major"]
    grade = request.session["grade"]
    advice = list(Program.objects.filter(Q(major=major),Q(grade=grade)))
    adv_list = []
    for adv in advice:
        code = adv.advice
        name = ClassInfo.objects.filter(code=code).first().name
        adv_list.append({"code": code, "name": name})

    return render(request, "program.html", locals())

# def score(request):


# def class_table(request):
#     address = {"/": "Home"}
#     pagename = "课程表查看"
#     user_id = request.session["user_id"]
#     cla = list(Classchoice.objects.filter(user_id_id=user_id))
#     class_table = [["", "", "", "", "", "", ""] for i in range(14)]
#     week_ref = {"周日": 0, "周一": 1, "周二": 2, "周三": 3, "周四": 4, "周五": 5, "周六": 6}
#     cla_list = []
#     for class_unit in cla:
#         classid = class_unit.classid_id
#         code = ClassInfo.objects.get(classid=classid).code
#         department = ClassInfo.objects.get(classid=classid).department
#         credit = ClassInfo.objects.get(classid=classid).credit
#         teacher_id = ClassInfo.objects.get(classid=classid).teacher_id
#         teacher = Teacher.objects.get(user_id_id=teacher_id).name
#         hour = ClassDetail.objects.get(classid=classid).hours
#         exam = ClassDetail.objects.get(classid=classid).exam
#         name = ClassInfo.objects.get(classid=classid).name
#         time = ClassDetail.objects.get(classid=classid).time
#         time_list = time.split("，")
#         row = time_list[1].split("-")
#         col = week_ref[time_list[0]]
#         for i in range(int(row[0]) - 1, int(row[1])):
#             class_table[i][col] = name
#
#     return render(request,"class_table.html",locals())

# def select_class(request):
#
#     Classchoice()