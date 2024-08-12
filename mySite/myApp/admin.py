from django.contrib import admin
from .models import *
# Register your models here.


# Registering Fish model
admin.site.register(Fish)

# Registering Fisherman model
admin.site.register(Fisherman)

# Registering Catch model
admin.site.register(Catch)

# Registering Advance model
admin.site.register(Advance)

# Registering Payment model
admin.site.register(Payment)

# Registering PaymentLog model
admin.site.register(PaymentLog)