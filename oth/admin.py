from django.contrib import admin
from oth import models

admin.site.site_header = 'COC Administration'

admin.site.register(models.Player)
admin.site.register(models.Question)
# admin.site.register(models.UserProfile)
admin.site.register(models.Notif)
admin.site.register(models.Answer)
admin.site.register(models.Module)
# admin.site.register(models.Emotion)