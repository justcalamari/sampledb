from jinja2 import Environment, FileSystemLoader
import os
import qrcode
import uuid
import subprocess
from glob import glob
import matplotlib.image
import numpy as np

LATEX_OPTS = ['-halt-on-error', '-file-line-error']

env = Environment(loader=FileSystemLoader([
    'templates',
    os.path.join(os.path.dirname(__file__), 'templates'), ]),
    block_start_string='%{',
    block_end_string='}%',
    variable_start_string='%{{',
    variable_end_string='}}%',
)

template = env.get_template('qr_template.tex')

base = 'test'

ctx = {'qrs': [],
       'gpath': base}

for i in range(5):
    u = str(uuid.uuid4())

    code = qrcode.make(u)

    fn = os.path.join(base, u + '.eps')

    code = np.array(code)

    matplotlib.image.imsave(fn, code, format='eps', cmap='gray')
    d = {'position': u + '.eps', 'uid': u}
    ctx['qrs'].append(d)

result = template.render(ctx)
print(result)

os.makedirs(base, exist_ok=True)


def run(cmd):
    subprocess.run(cmd, cwd=base, check=True)


with open(os.path.join(base, 'test.tex'), 'w') as f:
    f.write(result)

run(['latex'] + LATEX_OPTS + [base + '.tex'])
# run(['bibtex'] + [base + '.aux'])
run(['latex'] + LATEX_OPTS + [base + '.tex'])
run(['latex'] + LATEX_OPTS + [base + '.tex'])
run(['dvipdf', '-R0', base])


def clean():
    postfixes = ['*.dvi', '*.toc', '*.aux', '*.out', '*.log', '*.bbl',
                 '*.blg', '*.log', '*.spl', '*~', '*.spl', '*.run.xml',
                 '*-blx.bib', '*.eps']
    to_rm = []
    for pst in postfixes:
        to_rm += glob(os.path.join(base, pst))
    for f in set(to_rm):
        os.remove(f)


clean()
