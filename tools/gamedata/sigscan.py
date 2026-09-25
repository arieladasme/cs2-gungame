import json, re, sys
data = open('libserver.so', 'rb').read()
def rx(sig):
    return re.compile(b''.join(b'.' if t == '?' else re.escape(bytes([int(t, 16)])) for t in sig.split()), re.S)
def count(sig):
    return len(rx(sig).findall(data))
if __name__ == '__main__':
    gd = json.load(open('gamedata.json.bak'))
    for name, e in gd.items():
        s = e.get('signatures', {})
        if s.get('library') == 'server' and s.get('linux'):
            n = count(s['linux'])
            print(('OK  ' if n == 1 else 'FAIL') + f' {n:3} {name}')
