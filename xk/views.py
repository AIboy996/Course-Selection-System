# 内置库
import copy
import random
# 本地文件
from xk_models.models import ClassInfo, Teacher, ClassDetail, User, Classchoice, Student, Program, Evaluation, Week
from xk_models.models import Class_adjustment, Message, Temp_Score, Temp_Class, Classroom
from .forms import UserForm, SelectionForm, EvaluationForm, ScoreForm, Temp_ClassForm, \
    Adjustment_TimeForm, Comment_Form, Admin_ClassForm, ProgramForm, Class_DayForm
# django函数
from django.shortcuts import render, redirect
from django.db.models import Q


#################### 常量 ############################

week_ref = {"周日": 0, "周一": 1, "周二": 2, "周三": 3, "周四": 4, "周五": 5, "周六": 6}
identity_dict = {0: "同学", 1: "老师", 2: "教室管理老师", 3: "教务老师"}
grade_dict = {1: "大一上", 2: "大一下", 3: "大二上",
              4: "大二下", 5: "大三上", 6: "大三下", 7: "大四上", 8: "大四下"}
score_dict = {"A": 4, "A-": 3.7, "B+": 3.3, "B": 3, "B-": 2.7, "C+": 2.3, "C": 2, "C-": 1.7, "D+": 1.3, "D": 1,
              "D-": 0.7, "F": 0}
view_dict = {0: "未审核", 1: "已通过", -1: "未通过"}
index_page = {0: 'index', 1: 'teacher_index', 3: 'admin_index'}
httpErrors = {404: ['Not Found', '页面不存在'], 403: ['Forbidden', '无权限访问此页面']}


#################### 通用函数 ############################

def error(request, error_code):
    meaning, message = httpErrors[error_code]
    return render(request, 'error.html', locals())

def is_login(users: list):
    """带参数的装饰器，如果未登录则重定向到登录界面"""
    def decorator(func):
        def wrapper(*args, **kw):
            # 这里可能出问题，注意函数传递的第一个参数是不是request
            request = args[0]
            if request.session.get('is_login', False) == False:
                # 如果没登陆，就返回登录页面
                return redirect('/login')
            elif all(request.session['identity'] != user for user in users):
                # 如果不是对应的身份，则返回首页
                return error(request, 403)
            else:
                return func(*args, **kw)
        return wrapper
    return decorator


def login(request):
    """登录函数，验证登录信息，并且存储用户基本信息到session"""
    # 不允许重复登录
    if request.session.get('is_login', False):
        return redirect(f"/{request.session['index_page']}")

    if request.method == "POST":
        login_form = UserForm(request.POST)
        message = "请检查填写的内容！"
        if login_form.is_valid():
            email = login_form.cleaned_data['email']
            password = login_form.cleaned_data['password']
            try:
                user = User.objects.get(email=email)
                if user.password == password:
                    if '12345' in password:
                        request.session['defuault_password'] = 1
                    else:
                        request.session['defuault_password'] = 0
                    # 用户基本信息在登入时就传入系统
                    request.session['is_login'] = True
                    request.session['user_id'] = user.user_id
                    request.session['user_name'] = user.name
                    request.session['user_email'] = user.email
                    request.session["identity"] = \
                        [user.is_student, user.is_teacher,
                            user.is_roomadmin, user.is_classadmin].index(1)
                    # 假定为第5周
                    request.session["week"] = Week.objects.last().week
                    request.session["err"] = ""
                    request.session['index_page'] = index_page.get(
                        request.session['identity'])
                    request.session['index_page_file'] = request.session['index_page'] + '.html'
                    request.session['week'] = Week.objects.get(id=1).week
                    if request.session["identity"] == 0:
                        request.session["grade"] = Student.objects.get(
                            user_id_id=user.user_id).grade
                        request.session["major"] = Student.objects.get(
                            user_id_id=user.user_id).major

                        # 选课信息会在登入的界面就传入系统
                        cla = list(Classchoice.objects.filter(
                            user_id_id=user.user_id))
                        class_table = [["", "", "", "", "", "", ""]
                                       for i in range(14)]
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
                    elif request.session["identity"] == 1:
                        request.session["title"] = Teacher.objects.get(
                            name=user.name).title
                        teach_id = [x.classid for x in
                                    list(ClassInfo.objects.filter(teacher_id=user.user_id))]
                        request.session["teach_id"] = teach_id
                        return redirect("/teacher_index/")
                    elif request.session["identity"] == 3:
                        return redirect("/admin_index/")
                else:
                    message = "密码不正确！"
            except:
                message = "用户不存在！"
        return render(request, 'login.html', locals())

    login_form = UserForm()
    return render(request, 'login.html', locals())


@is_login([0, 1, 2, 3])
def logout(request):
    request.session.flush()
    return redirect("/login/", locals())


@is_login([0, 1, 2, 3])
def message(request):
    identity = request.session["identity"]
    id = request.session["user_id"]
    if identity == 0:
        address = {'/': 'Home'}
    elif identity == 1:
        address = {"/teacher_index": "Home"}
    elif identity == 3:
        address = {"/admin_index": "Home"}
    pagename = '信息中心'

    message = Message.objects.filter(to_id=id)
    mess_list = []
    for i in list(message):
        mess = i.message
        from_name = i.from_id.name
        mess_list.append(
            {"message": mess, "from": from_name, "from_id": i.from_id_id})

    return render(request, "message.html", locals())


