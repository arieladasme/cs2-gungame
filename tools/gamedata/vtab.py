import sys, re, struct
from elftools.elf.elffile import ELFFile
from elftools.elf.relocation import RelocationSection
from sigscan import data, rx
f = ELFFile(open('libserver.so', 'rb'))
loads = [s for s in f.iter_segments() if s['p_type'] == 'PT_LOAD']
def o2v(o):
    for s in loads:
        if s['p_offset'] <= o < s['p_offset'] + s['p_filesz']: return o - s['p_offset'] + s['p_vaddr']
rel = {}
for sec in f.iter_sections():
    if isinstance(sec, RelocationSection) and sec['sh_type'] == 'SHT_RELA':
        for r in sec.iter_relocations():
            if r['r_info_type'] == 8:  # R_X86_64_RELATIVE
                rel[r['r_offset']] = r['r_addend']
def vtable(cls):
    name = f'{len(cls)}{cls}'.encode() + b'\0'
    names = [o2v(m.start() + 1) for m in re.finditer(re.escape(b'\0' + name), data)]
    tis = [a - 8 for a, v in rel.items() if v in names]
    for t in tis:
        for a, v in rel.items():
            if v == t and struct.unpack_from('<q', data, a - 16 - [s for s in loads if s['p_vaddr'] <= a < s['p_vaddr'] + s['p_filesz']][0]['p_vaddr'] + [s for s in loads if s['p_vaddr'] <= a < s['p_vaddr'] + s['p_filesz']][0]['p_offset'] + 8)[0] == 0:
                return a + 8
def entries(vt, n=700):
    out = []
    for i in range(n):
        v = rel.get(vt + 8 * i)
        if v is None: break
        out.append(v)
    return out
def find_func(sig):
    ms = [o2v(m.start()) for m in rx(sig.replace('??', '?')).finditer(data)]
    return ms
if __name__ == '__main__':
    cls, sig = sys.argv[1], sys.argv[2]
    vt = vtable(cls); ents = entries(vt)
    print(f'{cls} vtable {vt:#x}, {len(ents)} entries')
    for a in find_func(sig):
        print(f'func {a:#x} -> index', [i for i, e in enumerate(ents) if e == a])
