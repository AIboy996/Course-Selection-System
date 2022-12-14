from django.shortcuts import render, HttpResponse, redirect
from xk_models.models import ClassInfo, Teacher, ClassDetail, User
from .forms import UserForm

def is_login(func):
    """装饰器，如果未登录则重定向到登录界面"""
    def wrapper(*args, **kw):
        ################################## 这里可能出问题，注意函数传递的第一个参数是不是request
        request = args[0]
        if request.session.get('is_login', False)==False:
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
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    request.session['user_email'] = user.email
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
    address = {'/':'Home'}
    pagename = '个人信息'
    return render(request, 'me.html', locals())

@is_login
def classinfo(request):
    address = {'/': 'Home'}
    pagename = '课程信息'
    objects = ClassInfo.objects.all()
    objects_values = list(objects.values())
    for obj in objects_values:
        obj['teacher'] = Teacher.objects.get(id=obj['teacher_id'])
        obj['detail'] = ClassDetail.objects.get(id=obj['detail_id'])

    class_lst = objects_values

    return render(request, 'classinfo.html', locals())

@is_login
def classinfo_detail(request):
    address = {'/':'Home', '/classinfo/':'课程信息'}
    pagename = '课程详情'
    classid = request.GET['classid']
    classname = ClassInfo.objects.get(classid=classid).name
    teacherid = ClassInfo.objects.get(classid=classid).teacher_id
    teachername = Teacher.objects.get(id=teacherid).name
    teachertitle = Teacher.objects.get(id=teacherid).title
    
    detail = ClassDetail.objects.get(classid=classid).to_dict()
    return render(request, 'classinfo_detail.html', locals())