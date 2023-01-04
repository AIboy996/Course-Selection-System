from django import forms
from xk_models.models import ClassDetail, Evaluation, Temp_Class


class UserForm(forms.Form):
    email = forms.CharField(label="邮箱",
                            max_length=50,
                            widget=forms.TextInput(
                                attrs={'class': 'IDCheckLoginName', 'placeholder': '邮箱（不是学号！）'}))
    password = forms.CharField(label="密码",
                               max_length=256,
                               widget=forms.PasswordInput(
                                   attrs={'class': 'IDCheckLoginPassWord', 'placeholder': '密码'}))


class TestModelForm(forms.ModelForm):
    class Meta:
        model = ClassDetail
        # fields = '__all__'
        exclude = ['prerequisites']
        # widgets = {
        #     'classid': forms.TextInput(attrs={'class': 'form-control'}),
        #     'exam': forms.Select(attrs={'class': 'form-select'}),
        #     'teacher_info': forms.TextInput(attrs={'class': 'form-control'}),
        # }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():

            if name == 'exam':
                field.widget.attrs = {'class': 'form-select'}
                continue
            elif name == 'teacher_info':
                field.widget = forms.Textarea(
                    attrs={'class': 'form-control', 'rows': '3'})
                continue
            elif name == 'assessment':
                field.widget = forms.Textarea(
                    attrs={'class': 'form-control', 'rows': '3'})
                continue
            elif name == 'brief':
                field.widget = forms.Textarea(
                    attrs={'class': 'form-control', 'rows': '5'})
                continue
            field.widget.attrs = {'class': 'form-control'}


class SelectionForm(forms.Form):
    classid = forms.CharField(required=False, label="课程序号",
                              max_length=50)
    code = forms.CharField(required=False, label="课程代码",
                           max_length=50)
    name = forms.CharField(required=False, label="课程名称",
                           max_length=50)
    department = forms.CharField(required=False, label="开课院系",
                                 max_length=50)
    time = forms.CharField(required=False, label="开课时间",
                           max_length=50)
    exam = forms.CharField(required=False, label="考试类型",
                           max_length=50)


class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        exclude = ["classid", "user_id"]
        error_messages = {
            "Com_course": {"max_length": "最大输入长度为50", "required": "请输入评论"},
            "Com_classroom": {"max_length": "最大输入长度为50", "required": "请输入评论"},
            "Com_textbook": {"max_length": "最大输入长度为50", "required": "请输入评论"}
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():

            if name == 'Com_course':
                field.widget = forms.Textarea(
                    attrs={'class': 'form-control', 'rows': '3', "placeholder": "请写您对课程的评价（50字以内）"})
                continue
            elif name == 'Com_classroom':
                field.widget = forms.Textarea(
                    attrs={'class': 'form-control', 'rows': '3', "placeholder": "请写您对教室的评价（50字以内）"})
                continue
            elif name == 'Com_textbook':
                field.widget = forms.Textarea(
                    attrs={'class': 'form-control', 'rows': '3', "placeholder": "请写您对教材的评价（50字以内）"})
                continue
            field.widget.attrs = {'class': 'form-control'}


class ScoreForm(forms.Form):
    score = forms.CharField(required=True, label="成绩",
                            max_length=5)


class Temp_ClassForm(forms.ModelForm):
    class Meta:
        model = Temp_Class
        exclude = ["teacher_id","views"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():

            if name == 'exam':
                field.widget.attrs = {'class': 'form-select', }
                continue
            elif name == 'teacher_info':
                field.widget = forms.Textarea(
                    attrs={'class': 'form-control', 'rows': '3', "placeholder": "简要概括授课老师"})
                continue
            elif name == 'teacher_info':
                field.widget = forms.Textarea(
                    attrs={'class': 'form-control', 'rows': '1', "placeholder": "每周所需学时"})
                continue
            elif name == 'time':
                field.widget = forms.Textarea(
                    attrs={'class': 'form-control', 'rows': '1', "col": '1',
                           "placeholder": "务必遵守格式：周X，a-b（如不连续请用分号（；）隔开，可多选用/隔"})
                continue
            elif name == 'assessment':
                field.widget = forms.Textarea(
                    attrs={'class': 'form-control', 'rows': '2', "placeholder": "简要概括评分方式"})
                continue
            elif name == 'weeks':
                field.widget = forms.Textarea(
                    attrs={'class': 'form-control', 'rows': '1', "placeholder": "课程开设周数"})
                continue
            elif name == 'brief':
                field.widget = forms.Textarea(
                    attrs={'class': 'form-control', 'rows': '4', "placeholder": "简要的课程简介"})
                continue
            field.widget.attrs = {'class': 'form-control'}


class Adjustment_TimeForm(forms.Form):
    days = forms.ChoiceField(choices=(("周一", "周一"),
                                      ("周二", "周二"),
                                      ("周三", "周三"),
                                      ("周四", "周四"),
                                      ("周五", "周五"),
                                      ("周六", "周六"),
                                      ("周日", "周日")))
    first_class = forms.IntegerField(max_value=13, min_value=1)
    from_time = forms.CharField(max_length=30, label="原定时间")


class Comment_Form(forms.Form):
    comment = forms.CharField(max_length=40, label="相关评论")


class Admin_ClassForm(forms.Form):
    classid = forms.CharField(required=False, label="课程序号",
                              max_length=50)
    code = forms.CharField(required=False, label="课程代码",
                           max_length=50)
    name = forms.CharField(required=False, label="课程名称",
                           max_length=50)
    teacher = forms.CharField(required=False, label="教师姓名",
                              max_length=50)


class ProgramForm(forms.Form):
    major = forms.CharField(required=False, label="课程序号",
                            max_length=50)
    grade = forms.IntegerField(max_value=8, min_value=1)

class Class_DayForm(forms.Form):
    days = forms.CharField(label="课程序号",
                            max_length=50)