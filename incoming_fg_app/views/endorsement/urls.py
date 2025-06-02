from django.urls import path
from incoming_fg_app.views import EndorsementT1CV, EndorsementT1LV

app_name = "endorsement"

urlpatterns = [
    path("create", EndorsementT1CV.as_view(), name="create"),
    path("list", EndorsementT1LV.as_view(), name="list"),
]