from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from .models import Comment
from django.urls import reverse
from django.shortcuts import redirect
from .forms import CommentForm

from django.http import JsonResponse

def update_comment(request):
    '''
    referer = request.META.get('HTTP_REFERER', reverse('home'))

    user = request.user

    if not user.is_authenticated:
        return render(request,'error.html',{'message':'用户未登录','redirect_to':referer})


    text = request.POST.get('text','').strip()
    #数据检查
    if text == '':
        return render(request,'error.html',{'message':'评论内容为空','redirect_to':referer})
    try :
        content_type = request.POST.get('content_type','')
        object_id =  int(request.POST.get("object_id"," "))

        #得到这些信息之后，对Comment模型进行实例化
        model_class = ContentType.objects.get(model = content_type).model_class()
        model_obj = model_class.objects.get(pk = object_id)
    except Exception as e:
        return render(request,'error.html',{'message':'评论对象不存在','redirect_to':referer})

    comment = Comment()
    comment.user= user
    comment.text = text
    comment.content_object = model_obj
    comment.save()


    return redirect(referer)
    '''
    # referer = request.META.get('HTTP_REFERER', reverse('home')) # 不理解


    comment_form = CommentForm(request.POST,user=request.user)

    data = {}

    if comment_form.is_valid():
        #检查通过，保存数据
        comment = Comment()
        comment.user =comment_form.cleaned_data['user']
        comment.text = comment_form.cleaned_data['text']
        comment.content_object = comment_form.cleaned_data['content_object']

        # views里面要加一些回复的数据进去

        # 首先判断它是不是顶级评论，如果不是顶级评论，那么就是回复，在对他进行处理
        # 如果不是顶级评论，那么就将它写入parent.root,
        # 如果是顶级评论，那么就将它写入parent
        parent = comment_form.cleaned_data['parent']
        if not parent is None:
            comment.root = parent.root if not parent.root is None else parent
            comment.parent = parent
            comment.reply_to = parent.user


        comment.save()

        # 返回数据

        data['status'] = 'SUCCESS'
        data['username'] = comment.user.username

        # 因为comment_time是DateTime数据类型，所以需要我们用strftime转化为字符串
        data['comment_time'] = comment.comment_time.strftime('%Y-%m-%d %H:%M:%S')
        data['text'] = comment.text

        if not parent is None:  #如果不是顶级评论
            data['reply_to'] = comment.reply_to.username   # 如果他是回复，获取它  回复给谁
        else:
            data['reply_to'] =''  # 如果不是，则返回空
        data['pk'] = comment.pk   #  最后获取主键值
        # 此时我们需要一个root_id,所以从后端要传入一个root_pk

        # 如果他是 not None 取到 root_pk
        data['root_pk'] = comment.root.pk if not comment.root is None else ''
        # return redirect(referer)

    else:

        data['status'] = 'ERROR'
        # 错误信息是一个字典，所以用字典里面的vlaues()
        # 方法，然后将字典转成列表，取列表的第一个错误信息 - --把他抛出去就可以啦
        # 这里还需要给改一下，因为这里取到的数据类型是数组,所以 list(comment_form.errors.values())[0][0]
        data['message'] = list(comment_form.errors.values())[0][0]
    return JsonResponse(data)
        # return render(request,'error.html',{'message':comment_form.errors,'redirect_to':referer})  # 不理解 'redirect_to':referer
