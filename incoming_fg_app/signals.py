from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db import transaction
from decimal import Decimal
from django.core.exceptions import ValidationError

from incoming_fg_app.models import EndorsementT1, EndorsementT2
from incoming_fg_app.helpers.helper import lot_str_to_value, lot_value_to_str

# signals for endorsement table 2 when endorsement table 1 is created
@receiver(pre_save, sender=EndorsementT1)
def calculate_wtlot(sender, instance, **kwargs):
    """
    Auto-calculate t_wtlot before saving T1 record
    """

    if instance.t_lotnumberwhole and instance.t_qtykg is not None:
        try:
            start_lot, end_lot = instance.t_lotnumberwhole.split('-')
            start_val = lot_str_to_value(start_lot)
            end_val = lot_str_to_value(end_lot)

            # Calculate number of lots (inclusive)
            num_lots = (end_val - start_val) + 1

            if num_lots <= 0:
                raise ValidationError("Invalid lot range: start must be <= end")

            # Calculate weight per lot (rounded to 2 decimals)
            instance.t_wtlot = (instance.t_qtykg / Decimal(num_lots)).quantize(
                Decimal('0.00'), 
                rounding='ROUND_HALF_UP'
            )
        
        except (ValueError, AttributeError) as e:
            raise ValidationError(f"Error calculating weight per lot: {str(e)}")

@receiver(post_save, sender=EndorsementT1)
def create_t2_records(sender, instance, created, **kwargs):
    """
    Create T2 records for each lot in the range when T1 is created
    """
    if created and instance.t_lotnumberwhole and instance.t_wtlot is not None:
        try:
            with transaction.atomic():
                start_lot, end_lot = instance.t_lotnumberwhole.split('-')
                current = lot_str_to_value(start_lot)
                end_val = lot_str_to_value(end_lot)
                
                # Prepare batch creation
                t2_instances = []
                
                while current <= end_val:
                    t2_instances.append(
                        EndorsementT2(
                            t_refno=instance,
                            t_lotnumbersingle=lot_value_to_str(current),
                            t_qty=instance.t_wtlot
                        )
                    )
                    current += 1
                
                # Bulk create for performance
                EndorsementT2.objects.bulk_create(t2_instances)
        except Exception as e:
            print(f"Failed creating t2 records: {str(e)}")
            # Log error but don't crash
            # import logging
            # logger = logging.getLogger(__name__)
            # logger.error(f"Failed creating T2 records: {str(e)}")