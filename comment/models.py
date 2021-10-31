from django.db import models

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
# Create your models here.
class Comment(models.Model):
    content_type = models.ForeignKey(ContentType,on_delete = models.CASCADE)
    object_id = models.PositiveIntegerField()
    #  content_object这个类型可以指向任何一个对象
    content_object = GenericForeignKey('content_type','object_id')

    text = models.TextField()
    comment_time = models.DateTimeField(auto_now_add = True)
    # 这是指谁写的评论
    user = models.ForeignKey(User,related_name = 'comments',on_delete = models.CASCADE)

    #现在获取一条评论下面的所有回复
    # root表示哪一条回复是基于哪一条评论开始的
    root = models.ForeignKey('self',related_name = 'root_comment',null = True,on_delete =models.CASCADE)

    # 记录是自己字段的一个信息
    # 在最顶级的时候直接评论文章，不一定有parent, 允许为空
    #parent 表示顶级评论
    parent = models.ForeignKey('self',null = True,on_delete = models.CASCADE)

    # 通过user反向得到comment里的东西
    # related_name :反向解析的意思
    # 所以通过写related_name来解决冲突问题，并且明确对应关系

    #这是指回复给谁
    reply_to  =models.ForeignKey(User,related_name = 'replies',null = True,on_delete = models.CASCADE)


    def __str__(self):
        return self.text

    #使评论按照评论时间倒序排列
    class Meta():
        ordering = ['comment_time']

