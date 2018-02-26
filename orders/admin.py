from django.contrib import admin

from shoppingcart.models import Line

from .models import Order


class LineInline(admin.TabularInline):
    model = Line
    extra = 0
    can_delete = False
    fields = ('product', 'final_price', 'quantity')
    readonly_fields = fields

    def has_add_permission(self, *args, **kwargs):
        return False


class OrderAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'status', 'total', 'email', 'date')
    list_editable = ('status',)
    list_filter = ('status',)
    search_fields = ('email',)
    readonly_fields = ('total',)

    inlines = (LineInline,)


admin.site.register(Order, OrderAdmin)
