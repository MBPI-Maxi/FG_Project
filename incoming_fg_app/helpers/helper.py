from decimal import Decimal, ROUND_HALF_UP
from typing import Type

def lot_str_to_value(lot_str):
    num = int(lot_str[:4])
    letters = lot_str[4:]
    val = (ord(letters[0]) - ord("A")) * 26 + (ord(letters[1]) - ord("A"))
    
    return num * 1000 + val


def value_to_lot_str(value):
    num = value // 1000
    letter_val = value % 1000
    first_letter = chr((letter_val // 26) + ord("A"))
    second_letter = chr((letter_val % 26) + ord("A"))
    
    return f"{num:04d}{first_letter}{second_letter}"


def generate_lot_range(start_lot, end_lot):
    start_val = lot_str_to_value(start_lot)
    end_val = lot_str_to_value(end_lot)
    
    if start_val > end_val:
        raise ValueError("Start lot must be less than or equal to end lot.")
    return [value_to_lot_str(v) for v in range(start_val, end_val + 1)]


def lot_number_handler(
    left_letter_first, left_letter_second,
    right_letter_first, right_letter_second,
    forms
) -> None:
    # Case 1: If first letter changes, second letter must wrap from Z → A  
    if left_letter_first != right_letter_first:
        if not (left_letter_second == "Z" and right_letter_second == "A"):
            raise forms.ValidationError(
                "When first letter changes, second letter must wrap from Z -> A (e.g., AZ -> BA)"
            )
    
    # Case 2: If first letter remains the same, second letter can only increment by 1
    else:
        if ord(right_letter_second) - ord(left_letter_second) not in (1, -25):
            raise forms.ValidationError(
                "Second letter must increment by 1 (e.g., AA -> AB)"
            )

def increment_lot(lot):
    num = int(lot[:4])
    letter1 = lot[4]
    letter2 = lot[5]

    # Increment second letter
    if letter2 != "Z":
        letter2 = chr(ord(letter2) + 1)
    else:
        letter2 = "A"
        # Increment first letter
        if letter1 != "Z":
            letter1 = chr(ord(letter1) + 1)
        else:
            letter1 = "A"
            num += 1  # Roll over to next number

    return f"{num:04d}{letter1}{letter2}"

def count_lot_range(start_lot, end_lot):
    current = start_lot
    count = 1  # Include start_lot
    while current != end_lot:
        current = increment_lot(current)
        count += 1
        if count > 10000:  # Prevent infinite loop
            raise ValueError("End lot is unreachable from start lot.")
    return count

def count_lot_range(start_lot: str, end_lot: str) -> Type[Decimal]:
    inclusive_number = 1
 
    start_lot = start_lot[0:4]
    end_lot = end_lot[0:4]

    start_lot_decimal = Decimal(start_lot).quantize(
        exp=Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )
    end_lot_decimal = Decimal(end_lot).quantize(
        exp=Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )

    lots = (end_lot_decimal - start_lot_decimal) + inclusive_number
    
    return lots
    
