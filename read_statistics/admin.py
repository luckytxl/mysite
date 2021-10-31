from django.contrib import admin
from read_statistics.models import ReadDetail
# Register your models here.
from .models import ReadNum

@admin.register(ReadNum)
class ReadNumAdmin(admin.ModelAdmin):
    list_display = ('read_num','content_object')


@admin.register(ReadDetail)
class ReadDetailAdmin(admin.ModelAdmin):
    list_display = ('date','read_num','content_object')

