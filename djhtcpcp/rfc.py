"""Protocol vocabulary from RFC 2324 (HTCPCP/1.0) and RFC 7168 (HTCPCP-TEA)."""

BREW = "BREW"
WHEN = "WHEN"
PROPFIND = "PROPFIND"
POST = "POST"

#: RFC 2324 section 4. Section 2.1.1 calls it "application/coffee-pot-command";
#: both spellings are accepted.
COFFEEPOT_MEDIA_TYPE = "message/coffeepot"
COFFEEPOT_MEDIA_TYPES = (COFFEEPOT_MEDIA_TYPE, "application/coffee-pot-command")
#: RFC 7168 section 3.
TEAPOT_MEDIA_TYPE = "message/teapot"
HTCPCP_MEDIA_TYPES = (*COFFEEPOT_MEDIA_TYPES, TEAPOT_MEDIA_TYPE)

START = "start"
STOP = "stop"

#: Accept-Additions vocabulary, RFC 2324 section 2.2.2.1 and RFC 7168 section 2.2.1.
#: sweetener-type and spice-type are named by the RFC but never enumerated.
ADDITIONS = {
    "milk": ("Cream", "Half-and-half", "Whole-milk", "Part-Skim", "Skim", "Non-Dairy"),
    "syrup": ("Vanilla", "Almond", "Raspberry", "Chocolate"),
    "alcohol": ("Whisky", "Rum", "Kahlua", "Aquavit"),
    "sugar": ("Sugar", "Xylitol", "Stevia"),
}

ALL_ADDITIONS = tuple(name for names in ADDITIONS.values() for name in names)

DEFAULT_STEEP_SECONDS = 180
