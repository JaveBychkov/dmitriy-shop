import pytest

from django.urls import reverse
from django.utils import translation

from orders.models import Order


@pytest.mark.django_db
def test_login_required_to_view_history(client):
    with translation.override('en'):
        response = client.get(reverse('order-history'), follow=True)

    assert response.status_code == 200
    assert 'Please login' in response.content.decode('utf-8')


@pytest.mark.django_db
def test_user_orders_in_context(client, admin_user):
    client.force_login(admin_user)
    response = client.get(reverse('order-history'))

    assert response.context.get('orders') is not None
    assert len(response.context['orders']) == 0


@pytest.mark.django_db
def test_pagination_returns_results(client, admin_user):
    client.force_login(admin_user)

    orders = [Order(user=admin_user) for i in range(6)]  # Create six orders.
    Order.objects.bulk_create(orders)

    response = client.get(reverse('order-history'))
    assert len(response.context['orders']) == 3
    ids_page1 = set([item.pk for item in response.context['orders']])

    url = '{}?page=2'.format(reverse('order-history'))
    response = client.get(url)

    assert len(response.context['orders']) == 3
    ids_page2 = set([item.pk for item in response.context['orders']])

    # Set intersection should be empty.
    assert ids_page1 & ids_page2 == set()

    paginator = response.context['orders'].paginator

    assert paginator.num_pages == 2
    assert paginator.count == 6
