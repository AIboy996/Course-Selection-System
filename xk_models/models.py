from django.db import models
import datetime


class User(models.Model):
    '''用户表'''
    user_id = models.CharField(max_length=30, primary_key=True, verbose_name="号码")
    name = models.CharField(max_length=128, verbose_name="名字")
    password = models.CharField(max_length=50, verbose_name="密码")
    email = models.EmailField(unique=True, verbose_name="邮箱")
    is_student = models.BooleanField(default=False, verbose_name="是否为学生")
    is_teacher = models.BooleanField(default=False, verbose_name="是否为老师")
    is_roomadmin = models.BooleanField(default=False, verbose_name="是否为教室管理员")
    is_classadmin = models.BooleanField(default=False, verbose_name="是否为教务")

    def __str__(self):
        return self.name


class Student(models.Model):
    '''学生信息'''
    user_id = models.OneToOneField("User", primary_key=True, on_delete=models.CASCADE, verbose_name="学号")
    gender = (
        ('male', '男'),
        ('female', '女'),
    )
    year = models.IntegerField(
        choices=[(r, r) for r in range(1984, datetime.date.today().year + 1)],
        default=datetime.date.today().year, verbose_name="入校年份"
    )
    grade = models.SmallIntegerField(verbose_name="年级")
    major = models.CharField(max_length=30, verbose_name="专业")


class ClassInfo(models.Model):
    """课程信息"""
    # 课程的唯一标识符，例如：MANA130373.01
    classid = models.CharField(max_length=13, primary_key=True, verbose_name="课程id")
    # 课程的编码，例如：MANA130373
    code = models.CharField(max_length=20, verbose_name="课程编码")
    # 课程的名称，例如：数据库与企业数据管理
    name = models.CharField(max_length=30, verbose_name="课程名称")
    # 开课院系，例如：管理学院
    department = models.CharField(max_length=20, verbose_name="开课院系")
    # 学分数，例如：3
    credit = models.SmallIntegerField(verbose_name="学分")
    # 授课老师，例如：张成洪
    teacher = models.ForeignKey("Teacher", on_delete=models.CASCADE, verbose_name="教师")
    # 课程详细信息
    detail = models.OneToOneField(
        "ClassDetail", on_delete=models.CASCADE, verbose_name="详细信息")  # 一对一
    # 课程教室安排
    classroom = models.ForeignKey("Classroom", on_delete=models.CASCADE, verbose_name="教室安排")  # 多对多关系


class Teacher(models.Model):
    """老师信息"""
    # 姓名
    user_id = models.OneToOneField("User", on_delete=models.CASCADE, primary_key=True, verbose_name="工号")
    name = models.CharField(max_length=20, verbose_name="名称")
    title = models.CharField(
        choices=[('教授', '教授'),
                 ('副教授', '副教授'),
                 ('讲师', '讲师'),
                 ('青年研究员', '青年研究员'),
                 ('其他', '其他')],
        default='其他',
        max_length=10, verbose_name="职称"
    )

class Classroom(models.Model):
    """教室信息"""
    # 教室编号，例如：H405
    roomid = models.CharField(max_length=20, verbose_name="教室编号")
    # 最大可容纳人数
    maxnum = models.SmallIntegerField(verbose_name="最大容量")


class ClassDetail(models.Model):
    """课程的详细信息"""
    # 课程的唯一标识符，例如：MANA130373.01
    classid = models.CharField(max_length=13, verbose_name="课程id")
    # 周学时，例如：3+1（奇数周2，偶数周4）
    hours = models.CharField(max_length=12, verbose_name="周学时")
    # 共计周数，例如：18
    weeks = models.SmallIntegerField(verbose_name="周数")
    # 排课时间
    time = models.CharField(max_length=50, verbose_name="排课时间")
    # 先修课程
    prerequisites = models.CharField(max_length=30, default='无', verbose_name="先修课程(分号隔开)")
    # 主讲教师简介
    teacher_info = models.CharField(max_length=200, default='', verbose_name="教师简介")
    # 教学内容安排
    brief = models.CharField(max_length=500, default='', verbose_name="教学内容")
    # 考核方式
    exam = models.CharField(
        choices=[('开卷考试', '开卷考试'),
                 ('闭卷考试', '闭卷考试'),
                 ('半开卷考试', '半开卷考试'),
                 ('课程论文', '课程论文'),
                 ('其他', '其他')],
        default='其他',
        max_length=10, verbose_name="考核方式"
    )
    # 评分细则
    assessment = models.CharField(max_length=200, default='', verbose_name="评分细则")

    def to_dict(self):
        return dict(
            zip(['课程代码', '周学时数', '授课周数', '授课时间', '教学内容', '教师简介', '考核方式'],
                [self.classid, self.hours, self.weeks, self.time, self.brief, self.teacher_info, self.assessment], )
        )


