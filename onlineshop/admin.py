from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.template.response import TemplateResponse

from mptt.admin import MPTTModelAdmin, TreeRelatedFieldListFilter

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

    list_display = ('title', 'price', 'discount', 'get_price', 'in_stock')
    list_editable = ('price', 'discount')
    list_filter = (
        ('category', TreeRelatedFieldListFilter),
    )

    def add_discount(self, request, queryset):
        """Custom action that allow to add discount for products in bulk
        using intermediate page, this action called twice in proccess.

        At first request this action returns template with form that contains
        hidden input with selected items and hidden input with action name.
        After inputing discount and submiting the form to admin view this
        action called second time because our form have hidden field with
        action name and _selected_action and admin would threat it like if we
        have send standard action form and because our form also have
        'apply' form data, the main body of action will be executed.
        """
        form = None
        message = _(
            'Succesfully added {percent}% discount to {number} products'
        )

        if 'apply' in request.POST:
            form = AddDiscountForm(request.POST)
            if form.is_valid():
                discount = form.cleaned_data['discount']

                updated = queryset.update(discount=discount)

                self.message_user(request,
                                  message.format({'percent': discount,
                                                  'number': updated}))

                return None

        if form is None:
            # admin.ACTION_CHECKBOX_NAME == _selected_action
            # _selected_action contains ID of selected products
            # actual action passed to view as action form param.
            selected = {'_selected_action':
                        request.POST.getlist(admin.ACTION_CHECKBOX_NAME)}
            form = AddDiscountForm(initial=selected)

        return TemplateResponse(request, 'admin/add_discount.html',
                                {'products': queryset, 'form': form})

        # Code below works too but i'll stick with more explicit version above.

        # selected = {'_selected_action':
        #             request.POST.getlist(admin.ACTION_CHECKBOX_NAME)}

        # form = AddDiscountForm(request.POST or None, initial=selected)

        # if form.is_valid():
        #     discount = form.cleaned_data['discount']
        #     updated = queryset.update(discount=discount)
        #     self.message_user(request, message.format(discount, updated))
        #     return None

        # return TemplateResponse(request, 'admin/add_discount.html',
        #                         {'products': queryset, 'form': form})

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
