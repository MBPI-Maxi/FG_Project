from django.views.generic.edit import CreateView
from django.views.generic import ListView
from django.contrib import messages
from django.urls import reverse_lazy
from incoming_fg_app.views.filters import EndorsementT1Filter
from incoming_fg_app.models import EndorsementT1
from incoming_fg_app.forms import EndorsementT1Form
from django.core.paginator import Paginator

class EndorsementT1CV(CreateView):
    model = EndorsementT1
    form_class = EndorsementT1Form
    template_name = "incoming_fg_app/endorsement/endorsementT1/form.html"
    success_url = reverse_lazy("endorsement:create")  # using the namespace then the name

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Entry successfully created.")
        
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = self.get_form()
        
        # remove the t_wtlot so that it will not render on the html
        form.fields.pop("t_wtlot", None)

        endorsements_qs = EndorsementT1.objects.all().order_by("-created_at")
        paginator = Paginator(endorsements_qs, 10)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context["endorsements"] = page_obj.object_list
        context["page_obj"] = page_obj
        context["paginator"] = paginator

        context["title"] = "Create Endorsement"
        context["field_with_labels"] = zip(
            form.visible_fields(), 
            self.generate_context_labels(form)
        )
        
        return context

    def generate_context_labels(self, form):
        context_list = [
            "Reference No",
            "Date Endorsed",
            "Production Date",
            "Category",
            "Production Code",
            "Lot no. Whole",
            "QTY KG",
            # "Weight Lot",
            "Endorsed By",
            "Status",
            "Location",
        ]

        if len(form.fields) == len(context_list):
            return context_list
        
        raise ValueError("Context List is not the same length in fields of form.")

class EndorsementT1LV(ListView):
    model = EndorsementT1
    template_name = "incoming_fg_app/endorsement/endorsementT1/list.html"
    context_object_name = "endorsements"  # name of the variable that will be available in the django template
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "List of Endorsements"
        context["filterset"] = self.filterset

        unwanted_fields = ["t_date_endorsed", "t_prod_date"]
        context["visible_fields"] = [
            field for field in self.filterset.form.visible_fields()
            if field.name not in unwanted_fields
        ]

        return context

    def get_queryset(self):
        """
        The - (minus sign) in Django's .order_by() means descending order.
        
        So:
            - order_by("created_at") → Oldest first
            - order_by("-created_at") → Newest first
        """
        
        queryset = super().get_queryset().order_by("-created_at")
        
        self.filterset = EndorsementT1Filter(self.request.GET, queryset)
        
        return self.filterset.qs