@is_login([0, 1, 2, 3])
def message_delete(request):
    if request.method == "GET":
        from_id = request.GET["from_id"]
        to_id = request.session["user_id"]
        mess = Message.objects.filter(
            Q(from_id=from_id), Q(to_id=to_id)).delete()

    return redirect("/message/", locals())


############### 学生相关函数 #######################
# Home页面
@is_login([0])
def index(request):
    address = {}
    pagename = '欢迎来到选课系统'
    week = Week.objects.get(id=1).week
    return render(request, 'index.html', locals())


@is_login([0])
def me(request):
    address = {'/': 'Home'}
    pagename = '个人中心'
    id = request.session["user_id"]
    email = request.session["user_email"]
    name = request.session["user_name"]
    identity = identity_dict[request.session["identity"]]
    stu = Student.objects.get(user_id_id=id)
    major = stu.major
    year = stu.year
    grade = grade_dict[stu.grade]

    return render(request, 'me.html', locals())


@is_login([0])
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
                    obj['teacher'] = Teacher.objects.get(
                        user_id_id=obj['teacher_id'])
                    obj['detail'] = ClassDetail.objects.get(
                        id=obj['detail_id'])
                    class_lst.append(obj)
        return render(request, 'classinfo.html', locals())

    # 从培养方案进入，直接定位相关课程
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


@is_login([0])
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


@is_login([0])
def classchoice(request):
    address = {'/': 'Home'}
    pagename = "选课列表"
    user_id = request.session["user_id"]
    class_table = request.session["class_table"]
    cla_list = request.session["cla_list"]
    cla_id = request.session["cla_id"]
    # 初始化 无课程出现
    choice = set()
    choi_list = []
    # 提交搜索申请，出现相关课程
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

    # 从课程信息跳入，直接定位相关课程
    if request.GET.get("classid"):
        classid = request.GET["classid"]
        if not Classchoice.objects.filter(Q(classid_id=classid), Q(user_id_id=user_id)).exists():
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

    # 从培养方案进入，直接定位相关课程
    if request.GET.get("code"):
        code = request.GET["code"]
        code_choice = [x.classid for x
                       in list(ClassInfo.objects.filter(code=code))]
        for id in code_choice:
            if not Classchoice.objects.filter(Q(classid_id=id), Q(user_id_id=user_id)).exists():
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

    # 如果有错误（选课同一时间冲突），汇报
    if request.session["err"]:
        error_dict = request.session["err"]
        request.session["err"] = ""
    else:
        error_dict = {"state": 0}

    return render(request, 'classchoice.html', locals())


@is_login([0])
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


@is_login([0])
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
        score = Classchoice.objects.get(
            Q(classid_id=clas), Q(user_id_id=stu_id)).score
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


@is_login([0])
def class_table(request):
    address = {"/": "Home"}
    pagename = "课程表查看"
    class_table = copy.deepcopy(request.session["class_table"])
    cla_id = request.session["cla_id"]
    cla_list = []
    week = request.session["week"]
    for row in range(14):
        for col in range(7):
            class_table[row][col] = {"normal": 0,
                                     "context": class_table[row][col]}
    for id in cla_id:
        clas_adjust = Class_adjustment.objects.filter(
            Q(classid_id=id), Q(week=week))
        if clas_adjust.count():
            for adj in list(clas_adjust):
                time = adj.time
                time_list = time.split("，")
                row = time_list[1].split("-")
                col = week_ref[time_list[0]]
                for i in range(int(row[0]) - 1, int(row[1])):
                    class_table[i][col] = {
                        "normal": 1, "context": adj.classid.name}
                from_time = adj.from_time
                time_list = from_time.split("，")
                row = time_list[1].split("-")
                col = week_ref[time_list[0]]
                for i in range(int(row[0]) - 1, int(row[1])):
                    class_table[i][col] = {"normal": 1, "context": ""}
                cla_list.append({"classid": id,
                                 "name": adj.classid.name,
                                 "time": time,
                                 "classroom": adj.room.roomid,
                                 "max_num": adj.room.maxnum, "state": 1})
        else:
            clas = ClassInfo.objects.get(classid=id)
            cla_list.append({"classid": id,
                             "name": clas.name,
                             "time": clas.detail.time,
                             "classroom": clas.classroom.roomid,
                             "max_num": clas.classroom.maxnum, "state": 0})

    return render(request, "classtable.html", locals())


@is_login([0])
def drop_class(request):
    if request.method == "GET":
        classid = request.GET.get("classid")
        stu_id = request.session["user_id"]
        # 数据库操作
        dropclass = Classchoice.objects.get(
            Q(classid_id=classid), Q(user_id_id=stu_id)).delete()
        # 系统变量操作-课堂字典
        cla_list = request.session["cla_list"]
        cla_inf = [cla for cla in cla_list if cla["classid"] == classid][0]
        time = cla_inf["time"]
        cla_list.remove(
            [cla for cla in cla_list if cla["classid"] == classid][0])
        # 系统变量操作-课程表
        class_table = request.session["class_table"]
        time_g = time.split("；")
        for t in time_g:
            time_list = t.split("，")
            row = time_list[1].split("-")
            col = week_ref[time_list[0]]
            for i in range(int(row[0]) - 1, int(row[1])):
                class_table[i][col] = ""
        # 系统变量操作-课程代码
        cla_id = request.session["cla_id"]
        cla_id.remove(classid)
        # 重新存储系统变量
        request.session["class_table"] = class_table
        request.session["cla_list"] = cla_list
        request.session["cla_id"] = cla_id

    return redirect("/classchoice/", locals())


