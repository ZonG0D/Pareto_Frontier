import re

def stabilize(text: str) -> str:
    """
    Ultra-fast, stable post-processing to strip visual artifacts and control chars.
    Preserves standard printable ASCII, common whitespace, and common UTF8 symbols.
    Removes any non-printable/garbage sequences that cause terminal misalignment.
    """
    if not isinstance(text, str):
        return ""

    # 1. Handle carriage returns by normalizing to \n first
    text = text.replace('\r', '')

    # 2. Remove all control characters EXCEPT: newline (\n), tab (\t)
    # This targets the M-bM... and ^[[... stuff if it's actually raw bytes.
    # Using a regex to keep only ASCII printable (32-126) and \n, \t. 
    # We add common UTF8 characters like emoji/non-latin later if needed, but for "dumb & stable", 
    # sticking to the core essentials is safest.
    # Actually, let's be a bit more generous: keep everything that isn't a control char (0-31).
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)

    # 3. Collapse multiple spaces into one, but preserve indentation/newlines.
    # (Standard pattern from before: don't collapse space at start of lines)
    text = re.sub(r'(?<!^)(?<!\n) +', ' ', text)
    
    # 4. Final pass for any remaining suspicious zero-width or invisible chars
    text = text.replace('\u200b', '').replace('\xa0', ' ').replace('\ufeff', '')

    return text.strip() if text.strip() else "" # Return empty string instead of whitespace only
