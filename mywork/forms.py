from django import forms


class AuthenticationForm(forms.Form):
    username = forms.CharField(label='用户名', widget=forms.TextInput())
    password = forms.CharField(label='密码', widget=forms.PasswordInput())

    class Meta:
        fields = ['username', 'password']