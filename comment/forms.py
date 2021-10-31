from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models import ObjectDoesNotExist
from .models import Comment
# 将django框变成 form 文本编辑框(需要引入的包)
from ckeditor.widgets import CKEditorWidget

class CommentForm(forms.Form):
    content_type = forms.CharField(widget = forms.HiddenInput)
    object_id = forms.IntegerField(widget = forms.HiddenInput)
    # text = forms.CharField(widget = forms.Textarea)
    text = forms.CharField(widget=CKEditorWidget(config_name = 'comment_ckeditor'),error_messages={'required':'评论内容不能为空'})





    #下来做回复功能
    # 回复对应评论的主键值
    #  （） 里的id值通过前端页面获取，因为这个没必要给用户看，隐藏起来
    #  这个字段有初始化的工作要做
    reply_comment_id = forms.IntegerField(widget = forms.HiddenInput(attrs={'id':'reply_comment_id'}))


    # 这一块用到了python类这一块的基础知识（有难度）
    # 用这种方法就把user对象传进来了，那么我们就可以对user进行验证
    def __init__(self, *args, **kwargs):
        # self.user = kwargs.get('user')
        # 如果获取得到的话就获取，获取不到就为None
        # 因为获取之后，参数还在kwargs里面，而传给原本初始化操作的时候，会看到原本这个关键字参数，他会判断这个关键字参数是否合法。如果他没有规定这个参数，我们写的这个参数他会报错
        # 所以在进行处理逻辑的时候，我们要将这个参数剔除掉
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(CommentForm, self).__init__(*args, **kwargs)

    def clean(self):

        #这个方法不理解什么意思
        # 因为在blog的views里面初始化的时候没有传入这个user参数
        # 所以没有直接参数给它使用，所以不应该用中括号这种形式，所以我们用get


        #判断用户是否登录
        if self.user.is_authenticated:
            self.cleaned_data['user'] = self.user
        else:
            raise forms.ValidationError('用户尚未登陆')


        #评论对象验证
        content_type = self.cleaned_data['content_type']
        object_id= self.cleaned_data['object_id']
        try:
            model_class = ContentType.objects.get(model = content_type).model_class()
            model_obj = model_class.objects.get(pk = object_id)
            self.cleaned_data['content_object'] = model_obj # 不理解
        except ObjectDoesNotExist:
            raise forms.ValidationError('评论对象不存在')
        return self.cleaned_data

    def clean_reply_comment_id(self):
        reply_comment_id = self.cleaned_data['reply_comment_id']
        if reply_comment_id < 0:
            raise forms.ValidationError('回复出错')
        elif reply_comment_id == 0:
            self.cleaned_data['parent'] = None
        elif Comment.objects.filter(pk = reply_comment_id).exists():
            self.cleaned_data['parent'] = Comment.objects.get(pk = reply_comment_id)
        else:
            raise forms.ValidationError('回复错误')
        return reply_comment_id