@is_login([0])
def add_class(request):
    if request.method == "GET":
        classid = request.GET.get("classid")
        stu_id = request.session["user_id"]
        # 查找instance
        selectclass = Classchoice(classid_id=classid, user_id_id=stu_id)
        # 系统变量操作-课程表(顺便判断了是否选课冲突)
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
        # 数据库保存操作
        selectclass.save()
        # 系统变量操作-课堂字典
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
        # 系统变量操作-课程id
        cla_id = request.session["cla_id"]
        cla_id.append(classid)
        # 重新存储系统变量
        request.session["class_table"] = class_table
        request.session["cla_list"] = cla_list
        request.session["cla_id"] = cla_id

    return redirect("/classchoice/", locals())


@is_login([0])
def evaluation(request, classid):
    address = {"/": "Home"}
    pagename = "评教系统"
    # 创建表单收取评教
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

    # 查找出没有评教的课程
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


@is_login([0])
def student_note(request):
    if request.method == 'POST':
        request.session['note'] = request.POST['note']
        # refer即为跳转前的链接
        print(request.META['HTTP_REFERER'])
        print('被盗用')
    return redirect(request.META['HTTP_REFERER'])


################## 教师相关函数 ###############################
@is_login([1])
def teacher_index(request):
    address = {}
    pagename = '欢迎来到课务系统'
    return render(request, 'teacher_index.html', locals())


@is_login([1])
def teacher_me(request):
    address = {'/teacher_index': 'Home'}
    pagename = '个人中心'
    identity = identity_dict[request.session["identity"]]
    return render(request, "teacher_me.html", locals())


@is_login([1])
def evaluation_view(request):
    address = {'/teacher_index': 'Home'}
    pagename = '评教查询'
    teach_id = request.session["teach_id"]
    eva_list = []
    for id in teach_id:
        clas = ClassInfo.objects.get(classid=id)
        num = Evaluation.objects.filter(classid=id).count()
        all_num = Classchoice.objects.all().count()
        eva_list.append({"classid": id,
                         "name": clas.name,
                         "num": num,
                         "all_num": all_num
                         })
    return render(request, "evaluation_view.html", locals())


@is_login([1])
def evaluation_detail(request):
    address = {'/teacher_index': 'Home', '/evaluation_view/': '评教查询'}
    pagename = '评教详情'
    classid = request.GET.get("classid")
    eva_list = list(Evaluation.objects.filter(classid=classid))
    i = 1
    detail_list = []
    for eva in eva_list:
        detail_list.append({"order": i,
                            "course": eva.Com_course,
                            "classroom": eva.Com_classroom,
                            "textbook": eva.Com_textbook
                            })
        i += 1

    return render(request, "evaluation_detail.html", locals())


@is_login([1])
def teach_table(request):
    address = {'/teacher_index': 'Home'}
    pagename = '授课课表'
    teach_table = [[{"normal": 0, "context": ""}] * 7 for i in range(14)]
    teach_id = request.session["teach_id"]
    week = request.session["week"]
    clas_list = []
    for id in teach_id:
        clas_adj = list(Class_adjustment.objects.filter(
            Q(week=week), Q(classid=id)))
        if clas_adj:
            clas_adj = clas_adj[0]
            time = clas_adj.time
            from_time = clas_adj.from_time
            time_all = ClassInfo.objects.get(classid=id).detail.time
            time_g = time_all.split("；")
            t_diff = []
            for t in time_g:
                if t == from_time:
                    time_list = time.split("，")
                    row = time_list[1].split("-")
                    col = week_ref[time_list[0]]
                    for i in range(int(row[0]) - 1, int(row[1])):
                        teach_table[i][col] = {
                            "normal": 1, "context": clas_adj.classid.name}
                else:
                    t_diff.append(t)
                    time_list = t.split("，")
                    row = time_list[1].split("-")
                    col = week_ref[time_list[0]]
                    for i in range(int(row[0]) - 1, int(row[1])):
                        teach_table[i][col] = {
                            "normal": 0, "context": clas_adj.classid.name}

            if t_diff:
                time_form = "；".join(t_diff.append(time))
                clas_list.append({"classid": id,
                                  "name": clas_adj.classid.name,
                                  "time": time_form,
                                  "classroom": clas_adj.room.roomid,
                                  "max_num": clas_adj.room.maxnum,
                                  "state": 1})
            else:
                clas_list.append({"classid": id,
                                  "name": clas_adj.classid.name,
                                  "time": time,
                                  "classroom": clas_adj.room.roomid,
                                  "max_num": clas_adj.room.maxnum,
                                  "state": 1})
        elif not clas_adj:
            clas = ClassInfo.objects.get(classid=id)
            time = clas.detail.time
            time_g = time.split("；")
            for t in time_g:
                time_list = t.split("，")
                row = time_list[1].split("-")
                col = week_ref[time_list[0]]
                for i in range(int(row[0]) - 1, int(row[1])):
                    teach_table[i][col] = {"normal": 0, "context": clas.name}
            clas_list.append({"classid": id,
                              "name": clas.name,
                              "time": time,
                              "classroom": clas.classroom.roomid,
                              "max_num": clas.classroom.maxnum,
                              "state": 0})

    return render(request, "teach_table.html", locals())


