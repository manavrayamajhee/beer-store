from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import requires_csrf_token
from django.urls import reverse
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from users.models import Profile
from storefront.models import Product

from cart.models import Order,Transaction,OrderItem
from cart.extras import generate_order_id


def Cart_Quantity(request):
    user_profile = get_object_or_404(Profile, user=request.user)
    order = OrderItem.objects.filter(owner=user_profile)
    if order.exists():
        subtotal=sum([item.total for item in order])
        cartq=round(sum([item.quantity for item in order]),0)
        
        request.session["subtotal"]=int(subtotal)
        request.session["num"]=int(cartq)

        context={
                'subtotal':subtotal,
                'cartQuantity':cartq
        }
        
        return context
    request.session["num"]=0   
    return 0

def get_OrderItem(request):
    user_profile = get_object_or_404(Profile, user=request.user)
    order = OrderItem.objects.filter(owner=user_profile)

    if order.exists():
        subtotal=sum([item.total for item in order])
        items_n=round(sum([item.quantity for item in order]),0)
        request.session["num"]=int(items_n)
        request.session.modified = True
        context={
                'order':order,
                'subtotal':subtotal,
                'items':items_n
        }
        return render(request, 'cart/order_summary_detail.html',context)
    else:
        messages.info(request, "Cart is Empty")
        return redirect(reverse('products')) 


@login_required
def add_to_order(request, **kwargs):
    data =  dict()
    user_profile = get_object_or_404(Profile, user=request.user)
    product = Product.objects.filter(id=kwargs.get('item_id', "")).first()
    qs=OrderItem.objects.filter(owner=user_profile,item=product).first()

    if qs:
        qs.quantity+=1
        if qs.quantity>1:
            qs.total=qs.quantity*product.price
        qs.save()
        data=Cart_Quantity(request)
        return JsonResponse(data) 
    
    OrderItem.objects.create(owner=user_profile,item=product,quantity=1,total=product.price)
    Cart_Quantity(request)#Set Quantity in session
    
    messages.info(request, "Item added to cart")
    
    data=Cart_Quantity(request)
    return JsonResponse(data)
    #return redirect(reverse('products'))#while rerouting its forgetting the page its coming for or the page context

@login_required
@requires_csrf_token
def ChangeQuantity(request,**kwargs):
    user_profile = get_object_or_404(Profile, user=request.user)
    product = Product.objects.filter(id=kwargs.get('item_id', "")).first()
    amount=kwargs.get('amount')
    qs=OrderItem.objects.filter(owner=user_profile,item=product).first()
    data =  dict()
    if qs:
        qs.quantity=amount
        if qs.quantity>=1:
            qs.total=qs.quantity*product.price
        qs.save()

        data=Cart_Quantity(request)

        return JsonResponse(data)
    data['message'] = 0
    return JsonResponse(data)

@login_required
def add_to_cart(request, **kwargs):
    # get the user profile
    user_profile = get_object_or_404(Profile, user=request.user)
    # filter products by id
    product = Product.objects.filter(id=kwargs.get('item_id', "")).first()
    user_order, status = Order.objects.get_or_create(owner=user_profile, is_ordered=False)
    
    if product in user_order.items.all():
        messages.info(request, 'One More item added to Cart')
        return redirect(reverse('products')) 
    # create order associated with the user
    
    user_order.items.add(product)
    if status:
        # generate a reference code
        user_order.ref_code=generate_order_id()
        user_order.save()

    # show confirmation message and redirect back to the same page
    messages.info(request, "Item added to cart")
    return redirect(reverse('order_summary'))

@login_required
def delete_from_cart(request,**kwargs):
    user_profile = get_object_or_404(Profile, user=request.user)
    # filter products by id
    product = Product.objects.filter(id=kwargs.get('item_id', "")).first()
    qs=OrderItem.objects.filter(owner=user_profile,item=product).first()
    if qs:
        qs.delete()
        if not OrderItem.objects.filter(owner=user_profile):
            Cart_Quantity(request) 
            messages.info(request, "Cart is Empty")
            return redirect(reverse('products'))
        else:
            messages.info(request, "Item deleted from Cart")
        return redirect(reverse('order_summary')) 


"""@login_required
def order_details(request, **kwargs):
    existing_order = get_OrderItem(request)
    context = {
        'order': existing_order
    }
    return render(request, 'cart/order_summary_detail.html', context)"""





def success(request, **kwargs):
    # a view signifying the transcation was successful
    return render(request, 'shopping_cart/purchase_success.html', {})