from django.db import models
import datetime


class User(models.Model):
    '''用户表'''

    gender = (
        ('male', '男'),
        ('female', '女'),
    )
    name = models.CharField(max_length=128)
    password = models.CharField(max_length=50)
    email = models.EmailField(unique=True,)
    sex = models.CharField(max_length=32, choices=gender, default='男')
    # 入学年份
    year = models.IntegerField(
        choices=[(r, r) for r in range(1984, datetime.date.today().year+1)],
        default=datetime.date.today().year,
    )

    def __str__(self):
        return self.name


class ClassInfo(models.Model):
    """课程信息"""
    # 课程的唯一标识符，例如：MANA130373.01
    classid = models.CharField(max_length=13)
    # 课程的编码，例如：MANA130373
    code = models.CharField(max_length=20)
    # 课程的名称，例如：数据库与企业数据管理
    name = models.CharField(max_length=30)
    # 开课院系，例如：管理学院
    department = models.CharField(max_length=20)
    # 学分数，例如：3
    credit = models.SmallIntegerField()
    # 授课老师，例如：张成洪
    teacher = models.OneToOneField("Teacher", on_delete=models.CASCADE)
    # 课程详细信息
    detail = models.OneToOneField(
        "ClassDetail", on_delete=models.CASCADE)  # 一对一
    # 课程教室安排
    classroom = models.ManyToManyField("Classroom")  # 多对多关系


class Teacher(models.Model):
    """老师信息"""
    # 姓名
    name = models.CharField(max_length=20)
    title = models.CharField(
        choices=[('教授', '教授'),
                 ('副教授', '副教授'),
                 ('讲师', '讲师'),
                 ('青年研究员', '青年研究员'),
                 ('其他', '其他')], 
        default='其他',
        max_length=10
    )


class Classroom(models.Model):
    """教室信息"""
    # 教室编号，例如：H405
    roomid = models.CharField(max_length=20)
    # 最大可容纳人数
    maxnum = models.SmallIntegerField()


class ClassDetail(models.Model):
    """课程的详细信息"""
    # 课程的唯一标识符，例如：MANA130373.01
    classid = models.CharField(max_length=13)
    # 周学时，例如：3+1（奇数周2，偶数周4）
    hours = models.CharField(max_length=12)
    # 共计周数，例如：18
    weeks = models.SmallIntegerField()
    # 排课时间
    time = models.CharField(max_length=12)
    # 先修课程
    prerequisites = models.ManyToManyField("ClassInfo", default=None)
    # 主讲教师简介
    teacher_info = models.CharField(max_length=200, default='')
    # 教学内容安排
    brief = models.CharField(max_length=500, default='')
    # 考核方式
    exam = models.CharField(
        choices=[('开卷考试', '开卷考试'),
                 ('闭卷考试', '闭卷考试'),
                 ('半开卷考试', '半开卷考试'),
                 ('课程论文', '课程论文'),
                 ('其他', '其他')], 
        default='其他',
        max_length=10
    )
    # 评分细则
    assessment = models.CharField(max_length=200, default='')

    def to_dict(self):
        return dict(
            zip(['课程代码', '周学时数', '授课周数', '授课时间', '教学内容', '教师简介', '考核方式'],
                [self.classid, self.hours, self.weeks, self.time, self.brief, self.teacher_info, self.assessment],)
        )