class Classchoice(models.Model):
    '''选课信息'''
    classid = models.ForeignKey("classinfo", on_delete=models.CASCADE, verbose_name="课程id")
    user_id = models.ForeignKey("User", on_delete=models.CASCADE, verbose_name="学生id")
    score = models.CharField(max_length=10, default="未发布", verbose_name="成绩")

    class Meta:
        unique_together = (("classid", "user_id"),)


class Evaluation(models.Model):
    '''评教信息'''
    classid = models.ForeignKey("classinfo", on_delete=models.CASCADE, verbose_name="课程id")
    user_id = models.ForeignKey("User", on_delete=models.CASCADE, verbose_name="学生id")
    Com_course = models.CharField(max_length=50, verbose_name="课程评价")
    Com_classroom = models.CharField(max_length=50, verbose_name="教室评价")
    Com_textbook = models.CharField(max_length=50, verbose_name="教材评价")

    class Meta:
        unique_together = (("classid", "user_id"),)


class Program(models.Model):
    '''培养方案'''
    major = models.CharField(max_length=30, verbose_name="专业")
    grade = models.SmallIntegerField(verbose_name="年级")
    advice = models.CharField(max_length=30, verbose_name="建议课程")


class Week(models.Model):
    '''周数（虚拟表）'''
    week = models.SmallIntegerField(verbose_name="第几周")


class Message(models.Model):
    '''通知发布'''
    from_id = models.ForeignKey("User", on_delete=models.CASCADE, verbose_name="发布者", related_name="from_id")
    to_id = models.ForeignKey("User", on_delete=models.CASCADE, verbose_name="接受者", related_name="to_id")
    message = models.CharField(max_length=200, verbose_name="通知")


class Class_adjustment(models.Model):
    '''课程调整'''
    classid = models.ForeignKey("ClassInfo", on_delete=models.CASCADE, verbose_name="课程编号")
    week = models.SmallIntegerField(verbose_name="调课周")
    from_time = models.CharField(max_length=50, verbose_name="原来时间")
    time = models.CharField(max_length=50, verbose_name="调课时间")
    room = models.ForeignKey("Classroom", on_delete=models.CASCADE, verbose_name="调整教室")


class Temp_Class(models.Model):
    '''开课审核'''
    teacher_id = models.ForeignKey("User", on_delete=models.CASCADE, verbose_name="教师工号")
    # 课程名称
    name = models.CharField(max_length=30, verbose_name="课程名称")
    # 课程周学时
    hours = models.CharField(max_length=12, verbose_name="周学时")
    # 共计周数，例如：18
    weeks = models.SmallIntegerField(verbose_name="周数")
    # 排课时间
    time = models.CharField(max_length=50, verbose_name="排课时间")
    # 先修课程
    prerequisites = models.CharField(max_length=30, default='无', verbose_name="先修课程")
    # 主讲教师简介
    teacher_info = models.CharField(max_length=200, default='', verbose_name="教师简介")
    # 教学内容安排
    brief = models.CharField(max_length=500, default='', verbose_name="教学内容")
    # 考核方式
    exam = models.CharField(
        choices=[('开卷考试', '开卷考试'),
                 ('闭卷考试', '闭卷考试'),
                 ('半开卷考试', '半开卷考试'),
                 ('课程论文', '课程论文'),
                 ('其他', '其他')],
        default='其他',
        max_length=10, verbose_name="考核方式"
    )
    # 评分细则
    assessment = models.CharField(max_length=200, default='', verbose_name="评分细则")
    # 审核结果
    views = models.SmallIntegerField(verbose_name="审核状况", default=0)


class Temp_Score(models.Model):
    '''成绩审核'''
    classid = models.ForeignKey("classinfo", on_delete=models.CASCADE, verbose_name="课程id")
    user_id = models.ForeignKey("User", on_delete=models.CASCADE, verbose_name="学生id")
    score = models.CharField(max_length=10, default="未发布", verbose_name="成绩")
    audit = models.SmallIntegerField(verbose_name="审核状态")

    class Meta:
        unique_together = (("classid", "user_id"),)
