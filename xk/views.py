from django.shortcuts import render, HttpResponse, redirect
from xk_models.models import ClassInfo, Teacher, ClassDetail, User, Classchoice, Student, Program, Evaluation
from .forms import UserForm, TestModelForm, SelectionForm, EvaluationForm
from django.db.models import Q
from django.template import RequestContext
import copy

'''全局变量声明'''
week_ref = {"周日": 0, "周一": 1, "周二": 2, "周三": 3, "周四": 4, "周五": 5, "周六": 6}
identity_dict = {0: "同学", 1: "老师", 3: "教务老师", 2: "教室管理老师"}
grade_dict = {1: "大一上", 2: "大一下", 3: "大二上", 4: "大二下", 5: "大三上", 6: "大三下", 7: "大四上", 8: "大四下"}
score_dict = {"A": 4, "A-": 3.7, "B+": 3.3, "B": 3, "B-": 2.7, "C+": 2.3, "C": 2, "C-": 1.7, "D+": 1.3, "D": 1,
              "D-": 0.7, "F": 0}
'''不要修改全局变量，主要做对应字典用处'''


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
                    ## 学生基本信息在登入时就传入系统
                    request.session['is_login'] = True
                    request.session['user_id'] = user.user_id
                    request.session['user_name'] = user.name
                    request.session['user_email'] = user.email
                    request.session["identity"] = \
                        [user.is_student, user.is_teacher, user.is_roomadmin, user.is_classadmin].index(1)
                    request.session["grade"] = Student.objects.get(user_id_id=user.user_id).grade
                    request.session["major"] = Student.objects.get(user_id_id=user.user_id).major
                    request.session["err"] = ""

                    ## 选课信息会在登入的界面就传入系统
                    cla = list(Classchoice.objects.filter(user_id_id=user.user_id))
                    class_table = [["", "", "", "", "", "", ""] for i in range(14)]
                    cla_list = []
                    cla_id = []
                    for class_unit in cla:
                        classid = class_unit.classid_id
                        clas = ClassInfo.objects.get(classid=classid)
                        time = clas.detail.time
                        time_g = time.split("；")
                        for t in time_g:
                            time_list = t.split("，")
                            row = time_list[1].split("-")
                            col = week_ref[time_list[0]]
                            for i in range(int(row[0]) - 1, int(row[1])):
                                class_table[i][col] = clas.name

                        class_dict = {"classid": classid,
                                      "code": clas.code,
                                      "department": clas.department,
                                      "credit": clas.credit,
                                      "teacher": clas.teacher.name,
                                      "hour": clas.detail.hours,
                                      "exam": clas.detail.exam,
                                      "name": clas.name,
                                      "time": time}

                        cla_list.append(class_dict)
                        cla_id.append(classid)

                    request.session["class_table"] = class_table
                    request.session["cla_list"] = cla_list
                    request.session["cla_id"] = cla_id

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
    identity = identity_dict[request.session["identity"]]
    stu = Student.objects.get(user_id_id=id)
    major = stu.major
    year = stu.year
    grade = grade_dict[stu.grade]

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
    choice = set()
    if request.method == "POST":
        form = SelectionForm(request.POST)
        if form.is_valid():
            # print(form.cleaned_data["exam"])
            rec = 0
            for l, v in form.cleaned_data.items():
                if (l == "classid") and v:
                    id_choice = set([x.classid for x
                                     in list(ClassInfo.objects.filter(classid__icontains=v))])
                    rec = 1
                    choice = id_choice
                if (l == "code") and v:
                    code_choice = set([x.classid for x
                                       in list(ClassInfo.objects.filter(code__icontains=v))])
                    rec = 1
                    if choice:
                        choice = code_choice.intersection(choice)
                        if not choice:
                            break
                    else:
                        choice = code_choice
                if (l == "name") and v:
                    name_choice = set([x.classid for x
                                       in list(ClassInfo.objects.filter(name__contains=v))])
                    rec = 1
                    if choice:
                        choice = name_choice.intersection(choice)
                        if not choice:
                            break
                    else:
                        choice = name_choice
                if (l == "department") and v:
                    department_choice = set([x.classid for x
                                             in list(ClassInfo.objects.filter(department__contains=v))])
                    rec = 1
                    if choice:
                        choice = department_choice.intersection(choice)
                        if not choice:
                            break
                    else:
                        choice = department_choice
                if (l == "time") and (v != "开课时间"):
                    time_choice = set([x.classid for x
                                       in list(ClassDetail.objects.filter(time__contains=v))])
                    rec = 1
                    if choice:
                        choice = time_choice.intersection(choice)
                        if not choice:
                            break
                    else:
                        choice = time_choice
                if (l == "exam") and (v != "考试类型"):
                    exam_choice = set([x.classid for x
                                       in list(ClassDetail.objects.filter(exam=v))])
                    rec = 1
                    if choice:
                        choice = exam_choice.intersection(choice)
                        if not choice:
                            break
                    else:
                        choice = exam_choice

            if rec:
                class_lst = []
                for id in list(choice):
                    object = ClassInfo.objects.filter(classid=id)
                    obj = list(object.values())[0]
                    obj['teacher'] = Teacher.objects.get(user_id_id=obj['teacher_id'])
                    obj['detail'] = ClassDetail.objects.get(id=obj['detail_id'])
                    class_lst.append(obj)
        return render(request, 'classinfo.html', locals())

    ## 从培养方案进入，直接定位相关课程
    if request.GET.get("code"):
        class_lst = []
        code = request.GET["code"]
        code_choice = [x.classid for x
                       in list(ClassInfo.objects.filter(code=code))]
        for id in code_choice:
            object = ClassInfo.objects.filter(classid=id)
            obj = list(object.values())[0]
            obj['teacher'] = Teacher.objects.get(user_id_id=obj['teacher_id'])
            obj['detail'] = ClassDetail.objects.get(id=obj['detail_id'])
            class_lst.append(obj)
        return render(request, "classinfo.html", locals())

    return render(request, 'classinfo.html', locals())


