#!/usr/bin/env python3
"""
guia_rodaje.py · Plantilla fija de guías de rodaje · Histea Studios
--------------------------------------------------------------------
NO SE EDITA ESTE ARCHIVO PARA CADA PROYECTO.
El diseño (colores, tipografías, medidas, componentes) vive aquí y es siempre igual.
Para cada proyecto solo se escribe un JSON de contenido y se ejecuta:

    python3 guia_rodaje.py proyecto.json salida.pdf

El esquema del JSON está documentado en ESQUEMA.md (y en el ejemplo
ejemplo_la_ultima_campana.json).
"""
import json, math, os, random, re, sys, urllib.request

from reportlab.lib.colors import HexColor, Color
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.fonts import addMapping

# ════════════════════════════════════════════════════════════════════
# 1. DISEÑO FIJO
# ════════════════════════════════════════════════════════════════════
W, H = 405, 720          # página vertical
M = 22                   # margen
CW = W - 2 * M           # ancho útil (361)
TOP0 = 84                # inicio del contenido bajo el título
BOTTOM = 686             # límite inferior del contenido

BG = HexColor("#0F1523")        # fondo de página
CREMA = HexColor("#F3EEE4")     # texto principal
GRIS = HexColor("#8A93A6")      # texto secundario
ORO = HexColor("#D4AF6B")       # acento
CARD = HexColor("#F4F4F4")      # tarjetas claras
OSC = HexColor("#0F1523")       # texto sobre tarjeta
GRIS_C = HexColor("#5A6478")    # texto secundario sobre tarjeta
MARCO = HexColor("#26324A")     # borde de cuadros / filas neutras
CUADRO = HexColor("#090D17")    # fondo de cuadros del storyboard

BLOQUES = ["#E8A87C", "#D4AF6B", "#7FB7BE", "#C38D9E", "#9B8CFF",
           "#6FA8DC", "#E3C48B", "#8FC9A9"]

PALETA = {  # colores con nombre para los dibujos
    "fondo": "#0F1523", "cuadro": "#090D17", "marco": "#26324A",
    "azul": "#8395B3", "azul_osc": "#5C6E8C", "azul_prof": "#2A3A55",
    "crema": "#F3EBDD", "oro": "#D4AF6B", "coral": "#E8A87C",
    "verde": "#7FB7BE", "rosa": "#C38D9E", "violeta": "#9B8CFF",
    "celeste": "#6FA8DC", "gris": "#8A93A6", "blanco": "#FFFFFF",
    "negro": "#000000",
    # estilo diagrama (storyboard sobre papel claro)
    "papel": "#F4F7FB", "linea": "#A9BED3", "tinta": "#2A3A55", "naranja": "#EDA53A",
    "naranja_osc": "#B8681F", "amarillo": "#F3C969", "mov": "#2563A8", "gris_claro": "#DCE4EE",
}

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
FONTS = {
    "Poppins": "ofl/poppins/Poppins-Regular.ttf",
    "Poppins-Medium": "ofl/poppins/Poppins-Medium.ttf",
    "Poppins-SemiBold": "ofl/poppins/Poppins-SemiBold.ttf",
    "Poppins-Bold": "ofl/poppins/Poppins-Bold.ttf",
    "Poppins-Italic": "ofl/poppins/Poppins-Italic.ttf",
    "Serif": "ofl/dmserifdisplay/DMSerifDisplay-Regular.ttf",
    "Serif-Italic": "ofl/dmserifdisplay/DMSerifDisplay-Italic.ttf",
    "Mano": "ofl/gochihand/GochiHand-Regular.ttf",
}
DEJAVU = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
          "/usr/share/fonts/dejavu/DejaVuSans.ttf"]


def cargar_fuentes():
    os.makedirs(FONT_DIR, exist_ok=True)
    for name, rel in FONTS.items():
        path = os.path.join(FONT_DIR, os.path.basename(rel))
        if not os.path.exists(path):
            url = "https://raw.githubusercontent.com/google/fonts/main/" + rel
            urllib.request.urlretrieve(url, path)
        pdfmetrics.registerFont(TTFont(name, path))
    addMapping("Poppins", 0, 0, "Poppins")
    addMapping("Poppins", 1, 0, "Poppins-SemiBold")
    addMapping("Poppins", 0, 1, "Poppins-Italic")
    addMapping("Poppins", 1, 1, "Poppins-SemiBold")
    sym = "Poppins"
    for p in DEJAVU:
        if os.path.exists(p):
            pdfmetrics.registerFont(TTFont("Sym", p))
            sym = "Sym"
            break
    return sym


SYM = "Poppins"

# ════════════════════════════════════════════════════════════════════
# 2. TEXTO
# ════════════════════════════════════════════════════════════════════
_SYMS = "♪→←↑↓✓✕×↔⟶•"


def markup(t):
    """**negrita**, *cursiva*, símbolos con fuente de respaldo."""
    if t is None:
        return ""
    t = str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", t)
    if SYM != "Poppins":
        t = "".join(f'<font name="{SYM}">{ch}</font>' if ch in _SYMS and ch != "•" else ch for ch in t)
    return t.replace("\n", "<br/>")


def estilo(size, color, font="Poppins", lead=1.38, align=TA_LEFT):
    return ParagraphStyle("s", fontName=font, fontSize=size, leading=size * lead,
                          textColor=color, alignment=align)


def para(t, size=7.4, color=CREMA, font="Poppins", lead=1.38, align=TA_LEFT):
    return Paragraph(markup(t), estilo(size, color, font, lead, align))


def alto(p, w):
    return p.wrap(w, 10000)[1]


# ════════════════════════════════════════════════════════════════════
# 3. DOCUMENTO Y PÁGINAS
# ════════════════════════════════════════════════════════════════════
class CanvasSimbolos(canvas.Canvas):
    """Canvas que dibuja ♪ → etc. con una fuente de respaldo cuando la principal no los tiene."""

    def _segmentos(self, txt):
        segs, cur, sym = [], "", False
        for ch in txt:
            s = ch in _SYMS and SYM != "Poppins"
            if s != sym and cur:
                segs.append((cur, sym))
                cur = ""
            cur += ch
            sym = s
        if cur:
            segs.append((cur, sym))
        return segs

    def _ancho(self, txt):
        return sum(pdfmetrics.stringWidth(t, SYM if s else self._fontname, self._fontsize)
                   for t, s in self._segmentos(txt))

    def drawString(self, x, y, txt, *a, **k):
        txt = str(txt)
        if SYM == "Poppins" or not any(ch in _SYMS for ch in txt):
            return super().drawString(x, y, txt, *a, **k)
        fn, fs = self._fontname, self._fontsize
        for t, s in self._segmentos(txt):
            self.setFont(SYM if s else fn, fs)
            super().drawString(x, y, t)
            x += pdfmetrics.stringWidth(t, SYM if s else fn, fs)
        self.setFont(fn, fs)

    def drawRightString(self, x, y, txt, *a, **k):
        self.drawString(x - self._ancho(str(txt)), y, txt)

    def drawCentredString(self, x, y, txt, *a, **k):
        self.drawString(x - self._ancho(str(txt)) / 2, y, txt)


class Doc:
    def __init__(self, path, data):
        self.c = CanvasSimbolos(path, pagesize=(W, H))
        self.c.setTitle(f"{data['meta']['titulo']} — Guía de rodaje")
        self.c.setAuthor("Histea Studios")
        self.d = data
        self.pie = data["meta"]["pie"]
        self.n = 0
        self.y = TOP0
        self.hdr = None
        self.abierta = False

    # ── coordenadas de arriba hacia abajo
    def Y(self, t):
        return H - t

    def cerrar(self):
        if self.abierta:
            self.c.showPage()
            self.abierta = False

    def fondo(self):
        c = self.c
        c.setFillColor(BG)
        c.rect(0, 0, W, H, stroke=0, fill=1)
        self.n += 1
        self.abierta = True
        c.setFont("Poppins", 7)
        c.setFillColor(GRIS)
        c.drawString(M, self.Y(706), self.pie)
        c.drawRightString(W - M, self.Y(706), str(self.n))

    def pagina(self, eyebrow, titulo):
        self.cerrar()
        self.fondo()
        c = self.c
        c.setFont("Poppins-SemiBold", 7.2)
        c.setFillColor(ORO)
        c.drawString(M, self.Y(32), eyebrow.upper())
        c.setFont("Serif", 24)
        c.setFillColor(CREMA)
        c.drawString(M, self.Y(62), titulo)
        c.setStrokeColor(ORO)
        c.setLineWidth(1.5)
        c.line(M, self.Y(72), M + 26, self.Y(72))
        self.hdr = (eyebrow, titulo)
        self.y = TOP0

    def asegurar(self, h):
        if self.y + h > BOTTOM:
            self.pagina(*self.hdr)
            return True
        return False

    # ── piezas básicas
    def p(self, x, top, w, p):
        h = alto(p, w)
        p.drawOn(self.c, x, self.Y(top) - h)
        return h

    def texto_flujo(self, t, size=8, color=CREMA, gap=8, font="Poppins"):
        pr = para(t, size, color, font)
        h = alto(pr, CW)
        self.asegurar(h)
        self.p(M, self.y, CW, pr)
        self.y += h + gap

    def eyebrow(self, t, gap=8):
        self.asegurar(20)
        self.c.setFont("Poppins-SemiBold", 7.2)
        self.c.setFillColor(ORO)
        self.c.drawString(M, self.Y(self.y + 7), t.upper())
        self.y += 7 + gap

    def tarjeta(self, x, top, w, h, barra=True, fill=CARD):
        c = self.c
        c.setFillColor(fill)
        c.roundRect(x, self.Y(top + h), w, h, 6, stroke=0, fill=1)
        if barra:
            c.saveState()
            pth = c.beginPath()
            pth.roundRect(x, self.Y(top + h), w, h, 6)
            c.clipPath(pth, stroke=0, fill=0)
            c.setFillColor(ORO)
            c.rect(x, self.Y(top + h), 4, h, stroke=0, fill=1)
            c.restoreState()

    def contorno(self, x, top, w, h, color, lw=1.1):
        c = self.c
        c.setStrokeColor(color)
        c.setLineWidth(lw)
        c.roundRect(x, self.Y(top + h), w, h, 6, stroke=1, fill=0)

    def circulo_num(self, x, top, t, d=22, fill=ORO, color=OSC, size=None):
        c = self.c
        r = d / 2
        c.setFillColor(fill)
        c.circle(x + r, self.Y(top + r), r, stroke=0, fill=1)
        size = size or (10 if d >= 20 else 8)
        c.setFont("Poppins-Bold", size)
        c.setFillColor(color)
        c.drawCentredString(x + r, self.Y(top + r) - size * 0.36, str(t))

    def pastilla(self, xr, top, t, oro=True):
        """Insignia alineada a la derecha en xr. Devuelve el nuevo xr."""
        c = self.c
        t = str(t)
        w = pdfmetrics.stringWidth(t, "Poppins-SemiBold", 6.6) + 12
        c.setFillColor(ORO if oro else CREMA)
        c.roundRect(xr - w, self.Y(top + 13), w, 13, 6.5, stroke=0, fill=1)
        c.setFont("Poppins-SemiBold", 6.6)
        c.setFillColor(OSC)
        c.drawCentredString(xr - w / 2, self.Y(top + 9.2), t)
        return xr - w - 4

    def filas_tarjeta(self, filas, x, top, w, lab_w=96, size=7.4, color=OSC, lab_color=GRIS_C,
                      dibujar=True):
        """Filas etiqueta / valor. Devuelve alto."""
        y = top
        for lab, val in filas:
            pl = para(lab, 6.8, lab_color)
            pv = para(val, size, color)
            hv = max(alto(pl, lab_w - 6), alto(pv, w - lab_w))
            if dibujar:
                self.p(x, y + 0.6, lab_w - 6, pl)
                self.p(x + lab_w, y, w - lab_w, pv)
            y += hv + 5
        return y - top - 5 if filas else 0

    def tarjeta_bloque(self, titulo=None, texto=None, filas=None, lab_w=96, barra=True, derecha=None,
                       gap=8, pad=11):
        """Tarjeta clara genérica con título, párrafo y filas. Fluye con salto de página."""
        x, w = M, CW
        ix, iw = x + 14, w - 26
        h = pad
        if titulo:
            h += 13
        if texto:
            h += alto(para(texto, 7.4, OSC), iw) + 5
        if filas:
            h += self.filas_tarjeta(filas, ix, 0, iw, lab_w, dibujar=False) + 4
        h += pad - 4
        self.asegurar(h)
        top = self.y
        self.tarjeta(x, top, w, h, barra=barra)
        y = top + pad
        if titulo:
            self.c.setFont("Poppins-SemiBold", 8.6)
            self.c.setFillColor(OSC)
            self.c.drawString(ix, self.Y(y + 8), titulo)
            if derecha:
                self.c.setFont("Poppins", 6.6)
                self.c.setFillColor(GRIS_C)
                self.c.drawRightString(x + w - 12, self.Y(y + 8), derecha)
            y += 13
        if texto:
            y += self.p(ix, y, iw, para(texto, 7.4, OSC)) + 5
        if filas:
            y += self.filas_tarjeta(filas, ix, y, iw, lab_w) + 4
        self.y = top + h + gap

    def tabla_oscura(self, filas, lab_w=68, size=7.4, gap=3.5, x=M, w=CW):
        """Filas con etiqueta dorada en mayúsculas sobre fondo oscuro."""
        for lab, val in filas:
            if val is None:
                continue
            pl = para(str(lab).upper(), 6.6, ORO, "Poppins-SemiBold")
            pv = val if isinstance(val, Paragraph) else para(val, size, CREMA, lead=1.35)
            h = max(alto(pl, lab_w - 4), alto(pv, w - lab_w))
            self.asegurar(h)
            self.p(x, self.y + 0.8, lab_w - 4, pl)
            self.p(x + lab_w, self.y, w - lab_w, pv)
            self.y += h + gap


# ════════════════════════════════════════════════════════════════════
# 4. DIBUJOS (storyboard, portada, maquetas de título)
# ════════════════════════════════════════════════════════════════════
def col(v, default="azul"):
    v = v or default
    return HexColor(PALETA.get(v, v))