@is_login([1, 3])
def student_list(request):
    address = {'/teacher_index': 'Home', '/teach_table/': '授课课表'}
    pagename = '学生名单'
    if request.method == "GET":
        classid = request.GET["classid"]
        class_name = ClassInfo.objects.get(classid=classid).name
        choose_stu = list(Classchoice.objects.filter(classid=classid))
        stu_list = []
        for choose in choose_stu:
            stu = choose.user_id
            stu_list.append({"name": stu.name,
                             "id": stu.user_id,
                             "major": stu.student.major})

    return render(request, "student_list.html", locals())


@is_login([1])
def grade_mission(request):
    address = {'/teacher_index': 'Home'}
    pagename = '成绩发布'
    teach_id = request.session["teach_id"]
    cla_uncomp_list = []
    cla_comp_list = []
    for id in teach_id:
        uncomp = Classchoice.objects.filter(
            Q(classid=id), Q(score="未发布")).count()
        if uncomp:  # 未发布：可能是在审核或者还没有给
            temp_score = Temp_Score.objects.filter(Q(classid=id))
            score_num = temp_score.count()
            all_num = Classchoice.objects.filter(classid=id).count()
            if score_num < all_num:  # 没有给或没有给完
                clas = ClassInfo.objects.get(classid=id)
                cla_uncomp_list.append({"classid": id,
                                        "name": clas.name,
                                        "num": all_num - score_num})
            elif (score_num == all_num):  # 已经给完
                clas = ClassInfo.objects.get(classid=id)
                audit = temp_score.first().audit
                if not audit:  # 没有审核
                    cla_comp_list.append({"classid": id,
                                          "name": clas.name,
                                          "state": "审核中"})
                elif audit:  # 给完被驳回
                    cla_uncomp_list.append({"classid": id,
                                            "name": clas.name,
                                            "state": "被驳回"})

        elif not uncomp:  # 已经给了
            clas = ClassInfo.objects.get(classid=id)
            cla_comp_list.append({"classid": id,
                                  "name": clas.name,
                                  "state": "已发布"})

    return render(request, "grade_mission.html", locals())


@is_login([1])
def grade_set(request, classid, stu_id):
    address = {'/teacher_index': 'Home', "/grade_mission/": "成绩发布"}
    pagename = '成绩输入'
    if request.method == "POST":
        score_form = ScoreForm(request.POST)
        if score_form.is_valid():
            score = score_form.cleaned_data["score"]
            if score != "未发布":
                temp_score = Temp_Score(
                    score=score, classid_id=classid, user_id_id=stu_id, audit=0)
                locations = "/grade_mission/grade_set/" + classid + "/"
                temp_score.save()
                return redirect(locations, locals())
            else:
                locations = "/grade_mission/grade_set/" + classid + "/"
                return redirect(locations, locals())

    stu_list = list(Classchoice.objects.filter(classid=classid))
    score_uncomp_list = []
    score_comp_list = []
    for stu in stu_list:
        id = stu.user_id_id
        comp = Temp_Score.objects.filter(
            Q(user_id_id=id), Q(classid_id=classid))
        comp_num = comp.count()
        if not comp_num:
            score_uncomp_list.append({"name": stu.user_id.name,
                                      "id": id,
                                      "score": stu.score,
                                      "classid": classid})
        else:
            comp_score = comp.first().score
            score_comp_list.append({"name": stu.user_id.name,
                                    "id": id,
                                    "score": comp_score})
    if request.session["err"]:
        err = request.session["err"]
        print(err)
        request.session["err"] = ""

    return render(request, "grade_set.html", locals())


@is_login([1])
def grade_delete(request, classid, stu_id):
    temp_score = Temp_Score.objects.get(
        Q(classid=classid), Q(user_id_id=stu_id)).delete()
    locations = "/grade_mission/grade_set/" + classid + "/"
    return redirect(locations, locals())


@is_login([1])
def grade_message(request, classid):
    score_num = Temp_Score.objects.filter(classid=classid).count()
    all_num = Classchoice.objects.filter(classid=classid).count()
    if score_num == all_num:
        language = classid + "成绩已经提交，请审核"
        message = Message(
            message=language, from_id_id=request.session["user_id"], to_id_id="fdsm")
        message.save()
    else:
        request.session["err"] = "未完成所有学生成绩提交"
        locations = "/grade_mission/grade_set/" + classid + "/"
        return redirect(locations, locals())

    return redirect("/grade_mission/", locals())


@is_login([1])
def grade_views(request):
    address = {'/teacher_index': 'Home', "/grade_mission/": "成绩发布"}
    pagename = '成绩查看'
    if request.method == "GET":
        score_list = []
        classid = request.GET["classid"]
        temp_score = Temp_Score.objects.filter(classid=classid)
        if temp_score.count():
            for stu_score in list(temp_score):
                score_list.append({"name": stu_score.user_id.name,
                                   "id": stu_score.user_id_id,
                                   "score": stu_score.score
                                   })
        else:
            scores = Classchoice.objects.filter(classid=classid)
            for stu_score in list(scores):
                score_list.append({"name": stu_score.user_id.name,
                                   "id": stu_score.user_id_id,
                                   "score": stu_score.score
                                   })
    return render(request, "grade_views.html", locals())


