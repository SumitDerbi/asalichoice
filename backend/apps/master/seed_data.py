"""Default seed data for M01 Master Management.

Kept in a plain-Python module (not data migration) so the seeder can be
re-run idempotently and new entries can be appended without churning
migration history. See plan ``phase-1-modules/M01/01-api.md`` §10.
"""

from __future__ import annotations

from decimal import Decimal

# ---------------------------------------------------------------------------
# Country / State / GST state codes (India)
# ---------------------------------------------------------------------------

INDIA = {
    "iso2": "IN",
    "iso3": "IND",
    "name": "India",
    "phone_code": "+91",
    "currency": "INR",
}

# (code, name, gst_state_code). GST codes per CBIC master.
INDIAN_STATES: tuple[tuple[str, str, str], ...] = (
    ("JK", "Jammu and Kashmir", "01"),
    ("HP", "Himachal Pradesh", "02"),
    ("PB", "Punjab", "03"),
    ("CH", "Chandigarh", "04"),
    ("UK", "Uttarakhand", "05"),
    ("HR", "Haryana", "06"),
    ("DL", "Delhi", "07"),
    ("RJ", "Rajasthan", "08"),
    ("UP", "Uttar Pradesh", "09"),
    ("BR", "Bihar", "10"),
    ("SK", "Sikkim", "11"),
    ("AR", "Arunachal Pradesh", "12"),
    ("NL", "Nagaland", "13"),
    ("MN", "Manipur", "14"),
    ("MZ", "Mizoram", "15"),
    ("TR", "Tripura", "16"),
    ("ML", "Meghalaya", "17"),
    ("AS", "Assam", "18"),
    ("WB", "West Bengal", "19"),
    ("JH", "Jharkhand", "20"),
    ("OR", "Odisha", "21"),
    ("CG", "Chhattisgarh", "22"),
    ("MP", "Madhya Pradesh", "23"),
    ("GJ", "Gujarat", "24"),
    ("DD", "Daman and Diu", "25"),
    ("DN", "Dadra and Nagar Haveli", "26"),
    ("MH", "Maharashtra", "27"),
    ("KA", "Karnataka", "29"),
    ("GA", "Goa", "30"),
    ("LD", "Lakshadweep", "31"),
    ("KL", "Kerala", "32"),
    ("TN", "Tamil Nadu", "33"),
    ("PY", "Puducherry", "34"),
    ("AN", "Andaman and Nicobar Islands", "35"),
    ("TG", "Telangana", "36"),
    ("AP", "Andhra Pradesh", "37"),
    ("LA", "Ladakh", "38"),
)