class Lienzo:
    """Dibuja primitivas en coordenadas normalizadas (0–1) dentro de una caja."""

    def __init__(self, doc, x, top, w, h, claro=False):
        self.d, self.c = doc, doc.c
        self.x, self.top, self.w, self.h = x, top, w, h
        self.claro = claro
        self.acento = "mov" if claro else "oro"

    def X(self, u):
        return self.x + u * self.w

    def YY(self, v):
        return self.d.Y(self.top + v * self.h)

    def alpha(self, o):
        self.c.setFillAlpha(o)
        self.c.setStrokeAlpha(o)

    def prim(self, p):
        t = p.get("t")
        c = self.c
        c.saveState()
        self.alpha(p.get("o", 1))
        if t == "rect":
            c.setFillColor(col(p.get("c")))
            r = p.get("r", 0) * self.w
            x, y = self.X(p["x"]), self.YY(p["y"] + p["h"])
            if p.get("borde"):
                c.setStrokeColor(col(p["borde"]))
                c.setLineWidth(p.get("g", 0.8))
            c.roundRect(x, y, p["w"] * self.w, p["h"] * self.h, r,
                        stroke=1 if p.get("borde") else 0, fill=0 if p.get("vacio") else 1)
        elif t == "circ":
            c.setFillColor(col(p.get("c")))
            if p.get("borde"):
                c.setStrokeColor(col(p["borde"]))
                c.setLineWidth(p.get("g", 1))
            c.circle(self.X(p["x"]), self.YY(p["y"]), p["r"] * self.w,
                     stroke=1 if p.get("borde") else 0, fill=0 if p.get("vacio") else 1)
        elif t == "elipse":
            c.setFillColor(col(p.get("c")))
            cx, cy, ww, hh = p["x"], p["y"], p["w"], p["h"]
            c.ellipse(self.X(cx - ww / 2), self.YY(cy + hh / 2), self.X(cx + ww / 2), self.YY(cy - hh / 2),
                      stroke=0, fill=1)
        elif t == "poli":
            c.setFillColor(col(p.get("c")))
            pth = c.beginPath()
            pts = p["p"]
            pth.moveTo(self.X(pts[0][0]), self.YY(pts[0][1]))
            for u, v in pts[1:]:
                pth.lineTo(self.X(u), self.YY(v))
            pth.close()
            if p.get("borde"):
                c.setStrokeColor(col(p["borde"]))
                c.setLineWidth(p.get("g", 0.7))
            c.drawPath(pth, stroke=1 if p.get("borde") else 0, fill=1)
        elif t in ("linea", "flecha"):
            color = col(p.get("c"), self.acento if t == "flecha" else ("linea" if self.claro else "azul_osc"))
            c.setStrokeColor(color)
            c.setFillColor(color)
            c.setLineWidth(p.get("g", 1.6 if t == "flecha" else 0.8))
            c.setLineCap(1)
            if p.get("dash"):
                c.setDash(*p["dash"])
            pts = [(self.X(u), self.YY(v)) for u, v in p["p"]]
            pth = c.beginPath()
            pth.moveTo(*pts[0])
            if p.get("curva") and len(pts) == 3:
                (x0, y0), (x1, y1), (x2, y2) = pts
                pth.curveTo(x0 + 2 / 3 * (x1 - x0), y0 + 2 / 3 * (y1 - y0),
                            x2 + 2 / 3 * (x1 - x2), y2 + 2 / 3 * (y1 - y2), x2, y2)
                ref = (x1, y1)
            else:
                for pt in pts[1:]:
                    pth.lineTo(*pt)
                ref = pts[-2]
            c.drawPath(pth, stroke=1, fill=0)
            if t == "flecha":
                c.setDash()
                ex, ey = pts[-1]
                ang = math.atan2(ey - ref[1], ex - ref[0])
                L = p.get("punta", 6)
                a = c.beginPath()
                a.moveTo(ex, ey)
                a.lineTo(ex - L * math.cos(ang - 0.45), ey - L * math.sin(ang - 0.45))
                a.lineTo(ex - L * math.cos(ang + 0.45), ey - L * math.sin(ang + 0.45))
                a.close()
                c.drawPath(a, stroke=0, fill=1)
                if p.get("doble"):
                    sx, sy = pts[0]
                    nx, ny = pts[1] if not p.get("curva") else ref
                    ang = math.atan2(sy - ny, sx - nx)
                    a = c.beginPath()
                    a.moveTo(sx, sy)
                    a.lineTo(sx - L * math.cos(ang - 0.45), sy - L * math.sin(ang - 0.45))
                    a.lineTo(sx - L * math.cos(ang + 0.45), sy - L * math.sin(ang + 0.45))
                    a.close()
                    c.drawPath(a, stroke=0, fill=1)
        elif t == "arco":
            c.setStrokeColor(col(p.get("c"), self.acento))
            c.setLineWidth(p.get("g", 1.3))
            r = p["r"] * self.w
            cx, cy = self.X(p["x"]), self.YY(p["y"])
            c.arc(cx - r, cy - r, cx + r, cy + r, p.get("ini", 0), p.get("ext", 90))
        elif t == "persona":
            self.persona(p)
        elif t == "texto":
            fuente = {"mano": "Mano", "sans": "Poppins", "negrita": "Poppins-SemiBold",
                      "serif": "Serif", "serif_i": "Serif-Italic"}.get(p.get("f", "mano"), "Mano")
            s = p.get("s", 8)
            c.setFont(fuente, s)
            c.setFillColor(col(p.get("c"), self.acento))
            x, y = self.X(p["x"]), self.YY(p["y"]) - s * 0.35
            a = p.get("a", "centro")
            txt = str(p["t"])
            if p.get("esp"):
                txt = (" " * 0).join(txt)
            if a == "izq":
                c.drawString(x, y, txt)
            elif a == "der":
                c.drawRightString(x, y, txt)
            else:
                c.drawCentredString(x, y, txt)
        elif t == "bokeh":
            rnd = random.Random(p.get("seed", 1))
            ax, ay, aw, ah = p.get("area", [0, 0, 1, 0.5])
            rmin, rmax = p.get("r", [0.015, 0.045])
            cols = p.get("cols", ["oro", "coral", "crema", "azul_osc"])
            for _ in range(p.get("n", 12)):
                c.setFillColor(col(rnd.choice(cols)))
                c.setFillAlpha(p.get("o", 1) * rnd.uniform(0.25, 0.75))
                c.circle(self.X(ax + rnd.random() * aw), self.YY(ay + rnd.random() * ah),
                         rnd.uniform(rmin, rmax) * self.w, stroke=0, fill=1)
        elif t == "haz":
            c.setFillColor(col(p.get("c"), "crema"))
            c.setFillAlpha(p.get("o", 0.12))
            x, y = p["x"], p["y"]
            ang = math.radians(p.get("ang", 90))
            L, A = p.get("largo", 0.8), p.get("ancho", 0.12)
            ex, ey = x + L * math.cos(ang) * self.h / self.w, y + L * math.sin(ang)
            px, py = -math.sin(ang) * A / 2, math.cos(ang) * A / 2
            pth = c.beginPath()
            pth.moveTo(self.X(x), self.YY(y))
            pth.lineTo(self.X(ex + px), self.YY(ey + py * 0))
            pth.lineTo(self.X(ex - px), self.YY(ey - py * 0))
            pth.close()
            c.drawPath(pth, stroke=0, fill=1)
        elif t == "lista":
            self.lista(p)
        elif t == "nota":
            colr = col(p.get("c"), "tinta" if self.claro else "crema")
            c.setStrokeColor(colr)
            c.setFillColor(colr)
            c.setLineWidth(0.6)
            if "px" in p:
                c.line(self.X(p["x"]), self.YY(p["y"]), self.X(p["px"]), self.YY(p["py"]))
                c.circle(self.X(p["px"]), self.YY(p["py"]), 1.3, stroke=0, fill=1)
            c.setFont("Mano", p.get("s", 7.5))
            a = p.get("a", "centro")
            ty = self.YY(p["y"]) + (2.5 if p.get("py", 1) > p["y"] else -8)
            if a == "izq":
                c.drawString(self.X(p["x"]), ty, p["t"])
            elif a == "der":
                c.drawRightString(self.X(p["x"]), ty, p["t"])
            else:
                c.drawCentredString(self.X(p["x"]), ty, p["t"])
        c.restoreState()

    def persona(self, p):
        if self.claro:
            pose = p.get("pose", "brazos_arriba" if p.get("brazos") else "normal")
            muneco(self.c, self.X(p["x"]), self.YY(p["y"]), p.get("h", 0.3) * self.h, pose,
                   p.get("persp", "normal"), p.get("espalda", False))
            return
        c = self.c
        x, pie, h = p["x"], p["y"], p.get("h", 0.3)
        color = col(p.get("c"), "azul")
        c.setFillColor(color)
        escala = min(1.0, ((self.w / self.h) / (16 / 9)) ** 0.5)  # personas proporcionadas en cuadros verticales
        hh = h * self.h * escala
        cx = self.X(x)
        base = self.YY(pie)
        cab = hh * 0.2
        cuerpo_w = hh * 0.38
        cuerpo_h = hh - cab * 1.9
        c.roundRect(cx - cuerpo_w / 2, base, cuerpo_w, cuerpo_h, cuerpo_w * 0.35, stroke=0, fill=1)
        c.circle(cx, base + cuerpo_h + cab * 0.95, cab * 0.9, stroke=0, fill=1)
        if p.get("brazos"):
            c.setStrokeColor(color)
            c.setLineWidth(max(1.2, cuerpo_w * 0.18))
            c.setLineCap(1)
            sh = base + cuerpo_h * 0.85
            c.line(cx - cuerpo_w * 0.4, sh, cx - cuerpo_w * 0.85, sh + cab * 2.4)
            c.line(cx + cuerpo_w * 0.4, sh, cx + cuerpo_w * 0.85, sh + cab * 2.4)

    def lista(self, p):
        c = self.c
        x0, y0, w = p["x"], p["y"], p.get("w", 0.8)
        paso = p.get("paso", 0.085)
        if p.get("titulo"):
            c.setFont("Mano", 8)
            c.setFillColor(ORO)
            c.drawString(self.X(x0), self.YY(y0), p["titulo"])
            y0 += paso
        for i, fila in enumerate(p.get("filas", [])):
            izq, der = (fila + [""])[:2]
            o = 1 if i < p.get("visibles", 99) else 0.4
            c.setFillAlpha(o)
            c.setFont("Poppins", 6.8)
            c.setFillColor(CREMA)
            c.drawString(self.X(x0), self.YY(y0 + i * paso), izq)
            if der:
                c.setFont("Mano", 7.5)
                c.setFillColor(ORO)
                c.drawRightString(self.X(x0 + w), self.YY(y0 + i * paso), der)
            c.setStrokeColor(MARCO)
            c.setLineWidth(0.6)
            c.line(self.X(x0), self.YY(y0 + i * paso + paso * 0.35), self.X(x0 + w),
                   self.YY(y0 + i * paso + paso * 0.35))
        c.setFillAlpha(1)


# ── Escenas prediseñadas: devuelven listas de primitivas
def escena(nombre, n=4, seed=1):
    rnd = random.Random(seed)
    P = []
    suelo = {"t": "elipse", "x": 0.5, "y": 0.86, "w": 1.3, "h": 0.42, "c": "azul_prof"}
    if nombre == "aereo":
        P += [{"t": "linea", "p": [[0.5, 0.42], [x, 1.0]], "c": "azul_prof", "g": 0.7}
              for x in [-0.3, 0.0, 0.25, 0.5, 0.75, 1.0, 1.3]]
        P += [{"t": "linea", "p": [[0, 0.42], [1, 0.42]], "c": "azul_prof", "g": 0.7}]
        P += [{"t": "poli", "p": [[0.36, 0.42], [0.5, 0.28], [0.64, 0.42]], "c": "azul"},
              {"t": "rect", "x": 0.36, "y": 0.42, "w": 0.28, "h": 0.2, "c": "azul"}]
        P += [{"t": "rect", "x": 0.39 + i * 0.05, "y": 0.48, "w": 0.025, "h": 0.06, "c": "oro"} for i in range(5)]
        P += [{"t": "circ", "x": x, "y": 0.5 + rnd.uniform(-0.03, 0.03), "r": 0.033, "c": "azul_osc"}
              for x in [0.12, 0.2, 0.28, 0.72, 0.8, 0.88]]
        P += [{"t": "circ", "x": 0.82, "y": 0.2, "r": 0.06, "c": "coral", "o": 0.9}]
    elif nombre == "exterior_noche":
        P += [{"t": "bokeh", "n": 14, "seed": seed, "area": [0, 0, 1, 0.35], "r": [0.003, 0.008],
               "cols": ["crema"]}]
        P += [{"t": "rect", "x": 0.15, "y": 0.2, "w": 0.7, "h": 0.62, "c": "azul_prof"},
              {"t": "rect", "x": 0.42, "y": 0.42, "w": 0.16, "h": 0.4, "c": "oro", "o": 0.95},
              {"t": "rect", "x": 0.0, "y": 0.82, "w": 1, "h": 0.18, "c": "azul_prof", "o": 0.6}]
        P += [{"t": "persona", "x": x, "y": 0.93, "h": 0.32, "c": "cuadro"} for x in [0.44, 0.52, 0.6][:max(1, n)]]
    elif nombre in ("interior", "salon"):
        P += [{"t": "bokeh", "n": 16, "seed": seed, "area": [0, 0, 1, 0.45]}, suelo]
        P += [{"t": "persona", "x": 0.15 + i * (0.7 / max(1, n - 1)), "y": 0.86, "h": rnd.uniform(0.34, 0.42),
               "c": rnd.choice(["azul", "azul_osc", "rosa", "verde"])} for i in range(n)] if n else []
    elif nombre == "mesa":
        P += [{"t": "bokeh", "n": 14, "seed": seed, "area": [0, 0, 1, 0.45]},
              {"t": "elipse", "x": 0.5, "y": 0.78, "w": 1.0, "h": 0.34, "c": "azul_osc"},
              {"t": "elipse", "x": 0.5, "y": 0.76, "w": 0.9, "h": 0.26, "c": "crema", "o": 0.9}]
        P += [{"t": "rect", "x": 0.47, "y": 0.52, "w": 0.06, "h": 0.2, "c": "azul"},
              {"t": "circ", "x": 0.5, "y": 0.5, "r": 0.05, "c": "rosa"},
              {"t": "circ", "x": 0.47, "y": 0.47, "r": 0.035, "c": "coral"},
              {"t": "circ", "x": 0.53, "y": 0.46, "r": 0.03, "c": "crema"}]
        for x in [0.25, 0.33, 0.67, 0.75]:
            P += [{"t": "circ", "x": x, "y": 0.66, "r": 0.02, "c": "crema", "vacio": True, "borde": "crema", "g": 0.8},
                  {"t": "linea", "p": [[x, 0.7], [x, 0.76]], "c": "crema", "g": 0.8}]
    elif nombre == "retrato":
        P += [{"t": "bokeh", "n": 18, "seed": seed, "area": [0, 0, 1, 0.8], "r": [0.02, 0.06]},
              {"t": "persona", "x": p_x(n), "y": 1.25, "h": 1.0, "c": "azul"}]
    elif nombre == "grupo":
        P += [{"t": "bokeh", "n": 12, "seed": seed, "area": [0, 0, 1, 0.4]}, suelo]
        n = max(2, n)
        P += [{"t": "persona", "x": 0.2 + i * (0.6 / (n - 1)), "y": 0.84, "h": rnd.uniform(0.44, 0.52),
               "c": ["azul", "rosa", "verde", "azul_osc", "coral", "violeta"][i % 6]} for i in range(n)]
    elif nombre == "podio":
        P += [{"t": "bokeh", "n": 10, "seed": seed, "area": [0, 0, 1, 0.3]},
              {"t": "rect", "x": 0, "y": 0.58, "w": 1, "h": 0.06, "c": "azul_prof"},
              {"t": "persona", "x": 0.5, "y": 0.6, "h": 0.42, "c": "azul"},
              {"t": "poli", "p": [[0.43, 0.6], [0.57, 0.6], [0.55, 0.42], [0.45, 0.42]], "c": "azul_osc"},
              {"t": "circ", "x": 0.5, "y": 0.4, "r": 0.008, "c": "oro"}]
        P += [{"t": "circ", "x": 0.06 + i * 0.11, "y": 0.86 + (i % 2) * 0.04, "r": 0.04, "c": "azul_osc"} for i in range(9)]
    elif nombre == "pista":
        P += [{"t": "haz", "x": x, "y": 0.0, "ang": a, "largo": 0.95, "ancho": 0.18,
               "c": c_, "o": 0.18} for x, a, c_ in [(0.15, 70, "violeta"), (0.5, 95, "crema"), (0.85, 110, "celeste")]]
        P += [{"t": "elipse", "x": 0.5, "y": 0.72, "w": 1.1, "h": 0.25, "c": "crema", "o": 0.08}, suelo]
        P += [{"t": "persona", "x": 0.08 + i * (0.84 / max(1, n - 1)), "y": 0.9 + rnd.uniform(-0.03, 0.03),
               "h": rnd.uniform(0.36, 0.46), "c": ["violeta", "rosa", "celeste", "coral", "azul"][i % 5],
               "brazos": i % 2 == 0} for i in range(max(1, n))]
    elif nombre == "pantalla":
        P += [{"t": "rect", "x": 0.2, "y": 0.08, "w": 0.6, "h": 0.32, "c": "crema", "o": 0.9},
              {"t": "haz", "x": 0.5, "y": 0.4, "ang": 90, "largo": 0.6, "ancho": 0.8, "c": "crema", "o": 0.1}]
        P += [{"t": "circ", "x": 0.15 + i * 0.14, "y": 0.78 + (i % 2) * 0.05, "r": 0.06, "c": "crema", "o": 0.75}
              for i in range(6)]
    elif nombre == "detalle":
        P += [{"t": "bokeh", "n": 20, "seed": seed, "area": [0, 0, 1, 1], "r": [0.03, 0.08], "o": 0.7}]
    elif nombre == "plato":
        P += [{"t": "rect", "x": 0, "y": 0, "w": 1, "h": 1, "c": "azul_prof"},
              {"t": "circ", "x": 0.5, "y": 0.52, "r": 0.24, "c": "crema"},
              {"t": "circ", "x": 0.5, "y": 0.52, "r": 0.17, "c": "blanco", "o": 0.9},
              {"t": "elipse", "x": 0.45, "y": 0.47, "w": 0.16, "h": 0.14, "c": "coral"},
              {"t": "elipse", "x": 0.56, "y": 0.52, "w": 0.13, "h": 0.12, "c": "verde"},
              {"t": "elipse", "x": 0.5, "y": 0.58, "w": 0.1, "h": 0.08, "c": "oro"},
              {"t": "linea", "p": [[0.12, 0.25], [0.12, 0.8]], "c": "gris", "g": 1.6},
              {"t": "linea", "p": [[0.88, 0.25], [0.88, 0.8]], "c": "gris", "g": 1.6}]
    elif nombre == "cocina":
        P += [{"t": "bokeh", "n": 8, "seed": seed, "area": [0, 0, 1, 0.35], "cols": ["crema", "oro"]},
              {"t": "persona", "x": 0.5, "y": 0.78, "h": 0.6, "c": "crema"},
              {"t": "rect", "x": 0, "y": 0.68, "w": 1, "h": 0.32, "c": "azul_osc"},
              {"t": "elipse", "x": 0.5, "y": 0.66, "w": 0.34, "h": 0.07, "c": "gris"},
              {"t": "poli", "p": [[0.42, 0.66], [0.46, 0.55], [0.5, 0.62], [0.54, 0.52], [0.58, 0.66]], "c": "coral", "o": 0.9},
              {"t": "poli", "p": [[0.46, 0.66], [0.5, 0.58], [0.54, 0.66]], "c": "oro"}]
        P += [{"t": "linea", "p": [[x, 0.5], [x - 0.02, 0.38], [x + 0.02, 0.26]], "c": "crema", "g": 0.8, "o": 0.4}
              for x in [0.44, 0.5, 0.56]]
    elif nombre == "foodtruck":
        P += [{"t": "bokeh", "n": 18, "seed": seed, "area": [0, 0.02, 1, 0.12], "r": [0.006, 0.012], "cols": ["oro", "crema"]},
              {"t": "rect", "x": 0, "y": 0.82, "w": 1, "h": 0.18, "c": "azul_prof"},
              {"t": "rect", "x": 0.15, "y": 0.3, "w": 0.7, "h": 0.46, "c": "coral", "r": 0.03},
              {"t": "rect", "x": 0.25, "y": 0.38, "w": 0.42, "h": 0.2, "c": "oro", "o": 0.95},
              {"t": "poli", "p": [[0.22, 0.38], [0.7, 0.38], [0.74, 0.3], [0.18, 0.3]], "c": "crema", "o": 0.9},
              {"t": "rect", "x": 0.25, "y": 0.58, "w": 0.42, "h": 0.03, "c": "crema"},
              {"t": "circ", "x": 0.3, "y": 0.78, "r": 0.05, "c": "cuadro"},
              {"t": "circ", "x": 0.72, "y": 0.78, "r": 0.05, "c": "cuadro"}]
        P += [{"t": "persona", "x": 0.08 + i * 0.07, "y": 0.92, "h": 0.32, "c": ["azul", "rosa", "verde"][i % 3]}
              for i in range(min(n, 3))]
    elif nombre == "gym":
        P += [{"t": "rect", "x": 0.05, "y": 0.08, "w": 0.9, "h": 0.6, "c": "azul_prof", "o": 0.6},
              {"t": "rect", "x": 0, "y": 0.84, "w": 1, "h": 0.16, "c": "azul_osc"},
              {"t": "persona", "x": 0.5, "y": 0.86, "h": 0.5, "c": "azul", "brazos": True},
              {"t": "linea", "p": [[0.15, 0.3], [0.85, 0.3]], "c": "gris", "g": 2.4},
              {"t": "rect", "x": 0.14, "y": 0.2, "w": 0.05, "h": 0.2, "c": "crema", "r": 0.01},
              {"t": "rect", "x": 0.81, "y": 0.2, "w": 0.05, "h": 0.2, "c": "crema", "r": 0.01}]
    elif nombre == "dj":
        P += [{"t": "haz", "x": x, "y": 0.0, "ang": a, "largo": 0.95, "ancho": 0.2, "c": c_, "o": 0.2}
              for x, a, c_ in [(0.2, 75, "violeta"), (0.8, 105, "celeste"), (0.5, 90, "rosa")]]
        P += [{"t": "persona", "x": 0.5, "y": 0.62, "h": 0.42, "c": "azul", "brazos": True},
              {"t": "rect", "x": 0.2, "y": 0.58, "w": 0.6, "h": 0.16, "c": "azul_osc", "r": 0.02},
              {"t": "circ", "x": 0.34, "y": 0.62, "r": 0.035, "c": "violeta", "o": 0.9},
              {"t": "circ", "x": 0.66, "y": 0.62, "r": 0.035, "c": "celeste", "o": 0.9}]
        P += [{"t": "circ", "x": 0.05 + i * 0.1, "y": 0.92 + (i % 2) * 0.04, "r": 0.045, "c": "azul_prof"}
              for i in range(10)]
    elif nombre == "barra":
        P += [{"t": "rect", "x": 0, "y": 0.12, "w": 1, "h": 0.03, "c": "azul_osc"},
              {"t": "rect", "x": 0, "y": 0.36, "w": 1, "h": 0.03, "c": "azul_osc"}]
        P += [{"t": "rect", "x": 0.05 + i * 0.105, "y": y - 0.11, "w": 0.045, "h": 0.11,
               "c": ["oro", "verde", "coral", "crema", "rosa"][(i + k) % 5], "r": 0.01, "o": 0.85}
              for k, y in enumerate([0.12, 0.36]) for i in range(9)]
        P += [{"t": "persona", "x": 0.55, "y": 0.8, "h": 0.5, "c": "azul"},
              {"t": "rect", "x": 0, "y": 0.72, "w": 1, "h": 0.28, "c": "azul_osc"},
              {"t": "poli", "p": [[0.28, 0.6], [0.36, 0.6], [0.34, 0.7], [0.3, 0.7]], "c": "crema", "o": 0.8}]
    elif nombre == "naturaleza":
        P += [{"t": "poli", "p": [[0, 0.65], [0.25, 0.3], [0.45, 0.6], [0.65, 0.25], [1, 0.62], [1, 1], [0, 1]],
               "c": "azul_prof"},
              {"t": "poli", "p": [[0, 0.8], [0.35, 0.55], [0.7, 0.8], [1, 0.7], [1, 1], [0, 1]], "c": "azul_osc"},
              {"t": "circ", "x": 0.78, "y": 0.2, "r": 0.05, "c": "coral", "o": 0.9}]
    return P


