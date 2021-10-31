from django import forms

from django.contrib.auth import authenticate,login

from django.contrib.auth.models import User
#登录功能
class LoginForm(forms.Form):
    username = forms.CharField(label = '用户名',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'请输入用户名'}))
    password = forms.CharField(label = '密码',widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'请输入密码'}))
    # clean方法用来验证字段,相当于执行is_valid()方法
    # 验证的操作放到form里面，其他操作放到处理方法views中
    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        user = authenticate(username=username, password=password)
        if user is None:
            raise forms.ValidationError('用户名或密码不正确')
        else:
            # 可以把user获取，再返回出来，并不是这个方法没有用
            # 返回的cleaned_data包含了
            # user这个信息
            # 从这个层面讲，一定要返回cleand_data否则他一定有问题
            self.cleaned_data['user'] = user
        return self.cleaned_data

#注册功能
class RegForm(forms.Form):
    username = forms.CharField(label='用户名',max_length = 30,min_length =3,
                               widget=forms.TextInput(attrs={'class':'form-control','placeholder':'请输入3-30位字符'}))
    email = forms.EmailField(label = '邮箱',widget = forms.EmailInput(attrs={'class':'form-control','placeholder':'请输入邮箱'}))
    password = forms.CharField(label='密码',min_length = 6,
                               widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'请输入密码'}))
    password_again = forms.CharField(label='请在输入一次密码', min_length=6,
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请在输入一次密码'}))
    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username = username).exists():
            raise forms.ValidationError('用户名已经存在')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email = email).exists():
            raise forms.ValidationError('邮箱已经存在')
        return email

    def clean_password_again(self):
        password = self.cleaned_data['password']
        password_again = self.cleaned_data['password_again']
        if password != password_again:
            forms.ValidationError('两次输入的密码不一致')
        return password_again
