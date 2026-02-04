from django.contrib import admin
from users.models import User, Payments, Subscription

admin.site.register(User)
admin.site.register(Payments)
admin.site.register(Subscription)