def p_x(n):
    return 0.5 if not isinstance(n, (int, float)) or n <= 1 else 0.38


def movimiento(tipo, etiqueta=None):
    """Flechas doradas prediseñadas para el movimiento de cámara."""
    F = []
    if tipo == "avance":
        F = [{"t": "flecha", "p": [[0.5, 0.95], [0.5, 0.62]]}]
    elif tipo == "retroceso":
        F = [{"t": "flecha", "p": [[0.5, 0.62], [0.5, 0.95]]},
             {"t": "flecha", "p": [[0.3, 0.3], [0.12, 0.15]], "g": 1.1},
             {"t": "flecha", "p": [[0.7, 0.3], [0.88, 0.15]], "g": 1.1}]
    elif tipo in ("lateral", "lateral_der"):
        F = [{"t": "flecha", "p": [[0.18, 0.93], [0.62, 0.93]]}]
    elif tipo == "lateral_izq":
        F = [{"t": "flecha", "p": [[0.82, 0.93], [0.38, 0.93]]}]
    elif tipo == "orbita":
        F = [{"t": "flecha", "p": [[0.18, 0.88], [0.5, 1.05], [0.82, 0.88]], "curva": True}]
    elif tipo in ("sube", "pedestal"):
        F = [{"t": "flecha", "p": [[0.08, 0.8], [0.06, 0.55], [0.1, 0.3]], "curva": True}]
    elif tipo == "baja":
        F = [{"t": "flecha", "p": [[0.08, 0.3], [0.06, 0.55], [0.1, 0.8]], "curva": True}]
    elif tipo == "giro":
        F = [{"t": "arco", "x": 0.5, "y": 0.5, "r": 0.12, "ini": 30, "ext": 300, "g": 1.6},
             {"t": "flecha", "p": [[0.585, 0.37], [0.6, 0.39]], "g": 1.6}]
    elif tipo == "paneo":
        F = [{"t": "flecha", "p": [[0.2, 0.12], [0.5, 0.04], [0.8, 0.12]], "curva": True}]
    elif tipo == "paneo_ida_vuelta":
        F = [{"t": "flecha", "p": [[0.25, 0.1], [0.5, 0.03], [0.75, 0.1]], "curva": True, "doble": True}]
    elif tipo == "barrido":
        F = [{"t": "linea", "p": [[0.1, y], [0.55, y]], "c": "crema", "g": 0.7, "o": 0.5} for y in [0.3, 0.42, 0.54, 0.66]]
        F += [{"t": "flecha", "p": [[0.2, 0.9], [0.8, 0.9]], "g": 2}]
    elif tipo == "zoom":
        F = [{"t": "flecha", "p": [[0.15, 0.15], [0.3, 0.28]], "g": 1.1},
             {"t": "flecha", "p": [[0.85, 0.15], [0.7, 0.28]], "g": 1.1},
             {"t": "flecha", "p": [[0.15, 0.85], [0.3, 0.72]], "g": 1.1},
             {"t": "flecha", "p": [[0.85, 0.85], [0.7, 0.72]], "g": 1.1}]
    if etiqueta:
        F.append({"t": "texto", "x": 0.5 if tipo not in ("sube", "baja", "pedestal") else 0.15,
                  "y": 0.06 if tipo not in ("avance", "retroceso", "lateral", "lateral_izq", "lateral_der", "orbita", "barrido") else 0.82,
                  "t": etiqueta, "s": 8, "a": "centro" if tipo not in ("sube", "baja", "pedestal") else "izq"})
    return F


def iconos(nombre):
    """Íconos de portada en caja cuadrada normalizada (dorado)."""
    O = "oro"
    if nombre == "campana":
        return ([{"t": "arco", "x": 0.5, "y": 0.42, "r": r, "ini": a, "ext": 50, "g": 1.3, "c": "gris"}
                 for r in [0.28, 0.38, 0.48] for a in [20, 110]] +
                [{"t": "poli", "p": [[0.28, 0.75], [0.32, 0.62], [0.33, 0.4], [0.4, 0.3], [0.5, 0.27], [0.6, 0.3],
                                     [0.67, 0.4], [0.68, 0.62], [0.72, 0.75]], "c": O},
                 {"t": "rect", "x": 0.25, "y": 0.75, "w": 0.5, "h": 0.05, "c": O, "r": 0.02},
                 {"t": "circ", "x": 0.5, "y": 0.85, "r": 0.04, "c": O},
                 {"t": "circ", "x": 0.5, "y": 0.25, "r": 0.03, "c": O}])
    if nombre == "camara":
        return [{"t": "rect", "x": 0.18, "y": 0.35, "w": 0.64, "h": 0.42, "c": O, "r": 0.06},
                {"t": "rect", "x": 0.3, "y": 0.27, "w": 0.18, "h": 0.1, "c": O, "r": 0.02},
                {"t": "circ", "x": 0.5, "y": 0.56, "r": 0.14, "c": "fondo"},
                {"t": "circ", "x": 0.5, "y": 0.56, "r": 0.1, "c": O},
                {"t": "circ", "x": 0.5, "y": 0.56, "r": 0.05, "c": "fondo"}]
    if nombre == "claqueta":
        return [{"t": "rect", "x": 0.2, "y": 0.42, "w": 0.6, "h": 0.38, "c": O, "r": 0.03},
                {"t": "poli", "p": [[0.2, 0.4], [0.78, 0.26], [0.8, 0.34], [0.22, 0.48]], "c": O},
                {"t": "linea", "p": [[0.28, 0.55], [0.72, 0.55]], "c": "fondo", "g": 2},
                {"t": "linea", "p": [[0.28, 0.65], [0.6, 0.65]], "c": "fondo", "g": 2}]
    if nombre == "birrete":
        return [{"t": "poli", "p": [[0.15, 0.42], [0.5, 0.28], [0.85, 0.42], [0.5, 0.56]], "c": O},
                {"t": "poli", "p": [[0.3, 0.5], [0.3, 0.68], [0.5, 0.75], [0.7, 0.68], [0.7, 0.5], [0.5, 0.58]], "c": O},
                {"t": "linea", "p": [[0.8, 0.44], [0.8, 0.7]], "c": O, "g": 1.5},
                {"t": "circ", "x": 0.8, "y": 0.72, "r": 0.025, "c": O}]
    if nombre == "anillos":
        return [{"t": "circ", "x": 0.42, "y": 0.55, "r": 0.17, "vacio": True, "borde": O, "g": 4},
                {"t": "circ", "x": 0.6, "y": 0.55, "r": 0.17, "vacio": True, "borde": O, "g": 4}]
    if nombre == "montana":
        return [{"t": "poli", "p": [[0.12, 0.78], [0.42, 0.32], [0.58, 0.55], [0.68, 0.42], [0.9, 0.78]], "c": O},
                {"t": "circ", "x": 0.72, "y": 0.26, "r": 0.06, "c": O}]
    if nombre == "copa":
        return [{"t": "poli", "p": [[0.32, 0.25], [0.68, 0.25], [0.6, 0.5], [0.4, 0.5]], "c": O},
                {"t": "rect", "x": 0.48, "y": 0.5, "w": 0.04, "h": 0.22, "c": O},
                {"t": "rect", "x": 0.36, "y": 0.72, "w": 0.28, "h": 0.04, "c": O, "r": 0.02}]
    return iconos("camara")


# ════════════════════════════════════════════════════════════════════
# 4b. ESTILO DIAGRAMA (storyboard): papel claro, perspectiva, muñecos
#     y vista lateral de la cámara con su cono de visión.
# ════════════════════════════════════════════════════════════════════
PAPEL = HexColor("#F4F7FB")
TINTA = HexColor("#2A3A55")
LINEA_P = HexColor("#A9BED3")
HORIZ = HexColor("#6F8BA8")
NAR = HexColor("#EDA53A")
NAR_OSC = HexColor("#B8681F")
AMAR = HexColor("#F3C969")
MOV = HexColor("#2563A8")

ANGULOS = {"normal": "normal", "contrapicado": "contrapicado", "picado": "picado",
           "cenital": "cenital", "nadir": "nadir", "holandes": "holandés"}


def angulo_de(t):
    a = (t.get("dibujo") or {}).get("angulo")
    if a:
        return a.replace("é", "e").replace("holandés", "holandes")
    txt = f"{t.get('plano', '')} {t.get('intencion', '')}".lower().replace("luz cenital", "")
    for clave, val in [("contrapicado", "contrapicado"), ("picado", "picado"), ("cenital", "cenital"),
                       ("nadir", "nadir"), ("holand", "holandes"), ("aéreo", "picado")]:
        if clave in txt:
            return val
    return "normal"


def escala_plano(plano):
    p = (plano or "").lower()
    tabla = [("gran plano general", "gpg", 0.24), ("detalle", "det", 0), ("recurso", "det", 0),
             ("primerísimo", "pp", 3.2), ("primer plano", "pp", 2.8), ("medio corto", "pmc", 1.9),
             ("americano", "pa", 1.1), ("medio largo", "pa", 1.1), ("medio", "pm", 1.45),
             ("entero", "pe", 0.8), ("general", "pg", 0.5), ("aéreo", "gpg", 0.18)]
    for k, cod, h in tabla:
        if k in p:
            return cod, h
    return "pg", 0.5


# fracción del cuerpo (desde la cabeza) que queda en el borde inferior en planos cerrados
CORTE = {"pa": 0.75, "pm": 0.55, "pmc": 0.4, "pp": 0.3}


ROPA_TERNO = HexColor("#34405A")
ROPA_TERNO_B = HexColor("#1B2638")


