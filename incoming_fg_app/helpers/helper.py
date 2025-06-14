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

