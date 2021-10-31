#以下是自己的代码
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import Blog
from django.core.paginator import Paginator
from .models import BlogType
# from .models import ReadNum
from django.conf import settings

from django.contrib.contenttypes.models import ContentType
from read_statistics.models import ReadNum
#计数的annotate
from django.db.models import Count

from read_statistics.utils import read_statistics_once_read

from comment.models import Comment

from comment.forms import CommentForm
def get_blog_list_common(request,blogs_all_list):
    paginator = Paginator(blogs_all_list, settings.EACH_PAGE_BLOGS_NUM)

    page_num = request.GET.get('page', 1)  # 获取url的页面参数（GET请求，request.GET获得一个字典类型）
    page_of_blogs = paginator.get_page(page_num)
    # 实现代码折叠功能
    # 获取当前页
    current_page_num = page_of_blogs.number
    # 获取当前页码前后各两页的页码范围
    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + list(
        range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))  # 不太懂

    # 加上省略页码标记
    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')  # 不太懂

    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    #获取博客分类的对应博客数量
    # 当使用这行代码的时候才将数量拉到内存当中
    # BlogType.objects.annotate(blog_count = Count('blog'))  #这行代码的效果，解析出来是一条sql语句

    '''
    # for循环会把数据拿到服务器里面，会增加服务器负担
    #最开始的实现计数的方法
    blog_types = BlogType.objects.all()
    blog_types_list = [ ]
    for blog_type in blog_types:
        # 左边的 blogtype 是models里面的字段
        blog_type.blog_count = Blog.objects.filter(blogtype = blog_type).count()
        # 给原本的blog_type新加一个属性 blog_type.blog_conunt,但是此时它在for循环里面是临时的,现在在外部创建一个变量，让它永久
        blog_types_list.append(blog_type)  # 此时，这个列表就带有三个分类，并且这些分类是带有数量统计的


    '''


    #获取日期归档对应的博客数量
    blog_dates = Blog.objects.dates('createtime', 'month', order='DESC')

    blog_dates_dict = { }
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(createtime__year = blog_date.year,createtime__month = blog_date.month).count()
        blog_dates_dict[blog_date] = blog_count  # []  里面不加 引号



    context = {}
    # context['blogs'] = Blog.objects.all()
    # 获取博文数量
    # context['blogs_count'] = Blog.objects.all().count()
    # context['blog_types']=BlogType.objects.all()  下面有重复
    context['blogs'] = page_of_blogs.object_list
    context['page_of_blogs'] = page_of_blogs

    # 加入这行代码，实现5个页码
    context['page_range'] = page_range

    # 通过 annotate实现 获取博客分类的对应博客数量
    context['blog_types'] = BlogType.objects.annotate(blog_count=Count('blog'))  # 这行代码的效果，解析出来是一条sql语句
    # context['blog_types'] = blog_types_list  被上面一行代码替换掉  （上面的for循环得到的 blog_types_list，但是 被上面一行代码替换掉 《更优化了》）
    # context['blog_types'] = BlogType.objects.all() 被上面一行代码替换掉 （最原始的）  优化了

    # 根据日期显示列表
    context['blog_dates'] = blog_dates_dict  # DESC倒序

    return context




def blog_list(request):
    blogs_all_list = Blog.objects.all()

    context = get_blog_list_common(request,blogs_all_list)

    return render(request,'blog/blog_list.html',context)


def blogs_with_type(request,blog_type_pk):

    blog_type = get_object_or_404(BlogType,pk = blog_type_pk)

    blogs_all_list = Blog.objects.filter(blogtype=blog_type)
    #调用函数
    context = get_blog_list_common(request,blogs_all_list)

    context['blog_type'] = blog_type


    return render(request,'blog/blogs_with_type.html',context)


def blogs_with_data(request, year, month):


    blogs_all_list = Blog.objects.filter(createtime__year = year,createtime__month = month)

    # 调用函数
    context = get_blog_list_common(request,blogs_all_list)

    context['blogs_with_date'] = '%s年%s月'%(year,month)



    return render(request,'blog/blogs_with_date.html', context)


def blog_detail(request,blog_pk):
    blog = get_object_or_404(Blog, pk=blog_pk)
    read_cookie_key = read_statistics_once_read(request,blog)

    #显示评论内容所做的工作
    blog_content_type = ContentType.objects.get_for_model(blog)
    #关联评论模块
    # 通过筛选将这篇博客的类型，以及这篇博客的主键值 - ----得到这篇博客相关的所有评论内容 ------parent =None表示 在最顶级的时候直接评论文章，不一定有parents, 允许为空
    comments = Comment.objects.filter(content_type = blog_content_type,object_id = blog.pk,parent =None)



    '''
    if not request.COOKIES.get('blog_%s_readed'%blog_pk):
        ct = ContentType.objects.get_for_model(Blog)
        if ReadNum.objects.filter(content_type = ct,object_id = blog.pk).count():
            #存在记录
            readnum = ReadNum.objects.get(content_type=ct, object_id=blog.pk)
        else:
            #不存在记录
            readnum = ReadNum(content_type=ct, object_id=blog.pk)
        #计数加1
        readnum.read_num += 1
        readnum.save()

        
        if ReadNum.objects.filter(blog = blog).count():
            #存在记录，把阅读数取出来
            readnum = ReadNum.objects.get(blog = blog)

        else:
            #不存在记录
            readnum = ReadNum(blog=blog)
            readnum.read_num += 1
        readnum.blog = blog
        readnum.save()
        
    '''





    context = {}

    context['previous_blog'] = Blog.objects.filter(createtime__gt=blog.createtime).last()
    # next_blog = Blog.objects.filter(createtime__lt=blog.createtime)[0]
    context['next_blog'] = Blog.objects.filter(createtime__lt=blog.createtime).first()
    context['blog'] = blog

    #这样就实现了, 正常评论是倒序,而回复是正序
    context['comments'] = comments.order_by('-comment_time')
    #reply_comment_i--- 当这个字段是顶级类型时，我们写个0
    context['comment_form'] = CommentForm(initial ={'content_type':blog_content_type.model,'object_id': blog_pk,'reply_comment_id':0})
    #request有一个user属性，我们可以获得这个user属性给前端页面
    # context['user'] = request.user   render方法里面，封装了user信息，所以不用获得

    response =  render(request,'blog/blog_detail.html',context) # response 是响应

    # response.set_cookie('blog_%s_readed'%blog_pk,'true')
    response.set_cookie(read_cookie_key,'true')  #阅读cookie标记

    return response