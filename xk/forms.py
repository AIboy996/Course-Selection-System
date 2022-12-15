from django import forms
from xk_models.models import ClassDetail


class UserForm(forms.Form):
    email = forms.CharField(label="邮箱",
                            max_length=50,
                            widget=forms.TextInput(attrs={'class': 'IDCheckLoginName', 'placeholder': '邮箱（不是学号！）'}))
    password = forms.CharField(label="密码",
                               max_length=256,
                               widget=forms.PasswordInput(attrs={'class': 'IDCheckLoginPassWord', 'placeholder': '密码'}))


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
