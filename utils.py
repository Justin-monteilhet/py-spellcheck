from typing import Tuple
import re


_CLEAN_TAGS = re.compile('<.*?>')


def remove_tags(txt:str) -> str:
    """Remove all HTML tags from string

    Args:
        txt (str): HTML text to clean

    Returns:
        str: Cleaned text
    """
    return re.sub(_CLEAN_TAGS, '', txt)


def get_first_sentence(txt:str) -> str:
    """Returns first sentence of a string, considering every sentences end with a dot symbol (.)

    Args:
        txt (str): Base text

    Returns:
        str: First sentence
    """
    point = txt.find('.')
    if not point : return txt
    
    return txt.split(".")[0] + "."


def replace_selection(txt:str, selection:Tuple[int, int], replacement:str) -> str:
    """Replaces section of a text with desired string. Works like str.replace but with indexes instead of string

    Args:
        txt (str): Base text
        selection (Tuple[int, int]): start index included, end index excluded
        replacement (str): string to put instead

    Returns:
        str: _description_
    """
    return txt[:selection[0]] + replacement + txt[selection[1]:]


def replace_line(txt:str, line:int, new_line:str) -> str:
    """Replaces a line within a string by another string

    Args:
        txt (str): Base text
        line (int): 0-indexed line number
        new_line (str): New line to insert

    Returns:
        str: Text with line replaced
    """
    
    lines = txt.split('\n')
    lines[line] = new_line
    return '\n'.join(lines)


def get_line(txt:str, line:int) -> str:
    """Returns a line from a text

    Args:
        txt (str): Base text
        line (int): Line number

    Returns:
        str: The line at the specified number
    """
    
    return txt.split('\n')[line]


def insert_after(txt:str, index:int, insertion:str) -> str:
    """Inserts a string in another string

    Args:
        txt (str): Base text
        index (int): Index to insert at
        insertion (str): String to insert

    Returns:
        str: Text with string inserted
    """
    
    return txt[:index] + insertion + txt[index:]