def muneco(c, cx, pies, H, pose="normal", persp="normal", espalda=False, fill=NAR, borde=NAR_OSC,
           ropa=None, color_ropa=None):
    """Muñeco estilo diagrama. pies = y (página) de los pies; H = alto en puntos.
    ropa: None, "terno", "vestido", "novia", "casual", "chef"."""
    top = pies + H
    Y = lambda t: top - t * H
    r = {"picado": 0.13, "contrapicado": 0.085}.get(persp, 0.1) * H
    abre = {"contrapicado": 0.14, "picado": 0.07}.get(persp, 0.09) * H
    grosor = max(1.2, 0.1 * H)
    o = max(0.6, 0.018 * H)
    cr = HexColor(PALETA.get(color_ropa, color_ropa)) if color_ropa else None
    piel, piel_b = fill, borde
    torso_c, torso_b = piel, piel_b
    brazo_c, brazo_b = piel, piel_b
    pierna_c, pierna_b = piel, piel_b
    if ropa == "terno":
        torso_c = brazo_c = pierna_c = cr or ROPA_TERNO
        torso_b = brazo_b = pierna_b = ROPA_TERNO_B
    elif ropa == "vestido":
        torso_c, torso_b = cr or HexColor("#C38D9E"), HexColor("#7E5563")
    elif ropa == "novia":
        torso_c, torso_b = HexColor("#FFFFFF"), HexColor("#9AA8BA")
    elif ropa == "casual":
        torso_c, torso_b = cr or HexColor("#6FA8DC"), HexColor("#3E6C96")
        pierna_c, pierna_b = HexColor("#3D5A80"), HexColor("#26384F")
    elif ropa == "chef":
        torso_c, torso_b = HexColor("#FFFFFF"), HexColor("#9AA8BA")
        brazo_c, brazo_b = torso_c, torso_b
        pierna_c, pierna_b = ROPA_TERNO, ROPA_TERNO_B
    c.saveState()
    c.setLineCap(1)
    c.setLineJoin(1)

    def miembro(colr, x0, y0, x1, y1, x2=None, y2=None):
        for ancho, cc in ((grosor + 2 * o, colr[1]), (grosor, colr[0])):
            c.setStrokeColor(cc)
            c.setLineWidth(ancho)
            p = c.beginPath()
            p.moveTo(x0, y0)
            p.lineTo(x1, y1)
            if x2 is not None:
                p.lineTo(x2, y2)
            c.drawPath(p, stroke=1, fill=0)

    hip = Y(0.57)
    miembro((pierna_c, pierna_b), cx - 0.055 * H, hip, cx - abre, Y(1.0))
    miembro((pierna_c, pierna_b), cx + 0.055 * H, hip, cx + abre, Y(1.0))
    if ropa == "novia":  # velo detrás
        c.setFillColor(HexColor("#FFFFFF"))
        c.setFillAlpha(0.55)
        p = c.beginPath()
        p.moveTo(cx - r * 0.9, Y(0.06))
        p.lineTo(cx - 0.24 * H, Y(0.62))
        p.lineTo(cx + 0.24 * H, Y(0.62))
        p.lineTo(cx + r * 0.9, Y(0.06))
        p.close()
        c.drawPath(p, stroke=0, fill=1)
        c.setFillAlpha(1)
    sh = Y(0.28)
    brazos = {
        "normal": [((cx - 0.12 * H, sh), (cx - 0.17 * H, Y(0.56)), None),
                   ((cx + 0.12 * H, sh), (cx + 0.17 * H, Y(0.56)), None)],
        "saluda": [((cx - 0.12 * H, sh), (cx - 0.2 * H, Y(0.42)), (cx - 0.12 * H, Y(0.55))),
                   ((cx + 0.12 * H, sh), (cx + 0.24 * H, Y(0.2)), (cx + 0.22 * H, Y(0.04)))],
        "brazos_arriba": [((cx - 0.12 * H, sh), (cx - 0.2 * H, Y(0.12)), (cx - 0.22 * H, Y(-0.04))),
                          ((cx + 0.12 * H, sh), (cx + 0.2 * H, Y(0.12)), (cx + 0.22 * H, Y(-0.04)))],
        "jarras": [((cx - 0.12 * H, sh), (cx - 0.22 * H, Y(0.42)), (cx - 0.12 * H, Y(0.55))),
                   ((cx + 0.12 * H, sh), (cx + 0.22 * H, Y(0.42)), (cx + 0.12 * H, Y(0.55)))],
        "abrazo": [((cx - 0.12 * H, sh), (cx - 0.26 * H, Y(0.36)), None),
                   ((cx + 0.12 * H, sh), (cx + 0.26 * H, Y(0.36)), None)],
        "brindis": [((cx - 0.12 * H, sh), (cx - 0.17 * H, Y(0.56)), None),
                    ((cx + 0.12 * H, sh), (cx + 0.24 * H, Y(0.36)), (cx + 0.2 * H, Y(0.16)))],
        "manos_juntas": [((cx - 0.12 * H, sh), (cx - 0.12 * H, Y(0.44)), (cx, Y(0.42))),
                         ((cx + 0.12 * H, sh), (cx + 0.12 * H, Y(0.44)), (cx, Y(0.42)))],
    }.get(pose, None) or []
    for a, b, d in brazos:
        if d:
            miembro((brazo_c, brazo_b), a[0], a[1], b[0], b[1], d[0], d[1])
        else:
            miembro((brazo_c, brazo_b), a[0], a[1], b[0], b[1])
    if pose == "brindis":   # copa en la mano levantada
        c.setStrokeColor(TINTA)
        c.setLineWidth(max(0.5, 0.012 * H))
        c.setFillColor(HexColor("#FFFFFF"))
        gx, gy = cx + 0.2 * H, Y(0.13)
        p = c.beginPath()
        p.moveTo(gx - 0.035 * H, gy + 0.08 * H)
        p.lineTo(gx + 0.035 * H, gy + 0.08 * H)
        p.lineTo(gx, gy)
        p.close()
        c.drawPath(p, stroke=1, fill=1)
    # torso
    tw = 0.27 * H
    c.setFillColor(torso_c)
    c.setStrokeColor(torso_b)
    c.setLineWidth(o)
    c.roundRect(cx - tw / 2, Y(0.62), tw, (0.62 - 0.2) * H, tw * 0.45, stroke=1, fill=1)
    if ropa in ("vestido", "novia"):  # falda
        largo = 1.0 if ropa == "novia" else 0.9
        ancho = 0.3 if ropa == "novia" else 0.22
        p = c.beginPath()
        p.moveTo(cx - 0.12 * H, Y(0.5))
        p.lineTo(cx - ancho * H, Y(largo))
        p.lineTo(cx + ancho * H, Y(largo))
        p.lineTo(cx + 0.12 * H, Y(0.5))
        p.close()
        c.drawPath(p, stroke=1, fill=1)
    if ropa == "terno" and not espalda:  # camisa y corbata
        c.setFillColor(HexColor("#FFFFFF"))
        p = c.beginPath()
        p.moveTo(cx - 0.055 * H, Y(0.2))
        p.lineTo(cx + 0.055 * H, Y(0.2))
        p.lineTo(cx, Y(0.38))
        p.close()
        c.drawPath(p, stroke=0, fill=1)
        c.setStrokeColor(HexColor("#8C2F39"))
        c.setLineWidth(max(0.8, 0.025 * H))
        c.line(cx, Y(0.22), cx, Y(0.34))
    # cabeza
    c.setFillColor(piel)
    c.setStrokeColor(piel_b)
    c.setLineWidth(o)
    c.circle(cx, Y(0.11), r, stroke=1, fill=1)
    if ropa == "chef":
        c.setFillColor(HexColor("#FFFFFF"))
        c.setStrokeColor(HexColor("#9AA8BA"))
        c.roundRect(cx - r * 0.8, Y(0.11) + r * 0.7, r * 1.6, r * 0.7, r * 0.2, stroke=1, fill=1)
        c.circle(cx, Y(0.11) + r * 1.55, r * 0.75, stroke=1, fill=1)
    if H > 42 and not espalda:
        c.setFillColor(TINTA)
        c.circle(cx - r * 0.33, Y(0.11) + r * 0.15, max(0.5, r * 0.08), stroke=0, fill=1)
        c.circle(cx + r * 0.33, Y(0.11) + r * 0.15, max(0.5, r * 0.08), stroke=0, fill=1)
        c.setStrokeColor(TINTA)
        c.setLineWidth(max(0.5, r * 0.06))
        c.arc(cx - r * 0.42, Y(0.11) - r * 0.55, cx + r * 0.42, Y(0.11) + r * 0.05, 200, 140)
    c.restoreState()


def muneco_cenital(c, cx, cy, s, fill=NAR, borde=NAR_OSC):
    c.saveState()
    c.setFillColor(fill)
    c.setStrokeColor(borde)
    c.setLineWidth(max(0.6, s * 0.03))
    c.ellipse(cx - s * 0.32, cy - s * 0.13, cx + s * 0.32, cy + s * 0.13, stroke=1, fill=1)
    c.circle(cx, cy, s * 0.14, stroke=1, fill=1)
    c.restoreState()


def piso(L, angulo, vx=0.5):
    """Líneas de perspectiva y horizonte. Devuelve la altura del horizonte (0–1)."""
    c = L.c
    c.saveState()
    c.setStrokeColor(LINEA_P)
    c.setLineWidth(0.55)
    if angulo == "cenital":
        paso = L.h / 6
        x = L.x
        while x <= L.x + L.w:
            c.line(x, L.YY(0), x, L.YY(1))
            x += paso
        for k in range(7):
            c.line(L.X(0), L.YY(k / 6), L.X(1), L.YY(k / 6))
        c.restoreState()
        return None
    if angulo == "nadir":
        cx, cy = L.X(0.5), L.YY(0.5)
        for k in range(16):
            a = 2 * math.pi * k / 16
            c.line(cx, cy, cx + math.cos(a) * L.w, cy + math.sin(a) * L.w)
        c.setStrokeAlpha(0.5)
        for rr in (0.15, 0.32, 0.55):
            c.circle(cx, cy, rr * L.w, stroke=1, fill=0)
        c.restoreState()
        return 0.5
    hz = {"contrapicado": 0.8, "picado": 0.05}.get(angulo, 0.36)
    vxp, vyp = L.X(vx), L.YY(hz)
    for k in range(-9, 10):
        c.line(vxp, vyp, L.X(vx + k * 0.17), L.YY(1.0))
    for i in range(1, 7):
        t = (i / 6.6) ** 1.9
        y = hz + (1 - hz) * t
        c.line(L.X(0), L.YY(y), L.X(1), L.YY(y))
    if angulo == "contrapicado":
        c.setStrokeAlpha(0.55)
        for k in range(-9, 10):
            c.line(vxp, vyp, L.X(vx + k * 0.17), L.YY(0.0))
        for i in range(1, 6):
            t = (i / 5.6) ** 1.9
            c.line(L.X(0), L.YY(hz - hz * t), L.X(1), L.YY(hz - hz * t))
        c.setStrokeAlpha(1)
    c.setStrokeColor(HORIZ)
    c.setLineWidth(0.9)
    c.line(L.X(0), vyp, L.X(1), vyp)
    c.restoreState()
    return hz


