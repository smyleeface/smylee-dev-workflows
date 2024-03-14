def split_string(input_string, max_length=72) -> []:
    """
    Split a string into lines with a maximum length, without breaking words.

    Parameters:
    - input_string: The input string to split.
    - max_length: The maximum length of each line (default is 72).

    Returns:
    - A list of lines, each with a maximum length of max_length characters.
    """
    lines = []
    current_line = ""

    for word in input_string.split():
        if len(current_line) + len(word) <= max_length:
            # Add the word to the current line
            current_line += " " + word if current_line else word
        else:
            # Start a new line
            lines.append(current_line.strip())
            current_line = word

    # Add the last line
    if current_line:
        lines.append(current_line.strip())

    return lines