# ---------------------------------------------------------------------------
# Top-100 cities — (state_code, city_name). Curated, capital + major commercial
# centres so the seed stays compact yet covers every state.
# ---------------------------------------------------------------------------
TOP_CITIES: tuple[tuple[str, str], ...] = (
    # Tier-1 metros
    ("MH", "Mumbai"),
    ("MH", "Pune"),
    ("MH", "Nagpur"),
    ("MH", "Nashik"),
    ("MH", "Aurangabad"),
    ("MH", "Thane"),
    ("DL", "New Delhi"),
    ("KA", "Bengaluru"),
    ("KA", "Mysuru"),
    ("KA", "Mangaluru"),
    ("KA", "Hubli"),
    ("TN", "Chennai"),
    ("TN", "Coimbatore"),
    ("TN", "Madurai"),
    ("TN", "Tiruchirappalli"),
    ("TN", "Salem"),
    ("WB", "Kolkata"),
    ("WB", "Howrah"),
    ("WB", "Durgapur"),
    ("WB", "Siliguri"),
    ("TG", "Hyderabad"),
    ("TG", "Warangal"),
    ("AP", "Visakhapatnam"),
    ("AP", "Vijayawada"),
    ("AP", "Guntur"),
    ("AP", "Tirupati"),
    # North
    ("UP", "Lucknow"),
    ("UP", "Kanpur"),
    ("UP", "Agra"),
    ("UP", "Varanasi"),
    ("UP", "Noida"),
    ("UP", "Ghaziabad"),
    ("UP", "Meerut"),
    ("UP", "Prayagraj"),
    ("HR", "Gurugram"),
    ("HR", "Faridabad"),
    ("HR", "Panipat"),
    ("HR", "Karnal"),
    ("RJ", "Jaipur"),
    ("RJ", "Jodhpur"),
    ("RJ", "Udaipur"),
    ("RJ", "Kota"),
    ("RJ", "Ajmer"),
    ("PB", "Ludhiana"),
    ("PB", "Amritsar"),
    ("PB", "Jalandhar"),
    ("PB", "Mohali"),
    ("CH", "Chandigarh"),
    ("HP", "Shimla"),
    ("HP", "Dharamshala"),
    ("UK", "Dehradun"),
    ("UK", "Haridwar"),
    ("JK", "Srinagar"),
    ("JK", "Jammu"),
    ("LA", "Leh"),
    # West / Central
    ("GJ", "Ahmedabad"),
    ("GJ", "Surat"),
    ("GJ", "Vadodara"),
    ("GJ", "Rajkot"),
    ("GJ", "Gandhinagar"),
    ("MP", "Bhopal"),
    ("MP", "Indore"),
    ("MP", "Gwalior"),
    ("MP", "Jabalpur"),
    ("CG", "Raipur"),
    ("CG", "Bhilai"),
    ("GA", "Panaji"),
    ("GA", "Margao"),
    ("DD", "Daman"),
    ("DN", "Silvassa"),
    # East / North-East
    ("BR", "Patna"),
    ("BR", "Gaya"),
    ("BR", "Muzaffarpur"),
    ("JH", "Ranchi"),
    ("JH", "Jamshedpur"),
    ("JH", "Dhanbad"),
    ("OR", "Bhubaneswar"),
    ("OR", "Cuttack"),
    ("OR", "Rourkela"),
    ("AS", "Guwahati"),
    ("AS", "Dibrugarh"),
    ("SK", "Gangtok"),
    ("AR", "Itanagar"),
    ("NL", "Kohima"),
    ("MN", "Imphal"),
    ("MZ", "Aizawl"),
    ("TR", "Agartala"),
    ("ML", "Shillong"),
    # South / Islands
    ("KL", "Thiruvananthapuram"),
    ("KL", "Kochi"),
    ("KL", "Kozhikode"),
    ("KL", "Thrissur"),
    ("PY", "Puducherry"),
    ("AN", "Port Blair"),
    ("LD", "Kavaratti"),
)


# ---------------------------------------------------------------------------
# UoMs, Tax slabs, Payment modes, Default branch
# ---------------------------------------------------------------------------

# (code, name, symbol, decimals)
DEFAULT_UOMS: tuple[tuple[str, str, str, int], ...] = (
    ("PCS", "Piece", "pc", 0),
    ("KG", "Kilogram", "kg", 3),
    ("GRAM", "Gram", "g", 0),
    ("LITRE", "Litre", "L", 3),
    ("ML", "Millilitre", "ml", 0),
    ("METER", "Metre", "m", 2),
    ("BOX", "Box", "box", 0),
    ("PACK", "Pack", "pack", 0),
)


def _gst_split(rate_total: Decimal) -> list[dict]:
    """Return CGST+SGST equal halves matching ``rate_total``."""
    half = (rate_total / Decimal("2")).quantize(Decimal("0.01"))
    # Bias remainder onto SGST to keep the sum equal to rate_total.
    sgst = rate_total - half
    return [
        {"type": "CGST", "rate": str(half)},
        {"type": "SGST", "rate": str(sgst)},
    ]


# (code, name, rate_total). Components computed as CGST/SGST split.
DEFAULT_TAX_SLABS: tuple[tuple[str, str, str], ...] = (
    ("GST0", "GST 0%", "0"),
    ("GST5", "GST 5%", "5"),
    ("GST12", "GST 12%", "12"),
    ("GST18", "GST 18%", "18"),
    ("GST28", "GST 28%", "28"),
)


def gst_components(rate_total: str) -> list[dict]:
    return _gst_split(Decimal(rate_total))


# (code, name, type, is_online)
DEFAULT_PAYMENT_MODES: tuple[tuple[str, str, str, bool], ...] = (
    ("CASH", "Cash", "CASH", False),
    ("UPI", "UPI", "UPI", True),
    ("CARD", "Debit/Credit Card", "CARD", True),
    ("COD", "Cash on Delivery", "COD", False),
)


DEFAULT_BRANCH = {
    "code": "HQ",
    "name": "Head Office",
    "type": "HQ",
}
