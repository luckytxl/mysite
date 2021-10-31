import datetime
from django.shortcuts import render
from django.shortcuts import redirect
from blog.models import Blog
from django.contrib.contenttypes.models import ContentType
from read_statistics.utils import get_seven_days_read_date
from read_statistics.utils import get_today_hot_data
from read_statistics.utils import get_yesterday_hot_data
from django.utils import timezone
from django.db.models import Sum
from django.core.cache import cache

from django.contrib.auth import authenticate,login
from django.urls import reverse

from .forms import LoginForm
from .forms import RegForm
from django.contrib.auth.models import User


def get_7_days_hot_blogs():
    today = timezone.now().date()
    date = today - datetime.timedelta(days=7)

    blog =Blog.objects.filter(read_details__date__lt=today,read_details__date__gte=date)\
        .values('id','title')\
        .annotate(read_num_sum = Sum('read_details__read_num'))\
        .order_by('-read_num_sum')
    return blog[:7]


def home(request):

    blog_content_type= ContentType.objects.get_for_model(Blog)
    dates,read_nums = get_seven_days_read_date(blog_content_type)
    # today_hot_data = get_today_hot_data(blog_content_type)  多余,被下面替换
    # yesterday =  get_yesterday_hot_data(blog_content_type)  多余,被下面替换

    #获取7天热门博客的缓存数据
    hot_blogs_for_7_dates = cache.get('hot_blogs_for_7_dates')
    if hot_blogs_for_7_dates is None:
        hot_blogs_for_7_dates = get_7_days_hot_blogs()
        cache.set('hot_blogs_for_7_dates',hot_blogs_for_7_dates,3600)

    #测试
    #     print('calculate')
    # else:
    #     print('use cache')

    context = {}
    context['dates'] =dates
    context['read_nums'] = read_nums
    context['today_hot_data'] = get_today_hot_data(blog_content_type)
    context['yesterday_hot_data'] = get_yesterday_hot_data(blog_content_type)
    context['hot_blogs_for_7_dates'] = get_7_days_hot_blogs()
    return render(request,'home.html',context)

def user_login(request):
    '''
    username = request.POST.get('username','')
    password = request.POST.get('password','')
    user = authenticate(request,username = username,password = password)

    # 通过别名解析，获得反向的链接（把home解析成正向的链接）
    referer = request.META.get('HTTP_REFERER',reverse('home'))

    if user is not None:
        login(request,user)
        return redirect(referer)
    else:
        return render(request,'error.html',{'message':'用户名或密码不正确'})
    '''
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = login_form.cleaned_data['user']
            login(request, user)
            return redirect(request.GET.get('from', reverse('home')))


    else:
        login_form = LoginForm()

    context = {}
    context['login_form'] = login_form
    return render(request,'user_login.html',context)
#实例化Form类


def register(request):
    # 如果是POST，用POST方法对它进行实例化
    # 如果是GET，用普通方法对它进行实例化
    if request.method == 'POST':
        reg_form = RegForm(request.POST)
        if reg_form.is_valid():
            username = reg_form.cleaned_data['username']
            email = reg_form.cleaned_data['email']
            password = reg_form.cleaned_data['password']

            #创建用户
            user  = User.objects.create_user(username,email,password)
            user.save()
            #登陆用户
            user = authenticate(username = username,password = password)
            login(request,user)
            return redirect(request.GET.get('from',reverse('home')))
    else:
        reg_form = RegForm()
    context = {}
    context['reg_form'] = reg_form
    return render(request,'register.html',context)