from django import forms
from incoming_fg_app.models import EndorsementT1, EndorsementT2
import re
from datetime import timedelta

class EndorsementT1Form(forms.ModelForm):
    class Meta:
        model = EndorsementT1
        fields = [
            "t_refno",
            "t_date_endorsed",
            "t_prod_date",
            "t_category",
            "t_prodcode",
            "t_lotnumberwhole",
            "t_qtykg",
            "t_wtlot",
            "t_endorsedby",
            "t_status",
            "t_loc",
        ]

        widgets = {
            "t_date_endorsed": forms.DateInput(
                attrs={
                    "type": "date",
                    "id": "endorse-date-form",
                    "placeholder": "YYYY-MM-DD",
                }
            ),
            "t_prod_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "id": "endorse-prod-date-form",
                    "placeholder": "YYYY-MM-DD",
                }
            ),
        }

    def clean_t_prodcode(self):
        prodcode = self.cleaned_data.get("t_prodcode")
        valid_length = 16

        if prodcode and len(prodcode) < valid_length:
            raise forms.ValidationError("Production code should be at least 16-character product code matching master data")

        return prodcode

    def clean_t_refno(self):
        refno = self.cleaned_data.get("t_refno")

        if not re.fullmatch(r"\d{7}", str(refno)):
            raise forms.ValidationError("Reference number must be exactly 7 digits")

        return refno

    def clean_t_category(self):
        category = self.cleaned_data.get("t_category")

        if category not in ("MB", "DC"):
            raise forms.ValidationError("Category should be 'MB' or 'DC'")

        return category

    def clean_t_lotnumberwhole(self):
        lot_range = self.cleaned_data.get("t_lotnumberwhole")

        if not re.fullmatch(r"\d{4}[A-Z]{2}-\d{4}[A-Z]{2}", str(lot_range)):
            raise forms.ValidationError("Lot range must be in the format 8888AA-9999AA")

        return lot_range

    def clean_t_qtykg(self):
        qty = self.cleaned_data.get("t_qtykg")

        if qty < 0 and qty is not None:
            raise forms.ValidationError("Quantity (kg) must be a positive number")

        return qty

    def clean_t_wtlot(self):
        wt = self.cleaned_data.get("t_wtlot")

        if wt < 0 and wt is not None:
            raise forms.ValidationError("Weight per lot must be a positive number")

        return wt

    def clean_t_endorsedby(self):
        endorsed_by = self.cleaned_data.get("t_endorsedby")

        if endorsed_by and len(endorsed_by) < 3:
            raise forms.ValidationError("Endorsedby must be at least 3 characters long")

        return endorsed_by

    def clean_t_status(self):
        status = self.cleaned_data.get("t_status")

        if status not in ("Passed", "Failed"):
            raise forms.ValidationError("Status must be either 'Passed' or 'Failed'")

        return status

    def clean_t_loc(self):
        loc = self.cleaned_data.get("t_loc")

        if loc not in ("W1", "W2", "W4", "W5"):
            raise forms.ValidationError(
                "Location must be either 'W1', 'W2', 'W4', or 'W5'"
            )

        return loc

    def clean_t_qty(self):
        qty = self.cleaned_data.get("t_qty")

        if qty is not None and qty < 0:
            raise forms.ValidationError("Quantity must be a positive number.")

        return qty

    def clean(self):
        cleaned_data = super().clean()
        prod_date = cleaned_data.get("t_prod_date")
        endorsed_date = cleaned_data.get("t_date_endorsed")

        if prod_date and endorsed_date and prod_date > endorsed_date:
            self.add_error(
                "t_prod_date",
                "Prod date must be less than or equal to the endorsed date.",
            )


class EndorsementT2Form(forms.ModelForm):
    class Meta:
        model = EndorsementT2

        fields = ["t_refno", "t_lotnumbersingle", "t_qty", "t_encodedon"]
        widgets = {
            "t_encodedon": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def clean_t_lotnumbersingle(self):
        lot_number_single = self.cleaned_data.get("t_lotnumbersingle")

        if not re.fullmatch(r"\d{4}[A-Z]{2}", lot_number_single or ""):
            raise forms.ValidationError("Lot number must be in the format 9999AA.")

        return lot_number_single

    def clean(self):
        cleaned_data = super().clean()

        t_refno = cleaned_data.get("t_refno")
        t_qty = cleaned_data.get("t_qty")
        t_encodedon = cleaned_data.get("t_encodedon")
        t_lotnumbersingle = cleaned_data.get("t_lotnumbersingle")

        # Check if lot is in range of parent's lot range
        if t_refno and t_lotnumbersingle:
            try:
                lot_start, lot_end = t_refno.t_lotnumberwhole.split("-")
                if not (lot_start <= t_lotnumbersingle <= lot_end):
                    self.add_error(
                        "t_lotnumbersingle",
                        "Lot number must fall within the parent's lot range.",
                    )
            except ValueError:
                self.add_error(
                    "t_refno",
                    "Invalid lot range format in parent (expected: 8888AA-9999AA).",
                )

        # Check if t_qty exceeds parent's t_qtykg
        if t_refno and t_qty is not None and t_qty > t_refno.t_qtykg:
            self.add_error(
                "t_qty", "Quantity cannot exceed the parent's total quantity (t_qtykg)."
            )

        # Check if encoded time is within 1 hour of parent's created_at
        if t_refno and t_encodedon:
            parent_created = t_refno.created_at
            
            if abs(t_encodedon - parent_created) > timedelta(hours=1):
                self.add_error(
                    "t_encodedon",
                    "Encoded time must be within 1 hour of the parent's creation time.",
                )
