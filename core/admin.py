from datetime import datetime

from django.contrib import admin
from django.utils.html import mark_safe
from django.contrib.auth.admin import UserAdmin

from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin, ImportExportActionModelAdmin
from import_export.widgets import ManyToManyWidget

from checkout.models import Order
from .models import Item, CartItem, Cart, Category, SubCategory, CustomUser, ItemImage
from .forms import CustomUserChangeForm, CustomUserCreationForm


class CartResource(resources.ModelResource):
    class Meta:
        model = Cart


class ItemResource(resources.ModelResource):
    categories = fields.Field(widget=ManyToManyWidget(Category, field='title'), attribute='categories')
    subcategories = fields.Field(widget=ManyToManyWidget(SubCategory, field='title'), attribute='subcategories')

    class Meta:
        model = Item


class ItemImageResource(resources.ModelResource):
    class Meta:
        model = ItemImage


class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category


class SubCategoryResource(resources.ModelResource):
    categories = fields.Field(widget=ManyToManyWidget(Category, field='title'), attribute='categories')

    class Meta:
        model = SubCategory
        # fields = ('id', 'title', 'slug', 'categories',)


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'phone_number', 'wholesaler', 'is_staff', 'is_active',)
    list_filter = ('is_staff', 'is_active',)
    readonly_fields = ['last_login', 'date_joined']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser')}),
        ('Profile', {'fields': ('first_name', 'last_name', 'phone_number',)}),
        ('Wholesaler', {'fields': ('wholesaler',)}),
        ('Details', {'fields': ('last_login', 'date_joined',)})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)


class ItemImageInline(admin.StackedInline):
    model = ItemImage


class ItemAdmin(ImportExportModelAdmin):
    resource_class = ItemResource
    search_fields = ['title', 'item_code', 'id']
    actions = ['change_avaliability_true', 'change_avaliability_false']
    list_filter = ['availability', 'add_date', 'subcategories', 'categories']
    list_display = ('id', 'item_code', 'title', 'description', 'price', 'availability', 'add_date')
    readonly_fields = ['image_preview']
    inlines = (ItemImageInline,)

    def image_preview(self, obj):
        return mark_safe('<img src="{url}" height="200px" />'.format(
            url=obj.image.url,
        ))

    def change_avaliability_true(self, request, queryset):
        queryset.update(availability='1')
    change_avaliability_true.short_description = 'Змінити статус на "Є в наявності"'

    def change_avaliability_false(self, request, queryset):
        queryset.update(availability='0')
    change_avaliability_false.short_description = 'Змінити статус на "Немає в наявності"'


@admin.register(ItemImage)
class ItemImageAdmin(ImportExportModelAdmin):
    actions = ['change_default_status_true', 'change_default_status_false']

    list_display = ('item', 'image', 'default')

    def change_default_status_true(self, request, queryset):
        queryset.update(default=True)
    change_default_status_true.short_description = 'Використовувати за замовчуванням'

    def change_default_status_false(self, request, queryset):
        queryset.update(default=True)
    change_default_status_false.short_description = 'Не використовувати за замовчуванням'


class CategoryAdmin(ImportExportModelAdmin):
    search_fields = ['title']
    resource_class = CategoryResource
    list_display = ('id', 'title', 'slug')
    # prepopulated_fields = {'slug': ['title']}


class SubCategoryAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    resource_class = SubCategoryResource
    search_fields = ['title']
    list_display = ('id', 'title', 'image', 'slug')
    filter_horizontal = ['categories']
    list_filter = ['categories']
    # prepopulated_fields = {'slug': ['title']}


class OrderInline(admin.StackedInline):
    model = Order


class CartAdmin(ImportExportModelAdmin):
    resource_class = CartResource
    inlines = (OrderInline,)
    search_fields = ['id']
    list_display = ('id', 'user', 'start_date', 'ordered', 'order_status')
    filter_horizontal = ['items']
    list_filter = ['ordered', 'order_status']


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(CartItem)
admin.site.register(Cart, CartAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
