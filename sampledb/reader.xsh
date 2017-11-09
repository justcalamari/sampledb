
def get_uid_from_qr():
    a = $(zbarcam)
    b = a.split()
    c = [z.strip('QR-Code:') for z in b]
    d = set(c)
    return d
