import struct, re, difflib, pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_64
md = Cs(CS_ARCH_X86, CS_MODE_64)
class Bin:
    def __init__(s, path):
        s.pe = pefile.PE(path, fast_load=True); s.data = s.pe.get_memory_mapped_image(); s.base = s.pe.OPTIONAL_HEADER.ImageBase
        s.text = [x for x in s.pe.sections if x.Name.startswith(b'.text')][0]
    def q(s, rva): return struct.unpack_from('<Q', s.data, rva)[0]
    def vtable(s, cls):
        td_name = b'.?AV' + cls.encode() + b'@@\0'
        tds = [m.start() - 0x10 for m in re.finditer(re.escape(td_name), s.data)]
        for td in tds:
            for m in re.finditer(re.escape(struct.pack('<IIII', 1, 0, 0, td)), s.data):
                col = m.start()
                for v in re.finditer(re.escape(struct.pack('<Q', s.base + col)), s.data):
                    return v.start() + 8
    def entries(s, vt):
        out = []; lo = s.base + s.text.VirtualAddress; hi = lo + s.text.Misc_VirtualSize
        while True:
            p = s.q(vt + 8 * len(out))
            if not lo <= p < hi: return out
            out.append(p - s.base)
    def fp(s, rva, n=48):
        ops = []
        for i in md.disasm(bytes(s.data[rva:rva + 400]), rva):
            o = re.sub(r'0x[0-9a-f]{5,}', 'X', i.op_str)
            o = re.sub(r'\[rip [+-] 0x[0-9a-f]+\]', '[rip]', o)
            ops.append(i.mnemonic + ' ' + o)
            if len(ops) >= n or i.mnemonic in ('ret', 'int3') or (i.mnemonic == 'jmp' and len(ops) < 3 and 'rip' not in i.op_str): break
        return ops
def align(a, b, cls):
    ea, eb = a.entries(a.vtable(cls)), b.entries(b.vtable(cls))
    fa, fb = [a.fp(x) for x in ea], [b.fp(x) for x in eb]
    n, m = len(fa), len(fb)
    sim = lambda i, j: difflib.SequenceMatcher(None, fa[i], fb[j]).ratio()
    # DP alignment with gap penalty
    import functools
    G = -0.3
    S = [[0.0] * (m + 1) for _ in range(n + 1)]; T = [[None] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1): S[i][0] = i * G; T[i][0] = 'u'
    for j in range(1, m + 1): S[0][j] = j * G; T[0][j] = 'l'
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            d = S[i-1][j-1] + (sim(i-1, j-1) - 0.5) * 2 if abs(i - j) < 40 else -9
            u, l = S[i-1][j] + G, S[i][j-1] + G
            S[i][j], T[i][j] = max((d, 'd'), (u, 'u'), (l, 'l'))
    i, j, mp = n, m, {}
    while i or j:
        t = T[i][j]
        if t == 'd': mp[i-1] = j-1; i -= 1; j -= 1
        elif t == 'u': i -= 1
        else: j -= 1
    return len(ea), len(eb), mp
