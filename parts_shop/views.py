from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from core.models import Item, Category, SubCategory, Order, OrderItem, ItemImage
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from parts_shop.forms import EditUserInfoForm, EditBillingAddressForm
from checkout.models import BillingAddress
from django.contrib.auth import get_user
from django.utils.translation import gettext as _


def category_detail(request, slug):
    category = Category.objects.get(slug=slug)
    categories = Category.objects.all()
    items = category.item_set.all()
    subcategories = category.subcategory_set.all()
    return render(request, 'category-detail.html', context={'category': category, 'subcategories': subcategories, 'items': items, 'categories': categories})


def subcategory_detail(request, slug):
    subcategory = SubCategory.objects.get(slug=slug)
    categories = Category.objects.all()
    items = subcategory.item_set.all()
    return render(request, 'subcategory-detail.html', context={'items': items, 'subcategory': subcategory, 'categories': categories})


def item_detail(request, slug):
    item = Item.objects.get(slug=slug)
    not_home = True
    item_images = ItemImage.objects.filter(item=item).all()
    print(item_images)
    category = item.categories.first()
    subcategory = item.subcategories.first()
    if category is not None:
        last_items = category.item_set.order_by('?')[:4]
    else:
        last_items = subcategory.item_set.order_by('?')[:4]

    return render(request, 'product-page.html', context={'item': item, 'item_images': item_images, 'category': category, 'subcategory': subcategory, 'last_items': last_items, 'not_home': not_home})


@login_required
def add_to_card(request, slug):
    print(request)
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, _('Додано ще одну одиницю товару в кошик!'))
            return redirect(request.META['HTTP_REFERER'])
        else:
            messages.info(request, _('Цей товар додано у кошик!'))
            order.items.add(order_item)
            return redirect(request.META['HTTP_REFERER'])
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, _('Цей товар додано у кошик!'))
        return redirect(request.META['HTTP_REFERER'])


@login_required
def remove_from_card(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, _('Цей товар видалено з кошика!'))
            return redirect('core:order-summary')
        else:
            # add a message that order doesn`t contain the item
            messages.info(request, _('Цього товару нема у вашому кошику!'))
            return redirect('item_detail', slug=slug)
    else:
        # add a message that user doesn`t have a order
        messages.info(request, _('Ви ще не маєте нічого в кошику!'))
        return redirect('item_detail', slug=slug)


@login_required
def remove_single_item_card(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, _('Мінус одна одиниця товару!'))
            return redirect('core:order-summary')
        else:
            # add a message that order doesn`t contain the item
            messages.info(request, _('Цього товару нема у вашому кошику!'))
            return redirect('core:order-summary')
    else:
        # add a message that user doesn`t have a order
        messages.info(request, _('Ви ще не маєте нічого в кошику!'))
        return redirect('core:order-summary')


def edit_account(request):
    user = get_user(request)
    saved_address = BillingAddress.objects.filter(user=user).last()
    print(saved_address)
    edit = True
    form1 = EditUserInfoForm(initial={
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'phone_number': user.phone_number})
    # form2 = EditBillingAddressForm(initial={
    #         'address': saved_address.address,
    #         'nova_poshta': saved_address.nova_poshta,
    #         'city': saved_address.city,
    #         'landmark': saved_address.landmark,
    #         'country': saved_address.country
    #     })

    if request.method == 'POST':
        form1 = EditUserInfoForm(request.POST, initial={
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone_number': user.phone_number
        })
        # form2 = EditBillingAddressForm(request.POST, initial={
        #     'address': saved_address.address,
        #     'nova_poshta': saved_address.nova_poshta,
        #     'city': saved_address.city,
        #     'landmark': saved_address.landmark,
        #     'country': saved_address.country
        # })
        if form1.is_valid():
            user.first_name = form1.cleaned_data['first_name']
            user.last_name = form1.cleaned_data['last_name']
            user.email = form1.cleaned_data['email']
            user.phone_number = form1.cleaned_data['phone_number']
            user.save()
            # saved_address = BillingAddress.objects.filter(user=request.user)
            # if saved_address.exists():
            #     print('exist')
            #     billingaddress = form2.save(commit=False)
            #     billingaddress.user = request.user
            #     billingaddress.save()
            # else:
            #     billingaddress = form2.save(commit=False)
            #     billingaddress.user = request.user
            #     billingaddress.save()
        return redirect('core:my_cabinet')

    return render(request, 'cabinet.html', context={'form1': form1, 'edit': edit})
