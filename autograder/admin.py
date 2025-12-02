from django.contrib import admin
from .models import CustomUser, MarkingTask, Report


admin.site.register(Report)
admin.site.register(CustomUser)
admin.site.register(MarkingTask)