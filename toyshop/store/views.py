from django.shortcuts import render, redirect, get_object_or_404
from .models import Product,Category
from django.http import JsonResponse
from .models import Product, Order, OrderItem
from .forms import PlaceOrderForm



def product_list(request):
    category_id = request.GET.get('category')  # Get the category from the query parameter
    if category_id:
        category = get_object_or_404(Category, id=category_id)
        products = Product.objects.filter(category=category)
    else:
        products = Product.objects.all()

    categories = Category.objects.all()  # Fetch all categories for the dropdown
    return render(request, 'store/product_list.html', {
        'products': products,
        'categories': categories,
    })



def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    if request.method == 'POST':
        # Retrieve the cart from the session (or initialize it if it doesn't exist)
        cart = request.session.get('cart', {})

        # Check if the product is already in the cart
        if str(product_id) in cart:  # Ensure product_id is a string since session stores keys as strings
            # If the product is already in the cart, increase the quantity by 1
            cart[str(product_id)] += 1
        else:
            # If the product is not in the cart, add it with quantity 1
            cart[str(product_id)] = 1

        # Save the updated cart in the session
        request.session['cart'] = cart
        request.session.modified = True  # Mark the session as modified

        # Provide feedback to the user
        message = f"{product.name} has been added to your cart."
        return render(request, 'store/product_detail.html', {'product': product, 'message': message})

    return render(request, 'store/product_detail.html', {'product': product})



def cart_view(request):
    # Get the cart from the session
    cart_items = request.session.get('cart', {})
    products_in_cart = []
    total_price = 0

    # Loop through cart items and get the product details
    for product_id, quantity in cart_items.items():
        product = get_object_or_404(Product, pk=product_id)
        item_total = product.price * quantity  # Calculate total for this item
        total_price += item_total  # Add the item's total to the total price
        products_in_cart.append({'product': product, 'quantity': quantity, 'item_total': item_total})

    return render(request, 'store/cart.html', {'products_in_cart': products_in_cart, 'total_price': total_price})

def update_cart(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})

        # Loop through all form inputs to update quantities or remove items
        for key, value in request.POST.items():
            # Check if the key is related to updating the quantity
            if key.startswith('quantity_'):
                product_id = key.split('_')[1]  # Extract product ID from the form field name
                try:
                    quantity = int(value)
                    if quantity > 0:
                        cart[product_id] = quantity  # Update the quantity in the cart
                    else:
                        del cart[product_id]  # If quantity is 0 or less, remove the product from the cart
                except ValueError:
                    continue  # If the quantity is not a valid number, skip

            # Check if the key is related to removing an item from the cart
            elif key.startswith('remove_'):
                product_id = key.split('_')[1]  # Extract product ID
                if product_id in cart:
                    del cart[product_id]  # Remove the product from the cart

        # Save the updated cart in the session
        request.session['cart'] = cart
        request.session.modified = True  # Mark the session as modified

        # Redirect back to the cart page to reflect changes
        return redirect('cart_view')

    # If the method is not POST, redirect to cart view
    return redirect('cart_view')




def place_order(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('cart_view')  # Redirect to cart if empty

    if request.method == 'POST':
        form = PlaceOrderForm(request.POST)
        if form.is_valid():
            # Save the order
            order = form.save()

            # Save each cart item as an OrderItem
            for product_id, quantity in cart.items():
                product = Product.objects.get(id=product_id)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price,
                )

            # Clear the cart after order placement
            request.session['cart'] = {}

            # Redirect to order confirmation page
            return redirect('order_confirmation', order_id=order.id)

    else:
        form = PlaceOrderForm()

    # Pass cart summary to the template
    cart_items = []
    total_price = 0
    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        total_price += product.price * quantity
        cart_items.append({'product': product, 'quantity': quantity, 'total': product.price * quantity})

    return render(request, 'store/place_order.html', {
        'form': form,
        'cart_items': cart_items,
        'total_price': total_price,
    })


def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = order.items.all()  # Use related_name to get order items
    total_price = sum(item.price * item.quantity for item in order_items)  # Calculate total price

    return render(
        request,
        'store/order_confirmation.html',
        {
            'order': order,
            'order_items': order_items,
            'total_price': total_price,
        },
    )


def track_order(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        order_id = request.POST.get('order_id')

        try:
            # Fetch the order based on email and order ID
            order = Order.objects.get(user_email=email, id=order_id)

            # Fetch the items associated with this order
            order_items = OrderItem.objects.filter(order=order)

            # Calculate the total price of the order
            total_price = sum(item.price * item.quantity for item in order_items)

            return render(request, 'store/track_order.html', {
                'order': order,
                'order_items': order_items,
                'total_price': total_price,
            })
        except Order.DoesNotExist:
            return render(request, 'store/track_order.html', {
                'error': 'Order not found!',
            })

    return render(request, 'store/track_order.html')