# escenas: (fondo, frente, posiciones de personas, personas por defecto, pose por defecto)
def escena_diagrama(nombre, seed=1):
    rnd = random.Random(seed)
    F, R = [], []
    slots, n, pose = None, 0, "normal"
    luces = [{"t": "circ", "x": 0.06 + i * 0.08, "y": 0.06 + 0.04 * math.sin(i * 0.9), "r": 0.009,
              "c": "amarillo", "borde": "naranja_osc", "g": 0.4} for i in range(12)]
    if nombre == "aereo":
        F = [{"t": "rect", "x": 0.36, "y": 0.42, "w": 0.28, "h": 0.22, "c": "blanco", "borde": "tinta", "g": 0.8},
             {"t": "poli", "p": [[0.34, 0.42], [0.5, 0.28], [0.66, 0.42]], "c": "linea"}]
        F += [{"t": "rect", "x": 0.39 + i * 0.05, "y": 0.48, "w": 0.025, "h": 0.06, "c": "amarillo"} for i in range(5)]
        F += [{"t": "circ", "x": x, "y": 0.58, "r": 0.03, "c": "verde", "o": 0.8} for x in (0.18, 0.26, 0.74, 0.82)]
        F += [{"t": "circ", "x": 0.85, "y": 0.14, "r": 0.05, "c": "amarillo"}]
    elif nombre == "exterior_noche":
        F = [{"t": "rect", "x": 0.18, "y": 0.12, "w": 0.64, "h": 0.66, "c": "gris_claro", "borde": "tinta", "g": 0.8},
             {"t": "rect", "x": 0.42, "y": 0.4, "w": 0.16, "h": 0.38, "c": "amarillo", "borde": "tinta", "g": 0.8}] + luces
        slots, n = [0.44, 0.52, 0.6], 2
    elif nombre in ("interior", "salon"):
        F = luces
        n = 3
    elif nombre == "mesa":
        F = luces
        R = [{"t": "elipse", "x": 0.5, "y": 0.8, "w": 0.95, "h": 0.3, "c": "blanco"},
             {"t": "elipse", "x": 0.5, "y": 0.8, "w": 0.95, "h": 0.3, "c": "linea", "o": 0.25}]
        R += [{"t": "circ", "x": x, "y": 0.8, "r": 0.035, "c": "blanco", "borde": "tinta", "g": 0.6} for x in (0.25, 0.42, 0.58, 0.75)]
        R += [{"t": "circ", "x": 0.5, "y": 0.72, "r": 0.04, "c": "rosa"}, {"t": "circ", "x": 0.47, "y": 0.69, "r": 0.025, "c": "naranja"}]
        slots, n = [0.3, 0.5, 0.7], 0
    elif nombre == "retrato":
        F = [{"t": "bokeh", "n": 14, "seed": seed, "area": [0, 0, 1, 0.7], "r": [0.02, 0.05],
              "cols": ["amarillo", "naranja", "linea"], "o": 0.6}]
        slots, n = [0.5], 1
    elif nombre == "grupo":
        F = luces
        n = 4
    elif nombre == "podio":
        F = [{"t": "rect", "x": 0.1, "y": 0.1, "w": 0.8, "h": 0.12, "c": "linea", "o": 0.4}]
        R = [{"t": "poli", "p": [[0.42, 0.92], [0.58, 0.92], [0.56, 0.62], [0.44, 0.62]], "c": "tinta"}]
        R += [{"t": "circ", "x": 0.05 + i * 0.1, "y": 1.0, "r": 0.05, "c": "tinta", "o": 0.75} for i in range(10)]
        slots, n = [0.5], 1
    elif nombre == "pista":
        F = [{"t": "haz", "x": x, "y": 0.0, "ang": a, "largo": 1.0, "ancho": 0.22, "c": c_, "o": 0.28}
             for x, a, c_ in [(0.15, 70, "violeta"), (0.5, 92, "amarillo"), (0.85, 110, "celeste")]]
        n, pose = 5, "brazos_arriba"
    elif nombre == "pantalla":
        F = [{"t": "rect", "x": 0.22, "y": 0.08, "w": 0.56, "h": 0.34, "c": "amarillo", "borde": "tinta", "g": 0.8},
             {"t": "haz", "x": 0.5, "y": 0.42, "ang": 90, "largo": 0.6, "ancho": 0.9, "c": "amarillo", "o": 0.25}]
        R = [{"t": "circ", "x": 0.14 + i * 0.145, "y": 0.86 + (i % 2) * 0.04, "r": 0.06, "c": "naranja", "borde": "naranja_osc", "g": 0.7}
             for i in range(6)]
        slots, n = [], 0
    elif nombre == "detalle":
        F = [{"t": "bokeh", "n": 16, "seed": seed, "area": [0, 0, 1, 1], "r": [0.03, 0.07],
              "cols": ["amarillo", "naranja", "linea"], "o": 0.55}]
        slots, n = [], 0
    elif nombre == "naturaleza":
        F = [{"t": "poli", "p": [[0, 0.36], [0.25, 0.14], [0.45, 0.33], [0.65, 0.1], [1, 0.36]], "c": "linea", "o": 0.7},
             {"t": "circ", "x": 0.8, "y": 0.1, "r": 0.04, "c": "amarillo"}]
        n = 0
    elif nombre == "plato":
        F = [{"t": "circ", "x": 0.5, "y": 0.5, "r": 0.24, "c": "blanco", "borde": "tinta", "g": 0.8},
             {"t": "circ", "x": 0.5, "y": 0.5, "r": 0.17, "c": "gris_claro"},
             {"t": "elipse", "x": 0.46, "y": 0.47, "w": 0.15, "h": 0.14, "c": "naranja"},
             {"t": "elipse", "x": 0.56, "y": 0.52, "w": 0.12, "h": 0.12, "c": "verde"},
             {"t": "elipse", "x": 0.5, "y": 0.58, "w": 0.09, "h": 0.08, "c": "rosa"},
             {"t": "linea", "p": [[0.14, 0.25], [0.14, 0.78]], "c": "tinta", "g": 1.6},
             {"t": "linea", "p": [[0.86, 0.25], [0.86, 0.78]], "c": "tinta", "g": 1.6}]
        slots, n = [], 0
    elif nombre == "cocina":
        F = [{"t": "rect", "x": 0.3, "y": 0.05, "w": 0.4, "h": 0.14, "c": "gris_claro", "borde": "tinta", "g": 0.7}]
        R = [{"t": "rect", "x": 0, "y": 0.7, "w": 1, "h": 0.3, "c": "tinta", "o": 0.9},
             {"t": "elipse", "x": 0.5, "y": 0.69, "w": 0.32, "h": 0.06, "c": "gris"},
             {"t": "poli", "p": [[0.42, 0.68], [0.46, 0.56], [0.5, 0.63], [0.54, 0.53], [0.58, 0.68]], "c": "naranja"},
             {"t": "poli", "p": [[0.46, 0.68], [0.5, 0.6], [0.54, 0.68]], "c": "amarillo"}]
        slots, n = [0.5], 1
    elif nombre == "foodtruck":
        F = luces + [{"t": "rect", "x": 0.3, "y": 0.28, "w": 0.62, "h": 0.46, "c": "coral", "r": 0.03, "borde": "tinta", "g": 0.8},
                     {"t": "rect", "x": 0.4, "y": 0.36, "w": 0.4, "h": 0.18, "c": "amarillo", "borde": "tinta", "g": 0.6},
                     {"t": "poli", "p": [[0.37, 0.36], [0.83, 0.36], [0.87, 0.28], [0.33, 0.28]], "c": "blanco", "o": 0.9},
                     {"t": "circ", "x": 0.42, "y": 0.75, "r": 0.04, "c": "tinta"},
                     {"t": "circ", "x": 0.8, "y": 0.75, "r": 0.04, "c": "tinta"}]
        slots, n = [0.1, 0.18, 0.26], 2
    elif nombre == "gym":
        F = [{"t": "rect", "x": 0.06, "y": 0.08, "w": 0.88, "h": 0.42, "c": "linea", "o": 0.25}]
        F += [{"t": "circ", "x": 0.12, "y": 0.6 + i * 0.07, "r": 0.03, "c": "tinta"} for i in range(3)]
        slots, n, pose = [0.5], 1, "brazos_arriba"
    elif nombre == "dj":
        F = [{"t": "haz", "x": x, "y": 0.0, "ang": a, "largo": 1.0, "ancho": 0.22, "c": c_, "o": 0.28}
             for x, a, c_ in [(0.18, 72, "violeta"), (0.82, 108, "celeste")]]
        R = [{"t": "rect", "x": 0.22, "y": 0.6, "w": 0.56, "h": 0.2, "c": "tinta", "r": 0.02},
             {"t": "circ", "x": 0.36, "y": 0.66, "r": 0.03, "c": "violeta"},
             {"t": "circ", "x": 0.64, "y": 0.66, "r": 0.03, "c": "celeste"}]
        R += [{"t": "circ", "x": 0.05 + i * 0.1, "y": 0.98, "r": 0.045, "c": "naranja", "borde": "naranja_osc", "g": 0.6}
              for i in range(10)]
        slots, n, pose = [0.5], 1, "brazos_arriba"
    elif nombre == "iglesia":
        F = [{"t": "rect", "x": 0.38, "y": 0.08, "w": 0.24, "h": 0.42, "c": "gris_claro", "r": 0.12, "borde": "tinta", "g": 0.7},
             {"t": "rect", "x": 0.42, "y": 0.42, "w": 0.16, "h": 0.08, "c": "blanco", "borde": "tinta", "g": 0.6},
             {"t": "linea", "p": [[0.5, 0.14], [0.5, 0.3]], "c": "amarillo", "g": 2},
             {"t": "linea", "p": [[0.45, 0.2], [0.55, 0.2]], "c": "amarillo", "g": 2},
             {"t": "rect", "x": 0.36, "y": 0.34, "w": 0.012, "h": 0.12, "c": "blanco", "borde": "tinta", "g": 0.4},
             {"t": "rect", "x": 0.63, "y": 0.34, "w": 0.012, "h": 0.12, "c": "blanco", "borde": "tinta", "g": 0.4},
             {"t": "circ", "x": 0.366, "y": 0.32, "r": 0.008, "c": "amarillo"},
             {"t": "circ", "x": 0.636, "y": 0.32, "r": 0.008, "c": "amarillo"},
             {"t": "poli", "p": [[0.46, 0.5], [0.54, 0.5], [0.7, 1.0], [0.3, 1.0]], "c": "rosa", "o": 0.45}]
        for k in range(4):
            yy = 0.58 + k * 0.1
            ww = 0.12 + k * 0.05
            F += [{"t": "rect", "x": 0.44 - ww - k * 0.05, "y": yy, "w": ww, "h": 0.04, "c": "linea", "borde": "tinta", "g": 0.4},
                  {"t": "rect", "x": 0.56 + k * 0.05, "y": yy, "w": ww, "h": 0.04, "c": "linea", "borde": "tinta", "g": 0.4}]
        slots, n = [0.45, 0.55], 2
    elif nombre == "ceremonia_exterior":
        F = [{"t": "arco", "x": 0.5, "y": 0.56, "r": 0.16, "ini": 0, "ext": 180, "c": "verde", "g": 5}]
        F += [{"t": "circ", "x": 0.5 + 0.16 * math.cos(math.radians(a)) * 0.5625 / 0.5625,
               "y": 0.56 - 0.16 * math.sin(math.radians(a)) * 1.78, "r": 0.016, "c": c_}
              for a, c_ in [(15, "rosa"), (45, "blanco"), (75, "rosa"), (105, "blanco"), (135, "rosa"), (165, "blanco")]]
        for k in range(3):
            yy = 0.72 + k * 0.09
            F += [{"t": "rect", "x": 0.06 + j * 0.07, "y": yy, "w": 0.05, "h": 0.04, "c": "blanco", "borde": "tinta", "g": 0.4} for j in range(4)]
            F += [{"t": "rect", "x": 0.66 + j * 0.07, "y": yy, "w": 0.05, "h": 0.04, "c": "blanco", "borde": "tinta", "g": 0.4} for j in range(4)]
        slots, n = [0.45, 0.55], 2
    elif nombre == "hogar":
        F = [{"t": "rect", "x": 0.07, "y": 0.1, "w": 0.26, "h": 0.42, "c": "amarillo", "o": 0.55, "borde": "tinta", "g": 0.8},
             {"t": "linea", "p": [[0.2, 0.1], [0.2, 0.52]], "c": "tinta", "g": 0.8},
             {"t": "linea", "p": [[0.07, 0.31], [0.33, 0.31]], "c": "tinta", "g": 0.8},
             {"t": "haz", "x": 0.2, "y": 0.3, "ang": 55, "largo": 0.7, "ancho": 0.4, "c": "amarillo", "o": 0.2},
             {"t": "linea", "p": [[0.86, 0.3], [0.86, 0.75]], "c": "tinta", "g": 1},
             {"t": "poli", "p": [[0.8, 0.3], [0.92, 0.3], [0.89, 0.2], [0.83, 0.2]], "c": "amarillo", "borde": "tinta"},
             {"t": "circ", "x": 0.08, "y": 0.7, "r": 0.04, "c": "verde"}, {"t": "rect", "x": 0.06, "y": 0.72, "w": 0.04, "h": 0.1, "c": "coral"},
             {"t": "rect", "x": 0.38, "y": 0.5, "w": 0.46, "h": 0.22, "c": "celeste", "r": 0.04, "borde": "tinta", "g": 0.7}]
        slots, n = [0.5, 0.64], 2
    elif nombre == "preparacion":
        F = [{"t": "rect", "x": 0.52, "y": 0.1, "w": 0.32, "h": 0.46, "c": "blanco", "r": 0.04, "borde": "tinta", "g": 1},
             {"t": "rect", "x": 0.55, "y": 0.14, "w": 0.26, "h": 0.38, "c": "linea", "o": 0.35}]
        F += [{"t": "circ", "x": 0.52 + 0.32 * j / 5, "y": 0.08, "r": 0.012, "c": "amarillo", "borde": "naranja_osc", "g": 0.4} for j in range(6)]
        R = [{"t": "rect", "x": 0.48, "y": 0.62, "w": 0.4, "h": 0.06, "c": "tinta"},
             {"t": "rect", "x": 0.56, "y": 0.56, "w": 0.03, "h": 0.06, "c": "rosa"},
             {"t": "circ", "x": 0.7, "y": 0.58, "r": 0.025, "c": "blanco", "borde": "tinta", "g": 0.5}]
        slots, n = [0.32], 1
    elif nombre == "auto":
        F = [{"t": "rect", "x": 0.42, "y": 0.5, "w": 0.52, "h": 0.22, "c": "blanco", "r": 0.05, "borde": "tinta", "g": 0.9},
             {"t": "poli", "p": [[0.5, 0.5], [0.58, 0.36], [0.82, 0.36], [0.9, 0.5]], "c": "blanco", "borde": "tinta"},
             {"t": "poli", "p": [[0.54, 0.49], [0.6, 0.39], [0.69, 0.39], [0.69, 0.49]], "c": "linea"},
             {"t": "poli", "p": [[0.71, 0.49], [0.71, 0.39], [0.8, 0.39], [0.86, 0.49]], "c": "linea"},
             {"t": "circ", "x": 0.54, "y": 0.73, "r": 0.04, "c": "tinta"}, {"t": "circ", "x": 0.84, "y": 0.73, "r": 0.04, "c": "tinta"},
             {"t": "linea", "p": [[0.94, 0.55], [0.99, 0.6]], "c": "rosa", "g": 1.5}]
        slots, n = [0.22, 0.32], 2
    elif nombre == "barra":
        for k, y in enumerate([0.14, 0.34]):
            F.append({"t": "rect", "x": 0, "y": y, "w": 1, "h": 0.02, "c": "tinta"})
            F += [{"t": "rect", "x": 0.05 + i * 0.105, "y": y - 0.1, "w": 0.04, "h": 0.1,
                   "c": ["amarillo", "verde", "coral", "celeste", "rosa"][(i + k) % 5], "r": 0.01} for i in range(9)]
        R = [{"t": "rect", "x": 0, "y": 0.72, "w": 1, "h": 0.28, "c": "tinta", "o": 0.9}]
        slots, n = [0.55], 1
    return F, R, slots, n, pose


def dibujar_figuras(L, spec, plano, angulo, slots, n_def, pose_def, hz):
    cod, hrel = escala_plano(plano)
    n = spec.get("personas", n_def)
    if cod == "det" and "personas" not in spec:
        n = 0
    if not n:
        return
    tope = {"pp": 2 if "doble" in (plano or "").lower() else 1, "pmc": 2, "pm": 3, "pa": 4}.get(cod)
    if tope:
        n = min(n, tope)
    if slots and len(slots) >= n:
        xs = slots[:n]
    elif n == 1:
        xs = [spec.get("x", 0.5)]
    else:
        ancho = 0.62 if cod in CORTE else min(0.62, 0.18 * (n - 1))
        xs = [0.5 - ancho / 2 + ancho * i / (n - 1) for i in range(n)]
    poses = spec.get("poses") or [spec.get("pose", pose_def)] * n
    c = L.c
    if angulo == "cenital":
        s = min(L.h, L.w) * max(0.22, min(0.9, hrel * 0.45))
        for i, x in enumerate(xs):
            muneco_cenital(c, L.X(x), L.YY(0.55 + 0.08 * ((i % 2) - 0.5)), s)
        return
    persp = angulo if angulo in ("contrapicado", "picado") else "normal"
    # referencia de tamaño: en cuadros verticales manda el ancho, no el alto
    ref_cerca = min(L.h, L.w * 0.75)
    ref_lejos = min(L.h, L.w)
    if cod in CORTE:
        H = hrel * ref_cerca
        if L.h > L.w:   # cuadro vertical: la cabeza queda en el tercio superior y el cuerpo sigue hacia abajo
            pies_v = 0.16 + H / L.h
        else:
            pies_v = 1 + (1 - CORTE[cod]) * H / L.h
    else:
        base = {"normal": 0.9, "holandes": 0.9, "contrapicado": 0.96, "picado": 0.86, "nadir": 0.95}.get(angulo, 0.9)
        if cod == "gpg":
            base = (hz or 0.36) + (base - (hz or 0.36)) * 0.45
        if angulo == "contrapicado":
            hrel *= 1.25
        H = hrel * ref_lejos
        pies_v = base
    ropas = spec.get("ropas") or [spec.get("ropa")] * n
    colores = spec.get("colores_ropa") or [spec.get("color_ropa")] * n
    etiquetas = spec.get("etiquetas") or []
    # público o invitados de fondo, más chicos y transparentes
    k = spec.get("fondo", 0)
    if k:
        rnd = random.Random(spec.get("seed", 1) + 7)
        hb = 0.5 * ref_lejos * 0.55
        yb = min(0.92, (hz or 0.36) + 0.3)
        c.saveState()
        c.setFillAlpha(0.45)
        c.setStrokeAlpha(0.45)
        for j in range(k):
            muneco(c, L.X(0.06 + 0.88 * (j + rnd.random() * 0.6) / k), L.YY(yb + rnd.uniform(-0.03, 0.03)),
                   hb * rnd.uniform(0.85, 1.1), rnd.choice(["normal", "normal", "jarras", "brindis"]), persp,
                   ropa=rnd.choice([None, "terno", "vestido", "casual"]))
        c.restoreState()
    for i, x in enumerate(xs):
        jitter = 0 if n == 1 else (0.02 if i % 2 else -0.01)
        pies = L.YY(pies_v + jitter)
        muneco(c, L.X(x), pies, H, poses[i % len(poses)], persp, spec.get("espalda", False),
               ropa=ropas[i % len(ropas)], color_ropa=colores[i % len(colores)])
        if i < len(etiquetas) and etiquetas[i]:
            ty = min(pies + H + 6, L.YY(0) - 9)
            c.setFont("Mano", 8)
            c.setFillColor(TINTA)
            c.drawCentredString(L.X(x), ty, etiquetas[i])
    accion = spec.get("accion")
    if accion:
        gx = sum(xs) / len(xs)
        gy = max(0.1, min(0.85, pies_v - (H / L.h) * 0.45))
        A = {"entra_izq": [[gx - 0.3, gy], [gx - 0.08, gy]], "entra_der": [[gx + 0.3, gy], [gx + 0.08, gy]],
             "sale_izq": [[gx - 0.08, gy], [gx - 0.3, gy]], "sale_der": [[gx + 0.08, gy], [gx + 0.3, gy]],
             "se_acerca": [[gx + 0.12, gy - 0.12], [gx + 0.2, gy + 0.18]],
             "se_aleja": [[gx + 0.2, gy + 0.18], [gx + 0.12, gy - 0.12]],
             "camina": [[gx - 0.15, min(0.95, pies_v + 0.02)], [gx + 0.15, min(0.95, pies_v + 0.02)]]}
        flechas = []
        if accion in A:
            flechas = [{"t": "flecha", "p": A[accion], "c": "naranja_osc", "dash": [3, 2], "g": 1.4}]
        elif accion in ("baila", "gira"):
            flechas = [{"t": "flecha", "p": [[gx - 0.12, gy + 0.05], [gx, gy - 0.12], [gx + 0.12, gy + 0.05]],
                        "curva": True, "c": "naranja_osc", "dash": [3, 2], "g": 1.4},
                       {"t": "flecha", "p": [[gx + 0.12, gy + 0.12], [gx, gy + 0.25], [gx - 0.12, gy + 0.12]],
                        "curva": True, "c": "naranja_osc", "dash": [3, 2], "g": 1.4}]
        for p in flechas:
            L.prim(p)


def camara_icono(c, x, y, s, ang):
    """Cámara de cine (dos bobinas). (x, y) = punta del lente. ang en grados."""
    c.saveState()
    c.translate(x, y)
    c.rotate(ang)
    c.setFillColor(TINTA)
    c.setStrokeColor(TINTA)
    c.roundRect(-1.25 * s, -0.3 * s, 0.85 * s, 0.6 * s, 0.08 * s, stroke=0, fill=1)
    c.circle(-1.05 * s, 0.55 * s, 0.26 * s, stroke=0, fill=1)
    c.circle(-0.55 * s, 0.6 * s, 0.3 * s, stroke=0, fill=1)
    p = c.beginPath()
    p.moveTo(-0.4 * s, -0.14 * s)
    p.lineTo(0, -0.26 * s)
    p.lineTo(0, 0.26 * s)
    p.lineTo(-0.4 * s, 0.14 * s)
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.restoreState()


