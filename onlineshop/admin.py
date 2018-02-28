from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.template.response import TemplateResponse

from mptt.admin import MPTTModelAdmin, TreeRelatedFieldListFilter

from shoppingcart.signals import price_changed
from remindme.signals import product_in_stock

from .models import Category, Product, Attribute, ProductAttributeValue
from .forms import AddDiscountForm


class ProductAttributeValueInline(admin.TabularInline):
    model = ProductAttributeValue
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    inlines = (ProductAttributeValueInline,)
    prepopulated_fields = {'slug': ('title', )}
    date_hierarchy = 'date_added'
    actions = ('add_discount',)

    list_display = ('title', 'price', 'discount', 'get_price',
                    '_in_stock_admin')
    list_editable = ('price', 'discount')
    list_filter = (
        ('category', TreeRelatedFieldListFilter),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change:
            data = form.changed_data
            initial = form.initial

            if any([x in data for x in ['price', 'discount']]):
                price_changed.send(sender=self.__class__, product=obj)

            if initial['stock'] == 0 and obj.stock > 0:
                product_in_stock.send(
                    sender=self.__class__, product=obj, request=request
                )

    def add_discount(self, request, queryset):
        """Custom action that allow to add discount for products in bulk
        using intermediate page, this action called twice in proccess.

        At first request this action returns template with form that repeat
        original admin action form.
        After inputing discount and submiting the form to admin view this
        action called second time because our form have hidden field with
        action name and _selected_action and admin view would threat it like if
        we had sent standard action form and because our form also have
        additional 'apply' form data - the main body of action
        will be executed.
        """
        form = None
        message = _(
            'Succesfully added {percent}% \\discount to {number} products'
        )

        if 'apply' in request.POST:
            form = AddDiscountForm(request.POST)
            if form.is_valid():
                discount = form.cleaned_data['discount']

                updated = queryset.update(discount=discount)

                self.message_user(request,
                                  message.format(percent=discount,
                                                 number=updated))

                return None

        if form is None:
            selected = {'_selected_action':
                        request.POST.getlist(admin.ACTION_CHECKBOX_NAME)}
            form = AddDiscountForm(initial=selected)

        return TemplateResponse(request, 'admin/add_discount.html',
                                {'products': queryset, 'form': form})

    add_discount.short_description = _('Add discount to products')


class CategoryAdmin(MPTTModelAdmin):
    prepopulated_fields = {'slug': ('title', )}


class AttributeAdmin(admin.ModelAdmin):
    """Work around found in internet that allow to hide
    registered model in admin page but still allow to add
    objects from related models pages.
    """
    def get_model_perms(self, request):
        return {}


admin.site.register(Attribute, AttributeAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