@is_login([1])
def class_open(request):
    address = {'/teacher_index': 'Home'}
    pagename = '开课申请'
    temp_class = Temp_ClassForm()
    teach_id = request.session["user_id"]
    if request.method == "POST":
        temp_class = Temp_ClassForm(request.POST)
        if temp_class.is_valid():
            temp_save = temp_class.save(commit=False)
            temp_save.teacher_id = User.objects.get(user_id=teach_id)
            temp_save.save()
            message = request.session["user_name"] + "已申请开设新课，请审核"
            mess = Message(message=message,
                           from_id_id=teach_id, to_id_id="fdsm")
            mess.save()
            return redirect("/class_open/", locals())
        else:
            request.session["err"] = "提交不成功"

    temp_clas = Temp_Class.objects.filter(teacher_id_id=teach_id)
    temp_clas_list = []
    for clas_value in list(temp_clas.values()):
        if clas_value["views"] == 0:
            clas_value["state"] = "审核中"
            temp_clas_list.append(clas_value)
        if clas_value["views"] == 1:
            clas_value["state"] = "已通过"
            temp_clas_list.append(clas_value)
        if clas_value["views"] == -1:
            clas_value["state"] = "被驳回"
            temp_clas_list.append(clas_value)

    if request.session["err"]:
        err = request.session["err"]
        request.session["err"] = ""

    return render(request, "class_open.html", locals())


@is_login([1])
def class_delete(request):
    if request.method == "GET":
        id = request.GET["id"]
        temp_class = Temp_Class.objects.filter(id=id).delete()
    return redirect("/class_open/", locals())


@is_login([1])
def class_adj(request):
    address = {'/teacher_index': 'Home'}
    pagename = '调课申请'
    teacher_id = request.session["user_id"]
    clas = ClassInfo.objects.filter(teacher_id=teacher_id)
    clas_list = []
    record_list = []
    now_week = request.session["week"]
    for cla in list(clas):
        clas_list.append({"name": cla.name, "id": cla.classid,
                          "classroom": cla.classroom.roomid,
                          "time": cla.detail.time})
        record = cla.class_adjustment_set.all()
        for rec in list(record):
            week = rec.week
            if week > now_week:
                state = "已通过"
            elif week == now_week:
                state = "本周生效"
            elif week < now_week:
                state = "已完成"
            record_list.append({"name": cla.name, "id": cla.classid,
                                "classroom": rec.room.roomid,
                                "from_time": rec.from_time,
                                "time": rec.time, "week": week, "state": state})
    if request.session["err"]:
        err = request.session["err"]
        request.session["err"] = ""

    return render(request, "class_adj.html", locals())


@is_login([1])
def adjust_views(request, classid):
    address = {'/teacher_index': 'Home', "/class_adj/": "调课申请"}
    pagename = '调课详情'
    week = request.session["week"]
    adj_his = Class_adjustment.objects.filter(
        Q(classid_id=classid), Q(week=week + 1)).count()
    clas = ClassInfo.objects.get(classid=classid)
    time_group = clas.detail.time.split("；")
    clas_list = [{"name": clas.name, "id": clas.classid,
                  "classroom": clas.classroom.roomid,
                  "time": clas.detail.time}]
    clas_classroom = []
    if adj_his:
        request.session["err"] = "您本周已经调过此门课程"
        return redirect("/class_adj/", locals())
    if request.method == "POST":
        clas_classroom = [x["roomid"]
                          for x in list(Classroom.objects.all().values())]
        adj_time = Adjustment_TimeForm(request.POST)
        if adj_time.is_valid():
            days = adj_time.cleaned_data["days"]
            first_class = adj_time.cleaned_data["first_class"]
            from_time = adj_time.cleaned_data["from_time"]
            if from_time == "...":
                request.session["err"] = "请选择需要调课时间"
                locations = "/class_adj/adjust_views/" + classid
                return redirect(locations, locals())

            time_class = [int(x) for x in from_time.split("，")[1].split("-")]

            len_class = time_class[1] - time_class[0] + 1
            if ((first_class <= 5) and (first_class + len_class - 1 > 5)) or \
                    ((first_class <= 10) and (first_class + len_class - 1 > 10)):
                request.session["err"] = "课程开始时间不合理，请重新设置"
                locations = "/class_adj/adjust_views/" + classid
                return redirect(locations, locals())

            class_time = list(range(first_class, first_class + len_class))
            class_form = days + "，" + \
                str(class_time[0]) + "-" + str(class_time[len_class - 1])

            stu_list = [x.user_id_id for x in list(
                Classchoice.objects.filter(classid_id=classid))]
            for stu in stu_list:
                stu_conflict = Classchoice.objects.filter(
                    Q(user_id_id=stu), ~Q(classid=classid))
                for clas in list(stu_conflict):
                    time_clas = clas.classid.detail.time
                    time_group = [t for t in time_clas.split("；") if days in t]
                    for t in time_group:
                        if days not in t:
                            continue
                        elif set(range(int(t.split("，")[1].split("-")[0]),
                                       int(t.split("，")[1].split("-")[1]) + 1)).intersection(set(class_time)):
                            request.session["err"] = "存在学生不满足调课要求"
                            locations = "/class_adj/adjust_views/" + classid
                            return redirect(locations, locals())

            clas_adj_conflict = Class_adjustment.objects.filter(Q(time__contains=days), ~Q(classid_id=classid),
                                                                Q(week=week + 1))
            clas_adj_list = []
            for clas in clas_adj_conflict:
                t = clas.time
                from_time = clas.from_time
                clas_adj_list.append([from_time, clas.classid_id])
                if set(range(int(t.split("，")[1].split("-")[0]),
                             int(t.split("，")[1].split("-")[1]) + 1)).intersection(set(class_time)):
                    if clas.room.roomid in clas_classroom:
                        clas_classroom.remove(clas.room.roomid)
                    if not clas_classroom:
                        request.session["err"] = "无匹配教室"
                        locations = "/class_adj/adjust_views/" + classid
                        return redirect(locations, locals())

            clas_conflict = ClassDetail.objects.filter(
                Q(time__contains=days), ~Q(classid=classid))
            for clas in clas_conflict:
                time_clas = clas.time
                time_group = [t for t in time_clas.split("；") if days in t]
                for t in time_group:
                    if [t, clas.classid] in clas_adj_list:
                        continue
                    if set(range(int(t.split("，")[1].split("-")[0]),
                                 int(t.split("，")[1].split("-")[1]) + 1)).intersection(set(class_time)):
                        if clas.classinfo.classroom.roomid in clas_classroom:
                            clas_classroom.remove(
                                clas.classinfo.classroom.roomid)
                        if not clas_classroom:
                            request.session["err"] = "无匹配教室"
                            locations = "/class_adj/adjust_views/" + classid
                            return redirect(locations, locals())
        else:
            request.session["err"] = "格式有误，请检查"
            locations = "/class_adj/adjust_views/" + classid
            return redirect(locations, locals())

    if request.session["err"]:
        err = request.session["err"]
        request.session["err"] = ""

    return render(request, "adjust_views.html", locals())


