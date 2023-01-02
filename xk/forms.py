from django import forms
from xk_models.models import ClassDetail,Evaluation


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
            "Com_course":{"max_length":"最大输入长度为50","required":"请输入评论"},
            "Com_classroom":{"max_length":"最大输入长度为50","required":"请输入评论"},
        "Com_textbook":{"max_length":"最大输入长度为50","required":"请输入评论"}
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():

            if name == 'Com_course':
                field.widget = forms.Textarea(
                    attrs={'class': 'form-control', 'rows': '3',"placeholder":"请写您对课程的评价（50字以内）"})
                continue
            elif name == 'Com_classroom':
                field.widget = forms.Textarea(
                    attrs={'class': 'form-control', 'rows': '3',"placeholder":"请写您对教室的评价（50字以内）"})
                continue
            elif name == 'Com_textbook':
                field.widget = forms.Textarea(
                    attrs={'class': 'form-control', 'rows': '3',"placeholder":"请写您对教材的评价（50字以内）"})
                continue
            field.widget.attrs = {'class': 'form-control'}