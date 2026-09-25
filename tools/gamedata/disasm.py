import re, sys
from capstone import Cs, CS_ARCH_X86, CS_MODE_64
from elftools.elf.elffile import ELFFile
from sigscan import rx, data
f = ELFFile(open('libserver.so', 'rb'))
# file offset -> vaddr via PT_LOAD
loads = [s for s in f.iter_segments() if s['p_type'] == 'PT_LOAD']
def o2v(o):
    for s in loads:
        if s['p_offset'] <= o < s['p_offset'] + s['p_filesz']: return o - s['p_offset'] + s['p_vaddr']
def v2o(v):
    for s in loads:
        if s['p_vaddr'] <= v < s['p_vaddr'] + s['p_filesz']: return v - s['p_vaddr'] + s['p_offset']
md = Cs(CS_ARCH_X86, CS_MODE_64)
def cstr(v):
    o = v2o(v)
    if o is None: return None
    e = data.find(b'\0', o, o + 200)
    s = data[o:e]
    return s.decode('latin1') if e > o and all(32 <= c < 127 or c in (9, 10) for c in s) else None
def dis(off, n=60):
    out = []
    for i in md.disasm(data[off:off + 600], o2v(off)):
        extra = ''
        if 'rip' in i.op_str and '[' in i.op_str:
            m = re.search(r'\[rip ([+-]) (0x[0-9a-f]+)\]', i.op_str)
            if m:
                t = i.address + i.size + (int(m.group(2), 16) * (1 if m.group(1) == '+' else -1))
                s = cstr(t); extra = f'   ; {s!r}' if s else f'   ; ->{t:#x}'
        out.append(f'{i.address:#x}: {i.bytes.hex(" ")[:40]:40} {i.mnemonic} {i.op_str}{extra}')
        if len(out) >= n or i.mnemonic == 'ret': break
    return out
if __name__ == '__main__':
    sig = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    for m in rx(sig).finditer(data):
        print(f'=== match file off {m.start():#x}')
        print('\n'.join(dis(m.start(), n)))