@is_login([1])
def adjust(request):
    if request.method == "GET":
        classid = request.GET["classid"]
        clas = ClassInfo.objects.get(classid=classid)
        time = request.GET["class_form"]
        classroom = request.GET["classroom"]
        teach_id = request.session["user_id"]
        room = Classroom.objects.get(roomid=classroom)
        adjustment = Class_adjustment(classid=clas, room=room,
                                      from_time=clas.detail.time,
                                      week=request.session["week"] + 1,
                                      time=time)
        adjustment.save()

        stu_list = Classchoice.objects.filter(classid=classid)
        for stu in list(stu_list):
            id = stu.user_id_id
            message = "第" + \
                str(request.session["week"] + 1) + \
                "周，" + classid + "由于教师因故无法上课而调课"
            mess = Message(message=message, from_id_id=teach_id, to_id_id=id)
            mess.save()

    return redirect("/class_adj/", locals())


################## 教务老师相关函数 ############
@is_login([3])
def admin_index(request):
    address = {}
    pagename = '欢迎来到课务系统'
    return render(request, 'admin_index.html', locals())


@is_login([3])
def admin_me(request):
    address = {'/admin_index': 'Home'}
    pagename = '个人中心'
    identity = identity_dict[request.session["identity"]]
    return render(request, "admin_me.html", locals())


@is_login([3])
def grade_audit(request):
    address = {'/admin_index': 'Home'}
    pagename = '成绩审核'
    id_view = Temp_Score.objects.values_list("classid_id").distinct()
    clas_list = []
    for id_t in list(id_view):
        id = id_t[0]
        view_num = Temp_Score.objects.filter(classid_id=id).count()
        all_num = Classchoice.objects.filter(classid_id=id).count()
        state = Temp_Score.objects.filter(classid_id=id).first().audit
        if (view_num == all_num) and (state == 0):  # 已经提交完成且未审核
            clas_view = ClassInfo.objects.get(classid=id)
            clas_list.append({"classid": id, "name": clas_view.name,
                              "num": view_num, "teacher": clas_view.teacher.name,
                              "state": "已提交"})
        elif (view_num == all_num) and (state == 1):  # 已提交但被驳回
            clas_view = ClassInfo.objects.get(classid=id)
            clas_list.append({"classid": id, "name": clas_view.name,
                              "num": view_num, "teacher": clas_view.teacher.name,
                              "state": "被驳回"})

    return render(request, "grade_audit.html", locals())


