from django.contrib import admin
from .models import (
    Flat,
    Category,
    Location
)
# Register your models here.

class FlatAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ('title',)}
    
    
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ('title',)}
    
    
class LocationAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ('title',)}
    
    
    
admin.site.register(Category, CategoryAdmin)
admin.site.register(Flat, FlatAdmin)
admin.site.register(Location, LocationAdmin)