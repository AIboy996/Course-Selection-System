from django import forms
from xk_models.models import ClassDetail


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
    time = forms.ChoiceField(required=False, label="开课时间",
                             choices=[("周一", "周一"),
                                      ("周二", "周二"),
                                      ('周三', '周三'),
                                      ('周四', '周四'),
                                      ('周五', '周五'),
                                      ('周六', '周六'),
                                      ('周日', '周日'), ],
                             initial="",
                             widget=forms.widgets.Select())
    exam = forms.ChoiceField(required=False, label="考试类型",
                             choices=[('开卷考试', '开卷考试'),
                                      ('闭卷考试', '闭卷考试'),
                                      ('半开卷考试', '半开卷考试'),
                                      ('课程论文', '课程论文'),
                                      ('其他', '其他')],
                             initial="其他",
                             widget=forms.widgets.Select())

