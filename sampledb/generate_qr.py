from jinja2 import Environment, FileSystemLoader
import os
import qrcode
import uuid
import subprocess
from glob import glob

LATEX_OPTS = ['-halt-on-error', '-file-line-error']

env = Environment(loader=FileSystemLoader([
    'templates',
    os.path.join(os.path.dirname(__file__), 'templates'), ]),
    block_start_string='\BLOCK{',
    block_end_string='}',
    variable_start_string='\VAR{',
    variable_end_string='}',
    comment_start_string='\#{',
    comment_end_string='}',
    line_statement_prefix='%%',
    line_comment_prefix='%#',
    trim_blocks=True,
    autoescape=False,
)

template = env.get_template('qr_template.tex')

base = 'test'

pages = 1
cols = 3
rows = 10
lmar = 0.1875
rmar = 0.1875
tmar = 0.5
bmar = 0.5
intercol = 0.6
interrow = 0
rbord = 0.0625
lbord = 0.0625
tbord = 0.125
bbord = 0.125
width = (8.5 - lmar - rmar - (cols - 1) * intercol) / cols - lbord - rbord
height = .8 * (11 - tmar - bmar - (rows - 1) * interrow) / rows - tbord - bbord

options = {
    'lmar': lmar,
    'rmar': rmar,
    'tmar': tmar,
    'bmar': bmar,
    'intercol': intercol,
    'interrow': interrow,
    'rbord': rbord,
    'lbord': lbord,
    'tbord': tbord,
    'bbord': bbord,
    'width': width,
    'height': height}
options = {k: str(v) + 'in' for k, v in options.items()}
options['cols'] = cols
options['rows'] = rows
options['gpath'] = base

codes = []
for i in range(pages * rows * cols):
    uid = str(uuid.uuid4())
    code = qrcode.make(uid)
    filename = uid + '.png'
    with open(os.path.join(base, filename), 'wb') as img:
        code.save(img, 'PNG')
    codes.append((filename, uid[:6]))
codes = [c for c in zip(codes[0::3], codes[1::3], codes[2::3])]
qrs = []
for c1, c2, c3 in zip(codes[0::3], codes[1::3], codes[2::3]):
    for i in range(3):
        for c in [c1, c2, c3]:
            qrs.append(c)

options['qrs'] = qrs
result = template.render(**options)

os.makedirs(base, exist_ok=True)


def run(cmd):
    subprocess.run(cmd, cwd=base, check=True)


with open(os.path.join(base, 'test.tex'), 'w') as f:
    f.write(result)

run(['pdflatex'] + LATEX_OPTS + [base + '.tex'])


def clean():
    postfixes = ['*.dvi', '*.toc', '*.aux', '*.out', '*.log', '*.bbl',
                 '*.blg', '*.log', '*.spl', '*~', '*.spl', '*.run.xml',
                 '*-blx.bib', '*.eps', '*.png']
    to_rm = []
    for pst in postfixes:
        to_rm += glob(os.path.join(base, pst))
    for f in set(to_rm):
        os.remove(f)


clean()
