import django_filters
from django.forms.widgets import NumberInput, DateInput, TextInput
from incoming_fg_app.models import EndorsementT1 

class EndorsementT1Filter(django_filters.FilterSet):
    # Filter by Reference Number (exact match for IntegerField)
    # Since t_refno is an IntegerField, a CharFilter with exact lookup works well for a precise search.
    # If you wanted to search for "contains" within a string representation of the number, you'd convert it to CharField for filtering.
    t_refno = django_filters.NumberFilter(
        label='Reference No. (Exact Match)',
        widget=NumberInput(attrs={'placeholder': 'e.g., 1234567'})
    )

    # Filter by Date Endorsed (range)
    # Using 'gte' (greater than or equal) and 'lte' (less than or equal) for date ranges.
    # The DateInput widget ensures an HTML5 date picker if supported by the browser.
    t_date_endorsed__gte = django_filters.DateFilter(
        field_name='t_date_endorsed',
        lookup_expr='gte',
        label='Date Endorsed (From)',
        widget=DateInput(attrs={'type': 'date'})
    )
    t_date_endorsed__lte = django_filters.DateFilter(
        field_name='t_date_endorsed',
        lookup_expr='lte',
        label='Date Endorsed (To)',
        widget=DateInput(attrs={'type': 'date'})
    )

    # Filter by Production Date (range)
    t_prod_date__gte = django_filters.DateFilter(
        field_name='t_prod_date',
        lookup_expr='gte',
        label='Prod Date (From)',
        widget=DateInput(attrs={'type': 'date'})
    )
    t_prod_date__lte = django_filters.DateFilter(
        field_name='t_prod_date',
        lookup_expr='lte',
        label='Prod Date (To)',
        widget=DateInput(attrs={'type': 'date'})
    )

    # Filter by Category (using model's choices)
    t_category = django_filters.ChoiceFilter(
        choices=EndorsementT1.t_category.field.choices, # Access choices directly from the model field
        empty_label="All Categories",
        label='Category'
    )

    # Filter by Product Code (case-insensitive contains)
    t_prodcode = django_filters.CharFilter(
        lookup_expr='icontains', # 'i' for case-insensitive
        label='Product Code (contains)',
        widget=TextInput(attrs={'placeholder': 'e.g., ABC123DEF456789'})
    )

    # Filter by Lot Number Range (case-insensitive contains)
    t_lotnumberwhole = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Lot Number (contains)',
        widget=TextInput(attrs={'placeholder': 'e.g., 8888AA-9999AA'})
    )
    
    # Filter by Status (using model's choices)
    t_status = django_filters.ChoiceFilter(
        choices=EndorsementT1.t_status.field.choices, # Access choices directly from the model field
        empty_label="All Statuses",
        label='Status'
    )

    # Filter by Location (using model's choices)
    t_loc = django_filters.ChoiceFilter(
        choices=EndorsementT1.t_loc.field.choices, # Access choices directly from the model field
        empty_label="All Locations",
        label='Location'
    )

    # Filter by Endorsed By (case-insensitive contains)
    t_endorsedby = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Endorsed By (contains)',
        widget=TextInput(attrs={'placeholder': 'e.g., John Doe'})
    )

    class Meta:
        model = EndorsementT1
        fields = [
            't_refno',
            't_date_endorsed',
            't_prod_date',
            't_category',
            't_prodcode',
            't_lotnumberwhole',
            't_status',
            't_loc',
            't_endorsedby',
            # Note: t_qtykg and t_wtlot are DecimalFields. While you *can* filter
            # them (e.g., t_qtykg__gte, t_qtykg__lte for ranges), they might be less
            # commonly used for direct search in a simple list filter.
            # If needed, you would add:
            # 't_qtykg',
            # 't_wtlot',
        ]