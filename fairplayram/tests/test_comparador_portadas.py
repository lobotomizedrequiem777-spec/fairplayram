import sys
from pathlib import Path
sys.path.insert(0, str(next(Path(__file__).resolve().parents[1].glob('Primera fase*'))))
from comparador_portadas import separar, html_resultado, analizar_par

def test_separar():
    assert separar({'Sword', 'Tree'}, {'sword', 'dragon'}) == (['tree'], ['dragon'], ['sword'])

def test_html_escape():
    html = html_resultado(['<script>'], [], [], ('<A>', 'B'))
    assert '<script>' not in html and '&lt;script&gt;' in html

def test_sin_par():
    assert 'Primero carga' in analizar_par(None)
