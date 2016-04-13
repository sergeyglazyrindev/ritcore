import ssl


def patch_ssl():
    ssl.HAS_SNI = False
