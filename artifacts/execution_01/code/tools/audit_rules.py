"""Pure R11lock rules; importing this module performs no input audit."""

from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP, localcontext
import re


_NUMBER = re.compile(r"[0-9]+(?:\.[0-9]+)?\Z")


def _decimal_text(text):
    if not isinstance(text, str) or not _NUMBER.fullmatch(text):
        raise ValueError("Expected a nonnegative decimal string")
    return Decimal(text)


def split_display_accuracy(text):
    """Return cleaned front/back strings, preserving their trailing zeroes."""
    if not isinstance(text, str) or text.count("+/-") != 1:
        raise ValueError("Display extraction failed: expected one literal +/-")
    parts = text.split("+/-")
    cleaned = tuple(
        "".join(c for c in part.strip() if c not in "*%" and not c.isspace())
        for part in parts
    )
    for part in cleaned:
        _decimal_text(part)
    return cleaned


def one_decimal(text):
    """Quantize a decimal string with HALF_UP and retain one decimal place."""
    value = _decimal_text(text)
    with localcontext() as context:
        context.prec = 50
        context.rounding = ROUND_HALF_EVEN
        return format(value.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP), "f")


def stderr_matches(computed_se, original_stderr, display_accuracy):
    """Extraction failure raises ValueError; otherwise compare all three strings."""
    _, displayed_se = split_display_accuracy(display_accuracy)
    return one_decimal(computed_se) == one_decimal(original_stderr) == displayed_se


def compatible_numerators(display, N):
    """Enumerate every 0 <= K <= N within the original display's HALF_UP bounds.

    N must be authorized by the protocol; this function never infers N or a label.
    Predictions are deliberately absent from the calculation.
    """
    if type(N) is not int or N <= 0:
        raise ValueError("N must be a positive integer")
    x = _decimal_text(display)
    if not Decimal(0) <= x <= Decimal(100):
        raise ValueError("Percentage must be between 0 and 100")
    d = len(display.partition(".")[2])
    with localcontext() as context:
        context.prec = 50
        context.rounding = ROUND_HALF_EVEN
        h = Decimal(1).scaleb(-d)
        lower = x - h / Decimal(2)
        upper = x + h / Decimal(2)
        # Scale bounds by N to avoid rounding a rational exactly on an endpoint.
        lower_scaled = lower * Decimal(N)
        upper_scaled = upper * Decimal(N)
        result = []
        for K in range(N + 1):
            numerator = Decimal(100) * Decimal(K)
            if lower_scaled <= numerator < upper_scaled:
                result.append(K)
    return result


def raw_percentage(K, N=210):
    """Return only the precision-50 fixed-point percentage for a placeholder."""
    if type(N) is not int or N <= 0 or type(K) is not int or not 0 <= K <= N:
        raise ValueError("Expected integer counts with 0 <= K <= N")
    with localcontext() as context:
        context.prec = 50
        context.rounding = ROUND_HALF_EVEN
        text = format(Decimal(K) / Decimal(N) * Decimal(100), "f")
        return text.rstrip("0").rstrip(".") if "." in text else text