@is_login
def classinfo_detail(request):
    address = {'/': 'Home', '/classinfo/': '课程信息'}
    pagename = '课程详情'
    classid = request.GET['classid']
    clas = ClassInfo.objects.get(classid=classid)
    classname = clas.name
    teachername = clas.teacher.name
    teachertitle = clas.teacher.title

    detail = clas.detail.to_dict()
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
    class_table = request.session["class_table"]
    cla_list = request.session["cla_list"]
    cla_id = request.session["cla_id"]
    ## 初始化 无课程出现
    choice = set()
    choi_list = []
    ## 提交搜索申请，出现相关课程
    if request.method == "POST":
        form = SelectionForm(request.POST)
        if form.is_valid():
            # print(form.cleaned_data["exam"])
            for l, v in form.cleaned_data.items():
                if (l == "classid") and v:
                    id_choice = set([x.classid for x
                                     in list(ClassInfo.objects.filter(classid__icontains=v))])
                    choice = id_choice
                if (l == "code") and v:
                    code_choice = set([x.classid for x
                                       in list(ClassInfo.objects.filter(code__icontains=v))])
                    if choice:
                        choice = code_choice.intersection(choice)
                        if not choice:
                            break
                    else:
                        choice = code_choice
                if (l == "name") and v:
                    name_choice = set([x.classid for x
                                       in list(ClassInfo.objects.filter(name__contains=v))])
                    if choice:
                        choice = name_choice.intersection(choice)
                        if not choice:
                            break
                    else:
                        choice = name_choice
                if (l == "department") and v:
                    department_choice = set([x.classid for x
                                             in list(ClassInfo.objects.filter(department__contains=v))])
                    if choice:
                        choice = department_choice.intersection(choice)
                        if not choice:
                            break
                    else:
                        choice = department_choice
                if (l == "time") and (v != "开课时间"):
                    time_choice = set([x.classid for x
                                       in list(ClassDetail.objects.filter(time__contains=v))])
                    if choice:
                        choice = time_choice.intersection(choice)
                        if not choice:
                            break
                    else:
                        choice = time_choice
                if (l == "exam") and (v != "考试类型"):
                    exam_choice = set([x.classid for x
                                       in list(ClassDetail.objects.filter(exam=v))])
                    if choice:
                        choice = exam_choice.intersection(choice)
                        if not choice:
                            break
                    else:
                        choice = exam_choice

            choice = choice.difference(set(cla_id))
            choice = list(choice)
            for id in choice:
                choi_class = ClassInfo.objects.get(classid=id)
                choi_list.append({"classid": id,
                                  "code": choi_class.code,
                                  "department": choi_class.department,
                                  "credit": choi_class.credit,
                                  "teacher": choi_class.teacher.name,
                                  "hour": choi_class.detail.hours,
                                  "exam": choi_class.detail.exam,
                                  "name": choi_class.name,
                                  "time": choi_class.detail.time})

            # print(choi_list)
            return render(request, 'classchoice.html', locals())

    ## 从课程信息跳入，直接定位相关课程
    if request.GET.get("classid"):
        classid = request.GET["classid"]
        choi_class = ClassInfo.objects.get(classid=classid)
        choi_list.append({"classid": classid,
                          "code": choi_class.code,
                          "department": choi_class.department,
                          "credit": choi_class.credit,
                          "teacher": choi_class.teacher.name,
                          "hour": choi_class.detail.hours,
                          "exam": choi_class.detail.exam,
                          "name": choi_class.name,
                          "time": choi_class.detail.time})
        return render(request, "classchoice.html", locals())

    ## 从培养方案进入，直接定位相关课程
    if request.GET.get("code"):
        code = request.GET["code"]
        code_choice = [x.classid for x
                       in list(ClassInfo.objects.filter(code=code))]
        for id in code_choice:
            choi_class = ClassInfo.objects.get(classid=id)
            choi_list.append({"classid": id,
                              "code": choi_class.code,
                              "department": choi_class.department,
                              "credit": choi_class.credit,
                              "teacher": choi_class.teacher.name,
                              "hour": choi_class.detail.hours,
                              "exam": choi_class.detail.exam,
                              "name": choi_class.name,
                              "time": choi_class.detail.time})
        return render(request, "classchoice.html", locals())

    ## 如果有错误（选课同一时间冲突），汇报
    if request.session["err"]:
        error_dict = request.session["err"]
        request.session["err"] = ""
    else:
        error_dict = {"state": 0}

    return render(request, 'classchoice.html', locals())

