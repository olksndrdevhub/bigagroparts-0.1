from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from core.models import Item, Category, SubCategory, Cart, CartItem, ItemImage
from django.contrib import messages
from parts_shop.forms import EditUserInfoForm
from checkout.models import Order
from django.contrib.auth import get_user
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required


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


def add_to_cart(request, slug):
    cart_id = request.session.get('cart_id')
    item = get_object_or_404(Item, slug=slug)
    ordered_date = timezone.now()

    if request.user.is_authenticated:
        cart_qs = Cart.objects.filter(user=request.user, ordered=False)
        cart_item, created = CartItem.objects.get_or_create(
            item=item,
            user=request.user,
            ordered=False)
        if request.user.wholesaler:
            cart_item.item_price = item.wholesaler_price
        else:
            cart_item.item_price = item.price
    else:
        cart_qs = Cart.objects.filter(id=cart_id, ordered=False)
        if not cart_qs.exists():
            cart = Cart.objects.create(ordered_date=ordered_date)
            cart_id = cart.id
        cart_item, created = CartItem.objects.get_or_create(
            cart_id=cart_id,
            item=item,
            ordered=False)
        cart_item.item_price = item.price
    cart_item.save()

    if cart_qs.exists():
        cart = cart_qs[0]
        # check if order item is in the order
        if cart.items.filter(item__slug=item.slug).exists():
            cart_item.quantity += 1
            cart_item.save()
            messages.info(request, _('Додано ще одну одиницю товару в кошик!'))
            return redirect(request.META['HTTP_REFERER'])
        else:
            messages.info(request, _('Цей товар додано у кошик!'))
            cart_item.cart_id = cart.id
            cart_item.save()
            cart.items.add(cart_item)
            return redirect(request.META['HTTP_REFERER'])
    else:
        if request.user.is_authenticated:
            cart = Cart.objects.create(user=request.user, ordered_date=ordered_date)
        
        request.session['cart_id'] = cart.id
        cart_item.cart_id = cart.id
        cart_item.save()
        cart.items.add(cart_item)
        messages.info(request, _('Цей товар додано у кошик!'))
        return redirect(request.META['HTTP_REFERER'])


def remove_from_cart(request, slug):
    cart_id = request.session.get('cart_id')
    item = get_object_or_404(Item, slug=slug)
    cart_qs = Cart.objects.filter(id=cart_id, ordered=False)
    if cart_qs.exists():
        cart = cart_qs[0]
        # check if order item is in the order
        if cart.items.filter(item__slug=item.slug).exists():
            cart_item = CartItem.objects.filter(
                item=item,
                cart_id=cart_id,
                ordered=False
            )[0]
            cart.items.remove(cart_item)
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



def remove_single_item_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    cart_id = request.session.get('cart_id')
    cart_qs = Cart.objects.filter(id=cart_id, ordered=False)
    if cart_qs.exists():
        cart = cart_qs[0]
        # check if order item is in the order
        if cart.items.filter(item__slug=item.slug).exists():
            cart_item = CartItem.objects.filter(
                item=item,
                cart_id=cart_id,
                ordered=False
            )[0]
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart.items.remove(cart_item)
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

@login_required
def edit_account(request):
    user = get_user(request)
    saved_address = Order.objects.filter(user=user).last()
    print(saved_address)
    edit = True
    form1 = EditUserInfoForm(initial={
        'first_name': user.first_name,
        'second_name': user.second_name,
        'last_name': user.last_name,
        'email': user.email,
        'phone_number': user.phone_number})


    if request.method == 'POST':
        form1 = EditUserInfoForm(request.POST, initial={
            'first_name': user.first_name,
            'second_name': user.second_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone_number': user.phone_number
        })

        if form1.is_valid():
            user.first_name = form1.cleaned_data['first_name']
            user.second_name = form1.cleaned_data['second_name']
            user.last_name = form1.cleaned_data['last_name']
            user.email = form1.cleaned_data['email']
            user.phone_number = form1.cleaned_data['phone_number']
            user.save()

        return redirect('core:my_cabinet')

    return render(request, 'cabinet.html', context={'form1': form1, 'edit': edit})
