def camel_case_to_snake_case(input_str: str) -> str:
    """
    >>> camel_case_to_snake_case('SomeSDK')
    'some_sdk'
    >>> camel_case_to_snake_case('RServoDrive')
    'r_servo_drive'
    >>> camel_case_to_snake_case("SDKDemo")
    'sdk_demo'
    """
    if not input_str:
        return input_str

    result = []
    prev_char_lower = False

    for i, char in enumerate(input_str):
        current_char_upper = char.isupper()
        if (
            i > 0
            and current_char_upper
            and (prev_char_lower or (i < len(input_str) - 1 and input_str[i + 1].islower()))
        ):
            result.append("_")

        result.append(char.lower())
        prev_char_lower = char.islower()

    return "".join(result)
