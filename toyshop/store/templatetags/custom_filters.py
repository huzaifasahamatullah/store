from django import template

register = template.Library()

@register.filter
def sum_price(order_items):
    """
    Custom filter to sum up the total price of the order items.
    """
    return sum(item.price * item.quantity for item in order_items)