@is_login
def program(request):
    address = {"/": "Home"}
    pagename = "培养方案推荐"
    major = request.session["major"]
    grade = request.session["grade"]
    cla_list = request.session["cla_list"]
    cla_code = [x["code"] for x in cla_list]
    advice = list(Program.objects.filter(Q(major=major), Q(grade=grade)))
    adv_list = []
    for adv in advice:
        code = adv.advice
        if not code in cla_code:
            name = ClassInfo.objects.filter(code=code).first().name
            adv_list.append({"code": code, "name": name})

    return render(request, "program.html", locals())


def score(request):
    address = {"/": "Home"}
    pagename = "成绩查询"
    cla_id = request.session["cla_id"]
    stu_id = request.session["user_id"]
    name = User.objects.get(user_id=stu_id).name
    score_list = []
    score_sum = 0
    credit_sum = 0
    for clas in cla_id:
        score = Classchoice.objects.get(Q(classid_id=clas), Q(user_id_id=stu_id)).score
        cla = ClassInfo.objects.get(classid=clas)
        if score != "未发布":
            credit = cla.credit
            score_sum += score_dict[score] * credit
            credit_sum += credit
            score_list.append({"score": score,
                               "classid": clas,
                               "name": cla.name,
                               "credit": credit})
    if credit_sum:
        average_score = score_sum / credit_sum

    return render(request, "score.html", locals())


def class_table(request):
    address = {"/": "Home"}
    pagename = "课程表查看"
    class_table = request.session["class_table"]
    cla_id = request.session["cla_id"]
    cla_list = []
    for id in cla_id:
        clas = ClassInfo.objects.get(classid=id)
        cla_list.append({"classid": id,
                         "name": clas.name,
                         "time": clas.detail.time,
                         "classroom": clas.classroom.roomid,
                         "max_num": clas.classroom.maxnum})

    return render(request, "classtable.html", locals())