@is_login([3])
def grade_detail(request, classid):
    address = {'/admin_index': 'Home', "/grade_audit": "成绩审核"}
    pagename = '审核细节'
    temp_score = Temp_Score.objects.filter(classid_id=classid)
    rec_list = []
    score_list = []
    num = temp_score.count()
    id = classid
    # print(id)
    for rec in list(temp_score):
        score_list.append(rec.score)
        rec_list.append(
            {"id": rec.user_id_id, "name": rec.user_id.name, "score": rec.score})

    a_per = "%.2f%%" % (round(float(sum(
        list(map(lambda x: "A" in x, score_list))) / num) * 100, 2))
    b_per = "%.2f%%" % (round(float(sum(
        list(map(lambda x: "B" in x, score_list))) / num) * 100, 2))
    c_per = "%.2f%%" % (round(float(sum(
        list(map(lambda x: "C" in x, score_list))) / num) * 100, 2))
    d_per = "%.2f%%" % (round(float(sum(
        list(map(lambda x: "D" in x, score_list))) / num) * 100, 2))
    f_per = "%.2f%%" % (round(float(sum(
        list(map(lambda x: "F" in x, score_list))) / num) * 100, 2))

    if request.method == "POST":
        comment = Comment_Form(request.POST)
        if comment.is_valid():
            comm = comment.cleaned_data["comment"]
            message = classid + "成绩审核不通过：" + comm
            mess = Message(message=message, from_id_id=request.session["user_id"],
                           to_id_id=ClassInfo.objects.get(classid=classid).teacher_id)
            mess.save()
            temp_score = Temp_Score.objects.filter(
                classid=classid).update(audit=1)
            return redirect("/grade_audit/", locals())
        else:
            request.session["err"] = "评论长度过长"
            locations = "/grade_audit/grade_detail/" + classid
            return redirect(locations, locals())

    if request.session["err"]:
        err = request.session["err"]
        request.session["err"] = ""

    return render(request, "grade_detail.html", locals())


@is_login([3])
def grade_confirm(request):
    if request.method == "GET":
        classid = request.GET["classid"]
        teach_id = ClassInfo.objects.get(classid=classid).teacher_id
        temp_score = Temp_Score.objects.filter(classid_id=classid)
        user_id = request.session["user_id"]
        for stu in list(temp_score):
            stu_score = stu.score
            stu_id = stu.user_id_id
            stu_update = Classchoice.objects \
                .get(Q(user_id_id=stu_id), Q(classid_id=classid))
            stu_update.score = stu_score
            stu_update.save()
            message = stu.classid_id + stu.classid.name + "课程成绩已发布"
            mess = Message(message=message,
                           from_id_id=user_id, to_id_id=stu_id)
            mess.save()
        temp_score.delete()
        message = classid + "课程成绩已发布"
        mess = Message(message=message, from_id_id=user_id, to_id_id=teach_id)
        mess.save()

    return redirect("/grade_audit/", locals())


@is_login([3])
def class_view(request):
    address = {'/admin_index': 'Home'}
    pagename = "课程查看"
    clas = ClassInfo.objects.all()
    clas_list = []
    for cla in clas:
        clas_list.append({"classid": cla.classid, "code": cla.code,
                          "name": cla.name, "teacher": cla.teacher.name})

    if request.method == "POST":
        clas_list = []
        admin_class = Admin_ClassForm(request.POST)
        if admin_class.is_valid():
            for l, v in admin_class.cleaned_data.items():
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
                if (l == "teacher") and v:
                    teacher = Teacher.objects.filter(name__contains=v)
                    id_list = [x.uer_id_id for x in list(teacher)]
                    teacher_cho = []
                    for id in id_list:
                        teacher_cho.append([x.classid for x
                                            in list(ClassInfo.objects.filter(teacher_id=id))])

                    teacher_choice = set(teacher_cho)

                    if choice:
                        choice = teacher_choice.intersection(choice)
                        if not choice:
                            break
                    else:
                        choice = teacher_choice
            choice = list(choice)
            for id in choice:
                choi_class = ClassInfo.objects.get(classid=id)
                clas_list.append({"classid": id,
                                  "code": choi_class.code,
                                  "teacher": choi_class.teacher.name,
                                  "name": choi_class.name})

    return render(request, "class_view.html", locals())


@is_login([3])
def admin_student_list(request):
    address = {'/admin_index': 'Home', '/class_view/': '课程查询'}
    pagename = '学生名单'
    if request.method == "GET":
        classid = request.GET["classid"]
        class_name = ClassInfo.objects.get(classid=classid).name
        choose_stu = list(Classchoice.objects.filter(classid=classid))
        stu_list = []
        for choose in choose_stu:
            stu = choose.user_id
            stu_list.append({"name": stu.name,
                             "id": stu.user_id,
                             "major": stu.student.major})

    return render(request, "student_list.html", locals())


@is_login([3])
def program_update(request):
    address = {'/admin_index': 'Home'}
    pagename = '培养方案更新'
    clas_all = ClassInfo.objects.all()
    clas_list = []
    prog_list = []
    code_list = []
    for clas in clas_all:
        code = clas.code
        if Program.objects.filter(advice=code).exists():
            if code not in code_list:
                prog = Program.objects.get(advice=code)
                prog_list.append({"code": code, "name": clas.name,
                                  "major": prog.major,
                                  "grade": grade_dict[prog.grade]})
                code_list.append(code)
            else:
                continue
        else:
            clas_list.append(
                {"classid": clas.classid, "name": clas.name, "teacher": clas.teacher.name})

    if request.session["err"]:
        err = request.session["err"]
        request.session["err"] = ""
    return render(request, "program_update.html", locals())


@is_login([3])
def program_set(request, classid):
    if request.method == "POST":
        prog = ProgramForm(request.POST)
        if prog.is_valid():
            major = prog.cleaned_data["major"]
            grade = prog.cleaned_data["grade"]
            code = classid.split(".")[0]
            program = Program(major=major, grade=grade, advice=code)
            program.save()
        else:
            request.session["err"] = "格式出现错误"
        return redirect("/program_update/", locals())


