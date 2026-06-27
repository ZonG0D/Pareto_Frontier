import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from core.orchestrator import sanitize_text

def test_sanitize_text():
    nbsp = "\u00a0"
    zwsp = "\u200b"
    crlf = "\r\n"
    
    test_cases = [
        # (Input string, Expected output string, Description)
        ("Normal text.", "Normal text.", "Standard text"),
        (f"Text with {nbsp} non-breaking space", "Text with non-breaking space", "Non-breaking space replacement"),
        (f"Text with {zwsp} zero-width space", "Text with zero-width space", "Zero-width space replacement"),
        ("Line 1\r\nLine 2", "Line 1\nLine 2", "Carriage return removal"),
        ("*  List item", "* List item", "Extra space in list (Artifact)"),
    ]

    print(f"{'Description':<30} | {'Status':<10}")
    print("-" * 45)

    for input_str, expected_output, desc in test_cases:
        actual = sanitize_text(input_str)
        status = "PASS" if actual == expected_output else "FAIL"
        print(f"{desc:<30} | {status}")
        if status == "FAIL":
            print(f"  Input repr:    {repr(input_str)}")
            print(f"  Expected repr: {repr(expected_output)}")
            print(f"  Actual repr:   {repr(actual)}")

if __name__ == "__main__":
    test_sanitize_text()