@is_login
def drop_class(request):
    if request.method == "GET":
        classid = request.GET.get("classid")
        stu_id = request.session["user_id"]
        ### 数据库操作
        dropclass = Classchoice.objects.get(Q(classid_id=classid), Q(user_id_id=stu_id)).delete()
        ## 系统变量操作-课堂字典
        cla_list = request.session["cla_list"]
        cla_inf = [cla for cla in cla_list if cla["classid"] == classid][0]
        time = cla_inf["time"]
        cla_list.remove([cla for cla in cla_list if cla["classid"] == classid][0])
        ## 系统变量操作-课程表
        class_table = request.session["class_table"]
        time_g = time.split("；")
        for t in time_g:
            time_list = t.split("，")
            row = time_list[1].split("-")
            col = week_ref[time_list[0]]
            for i in range(int(row[0]) - 1, int(row[1])):
                class_table[i][col] = ""
        ## 系统变量操作-课程代码
        cla_id = request.session["cla_id"]
        cla_id.remove(classid)
        ## 重新存储系统变量
        request.session["class_table"] = class_table
        request.session["cla_list"] = cla_list
        request.session["cla_id"] = cla_id

    return redirect("/classchoice/", locals())

@is_login
def add_class(request):
    if request.method == "GET":
        classid = request.GET.get("classid")
        stu_id = request.session["user_id"]
        ## 查找instance
        selectclass = Classchoice(classid_id=classid, user_id_id=stu_id)
        ## 系统变量操作-课程表(顺便判断了是否选课冲突)
        class_table = copy.deepcopy(request.session["class_table"])
        cla = ClassInfo.objects.get(classid=classid)
        name = cla.name
        time = cla.detail.time
        time_g = time.split("；")
        for t in time_g:
            time_list = t.split("，")
            row = time_list[1].split("-")
            col = week_ref[time_list[0]]
            for i in range(int(row[0]) - 1, int(row[1])):
                if not class_table[i][col]:
                    class_table[i][col] = name
                elif class_table[i][col]:
                    request.session["err"] = {"choose": name,
                                                "have": class_table[i][col],
                                                "state": 1}
                    class_table = request.session["class_table"]
                    return redirect("/classchoice/", locals())
        ## 数据库保存操作
        selectclass.save()
        ## 系统变量操作-课堂字典
        cla_list = request.session["cla_list"]
        cla = ClassInfo.objects.get(classid=classid)
        code = cla.code
        department = cla.department
        credit = cla.credit
        teacher = cla.teacher.name
        hour = cla.detail.hours
        exam = cla.detail.exam
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
        ## 系统变量操作-课程id
        cla_id = request.session["cla_id"]
        cla_id.append(classid)
        ## 重新存储系统变量
        request.session["class_table"] = class_table
        request.session["cla_list"] = cla_list
        request.session["cla_id"] = cla_id

    return redirect("/classchoice/", locals())


def evaluation(request, classid):
    address = {"/": "Home"}
    pagename = "评教系统"
    ## 创建表单收取评教
    stu_id = request.session["user_id"]
    stu_name = request.session["user_name"]
    evaluation = EvaluationForm()
    if request.method == "POST":
        evaluation = EvaluationForm(request.POST)
        if evaluation.is_valid():
            eva_save = evaluation.save(commit=False)

            eva_save.classid = ClassInfo.objects.get(classid=classid)
            eva_save.user_id = User.objects.get(user_id=stu_id)
            eva_save.save()
            return redirect("/evaluation/", locals())
        else:
            err = classid
            request.session["err"] = err
            return redirect("/evaluation/", locals())

    ## 查找出没有评教的课程
    cla_id = request.session["cla_id"]
    eva_cla = set([x["classid_id"] for x in
                   list(Evaluation.objects.filter(user_id_id=stu_id).values())])
    uneva_cla = list(set(cla_id).difference(eva_cla))
    uneva_list = []
    for id in uneva_cla:
        clas = ClassInfo.objects.get(classid=id)
        if request.session["err"]:
            if request.session["err"] == id:
                uneva_list.append({"classid": id,
                                   "name": clas.name,
                                   "teacher": clas.teacher.name,
                                   "classroom": clas.classroom.roomid,
                                   "state": "提交失败"})
                request.session["err"] = ""
            else:
                uneva_list.append({"classid": id,
                                   "name": clas.name,
                                   "teacher": clas.teacher.name,
                                   "classroom": clas.classroom.roomid,
                                   "state": "未完成"})
        else:
            uneva_list.append({"classid": id,
                               "name": clas.name,
                               "teacher": clas.teacher.name,
                               "classroom": clas.classroom.roomid,
                               "state": "未完成"})

    return render(request, "evaluation.html", locals())
