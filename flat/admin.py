from django.contrib import admin
from .models import (
    Flat,
    Category,
    Location,
    Family,
    Bachelor,
    Shop
)


class FlatAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ('title',)}
    list_display = ('id', 'title', 'owner', 'category', 'location', 'created_at')
    list_filter = ('category', 'created_at', 'commode', 'water_supply', 'kitchen', 'cctv')
    search_fields = ('title', 'owner__username', 'location')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('renters_who_messaged',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('owner', 'title', 'slug', 'category', 'location')
        }),
        ('Property Details', {
            'fields': ('washroom', 'floor', 'commode', 'water_supply', 'tiles', 'kitchen')
        }),
        ('Amenities', {
            'fields': ('cctv', 'roof_top_uses', 'garage'),
            'classes': ('collapse',)
        }),
        ('Images', {
            'fields': ('image_1', 'image_2', 'image_3', 'image_4', 'image_5'),
            'classes': ('collapse',)
        }),
        ('Messaging', {
            'fields': ('renters_who_messaged',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ('title',)}
    list_display = ('id', 'title', 'slug', 'created_at')
    search_fields = ('title',)
    readonly_fields = ('created_at',)


class LocationAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ('title',)}
    list_display = ('id', 'title', 'slug', 'created_at')
    search_fields = ('title',)
    readonly_fields = ('created_at',)


class FamilyAdmin(admin.ModelAdmin):
    list_display = ('id', 'flat', 'bed_room', 'rent', 'dining_room', 'drawing_room', 'balcony')
    list_filter = ('dining_room', 'drawing_room', 'balcony')
    search_fields = ('flat__title', 'address')
    raw_id_fields = ('flat',)
    
    fieldsets = (
        ('Flat Reference', {
            'fields': ('flat',)
        }),
        ('Room Details', {
            'fields': ('bed_room', 'dining_room', 'drawing_room', 'balcony')
        }),
        ('Financial & Location', {
            'fields': ('rent', 'address')
        })
    )


class BachelorAdmin(admin.ModelAdmin):
    list_display = ('id', 'flat', 'available_seats', 'total_members', 'expected_total_cost', 'khala_facility')
    list_filter = ('khala_facility',)
    search_fields = ('flat__title', 'available_seats', 'total_members')
    raw_id_fields = ('flat',)
    
    fieldsets = (
        ('Flat Reference', {
            'fields': ('flat',)
        }),
        ('Occupancy', {
            'fields': ('available_seats', 'total_members')
        }),
        ('Costs', {
            'fields': ('dininig_charge', 'meal_rate_range', 'extra_cost_range', 'expected_total_cost')
        }),
        ('Facilities', {
            'fields': ('khala_facility',)
        })
    )


class ShopAdmin(admin.ModelAdmin):
    list_display = ('id', 'flat', 'rent', 'square_feet', 'preaching_space')
    list_filter = ('preaching_space',)
    search_fields = ('flat__title', 'address')
    raw_id_fields = ('flat',)
    
    fieldsets = (
        ('Flat Reference', {
            'fields': ('flat',)
        }),
        ('Shop Details', {
            'fields': ('rent', 'square_feet', 'preaching_space')
        }),
        ('Location', {
            'fields': ('address',)
        })
    )


# Register models with their admin classes
admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Flat, FlatAdmin)
admin.site.register(Family, FamilyAdmin)
admin.site.register(Bachelor, BachelorAdmin)
admin.site.register(Shop, ShopAdmin)