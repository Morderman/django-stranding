from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import ListView, DetailView, View
from .models import Item, OrderItem, Order
from .forms import CheckoutForm

'''
def item_list(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, "home.html", context)


def products(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, 'products.html', context)


def checkout(request):
    return render(request, 'ckeckout.html')


def home(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, "home.html", context)
'''


class HomeView(ListView):
    model = Item
    paginate_by = 10
    template_name = 'home.html'


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form':form,
                'order': order
            }
            return render(self.request, "checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("core:checkout")


    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        #print(self.request.POST)
        if form.is_valid():
            #print(form.cleaned_data)
            print('The form is valid!')
            return redirect("core:checkout")

        else:
            messages.warning(self.request, "Failed checkout")
            return redirect('core:checkout')




class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("/")


class ItemDetailView(DetailView):
    model = Item
    template_name = 'product.html'


@login_required()
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if order item is in order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity is updated.")
            return redirect("core:order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "This item is added to your cart.")
            return redirect("core:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item is added to your cart.")
        return redirect("core:order-summary")


@login_required()
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if order item is in order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, "This item is removed from your cart.")
            return redirect("core:order-summary")
        else:
            # add a message saying the order doesn't contain an item
            messages.info(request, "This item is not in your cart.")
            return redirect("core:product", slug=slug)
    else:
        # add a message saying the user doesn't have an order
        messages.info(request, "You don't have an active order.")
        return redirect("core:product", slug=slug)


@login_required()
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if order item is in order
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
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            # add a message saying the order doesn't contain an item
            messages.info(request, "This item is not in your cart.")
            return redirect("core:product", slug=slug)
    else:
        # add a message saying the user doesn't have an order
        messages.info(request, "You don't have an active order.")
        return redirect("core:product", slug=slug)





