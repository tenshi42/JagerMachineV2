def unquote(string):
    if not string:
        return b''

    if isinstance(string, str):
        string = string.encode('utf-8')

    bits = string.split(b'%')
    if len(bits) == 1:
        return string

    res = [bits[0]]

    for item in bits[1:]:
        try:
            code = item[:2]
            char = bytes([int(code, 16)])
            res.append(char)
            res.append(item[2:])
        except KeyError:
            res.append(b'%')
            res.append(item)

    return b''.join(res)