def diagrama_lateral(doc, x, top, w, h, angulo, plano=""):
    """Vista lateral: cámara, cono de visión, línea de ojos y sujeto."""
    c = doc.c
    c.saveState()
    c.setFillColor(PAPEL)
    pth = c.beginPath()
    pth.roundRect(x, doc.Y(top + h), w, h, 5)
    c.drawPath(pth, stroke=0, fill=1)
    c.clipPath(pth, stroke=0, fill=0)
    suelo = doc.Y(top + h * 0.86)
    c.setStrokeColor(HORIZ)
    c.setLineWidth(0.8)
    c.line(x + 4, suelo, x + w - 4, suelo)
    fh = h * 0.5
    dist = {"gpg": 0.86, "pg": 0.8, "pe": 0.74, "pa": 0.7, "pm": 0.64, "pmc": 0.6, "pp": 0.56,
            "det": 0.52}.get(escala_plano(plano)[0], 0.78)
    sx = x + w * dist
    muneco(c, sx, suelo, fh, "jarras")
    ojos = suelo + fh * 0.89
    s = min(h * 0.11, w * 0.09)
    conf = {
        "normal": (x + w * 0.3, ojos, 0), "holandes": (x + w * 0.3, ojos, 0),
        "contrapicado": (x + w * 0.3, suelo + s * 0.9, 24),
        "picado": (x + w * 0.3, doc.Y(top + h * 0.16), -26),
        "cenital": (sx, doc.Y(top + h * 0.08), -90),
        "nadir": (x + w * 0.56, suelo + s * 0.4, 62),
    }
    lx, ly, ang = conf.get(angulo, conf["normal"])
    # cono de visión
    largo = max(w, h) * 1.1
    c.setFillColor(AMAR)
    c.setFillAlpha(0.45)
    p = c.beginPath()
    p.moveTo(lx, ly)
    for d in (-17, 17):
        a = math.radians(ang + d)
        p.lineTo(lx + largo * math.cos(a), ly + largo * math.sin(a))
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.setFillAlpha(1)
    if angulo in ("normal", "holandes"):
        c.setStrokeColor(HexColor("#C8962E"))
        c.setLineWidth(0.9)
        c.setDash(3, 2)
        c.line(lx, ly, sx - fh * 0.1, ly)
        c.setDash()
        # trípode
        c.setStrokeColor(TINTA)
        c.setLineWidth(max(0.8, s * 0.1))
        bx = lx - 0.85 * s
        c.line(bx, ly - 0.3 * s, bx - 0.5 * s, suelo)
        c.line(bx, ly - 0.3 * s, bx + 0.5 * s, suelo)
        c.line(bx - 0.25 * s, (ly + suelo) / 2, bx + 0.25 * s, (ly + suelo) / 2)
    roll = 15 if angulo == "holandes" else 0
    if roll:
        c.saveState()
        c.translate(lx - 0.8 * s, ly)
        c.rotate(roll)
        camara_icono(c, 0.8 * s, 0, s, 0)
        c.restoreState()
    else:
        camara_icono(c, lx, ly, s, ang)
    c.setFont("Mano", 8 if h > 80 else 7)
    c.setFillColor(TINTA)
    c.drawString(x + 6, doc.Y(top + 11), ANGULOS.get(angulo, angulo))
    c.restoreState()


def dibujar_cuadro(doc, x, top, w, h, spec, reel=True, guia=True, vertical=False, toma=None):
    """Cuadro del storyboard en estilo diagrama: papel claro, perspectiva según el ángulo,
    muñecos según el tipo de plano, flechas de movimiento, tercios y guía 9:16 / zona segura."""
    toma = toma or {}
    angulo = angulo_de(toma) if toma else spec.get("angulo", "normal")
    c = doc.c
    c.saveState()
    c.setFillColor(PAPEL)
    pth = c.beginPath()
    pth.roundRect(x, doc.Y(top + h), w, h, 5)
    c.drawPath(pth, stroke=0, fill=1)
    c.clipPath(pth, stroke=0, fill=0)
    L = Lienzo(doc, x, top, w, h, claro=True)
    nombre = spec.get("escena", "interior")
    fondo, frente, slots, n_def, pose_def = escena_diagrama(nombre, spec.get("seed", 1))
    c.saveState()
    if angulo == "holandes":
        cx, cy = x + w / 2, doc.Y(top + h / 2)
        c.translate(cx, cy)
        c.rotate(12)
        c.translate(-cx, -cy)
    # sin piso ni horizonte: solo se usa la altura del horizonte para ubicar a las personas
    hz = None if (nombre == "plato" or angulo == "cenital") else \
        {"contrapicado": 0.8, "picado": 0.05, "nadir": 0.5}.get(angulo, 0.36)
    for p in fondo:
        L.prim(p)
    dibujar_figuras(L, spec, toma.get("plano", ""), angulo, slots, n_def, pose_def, hz)
    for p in frente + spec.get("extras", []):
        L.prim(p)
    c.restoreState()
    if spec.get("mov"):
        for p in movimiento(spec["mov"], spec.get("mov_texto")):
            L.prim(p)
    if guia:
        c.setStrokeColor(HexColor("#7D93AD"))
        c.setStrokeAlpha(0.45)
        c.setLineWidth(0.5)
        for k in (1, 2):
            c.line(x + w * k / 3, doc.Y(top), x + w * k / 3, doc.Y(top + h))
            c.line(x, doc.Y(top + h * k / 3), x + w, doc.Y(top + h * k / 3))
        c.setStrokeAlpha(1)
    guia_oro = HexColor("#C8962E")
    if vertical and guia:
        c.setFillColor(TINTA)
        c.setFillAlpha(0.13)
        c.rect(x, doc.Y(top + h * 0.12), w, h * 0.12, stroke=0, fill=1)
        c.rect(x, doc.Y(top + h), w, h * 0.22, stroke=0, fill=1)
        c.setFillAlpha(1)
        c.setStrokeColor(guia_oro)
        c.setLineWidth(1.3)
        c.setDash(4, 3)
        c.line(x, doc.Y(top + h * 0.12), x + w, doc.Y(top + h * 0.12))
        c.line(x, doc.Y(top + h * 0.78), x + w, doc.Y(top + h * 0.78))
        c.setDash()
        c.setFont("Mano", 7.5)
        c.setFillColor(guia_oro)
        c.drawCentredString(x + w / 2, doc.Y(top + h * 0.12 + 10), "zona segura")
    elif reel and guia:
        cw = h * 9 / 16
        cx = x + w * spec.get("recorte_x", 0.5) - cw / 2
        cx = max(x, min(cx, x + w - cw))
        c.setFillColor(TINTA)
        c.setFillAlpha(0.13)
        c.rect(x, doc.Y(top + h), cx - x, h, stroke=0, fill=1)
        c.rect(cx + cw, doc.Y(top + h), x + w - cx - cw, h, stroke=0, fill=1)
        c.setFillAlpha(1)
        c.setStrokeColor(guia_oro)
        c.setLineWidth(1.3)
        c.setDash(4, 3)
        c.line(cx, doc.Y(top), cx, doc.Y(top + h))
        c.line(cx + cw, doc.Y(top), cx + cw, doc.Y(top + h))
        c.setDash()
        c.setFont("Mano", 8)
        c.setFillColor(guia_oro)
        c.drawCentredString(cx + cw / 2, doc.Y(top + 10), "9:16")
    c.restoreState()


# ════════════════════════════════════════════════════════════════════
# 5. UTILIDADES DE TIEMPO Y VALIDACIÓN
# ════════════════════════════════════════════════════════════════════
def seg(t):
    t = t.strip().replace("s", "").strip()
    if ":" in t:
        m, s = t.split(":")
        return int(m) * 60 + float(s)
    return float(t)


def rango(t):
    a, b = re.split(r"\s*[–-]\s*", t.strip(), maxsplit=1)
    return seg(a), seg(b)


AVISOS = []


def avisar(msg):
    AVISOS.append(msg)


def es_vertical(d):
    return d.get("modo", "pelicula_y_reel") == "solo_reel"


def validar(d):
    g = d.get("guion", [])
    prev = None
    for r in g:
        try:
            a, b = rango(r["tiempo"])
        except Exception:
            avisar(f"Guion: tiempo ilegible '{r['tiempo']}'")
            continue
        if prev is not None and abs(a - prev) > 0.01:
            avisar(f"Guion: salto o traslape antes de {r['tiempo']}")
        prev = b
    dur = d["portada"]["reel" if es_vertical(d) else "pelicula"]["valor"]
    try:
        if prev is not None and abs(prev - seg(dur)) > 0.01:
            avisar(f"Guion: termina en {prev:.0f} s pero la película dura {dur}")
    except Exception:
        pass
    ids = {str(t["id"]) for t in d.get("tomas", []) + d.get("especiales", [])}
    for t in d.get("referencias", {}).get("top", []):
        if str(t["toma"]) not in ids:
            avisar(f"Referencias: la toma {t['toma']} no existe en el storyboard")
    top = [t for t in d.get("tomas", []) + d.get("especiales", []) if t.get("top10")]
    if len(top) != len(d.get("referencias", {}).get("top", [])):
        avisar("Referencias: la cantidad de tomas TOP 10 no coincide con la lista de Frameset")
    tags = d.get("copy", {}).get("hashtags", [])
    if len(tags) != 5:
        avisar(f"Copy: hay {len(tags)} hashtags; deben ser exactamente 5")
    rr = [] if es_vertical(d) else d.get("reel", {}).get("tramos", [])
    prev = 0
    for r in rr:
        a, b = rango(r["tiempo"])
        if abs(a - prev) > 0.01:
            avisar(f"Reel: salto o traslape antes de {r['tiempo']}")
        prev = b


# ════════════════════════════════════════════════════════════════════
# 6. SECCIONES
# ════════════════════════════════════════════════════════════════════
def sec_portada(doc, d, indice):
    doc.fondo()
    c = doc.c
    m, po = d["meta"], d["portada"]
    L = Lienzo(doc, 102, 48, 200, 190)
    icono = po.get("icono", "camara")
    for p in (iconos(icono) if isinstance(icono, str) else icono):
        L.prim(p)
    c.setFont("Poppins-SemiBold", 7.5)
    c.setFillColor(ORO)
    c.drawCentredString(W / 2, doc.Y(271), m["tipo"].upper())
    lineas = m.get("titulo_lineas") or [m["titulo"]]
    if len(lineas) == 1 and pdfmetrics.stringWidth(lineas[0], "Serif", 44) > CW:
        pal = lineas[0].split()
        mejor = min(range(1, len(pal)), key=lambda k: abs(len(" ".join(pal[:k])) - len(" ".join(pal[k:]))),
                    default=1)
        lineas = [" ".join(pal[:mejor]), " ".join(pal[mejor:])] if len(pal) > 1 else lineas
    size = 44
    while size > 26 and max(pdfmetrics.stringWidth(l, "Serif", size) for l in lineas) > CW - 10:
        size -= 1
    c.setFont("Serif", size)
    c.setFillColor(CREMA)
    y = 330
    for l in lineas:
        c.drawCentredString(W / 2, doc.Y(y), l)
        y += size * 1.05
    y -= size * 1.05
    c.setStrokeColor(ORO)
    c.setLineWidth(1.5)
    c.line(W / 2 - 15, doc.Y(y + 15), W / 2 + 15, doc.Y(y + 15))
    c.setFont("Poppins", 9)
    c.setFillColor(GRIS)
    c.drawCentredString(W / 2, doc.Y(y + 31), m["subtitulo"])
    # tarjetas de datos
    claves = ["reel", "formato", "tomas"] if es_vertical(d) else ["pelicula", "reel", "tomas"]
    for i, key in enumerate(claves):
        x = M + i * 123
        doc.tarjeta(x, 428, 115, 58, barra=False)
        c.setFont("Poppins-SemiBold", 6.8)
        c.setFillColor(GRIS_C)
        c.drawCentredString(x + 57.5, doc.Y(444), {"pelicula": "PELÍCULA", "reel": "REEL", "tomas": "TOMAS",
                                                     "formato": "FORMATO"}[key])
        c.setFont("Serif", 17)
        c.setFillColor(OSC)
        c.drawCentredString(x + 57.5, doc.Y(465), po[key]["valor"])
        c.setFont("Poppins", 7)
        c.setFillColor(GRIS_C)
        c.drawCentredString(x + 57.5, doc.Y(478), po[key]["detalle"])
    # índice
    mitad = math.ceil(len(indice) / 2)
    for i, (num, nombre) in enumerate(indice):
        x = 30 if i < mitad else 210
        y = 513 + (i % mitad) * 15
        c.setFont("Poppins-SemiBold", 7.2)
        c.setFillColor(ORO)
        c.drawString(x, doc.Y(y), num)
        c.setFont("Poppins", 7.8)
        c.setFillColor(CREMA)
        c.drawString(x + 18, doc.Y(y), nombre)
    c.setFont("Poppins-SemiBold", 8)
    c.setFillColor(ORO)
    c.drawCentredString(W / 2, doc.Y(675), "H I S T E A   S T U D I O S")


def sec_concepto(doc, d, num):
    co = d["concepto"]
    doc.pagina(f"{num} · CONCEPTO", "El concepto")
    c = doc.c
    c.setFont("Serif", 40)
    c.setFillColor(ORO)
    c.drawString(20, doc.Y(115), "“")
    h = doc.p(42, doc.y + 2, CW - 20, para(co["cita"], 15.5, CREMA, "Serif-Italic", 1.36))
    doc.y += h + 12
    doc.y += doc.p(M, doc.y, CW, para(co["parrafo"], 9.2, CREMA)) + 12
    tarjetas = []
    if co.get("inicio"):
        tarjetas.append((f"Cómo empieza · {co['inicio']['tipo']}", co["inicio"]["texto"]))
    tarjetas += [(h_["titulo"], h_["texto"]) for h_ in co["hilos"]]
    if co.get("tono_visual"):
        tarjetas.append(("Tono visual", co["tono_visual"]))
    for t, tx in tarjetas:
        doc.tarjeta_bloque(t, tx, gap=7, pad=9)
    # arco de energía
    arco = co.get("arco")
    if arco:
        nota = para(arco.get("nota", ""), 7.4, GRIS)
        hn = alto(nota, CW) if arco.get("nota") else 0
        doc.asegurar(140 + hn)
        doc.eyebrow("ARCO DE ENERGÍA", 6)
        x0, top, w, h = 26, doc.y + 4, 353, 96
        pts = arco["puntos"]
        P = [(x0 + u * w, doc.Y(top + (1 - v) * h)) for u, v in pts]
        c.setStrokeColor(MARCO)
        c.setLineWidth(0.6)
        c.line(x0, doc.Y(top + h), x0 + w, doc.Y(top + h))
        c.setStrokeColor(ORO)
        c.setLineWidth(2.2)
        pth = c.beginPath()
        pth.moveTo(*P[0])
        for i in range(len(P) - 1):  # Catmull-Rom → Bézier
            p0 = P[i - 1] if i > 0 else P[i]
            p1, p2 = P[i], P[i + 1]
            p3 = P[i + 2] if i + 2 < len(P) else P[i + 1]
            pth.curveTo(p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6,
                        p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6, p2[0], p2[1])
        c.drawPath(pth, stroke=1, fill=0)
        for e in arco.get("etiquetas", []):
            u, v = pts[e["punto"]]
            c.setFont("Mano", 10)
            c.setFillColor(CREMA)
            dy = -9 if e.get("pos", "arriba") == "arriba" else 13
            c.drawCentredString(x0 + u * w + e.get("dx", 0), doc.Y(top + (1 - v) * h) - dy, e["texto"])
        nombres = arco.get("ejes") or [b.get("corto", b["nombre"]) for b in d["bloques"]]
        c.setFont("Poppins", 6.8)
        c.setFillColor(GRIS)
        for i, n in enumerate(nombres):
            u = i / max(1, len(nombres) - 1)
            fx = x0 + u * w
            if i == 0:
                c.drawString(fx - 2, doc.Y(top + h + 12), n)
            elif i == len(nombres) - 1:
                c.drawRightString(fx + 2, doc.Y(top + h + 12), n)
            else:
                c.drawCentredString(fx, doc.Y(top + h + 12), n)
        doc.y = top + h + 24
        if hn:
            doc.p(M, doc.y, CW, nota)
            doc.y += hn + 8


