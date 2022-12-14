from django import forms


class UserForm(forms.Form):
    email = forms.CharField(label="邮箱",
                            max_length=50,
                            widget=forms.TextInput(attrs={'class': 'IDCheckLoginName','placeholder':'邮箱（不是学号！）'}))
    password = forms.CharField(label="密码",
                               max_length=256, 
                               widget=forms.PasswordInput(attrs={'class': 'IDCheckLoginPassWord', 'placeholder':'密码'}))