@is_login([3])
def class_audit(request):
    address = {'/admin_index': 'Home'}
    pagename = '开课审核'
    temp_class = Temp_Class.objects.filter(views=0)
    clas_list = []
    i = 1
    for clas in temp_class:
        clas_list.append({"name": clas.name,
                          "teacher": clas.teacher_id.name, "id": clas.id, "num": i})

    if request.session["err"]:
        err = request.session["err"]
        request.session["err"] = ""

    return render(request, "class_audit.html", locals())


@is_login([3])
def class_set(request, id):
    address = {'/admin_index': 'Home', "/class_audit": '开课审核'}
    pagename = '课程细节'
    temp_class = Temp_Class.objects.get(id=id)
    clas_classroom = []
    while True:
        random_code = "MANA" + str((random.randint(100000, 199999)))
        if not ClassInfo.objects.filter(code=random_code).exists():
            break
    for i in range(1, 10):
        random_id = random_code + ".0" + str(i)
        if not ClassInfo.objects.filter(classid=random_id).exists():
            break

    if int(temp_class.hours) <= 3:
        credit = int(temp_class.hours)
    elif int(temp_class.hours) > 3:
        credit = int(temp_class.hours) - 1

    clas_dict = {"name": temp_class.name, "code": random_code,
                 "classid": random_id, "hours": temp_class.hours,
                 "weeks": temp_class.weeks,
                 "pre": temp_class.prerequisites, "teacher_info": temp_class.teacher_info,
                 "brief": temp_class.brief, "exam": temp_class.exam, "assessment": temp_class.assessment,
                 "teacher": temp_class.teacher_id.name, "id": id}

    time_combo = temp_class.time.split("/")

    if request.method == "POST":
        if request.POST.get("comment"):
            comment = Comment_Form(request.POST)
            if comment.is_valid():
                comm = comment.cleaned_data["comment"]
                message = clas_dict["name"] + "开课审核不通过：" + comm
                mess = Message(message=message, from_id_id=request.session["user_id"],
                               to_id_id=temp_class.teacher_id_id)
                mess.save()
                temp_class = Temp_Class.objects.filter(id=id).update(views=-1)
                return redirect("/class_audit/", locals())
            else:
                request.session["err"] = "评论长度过长"
                locations = "/class_audit/class_set/" + id

        if request.POST.get("days"):
            class_day = Class_DayForm(request.POST)
            if class_day.is_valid():
                from_time_group = class_day.cleaned_data["days"]
                if from_time_group == "...":
                    request.session["err"] = "请选择开课时间"
                    locations = "/class_aduit/class_set/" + id
                    return redirect(locations, locals())

                clas_classroom = [x["roomid"]
                                  for x in list(Classroom.objects.all().values())]
                for from_time in from_time_group.split("；"):
                    time_class = [int(x)
                                  for x in from_time.split("，")[1].split("-")]
                    class_time = list(range(time_class[0], time_class[1] + 1))
                    days = from_time.split("；")[0]
                    clas_conflict = ClassDetail.objects.filter(
                        time__contains=days)
                    for clas in clas_conflict:
                        time_clas = clas.time
                        time_group = [
                            t for t in time_clas.split("；") if days in t]
                        for t in time_group:
                            if set(range(int(t.split("，")[1].split("-")[0]),
                                         int(t.split("，")[1].split("-")[1]) + 1)).intersection(set(class_time)):
                                if clas.classinfo.classroom.roomid in clas_classroom:
                                    clas_classroom.remove(
                                        clas.classinfo.classroom.roomid)
                                if not clas_classroom:
                                    request.session["err"] = "无匹配教室"
                                    locations = "/class_audit/class_set/" + id
                                    return redirect(locations, locals())
        else:
            request.session["err"] = "格式有误，请检查"
            locations = "/class_audit/class_set/" + id
            return redirect(locations, locals())

        if request.session["err"]:
            err = request.session["err"]
            request.session["err"] = ""

    return render(request, "class_set.html", locals())


@is_login([3])
def settle(request):
    if request.method == "GET":
        id = request.GET["id"]
        credit = request.GET["credit"]
        classroom = request.GET["classroom"]
        classroom_id = Classroom.objects.get(roomid=classroom)
        classid = request.GET["classid"]
        time = request.GET["time"]
        code = classid.split(".")[0]
        temp_class = Temp_Class.objects.get(id=id)
        detail = ClassDetail(classid=classid, hours=temp_class.hours,
                             weeks=temp_class.weeks, time=time,
                             prerequisites=temp_class.prerequisites,
                             teacher_info=temp_class.teacher_info,
                             brief=temp_class.brief, exam=temp_class.exam,
                             assessment=temp_class.assessment)
        detail.save()
        detail_id = ClassDetail.objects.get(classid=classid)
        info = ClassInfo(classid=classid, code=code, name=temp_class.name, department="管理学院",
                         credit=credit, detail=detail_id,
                         teacher_id=temp_class.teacher_id_id, classroom=classroom_id)
        info.save()
        temp_class.views = 1
        temp_class.save()
        message = info.teacher.name + "您申请的" + temp_class.name + "已通过"
        mess = Message(
            message=message, from_id_id=request.session["user_id"], to_id=temp_class.teacher_id)
        mess.save()
    return redirect("/class_audit/", locals())
