# PyScript Python for the genetic code translator
from js import document

# Sample presets: simplified short sequences (containing single start codon)
SAMPLES = {
    'minta_01': {
        'nev': 'Sziklasárkány (Draco petraeus)',
        'leiras': 'A pikkely-keményítő enzim génje. Ez a fehérje felelős azért, hogy a sárkány bőre ellenálljon a vulkáni hőnek.',
        'dns': 'GCATCGTAGCTAGCCGATGCGCTACGGCTGGCAGTTTGACGTGAACAAATAACGATCGATCGACT'
    },
    'minta_02': {
        'nev': 'Zombi-vírus (Necrovirus cerebri)',
        'leiras': 'A rettegett agyevő protein. Ez a peptid veszi át az irányítást a fertőzött gazdatest idegrendszere felett.',
        'dns': 'TTCGACCGGTCAAATGGACGAGGGGTTTTCTATACCTAGACCTGTCGTGTAGCCTGCATGC'
    },
    'minta_03': {
        'nev': 'Kozmikus Űr-medúza (Medusa galactica)',
        'leiras': 'Asztro-fluoreszkáló fehérje. Lehetővé teszi, hogy az élőlény világítson a csillagközi sötétségben a gamma-sugárzás hatására.',
        'dns': 'ATATACGCGCGATGAAACCCGGGTTTACCGCCTGTAGCTATCACTGATTTAAACCCGGG'
    },
    'minta_04': {
        'nev': 'Láthatatlan Mocsári Manó (Goblinus invisibilis)',
        'leiras': 'Fénytörő enzim szakasza. A fehérje speciális szerkezete elhajlítja a látható fényt, optikai álcázást biztosítva.',
        'dns': 'CTCGATCGATATGACCTGCCCATACTACTTTAACCAGGGCATCTAAAGGCATCGTACG'
    }
}

CODON_TABLE = {
    # partial table for demo (RNA codons -> amino acid 3-letter code)
    'AUG': 'Met', 'UUU': 'Phe', 'UUC': 'Phe',
    'UUA': 'Leu', 'UUG': 'Leu', 'CUU': 'Leu', 'CUC': 'Leu', 'CUA': 'Leu', 'CUG': 'Leu',
    'UAA': 'STOP', 'UAG': 'STOP', 'UGA': 'STOP',
    'AUA': 'Ile', 'AUU': 'Ile', 'AUC': 'Ile',
    'GCU': 'Ala','GCC':'Ala','GCA':'Ala','GCG':'Ala',
    'UGG': 'Trp', 'UGU':'Cys','UGC':'Cys',
    'GAA':'Glu','GAG':'Glu',
    'AAA':'Lys','AAG':'Lys',
    'GAU':'Asp','GAC':'Asp',
    # ... add more as needed
}


def sanitize_dna(seq: str) -> str:
    return ''.join([c for c in seq.upper() if c in 'ATGC'])


def gc_content(seq: str) -> float:
    if not seq:
        return 0.0
    g = seq.count('G')
    c = seq.count('C')
    return round(100.0 * (g + c) / len(seq), 2)


def dna_to_mrna(dna: str) -> str:
    return dna.replace('T', 'U')


def translate(mrna: str):
    # find first AUG
    start = mrna.find('AUG')
    if start == -1:
        return [], None
    aa = []
    pos = start
    while pos + 3 <= len(mrna):
        codon = mrna[pos:pos+3]
        aa_name = CODON_TABLE.get(codon, '???')
        if aa_name == 'STOP':
            return aa, (start, pos+3)
        aa.append(aa_name)
        pos += 3
    return aa, (start, pos)


# UI helpers
out = document.getElementById('output')

def render_output(html: str):
    out.innerHTML = html


def load_preset(ev=None):
    sel = document.getElementById('preset')
    val = sel.value
    ta = document.getElementById('dna_input')
    info = document.getElementById('sample_info')
    if val == 'custom':
        ta.value = ''
        info.innerHTML = ''
    else:
        sample = SAMPLES.get(val)
        if sample:
            ta.value = sample['dns']
            info.innerHTML = f"<strong>{sample['nev']}</strong><p>{sample['leiras']}</p>"
        else:
            ta.value = ''
            info.innerHTML = ''


def clear_output(ev=None):
    render_output('')


def process(ev=None):
    ta = document.getElementById('dna_input')
    raw = ta.value or ''
    dna = sanitize_dna(raw)

    gc = gc_content(dna)
    mrna = dna_to_mrna(dna)
    aa_seq, region = translate(mrna)

    # build display for mRNA with highlighted region
    display_mrna = ''
    if mrna:
        if region:
            s, e = region
            display_mrna = f"{mrna[:s]}<span class='highlight'>{mrna[s:e]}</span>{mrna[e:]}"
        else:
            display_mrna = mrna

    aa_text = ', '.join(aa_seq) if aa_seq else '(nincs Start/AUG vagy rövid a szekvencia)'

    html = f""
    html += f"<h2>Eredmények</h2>"
    html += f"<p><strong>Beolvasott DNS:</strong> <code class='mrns'>{dna}</code></p>"
    html += f"<p><strong>GC-tartalom:</strong> {gc}%</p>"
    html += f"<p><strong>mRNS:</strong> <span class='mrns'>{display_mrna}</span></p>"
    html += f"<p><strong>Fordított aminosav-sorrend:</strong> <code>{aa_text}</code></p>"

    render_output(html)

# expose to PyScript
from pyodide.ffi import create_proxy

# Wire up button and select events
load_btn = document.querySelector("button[py-click='load_preset']")
if load_btn:
    load_btn.addEventListener('click', create_proxy(load_preset))

process_btn = document.querySelector("button[py-click='process']")
if process_btn:
    process_btn.addEventListener('click', create_proxy(process))

clear_btn = document.querySelector("button[py-click='clear_output']")
if clear_btn:
    clear_btn.addEventListener('click', create_proxy(clear_output))
