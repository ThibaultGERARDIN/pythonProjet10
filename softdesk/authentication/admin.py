from django.contrib import admin
from .models import MyUser


# Now register the new UserAdmin...
admin.site.register(MyUser)
