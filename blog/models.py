from django.db import models
#以下是自己的代码
from django.contrib.auth.models import User

#导入富文本编辑用的包
from ckeditor_uploader.fields import RichTextUploadingField
from read_statistics.models import ReadNumExpandmethod
from django.contrib.contenttypes.fields import GenericRelation
from read_statistics.models import ReadDetail

# from django.db.models.fields import exceptions
#
# from django.contrib.contenttypes.models import ContentType
# from read_statistics.models import ReadNum



class BlogType(models.Model):
    type_name = models.CharField(max_length = 15)
    def __str__(self):
        return self.type_name
class Blog(models.Model,ReadNumExpandmethod):
    title = models.CharField(max_length = 50)
    blogtype=models.ForeignKey(BlogType,on_delete = models.CASCADE)
    content = RichTextUploadingField()
    author = models.ForeignKey(User,on_delete = models.CASCADE)

    read_details = GenericRelation(ReadDetail)

    createtime = models.DateTimeField(auto_now_add = True)
    last_updated_time = models.DateTimeField(auto_now = True)

    '''
    def get_read_num(self):
        try:
            ct = ContentType.objects.get_for_model(self)
            readnum = ReadNum.objects.get(content_type = ct,object_id = self.pk)
            return readnum.read_num
        except exceptions.ObjectDoesNotExist:
            return 0
    '''

    '''
    def get_read_num(self):
        try:
            return self.readnum.read_num
        except exceptions.ObjectDoesNotExist:
            return 0
    '''

    def __str__(self):
        return '<Blog: %s>'%self.title
    class Meta():
        ordering = ['-createtime']


'''
class ReadNum(models.Model):
    read_num = models.IntegerField(default=0)
    # blog = models.ForeignKey(Blog,on_delete=models.CASCADE)
    blog = models.OneToOneField(Blog, on_delete=models.CASCADE)

'''
