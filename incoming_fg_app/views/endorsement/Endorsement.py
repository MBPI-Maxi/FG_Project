from django.views.generic.edit import CreateView
from django.views.generic import ListView
from django.urls import reverse_lazy
from incoming_fg_app.models import EndorsementT1
from incoming_fg_app.forms import EndorsementT1Form

class EndorsementT1CV(CreateView):
    model = EndorsementT1
    form_class = EndorsementT1Form
    template_name = "incoming_fg_app/endorsement/endorsementT1/form.html"
    success_url = reverse_lazy("endorsement:list") # using the namespace then the name 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = self.get_form()

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
            "Passedbeg ID",
            "Lot no. Whole",
            "QTY KG",
            "Weight Lot",
            "Endorsed By",
            "Status",
            "Location"
        ]

        if len(form.fields) == len(context_list):
            return context_list

        raise ValueError("Context List is not the same length in fields of form.")
    
class EndorsementT1LV(ListView):
    model = EndorsementT1
    template_name = "incoming_fg_app/endorsement/endorsementT1/list.html"
    context_object_name = "endorsements" # name of the variable that will be available in the django template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "List of Endorsements"

        return context
