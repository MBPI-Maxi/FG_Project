from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MinLengthValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import timedelta

class EndorsementT1(models.Model):
    class Meta:
        db_table = "incoming_endorsement_t1"

    t_id = models.AutoField(primary_key=True)
    t_refno = models.IntegerField(
        validators=[
            RegexValidator(
                regex=r"^\d{7}$",
                message="Reference number must be exactly 7 digits",
                code="invalid_refno",
            )
        ],
        help_text="Reference number must be exactly 7 digits",
        unique=True,
        null=False,
        blank=False
    )

    t_date_endorsed = models.DateField()
    t_prod_date = models.DateField(
        help_text="Prod date should be <= to the date endorsed"
    )

    t_category = models.CharField(
        max_length=5, choices=[("MB", "MB"), ("DC", "DC")], default="MB",
        help_text="MB:Masterbatch | DC:Dry Color"
    )

    t_prodcode = models.CharField(
        max_length=16,
        help_text="Must match 16-character format and exist in product master (Foreign key to master data)",
        null=False,
        blank=False
    )

    t_lotnumberwhole = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r"^\d{4}[A-Z]{2}-\d{4}[A-Z]{2}$",
                message="Lot range must be in the format 8888AA-9999AA",
                code="Lot range format mismatch (8888AA-9999AA)",
            )
        ],
    )

    t_qtykg = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal("0.00"))]
    )

    t_wtlot = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal("0.00"))],
        null=True,
        blank=True
    )

    t_endorsedby = models.CharField(
        max_length=100,
        validators=[
            MinLengthValidator(
                3, message="Endorsedby must be at least 3 characters long"
            )
        ],
    )

    t_status = models.CharField(
        max_length=10,
        choices=[("Passed", "Passed"), ("Failed", "Failed")],
        default="Passed",
    )

    t_loc = models.CharField(
        max_length=10,
        choices=[
            ("W1", "Warehouse 1"),
            ("W2", "Warehouse 2"),
            ("W4", "Warehouse 4"),
            ("W5", "Warehouse 5"),
        ],
        default="W1",
        help_text="W1:Warehouse1 | W2:Warehouse2 | W4:Warehouse4 | W5:Warehouse5"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Detail for Ref: {self.t_refno} | Lot: {self.t_lotnumberwhole}"


class EndorsementT2(models.Model):
    class Meta:
        db_table = "incoming_endorsement_t2"

    t_id = models.AutoField(primary_key=True)

    t_refno = models.ForeignKey(
        "incoming_fg_app.EndorsementT1",
        on_delete=models.CASCADE,
        to_field="t_refno",
        related_name="details",
    )

    t_lotnumbersingle = models.CharField(
        max_length=6,
        validators=[
            RegexValidator(
                regex=r"^\d{4}[A-Z]{2}$",
                message="Lot number must be in format (9999AA)",
                code="Invalid format",
            )
        ],
        null=False,
        blank=False
    )

    t_qty = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Positive number <= parent record's t_qtykg",
    )

    t_encodedon = models.DateTimeField(
        help_text="Must be within 1 hour of parent record's timestamp"
    )

    def clean(self):
        super().clean()

        if self.t_refno and self.t_refno.t_lotnumberwhole:
            try:
                lot_start, lot_end = self.t_refno.t_lotnumberwhole.split("-")

                if not (lot_start <= self.t_lotnumbersingle <= lot_end):
                    raise ValidationError(
                        {
                            "t_lotnumbersingle": "Lot number must fall within the parent's lot range."
                        }
                    )

            except ValueError:
                raise ValidationError(
                    {
                        "t_refno": "Invalid lot number range format in parent. Expected format: 8888AA-9999AA"
                    }
                )

        if self.t_refno and self.t_qty:
            if self.t_qty > self.t_refno.t_qtykg:
                raise ValidationError(
                    {
                        "t_qty": "Quantity cannot exceed the parent's total quantity (t_qtykg)"
                    }
                )

        if self.t_refno and self.t_encodedon:
            parent_time = self.t_refno.created_at
            time_diff = abs(self.t_encodedon - parent_time)

            if time_diff > timedelta(hours=1):
                raise ValidationError(
                    {
                        "t_encodedon": "Encoded time must be within 1 hour of parent's created_at."
                    }
                )

    def __str__(self):
        return f"Detail for Ref: {self.t_refno} | Lot: {self.t_lotnumbersingle}"
