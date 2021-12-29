from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import ListView, View
from .models import Category, SubCategory, Item, Order
from django.db.models import Q
from django.http import HttpResponse

import json

from checkout.models import BillingAddress


class HomeView(ListView):
    model = Category
    template_name = 'home-page.html'


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order,
            }
            return render(self.request, 'order-summary.html', context)
        except ObjectDoesNotExist:
            messages.info(self.request, 'Ви не маєте нічого в кошику!')
            return redirect('/')


def set_language(request):
    pass


def search_view(request):
    models = [Item, Category, SubCategory]
    template_name = 'home-page.html'
    query = request.POST.get('q')
    # print(query)
    # print('query: {}'.format(len(query)))
    if len(query):
        item_items = models[0].objects.filter(
            Q(title__icontains=query)
            | Q(item_code__icontains=query)
            | Q(description__icontains=query)
            | Q(id__icontains=query))
        category_items = models[1].objects.filter(
            Q(title__icontains=query)
        )
        subcategory_items = models[2].objects.filter(
            Q(title__icontains=query)
        )
        return render(request, template_name, context={'item_items': item_items, 'category_items': category_items, 'subcategory_items': subcategory_items, 'query': query})

    return redirect('/')


def autocomplete(request):
    if request.is_ajax():
        q = request.GET.get('term', '')
        search_qs = Item.objects.filter(Q(title__startswith=q) | Q(title__icontains=q) | Q(item_code__icontains=q) | Q(id__icontains=q))
        results = []
        # print(q)
        for r in search_qs:
            image = r.itemimage_set.filter(default=True).first()
            results.append({
                'value': r.title,
                'url': r.get_absolute_url(),
                'img': image.image.url,
                'price': r.price,
                'item_code': r.item_code,
                'item_id': r.id

            })
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


def contacts(request):
    # not_home=True
    return render(request, 'contacts.html')


def conditions(request):
    # not_home=True
    return render(request, 'conditions.html')


def specorder(request):
    # not_home=True
    return render(request, 'specorder.html')


def my_cabinet(request):
    # not_home=True
    user = get_user(request)
    address = BillingAddress.objects.filter(user=user).last()
    orders = Order.objects.filter(user=user, ordered=True).all().order_by('-ordered_date')
    return render(request, 'cabinet.html', context={'address': address, 'orders': orders})
