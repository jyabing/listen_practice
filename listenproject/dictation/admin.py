from django.contrib import admin
from .models import Category, Material, Question

admin.site.register(Category)
admin.site.register(Material)
admin.site.register(Question)