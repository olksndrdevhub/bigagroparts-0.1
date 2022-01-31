from django.conf import settings
from django.urls import reverse
from django.db import models
from autoslug import AutoSlugField
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
import re
from django.utils.translation import gettext as _
from phonenumber_field.modelfields import PhoneNumberField


def slugify(s):
    pattern = r'[^\w+]'
    return re.sub(pattern, '-', s)


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):

    first_name = models.CharField(max_length=150, blank=False, verbose_name="Ім'я")
    second_name = models.CharField(max_length=150, blank=True, null=True, verbose_name=_("Ім'я по батькові"))
    last_name = models.CharField(max_length=150, blank=False)
    email = models.EmailField(_('email address'), unique=True)
    phone_number = PhoneNumberField(verbose_name='Phone Number', help_text=_("Має починатися з +380"), blank=True, null=True)
    # company = models.CharField(verbose_name='Компанія, яку представляє', max_length=150, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True, editable=True)
    wholesaler = models.BooleanField(default=False, verbose_name='Статус оптовика')

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    class Meta:
        verbose_name = _("Користувач")
        verbose_name_plural = _("Користувачі")

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class Category(models.Model):
    title = models.CharField(max_length=100, null=True)
    image = models. ImageField(verbose_name='Фото категорії', upload_to='uploads/category_images', default='None/category.jpg', blank=True, null=True)
    slug = AutoSlugField(populate_from='title',
                         unique=True,
                         allow_unicode=True,
                         max_length=200,
                         null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})

    class Meta:
        verbose_name_plural = "Категорії"
        ordering = ('id',)


class SubCategory(models.Model):
    title = models.CharField(max_length=200)
    image = models. ImageField(verbose_name='Фото підкатегорії', upload_to='uploads/sub_category_images', default='None/subcategory.jpg', blank=True, null=True)
    slug = AutoSlugField(populate_from='title',
                         unique=True,
                         allow_unicode=True,
                         max_length=200,
                         null=True)
    categories = models.ManyToManyField(Category)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('subcategory_detail', kwargs={'slug': self.slug})

    class Meta:
        verbose_name_plural = "Підкатегорії"
        ordering = ('title',)


class Item(models.Model):

    AVAILABLE = '1'
    NOT_AVAILABLE = '0'
    NEED_TO_CHECK = '2'

    AVAILABILITY_CHOICES = (
        (AVAILABLE, _('Є в наявності')),
        (NOT_AVAILABLE, _('Немає в наявності')),
        (NEED_TO_CHECK, _('Уточніть наявність'))
    )

    title = models.CharField(max_length=200, verbose_name='Назва')
    # image = models.ImageField(verbose_name='Фото деталі', upload_to='uploads/', default='/None/item.jpg', blank=True, null=True)
    item_code = models.CharField(max_length=100, blank=True, verbose_name='Артикул', null=True)
    description = models.CharField(max_length=1000, blank=True, null=True, verbose_name='Опис')
    price = models.FloatField(max_length=200, verbose_name='Ціна')
    availability = models.CharField(choices=AVAILABILITY_CHOICES, default=AVAILABLE, verbose_name='Наявність', max_length=20)
    wholesaler_price = models.FloatField(max_length=200, verbose_name='Оптова ціна')
    add_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата створення', null=True, blank=True)
    slug = AutoSlugField(populate_from='title',
                         unique=True,
                         max_length=200,
                         allow_unicode=True,
                         null=True)
    subcategories = models.ManyToManyField(SubCategory, blank=True)
    categories = models.ManyToManyField(Category, blank=True)

    class Meta:
        verbose_name_plural = 'Товари'
        ordering = ('title',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('item_detail', kwargs={'slug': self.slug})

    def get_add_to_card_url(self):
        return reverse('add_to_cart', kwargs={'slug': self.slug})

    def get_remove_from_card_url(self):
        return reverse('remove_from_cart', kwargs={'slug': self.slug})


class ItemImage(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    image = models.ImageField(verbose_name='Фото деталі', upload_to='uploads/', default='None/item.jpg', blank=True, null=True)
    default = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'Image #{self.id} for {self.item.title}'

    class Meta:
        verbose_name_plural = 'Фото товарів'


class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, verbose_name='Користувач', blank=True, null=True)
    cart_id = models.IntegerField(verbose_name='ID кошика', default=0)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name='Товар')
    item_price = models.FloatField(max_length=200, verbose_name='Вартість товару', blank=True, default=0.0)
    quantity = models.IntegerField(default=1, verbose_name='Кількість')
    ordered = models.BooleanField(default=False, verbose_name='Замовлення підтверджено')

    def __str__(self):
        return f'{self.quantity} of {self.item.title}'

    def get_total_item_price(self):
        return self.quantity * self.item_price

    def get_final_price(self):
        return self.get_total_item_price()

    class Meta:
        verbose_name_plural = "Товари в кошику"
        ordering = ('id',)


class Cart(models.Model):

    LEFTED_CART = 'LC'
    ORDER_ACCEPTED = 'OA'
    ORDER_IS_PROCESSED = 'OIP'
    ORDER_FULLFILED = 'OF'

    ORDER_STATUS_CHOICES = (
        (LEFTED_CART, _('Залишений кошик')),
        (ORDER_ACCEPTED, _('Замовлення прийнято')),
        (ORDER_IS_PROCESSED, _('Замовлення виконується')),
        (ORDER_FULLFILED, _('Замовлення виконано'))
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, verbose_name='Користувач', blank=True, null=True)
    items = models.ManyToManyField(CartItem, verbose_name='Товари')
    start_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата оформлення')
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False, verbose_name='Замовлення підтверджено')
    order_total_price = models.FloatField(max_length=200, verbose_name='Вартість замовлення', blank=True, default=0.0)
    order_status = models.CharField(choices=ORDER_STATUS_CHOICES, verbose_name=_('Статус замовлення'), default=LEFTED_CART, max_length=20)

    def __str__(self):
        return 'Кошик: ' + str(self.id)

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
            self.order_total_price = total
        return total

    def set_total(self):
        self.order_total_price = self.get_total()

    class Meta:
        verbose_name_plural = "Кошик"
