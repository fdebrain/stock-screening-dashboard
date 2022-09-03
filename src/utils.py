def simplify_numbers(number):
    string = str(number)
    n = len(string)
    pos2letter = [("9", "B"), ("6", "M"), ("3", "K")]
    for pos, letter in pos2letter:
        if n > int(pos):
            pos_decimal = n - int(pos)
            return (
                string[:pos_decimal]
                + "."
                + string[pos_decimal : pos_decimal + 1]
                + letter
            )
    return string
