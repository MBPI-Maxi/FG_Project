from django import forms
from incoming_fg_app.models import EndorsementT1, EndorsementT2
import re
# from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP
from incoming_fg_app.helpers.helper import lot_str_to_value

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
            "t_lotnumberwhole": forms.TextInput(
                attrs={
                    "placeholder": "8888AA-9999AA",
                    "pattern": r"\d{4}[A-Z]{2}-\d{4}[A-Z]{2}",
                    "title": "Format: 8888AA-9999AA",
                    "class": "italic-placeholder"
                }
            ),
            "t_prodcode": forms.TextInput(
                attrs={
                    "title": "16-digit code",
                    "placeholder": "16-digit code",
                    "class": "italic-placeholder"
                }
            ),
            "t_refno": forms.TextInput(
                attrs={
                    "placeholder": "Must be 7 numbers",
                    "title": "Must be 7 numbers",
                    "class": "italic-placeholder"
                }
            ),
            "t_wtlot": forms.HiddenInput(),
        }

    def clean_t_prodcode(self):
        prodcode = self.cleaned_data.get("t_prodcode")
        valid_length = 16

        if prodcode and len(prodcode) < valid_length:
            raise forms.ValidationError(
                "Production code should be at least 16-character product code matching master data"
            )

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

    # def clean_t_lotnumberwhole(self):
    #     lot_range = self.cleaned_data.get("t_lotnumberwhole")

    #     if not re.fullmatch(r"\d{4}[A-Z]{2}-\d{4}[A-Z]{2}", str(lot_range)):
    #         raise forms.ValidationError("Lot range must be in the format 8888AA-9999AA")

    #     return lot_range

    def clean_t_lotnumberwhole(self):
        value = self.cleaned_data.get("t_lotnumberwhole")
        pattern = r"^(\d{4})([A-Z]{2})-(\d{4})([A-Z]{2})$"
        match = re.fullmatch(pattern, value)

        if not match:
            raise forms.ValidationError("Lot number must follow the format 8888AA-9999AA")

        num1, let1, num2, let2 = match.groups()

        def lot_to_value(num, letters):
            letter_value = (ord(letters[0]) - ord("A")) * 26 + (ord(letters[1]) - ord("A"))
            return int(num) * 1000 + letter_value
        
        start_value = lot_to_value(num1, let1)
        end_value = lot_to_value(num2, let2)
        MAX_VALUE = 9999 * 1000 + (25 * 26 + 25)  # 9999ZZ max value

        lot_diff = (end_value - start_value + MAX_VALUE) % MAX_VALUE

        if lot_diff == 0:
            raise forms.ValidationError("Start and end lot cannot be the same")

        return value

    def clean_t_qtykg(self):
        qty = self.cleaned_data.get("t_qtykg")

        if qty < 0 and qty is not None:
            raise forms.ValidationError("Quantity (kg) must be a positive number")

        return qty

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


    def clean(self):
        cleaned_data = super().clean()
        prod_date = cleaned_data.get("t_prod_date")
        endorsed_date = cleaned_data.get("t_date_endorsed")

        lot_range = cleaned_data.get("t_lotnumberwhole")
        qty_kg = cleaned_data.get("t_qtykg")

        if prod_date and endorsed_date and prod_date > endorsed_date:
            self.add_error(
                "t_prod_date",
                "Prod date must be less than or equal to the endorsed date.",
            )
        
        # during this process the weight will be auto filled based on the lot range
        if lot_range and qty_kg:
            try:
                start_lot_num, end_lot_num  = lot_range.split("-")

                start_val = lot_str_to_value(start_lot_num)
                end_val = lot_str_to_value(end_lot_num)
                num_lots = (end_val - start_val) + 1 # +1 because the value is inclusive

                wtlot = (Decimal(str(qty_kg)) / Decimal(str(num_lots))).quantize(
    Decimal("0.00"),  # Ensures 2 decimal places
    rounding=ROUND_HALF_UP  # Standard rounding (e.g., 1.235 → 1.24)
)
                cleaned_data["t_wtlot"] = wtlot # reassign the value here

            except ValueError as e:
                print(f"Error has occur: {e}")
                raise forms.ValidationError("Error computing the wtlot value")
        
        return cleaned_data
            
class EndorsementT2Form(forms.ModelForm):
    class Meta:
        model = EndorsementT2

        fields = ["t_refno", "t_lotnumbersingle", "t_qty"]
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
        # t_encodedon = cleaned_data.get("t_encodedon")
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

