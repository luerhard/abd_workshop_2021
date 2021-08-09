import unicodedata


def string_normalize(unistr: str) -> str:
    return unicodedata.normalize("NFC", unistr)


def string_to_ascii(unistr: str) -> str:
    if unistr is None:
        raise TypeError(f"{unistr} cannot be converted")
    for char in """"!"#$%&'()*+./:;<=>?@[\\]^_`{|}~""":
        unistr = unistr.replace(char, "")
    return unicodedata.normalize("NFKD", unistr).encode("ascii", "ignore").decode("utf-8")
