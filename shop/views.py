from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Product, Order, OrderItem
from django.views.decorators.http import require_POST

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    return render(request, 'shop/product/list.html', {
        'category': category,
        'categories': categories,
        'products': products
    })

def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    return render(request, 'shop/product/detail.html', {'product': product})

# Simple Cart Logic using Session
def get_cart(request):
    cart = request.session.get('cart', {})
    return cart

def cart_add(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)
    if product_id not in cart:
        cart[product_id] = {'quantity': 0, 'price': str(get_object_or_404(Product, id=product_id).price)}
    cart[product_id]['quantity'] += 1
    request.session['cart'] = cart
    return redirect('shop:cart_detail')

def cart_remove(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)
    if product_id in cart:
        del cart[product_id]
        request.session['cart'] = cart
    return redirect('shop:cart_detail')

def cart_detail(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    for product_id, item in cart.items():
        product = get_object_or_404(Product, id=product_id)
        item_total = float(item['price']) * item['quantity']
        cart_items.append({
            'product': product,
            'quantity': item['quantity'],
            'price': item['price'],
            'total_price': item_total
        })
        total_price += item_total
    return render(request, 'shop/cart/detail.html', {'cart_items': cart_items, 'total_price': total_price})

def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('shop:product_list')
    
    if request.method == 'POST':
        # Simple checkout - in real app, use a Form
        order = Order.objects.create(
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            email=request.POST.get('email'),
            address=request.POST.get('address'),
            postal_code=request.POST.get('postal_code'),
            city=request.POST.get('city'),
        )
        for product_id, item in cart.items():
            product = get_object_or_404(Product, id=product_id)
            OrderItem.objects.create(
                order=order,
                product=product,
                price=item['price'],
                quantity=item['quantity']
            )
        # Clear cart
        request.session['cart'] = {}
        return render(request, 'shop/order/created.html', {'order': order})
    
    return render(request, 'shop/order/checkout.html')