def sec_estructura(doc, d, num):
    doc.pagina(f"{num} · ESTRUCTURA", "Estructura")
    c = doc.c
    bl = d["bloques"]
    # tira de película
    top, h = doc.y, 56
    c.setFillColor(CUADRO)
    c.roundRect(M, doc.Y(top + h), CW, h, 4, stroke=0, fill=1)
    for i in range(40):
        for yy in (top + 4, top + h - 8):
            c.setFillColor(MARCO)
            c.rect(M + 4 + i * 9, doc.Y(yy + 4), 5, 4, stroke=0, fill=1)
    tot = sum(rango(b["tiempo"])[1] - rango(b["tiempo"])[0] for b in bl)
    x = M + 4
    for i, b in enumerate(bl):
        a, z = rango(b["tiempo"])
        ww = (CW - 8) * (z - a) / tot
        c.setFillColor(HexColor(BLOQUES[i % len(BLOQUES)]))
        c.rect(x, doc.Y(top + h - 12), ww - 1.5, h - 24, stroke=0, fill=1)
        c.setFont("Poppins-SemiBold", 5.6)
        c.setFillColor(OSC)
        etiqueta = b.get("corto", b["nombre"])
        while pdfmetrics.stringWidth(etiqueta, "Poppins-SemiBold", 5.6) > ww - 5 and len(etiqueta) > 3:
            etiqueta = etiqueta[:-2] + "…" if not etiqueta.endswith("…") else etiqueta[:-2] + "…"
        c.drawString(x + 2.5, doc.Y(top + h - 15), etiqueta)
        x += ww
    doc.y = top + h + 12
    for i, b in enumerate(bl):
        hh = 38
        doc.asegurar(hh)
        t = doc.y
        doc.tarjeta(M, t, CW, hh, barra=False)
        c.setFillColor(HexColor(BLOQUES[i % len(BLOQUES)]))
        c.circle(M + 16, doc.Y(t + hh / 2), 4.5, stroke=0, fill=1)
        c.setFont("Poppins-SemiBold", 9)
        c.setFillColor(OSC)
        c.drawString(M + 30, doc.Y(t + 16), b["nombre"])
        c.setFont("Poppins", 6.8)
        c.setFillColor(GRIS_C)
        c.drawString(M + 30, doc.Y(t + 28), b["tomas"])
        c.setFont("Poppins-SemiBold", 8.5)
        c.setFillColor(OSC)
        c.drawRightString(M + CW - 12, doc.Y(t + 22), b["tiempo"].replace("–", " – ").replace("  ", " "))
        doc.y += hh + 8
    actos_narrativos(doc, d)
    if d.get("estructura_nota"):
        doc.texto_flujo(d["estructura_nota"], 7.4, CREMA)


ACTOS = [("Presentación", 25), ("Nudo", 50), ("Clímax", 20), ("Desenlace", 5)]


def fmt_t(x):
    x = round(x)
    return f"{x // 60}:{x % 60:02d}"


def actos_narrativos(doc, d):
    tiempos = {}
    for b in d["bloques"]:
        if b.get("acto"):
            a, z = rango(b["tiempo"])
            ini, fin = tiempos.get(b["acto"], (a, z))
            tiempos[b["acto"]] = (min(ini, a), max(fin, z))
    if not tiempos:
        return
    c = doc.c
    tot = sum(z - a for a, z in tiempos.values())
    doc.y += 2
    doc.asegurar(70)
    doc.eyebrow("ESTRUCTURA NARRATIVA · OBJETIVO 25 / 50 / 20 / 5 %", 8)
    top, h = doc.y, 40
    x = M
    tonos = ["#E8D7B0", "#DCC28E", "#D4AF6B", "#B8955A"]
    presentes = [(i, a, m) for i, (a, m) in enumerate(ACTOS) if a in tiempos]
    minw = 62
    prop = {a: CW * (tiempos[a][1] - tiempos[a][0]) / tot for _, a, _ in presentes}
    chicos = {a for a in prop if prop[a] < minw}
    resto = CW - minw * len(chicos)
    grandes = sum(prop[a] for a in prop if a not in chicos) or 1
    anchos = {a: (minw if a in chicos else prop[a] * resto / grandes) for a in prop}
    for i, acto, meta in presentes:
        a, z = tiempos[acto]
        real = 100 * (z - a) / tot
        if abs(real - meta) > 10:
            avisar(f"Estructura: {acto} ocupa {real:.0f} % (objetivo {meta} %)")
        ww = anchos[acto]
        c.setFillColor(HexColor(tonos[i]))
        c.roundRect(x, doc.Y(top + h), ww - 3, h, 5, stroke=0, fill=1)
        c.setFillColor(OSC)
        c.setFont("Poppins-SemiBold", 7.4)
        c.drawString(x + 7, doc.Y(top + 14), acto)
        c.setFont("Poppins", 6.4)
        c.drawString(x + 7, doc.Y(top + 24), f"{real:.0f} %")
        c.drawString(x + 7, doc.Y(top + 33), f"{fmt_t(a)}–{fmt_t(z)}")
        x += ww
    doc.y = top + h + 10


def color_bloque(d, nombre):
    for i, b in enumerate(d["bloques"]):
        if b["nombre"] == nombre or b.get("corto") == nombre:
            return HexColor(BLOQUES[i % len(BLOQUES)])
    return MARCO


def filas_tiempo(doc, filas, d, color_fijo=None):
    c = doc.c
    for r in filas:
        pt = para(r["texto"], 7.4, CREMA)
        ps = para("♪ " + r["sonido"], 7.4, GRIS) if r.get("sonido") else None
        tw = CW - 96
        h = max(alto(pt, tw) + (alto(ps, tw) if ps else 0) + 9.4, 29.4)
        doc.asegurar(h + 3)
        t = doc.y
        doc.contorno(M, t, CW, h, color_fijo or color_bloque(d, r["bloque"]))
        c.setFont("Poppins-SemiBold", 8)
        c.setFillColor(ORO)
        c.drawString(M + 10, doc.Y(t + 12.5), r["tiempo"])
        c.setFont("Poppins", 6.4)
        c.setFillColor(GRIS)
        c.drawString(M + 10, doc.Y(t + 21.5), r["bloque"])
        y = t + 4.7
        y += doc.p(M + 86, y, tw, pt)
        if ps:
            doc.p(M + 86, y, tw, ps)
        doc.y += h + 3


def sec_guion(doc, d, num):
    if es_vertical(d):
        r = d.get("reel", {})
        doc.pagina(f"{num} · GUION DEL REEL · SEGUNDO A SEGUNDO", "Guion del reel")
        segs = [(b["tiempo"], b.get("corto", b["nombre"])) for b in d["bloques"]]
        top = doc.y
        yy = telefono(doc, top, segs, r.get("notas", []))
        doc.y = yy + 14
    else:
        doc.pagina(f"{num} · GUION DE EDICIÓN · MINUTO A MINUTO", "Guion de edición")
    filas_tiempo(doc, d["guion"], d)


def telefono(doc, top, segs, notas):
    """Maqueta de celular con tramos proporcionales y notas al costado. Devuelve el borde inferior."""
    c = doc.c
    pw, ph = 96, 196
    c.setFillColor(CUADRO)
    c.setStrokeColor(MARCO)
    c.setLineWidth(1.2)
    c.roundRect(M, doc.Y(top + ph), pw, ph, 14, stroke=1, fill=1)
    sx, st, sw, sh = M + 7, top + 12, pw - 14, ph - 24
    tot = rango(segs[-1][0])[1]
    y = st
    tonos = ["#E8D7B0", "#DCC28E", "#E8D7B0", "#D4B47A", "#E3CC9C", "#D9BC85"]
    for i, (tiempo, nombre) in enumerate(segs):
        a, b = rango(tiempo)
        hh = max(14, sh * (b - a) / tot)
        if y + hh > st + sh:
            hh = st + sh - y
        if hh <= 2:
            break
        c.setFillColor(HexColor(tonos[i % len(tonos)]))
        c.rect(sx, doc.Y(y + hh), sw, hh - 1.2, stroke=0, fill=1)
        c.setFont("Poppins-SemiBold", 5.4)
        c.setFillColor(OSC)
        c.drawString(sx + 4, doc.Y(y + 8), f"{tiempo} {nombre}")
        y += hh
    yy = top + 2
    for lead, tx in notas:
        pr = para(f"**{lead}** {tx}", 7.4, CREMA)
        yy += doc.p(M + pw + 14, yy, CW - pw - 14, pr) + 7
    return max(top + ph, yy)


def sec_configuracion(doc, d, num):
    doc.pagina(f"{num} · CONFIGURACIÓN", "Configuración")
    for t in d["configuracion"]:
        doc.tarjeta_bloque(t["titulo"], t.get("texto"), t.get("filas"), lab_w=t.get("ancho_etiqueta", 96), gap=8)


def sec_audio(doc, d, num):
    a = d["audio"]
    doc.pagina(f"{num} · AUDIO", "Audio")
    c = doc.c
    if a.get("intro"):
        doc.texto_flujo(a["intro"], 8, CREMA, 10)
    for b in a["bloques"]:
        pv = para(b["texto"], 7.4, OSC)
        pn = para(b["bloque"], 8, OSC, "Poppins-SemiBold")
        h = max(alto(pv, CW - 140) , alto(pn, 110) + 10) + 18
        doc.asegurar(h + 8)
        t = doc.y
        doc.tarjeta(M, t, CW, h)
        y = t + 9
        y += doc.p(M + 14, y, 110, pn)
        c.setFont("Poppins", 6.8)
        c.setFillColor(GRIS_C)
        c.drawString(M + 14, doc.Y(y + 7), b["mic"])
        doc.p(M + 128, t + 9, CW - 140, pv)
        doc.y += h + 8
    for n in a.get("notas", []):
        doc.texto_flujo(n, 7.4, CREMA, 6)
    e = a.get("entrevistas")
    if e:
        doc.y += 6
        doc.eyebrow(e.get("titulo", "ENTREVISTAS"), 8)
        for i, q in enumerate(e["preguntas"], 1):
            doc.asegurar(30)
            t = doc.y
            doc.tarjeta(M, t, CW, 26, barra=False)
            doc.circulo_num(M + 9, t + 5, i, 16, size=8)
            c.setFont("Poppins-Medium", 8.5)
            c.setFillColor(OSC)
            c.drawString(M + 34, doc.Y(t + 16), q)
            doc.y += 32
        doc.y += 2
        for s in e.get("consejos", []):
            pr = para(s, 7.2, CREMA)
            h = alto(pr, CW - 12)
            doc.asegurar(h + 5)
            c.setFillColor(ORO)
            c.circle(M + 3, doc.Y(doc.y + 5), 1.6, stroke=0, fill=1)
            doc.p(M + 12, doc.y, CW - 12, pr)
            doc.y += h + 5


def sec_dron(doc, d, num):
    dr = d["dron"]
    doc.pagina(f"{num} · DRON · {dr.get('modelo', '').upper()}".rstrip(" ·"), "Dron")
    for t in dr["tarjetas"]:
        doc.tarjeta_bloque(t["titulo"], t.get("texto"), t.get("filas"), gap=10)
    if dr.get("nota"):
        doc.texto_flujo(dr["nota"], 7.4, GRIS)


def sec_referencias(doc, d, num):
    r = d["referencias"]
    doc.pagina(f"{num} · REFERENCIAS · FRAMESET", "Referencias")
    c = doc.c
    doc.texto_flujo(r["intro"], 8, CREMA, 10)
    for t in r["top"]:
        doc.asegurar(36)
        top = doc.y
        doc.tarjeta(M, top, CW, 32)
        doc.circulo_num(M + 12, top + 7, t["toma"], 18, size=8)
        c.setFont("Poppins-Italic", 7.6)
        c.setFillColor(OSC)
        c.drawString(M + 40, doc.Y(top + 14), t["busqueda"])
        c.setFont("Poppins", 6.4)
        c.setFillColor(GRIS_C)
        c.drawString(M + 40, doc.Y(top + 25), t["filtros"])
        doc.y += 37
    # técnicas
    tc = d.get("tecnicas")
    if tc:
        doc.pagina(f"{num} · REFERENCIAS · EYECANNNDY", "Técnicas")
        doc.texto_flujo(tc["intro"], 8, CREMA, 10)
        for it in tc["items"]:
            pv = para(it["texto"], 7.4, OSC)
            h = alto(pv, CW - 26) + 30
            doc.asegurar(h + 8)
            top = doc.y
            doc.tarjeta(M, top, CW, h)
            c.setFont("Poppins-SemiBold", 8)
            c.setFillColor(OSC)
            c.drawString(M + 14, doc.Y(top + 15), it["nombre"])
            doc.pastilla(M + CW - 10, top + 6, it["tomas"])
            doc.p(M + 14, top + 21, CW - 26, pv)
            doc.y += h + 8


def alto_toma(t):
    w = CW - 68
    h = 34 + FH + 8
    vals = [t.get("intencion"), t.get("movimiento"), t.get("capturar"), t.get("camara"), t.get("audio")]
    fr = t.get("frameset")
    if fr:
        vals.append(f"*{fr['busqueda']}* · {fr['filtros']}")
    vals = [v for v in vals if v]
    for v in vals:
        h += alto(para(v, 7.4, CREMA, lead=1.35), w) + 3.5
    return h - 3.5


FW, FH = 242, 136.1          # cuadro horizontal 16:9 del storyboard
VW, VH = 118.1, 210          # cuadro vertical 9:16


def intencion_p(t):
    """La intención va en dorado: emoción → plano · movimiento · ángulo · luz."""
    v = t.get("intencion")
    if not v:
        return None
    return Paragraph(f"<font color='#D4AF6B'>{markup(v)}</font>", estilo(7.4, CREMA, lead=1.35))
V_TAB_X = M + VW + 14
V_TAB_W = CW - VW - 14
V_DIAG_H = 66


def alto_toma_v(t):
    w = V_TAB_W - 62
    vals = [t.get("intencion"), t.get("movimiento"), t.get("capturar"), t.get("camara"), t.get("audio")]
    fr = t.get("frameset")
    if fr:
        vals.append(f"*{fr['busqueda']}* · {fr['filtros']}")
    th = sum(alto(para(v, 7.4, CREMA, lead=1.35), w) + 5 for v in vals if v) - 5
    return 34 + max(VH, V_DIAG_H + 8 + th)


def dibujar_toma_v(doc, t, d):
    c = doc.c
    top = doc.y
    encabezado_toma(doc, t, top)
    dibujar_cuadro(doc, M, top + 34, VW, VH, t.get("dibujo", {}), reel=False, vertical=True, toma=t)
    diagrama_lateral(doc, V_TAB_X, top + 34, V_TAB_W, V_DIAG_H, angulo_de(t), t.get("plano", ""))
    doc.y = top + 34 + V_DIAG_H + 8
    fr = t.get("frameset")
    if not t.get("intencion"):
        avisar(f"Toma {t['id']}: falta 'intencion' (emoción → plano · movimiento · ángulo · luz)")
    filas = [("Intención", intencion_p(t)), ("Movimiento", t.get("movimiento")), ("Qué capturar", t.get("capturar")),
             ("Cámara", t.get("camara")), ("Audio", t.get("audio"))]
    if fr:
        html = f"<i>{markup(fr['busqueda'])}</i> <font color='#8A93A6'>· {markup(fr['filtros'])}</font>"
        filas.append(("Frameset", Paragraph(html, estilo(7.4, CREMA, lead=1.35))))
    doc.tabla_oscura(filas, lab_w=62, gap=5, x=V_TAB_X, w=V_TAB_W)
    doc.y = top + alto_toma_v(t)


def encabezado_toma(doc, t, top):
    c = doc.c
    doc.circulo_num(M, top, t["id"], 22, size=10 if len(str(t["id"])) < 3 else 8)
    c.setFont("Poppins-SemiBold", 10)
    c.setFillColor(CREMA)
    c.drawString(M + 28, doc.Y(top + 10), t["plano"])
    c.setFont("Poppins", 6.8)
    c.setFillColor(GRIS)
    c.drawString(M + 28, doc.Y(top + 20), t["bloque"].upper())
    xr = M + CW
    for etiqueta, oro in ([(t["duracion"], False)] if t.get("duracion") else []) + \
                         ([("120p", True)] if t.get("fps120") else []) + \
                         ([("REEL", True)] if t.get("reel") and not es_vertical(doc.d) else []) + \
                         ([("TOP 10", True)] if t.get("top10") else []) + \
                         [(x, True) for x in t.get("insignias", [])]:
        xr = doc.pastilla(xr, top + 15, etiqueta, oro)


