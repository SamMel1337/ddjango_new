import django_filters
from .models import Payment

class PaymentFilter(django_filters.FilterSet):
    date_of_payment = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Payment
        fields = []