def dibujar_toma(doc, t, d):
    if es_vertical(d):
        return dibujar_toma_v(doc, t, d)
    top = doc.y
    encabezado_toma(doc, t, top)
    fw, fh = FW, FH
    dw = CW - fw - 8
    diagrama_lateral(doc, M, top + 34, dw, fh, angulo_de(t), t.get("plano", ""))
    dibujar_cuadro(doc, M + dw + 8, top + 34, fw, fh, t.get("dibujo", {}), reel=True, toma=t)
    doc.y = top + 34 + fh + 8
    fr = t.get("frameset")
    if not t.get("intencion"):
        avisar(f"Toma {t['id']}: falta 'intencion' (emoción → plano · movimiento · ángulo · luz)")
    filas = [("Intención", intencion_p(t)), ("Movimiento", t.get("movimiento")), ("Qué capturar", t.get("capturar")),
             ("Cámara", t.get("camara")), ("Audio", t.get("audio"))]
    if fr:
        html = f"<i>{markup(fr['busqueda'])}</i> <font color='#8A93A6'>· {markup(fr['filtros'])}</font>"
        filas.append(("Frameset", Paragraph(html, estilo(7.4, CREMA, lead=1.35))))
    doc.tabla_oscura(filas, lab_w=68)


def sec_storyboard(doc, d, num, lista, nombre_sec, titulo_fijo=None):
    tomas = d[lista]
    i = 0
    while i < len(tomas):
        a = tomas[i]
        b = tomas[i + 1] if i + 1 < len(tomas) else None
        f_alto = alto_toma_v if es_vertical(d) else alto_toma
        par = b is not None and (TOP0 + f_alto(a) + 22 + f_alto(b) <= BOTTOM)
        grupo = [a, b] if par else [a]
        if b is not None and not par:
            avisar(f"Toma {a['id']} quedó sola en su página: acorta sus textos o los de la toma {b['id']}")
        ids = [str(x["id"]) for x in grupo]
        titulo = ("Tomas " + " y ".join(ids)) if len(ids) > 1 else f"Toma {ids[0]}"
        bloques = []
        for x in grupo:
            if x["bloque"] not in bloques:
                bloques.append(x["bloque"])
        if titulo_fijo:
            eb = f"{num} · {titulo_fijo}"
        else:
            rng = ""
            if len(bloques) == 1:
                for bb in d["bloques"]:
                    if bb["nombre"] == bloques[0] or bb.get("corto") == bloques[0]:
                        rng = " · " + bb["tiempo"].replace("–", " – ").replace("  ", " ")
            eb = f"{num} · {nombre_sec} · {' / '.join(bloques)}{rng}"
        doc.pagina(eb, titulo)
        for k, x in enumerate(grupo):
            if k == 1:
                doc.y += 10
                doc.c.setStrokeColor(MARCO)
                doc.c.setLineWidth(0.6)
                doc.c.setDash(2, 3)
                doc.c.line(M, doc.Y(doc.y), M + CW, doc.Y(doc.y))
                doc.c.setDash()
                doc.y += 12
            dibujar_toma(doc, x, d)
        i += len(grupo)


def sec_titulos(doc, d, num):
    ti = d["titulos"]
    c = doc.c
    for op in ti["opciones"]:
        doc.pagina(f"{num} · TÍTULO Y CRÉDITOS · IDEAS DE ART OF THE TITLE", f"Opción {op['letra']}")
        top = doc.y
        doc.circulo_num(M, top, op["letra"], 22)
        c.setFont("Poppins-SemiBold", 10)
        c.setFillColor(CREMA)
        c.drawString(M + 28, doc.Y(top + 15), op["nombre"])
        v = es_vertical(d)
        mw, mh = (146.25, 260) if v else (260, 146.25)
        maqueta(doc, M + (CW - mw) / 2, top + 32, op["maqueta"], v)
        doc.y = top + 32 + mh + 14
        filas = [("La idea", op["idea"]), ("Por qué funciona", op["porque"]),
                 ("En Resolve", op["resolve"]), ("Referencia", op["referencia"])]
        doc.tabla_oscura(filas, lab_w=80, gap=7)
    cr = ti.get("creditos")
    if cr:
        doc.pagina(f"{num} · TÍTULO Y CRÉDITOS · IDEAS DE ART OF THE TITLE", "Créditos")
        c.setFont("Poppins-SemiBold", 10)
        c.setFillColor(CREMA)
        c.drawString(M, doc.Y(doc.y + 10), cr["nombre"])
        v = es_vertical(d)
        mw, mh = (146.25, 260) if v else (260, 146.25)
        maqueta(doc, M + (CW - mw) / 2, doc.y + 22, cr["maqueta"], v)
        doc.y += 22 + mh + 14
        doc.tabla_oscura([("La idea", cr["idea"]), ("En Resolve", cr["resolve"])], lab_w=80, gap=7)
        doc.y += 8
    if ti.get("recomendacion"):
        doc.tarjeta_bloque("Mi recomendación", ti["recomendacion"], gap=8, pad=12)


def maqueta(doc, x, top, m, vertical=False):
    spec = {"escena": m.get("escena"), "personas": m.get("personas", 0), "seed": m.get("seed", 3),
            "extras": []}
    c = doc.c
    w, h = (146.25, 260) if vertical else (260, 146.25)
    c.saveState()
    c.setFillColor(CUADRO)
    pth = c.beginPath()
    pth.roundRect(x, doc.Y(top + h), w, h, 5)
    c.drawPath(pth, stroke=0, fill=1)
    c.clipPath(pth, stroke=0, fill=0)
    L = Lienzo(doc, x, top, w, h)
    prims = escena(spec["escena"], spec["personas"], spec["seed"]) if spec["escena"] else []
    for p in prims:
        p = dict(p)
        p["o"] = p.get("o", 1) * m.get("opacidad_escena", 0.45)
        L.prim(p)
    for p in m.get("extras", []):
        L.prim(p)
    if m.get("texto"):
        fuente = {"serif": "Serif", "serif_i": "Serif-Italic", "mano": "Mano", "sans": "Poppins-SemiBold"}[
            m.get("fuente", "serif")]
        s = m.get("tam", 24)
        lineas = str(m["texto"]).split("\n")
        while max(pdfmetrics.stringWidth(l, fuente, s) for l in lineas) > w - 20 and s > 8:
            s -= 1
        c.setFont(fuente, s)
        c.setFillColor(col(m.get("color", "crema")))
        y0 = doc.Y(top + h * m.get("y", 0.5)) - s * 0.3 + (len(lineas) - 1) * s * 1.05 / 2
        for k, l in enumerate(lineas):
            c.drawCentredString(x + w / 2, y0 - k * s * 1.05, l)
    if m.get("subtexto"):
        c.setFont("Poppins-SemiBold", 6)
        c.setFillColor(ORO)
        c.drawCentredString(x + w / 2, doc.Y(top + h * m.get("y", 0.5) + 18), m["subtexto"].upper())
    if m.get("notas"):
        c.setFont("Mano", 7.5)
        c.setFillColor(ORO)
        c.drawCentredString(x + w / 2, doc.Y(top + h - 12), m["notas"])
    c.restoreState()
    c.setStrokeColor(MARCO)
    c.setLineWidth(0.8)
    c.roundRect(x, doc.Y(top + h), w, h, 5, stroke=1, fill=0)


def sec_reel(doc, d, num):
    r = d["reel"]
    doc.pagina(f"{num} · REEL 9:16 · {r['duracion'].upper()}", "Reel 9:16")
    c = doc.c
    top = doc.y
    segs = [(t["tiempo"], t["nombre"]) for t in r["tramos"]]
    doc.y = telefono(doc, top, segs, r["notas"]) + 14
    filas = []
    for t in r["tramos"]:
        filas.append({"tiempo": t["tiempo"], "bloque": t["nombre"], "texto": t["texto"],
                      "sonido": t.get("detalle")})
    filas_tiempo_reel(doc, filas)


def filas_tiempo_reel(doc, filas):
    c = doc.c
    for r in filas:
        pt = para(r["texto"], 7.4, CREMA)
        ps = para(r["sonido"], 7.4, GRIS) if r.get("sonido") else None
        tw = CW - 96
        h = max(alto(pt, tw) + (alto(ps, tw) if ps else 0) + 9.4, 29.4)
        doc.asegurar(h + 3)
        t = doc.y
        doc.contorno(M, t, CW, h, MARCO, 1)
        c.setFont("Poppins-SemiBold", 8)
        c.setFillColor(ORO)
        c.drawString(M + 10, doc.Y(t + 12.5), r["tiempo"])
        c.setFont("Poppins", 6.4)
        c.setFillColor(GRIS)
        c.drawString(M + 10, doc.Y(t + 21.5), r["bloque"])
        y = t + 4.7
        y += doc.p(M + 86, y, tw, pt)
        if ps:
            doc.p(M + 86, y, tw, ps)
        doc.y += h + 3


def sec_musica(doc, d, num):
    mu = d["musica"]
    doc.pagina(f"{num} · MÚSICA · EPIDEMIC SOUND", "Música")
    doc.texto_flujo(mu["intro"], 8, CREMA, 10)
    for p in mu["pistas"]:
        txt = f"**Filtros:** {p['filtros']}\n**Buscar:** *{p['buscar']}*"
        if p.get("nota"):
            txt += "\n" + p["nota"]
        doc.tarjeta_bloque(p["nombre"], txt, derecha=f"Tramo: {p['tramo']}", gap=9, pad=12)
    if mu.get("licencia"):
        doc.tarjeta_bloque("Licencia", mu["licencia"], gap=9, pad=12)
    ef = d["efectos"]
    doc.pagina(f"{num} · EFECTOS DE SONIDO · EPIDEMIC SOUND", "Efectos")
    c = doc.c
    for e in ef["items"]:
        doc.asegurar(31)
        t = doc.y
        doc.tarjeta(M, t, CW, 27, barra=False)
        c.setFont("Poppins-SemiBold", 7.6)
        c.setFillColor(OSC)
        c.drawString(M + 12, doc.Y(t + 11.5), e["termino"])
        c.setFont("Poppins", 6.4)
        c.setFillColor(GRIS_C)
        c.drawString(M + 12, doc.Y(t + 21), e["donde"])
        pu = para(e["uso"], 7, OSC, align=TA_RIGHT)
        hu = alto(pu, 170)
        doc.p(M + CW - 182, t + (27 - hu) / 2, 170, pu)
        doc.y += 31
    if ef.get("nota"):
        doc.y += 2
        doc.texto_flujo(ef["nota"], 7.4, GRIS)


TIPS = [
    ("¿Qué movimiento de cámara usar?", [("Ansiedad", "Dolly zoom"), ("Impacto", "Crash zoom"),
        ("Distancia / soledad", "Travelling lateral"), ("Descubrir", "Panorámica de reconocimiento"),
        ("Grandeza / tensión", "Panorámica vertical")]),
    ("¿Qué plano usar?", [("Soledad", "Plano general"), ("Confusión", "Plano detalle"),
        ("Romance", "Plano medio corto"), ("Introducción", "Gran plano general"), ("Diálogo", "Plano medio"),
        ("Relación", "Plano doble"), ("Intimidad", "Plano medio corto"), ("Confrontación", "Plano contra plano"),
        ("Mirada", "Plano detalle"), ("Expectación", "Plano recurso (plano detalle)")]),
    ("¿Qué iluminación usar?", [("Tristeza", "Luz lateral suave"), ("Miedo", "Luz cenital"),
        ("Romance", "Luz cálida difusa"), ("Tensión", "Low key"), ("Poder", "Contraluz"),
        ("Incomodidad", "Luz central dura"), ("Soledad", "Una sola fuente (lámpara, ventana)"),
        ("Esperanza", "Luz natural de ventana")]),
    ("¿Qué ángulo usar?", [("Poder", "Contrapicado"), ("Vulnerabilidad", "Picado"),
        ("Desorientación", "Holandés"), ("Inferioridad", "Cenital"), ("Misterio", "Nadir")]),
    ("Tipos de plano", [("Plano general", "Muestra al personaje dentro del entorno; ideal para introducir lugares y situación."),
        ("Plano medio", "De la cintura hacia arriba; ideal para diálogos y escenas cotidianas."),
        ("Primer plano", "Rostro y emoción; resalta momentos de gran intensidad dramática."),
        ("Plano detalle", "Un objeto, parte del cuerpo o gesto; crea suspenso o revela información.")]),
    ("¿Cómo comenzar?", [("Enganchar", "Conflicto"), ("Curiosidad", "Pregunta"),
        ("Presentar protagonista", "Haciendo algo"), ("Tensión", "Problema")]),
    ("Estructura del guion", [("Presentación", "25 %"), ("Nudo", "50 %"), ("Clímax", "20 %"),
        ("Desenlace", "5 % · porcentajes según la duración total")]),
]


def sec_tips(doc, d, num):
    doc.pagina(f"{num} · TIPS DE FILMACIÓN · GUÍA RÁPIDA", "Tips de filmación")
    for titulo, filas in TIPS:
        doc.tarjeta_bloque(titulo, None, [(f"**{a}**", b) for a, b in filas], lab_w=100, gap=8, pad=10)


def sec_copy(doc, d, num):
    cp = d["copy"]
    doc.pagina(f"{num} · TEXTOS EN PANTALLA Y COPY", "Textos y copy")
    doc.eyebrow("TEXTOS EN PANTALLA", 8)
    for lab, val in cp["textos"]:
        pl = para(lab, 6.8, GRIS)
        pv = para(val, 7.4, CREMA)
        h = max(alto(pl, 96), alto(pv, CW - 110))
        doc.asegurar(h + 5)
        doc.p(M, doc.y + 0.6, 96, pl)
        doc.p(M + 110, doc.y, CW - 110, pv)
        doc.y += h + 6
    doc.y += 8
    tags = [("#" + t.lstrip("#")).lower().replace(" ", "") for t in cp["hashtags"]]
    for titulo, txt in [("Gancho (primera línea)", cp["gancho"]), ("Descripción", cp["descripcion"]),
                        ("Hashtags", " ".join(tags)), ("Texto alternativo", cp["alt"])]:
        doc.tarjeta_bloque(titulo, txt, gap=10, pad=12)


# ════════════════════════════════════════════════════════════════════
# 7. ARMADO
# ════════════════════════════════════════════════════════════════════
def generar(data, out):
    global SYM
    SYM = cargar_fuentes()
    validar(data)
    v = es_vertical(data)
    secciones = [("concepto", "Concepto"), ("estructura", "Estructura"),
                 ("guion", "Guion del reel" if v else "Guion de edición"), ("audio", "Audio")]
    secciones += [("referencias", "Referencias y técnicas"), ("storyboard", "Storyboard")]
    if data.get("especiales"):
        secciones.append(("especiales", "Tomas especiales"))
    secciones += [("titulos", "Título y créditos")]
    if not v:
        secciones.append(("reel", "Reel 9:16"))
    secciones += [("musica", "Música y efectos"), ("copy", "Textos y copy")]
    if data.get("tips", False):
        secciones.append(("tips", "Tips de filmación"))
    nums = {k: f"{i + 2:02d}" for i, (k, _) in enumerate(secciones)}
    indice = [(nums[k], n) for k, n in secciones]

    doc = Doc(out, data)
    sec_portada(doc, data, indice)
    sec_concepto(doc, data, nums["concepto"])
    sec_estructura(doc, data, nums["estructura"])
    sec_guion(doc, data, nums["guion"])
    sec_audio(doc, data, nums["audio"])
    sec_referencias(doc, data, nums["referencias"])
    sec_storyboard(doc, data, nums["storyboard"], "tomas", "STORYBOARD")
    if data.get("especiales"):
        sec_storyboard(doc, data, nums["especiales"], "especiales", "TOMAS ESPECIALES",
                       titulo_fijo="TOMAS ESPECIALES · TRANSICIONES Y TÉCNICAS")
    sec_titulos(doc, data, nums["titulos"])
    if not v:
        sec_reel(doc, data, nums["reel"])
    sec_musica(doc, data, nums["musica"])
    sec_copy(doc, data, nums["copy"])
    if data.get("tips", False):
        sec_tips(doc, data, nums["tips"])
    doc.cerrar()
    doc.c.save()
    print(f"PDF generado: {out} · {doc.n} páginas")
    for a in AVISOS:
        print("AVISO:", a)
    return doc.n


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python3 guia_rodaje.py proyecto.json salida.pdf")
        sys.exit(1)
    with open(sys.argv[1], encoding="utf-8") as f:
        datos = json.load(f)
    generar(datos, sys.argv[2])
