# xml2altimetria.py
# -*- coding: utf-8 -*-
"""
Genera el archivo altimetria.svg (perfil altimétrico de la etapa)
a partir de etapaEsquema.xml

- Lee etapaEsquema.xml (con espacio de nombres http://www.uniovi.es)
- Extrae distancias y altitudes con expresiones XPath
- Escribe altimetria.svg con una polilínea cerrada y rellena (efecto suelo),
  ejes con escala, y líneas y textos verticales para los puntos de la etapa

Uso:  python xml2altimetria.py [etapaEsquema.xml] [altimetria.svg]

@version 1.0
Basado en los ejercicios 02010-XPath.py y 02030-SVG.py de la asignatura
"""
import os
import sys
import xml.etree.ElementTree as ET


class Svg(object):
    """
    Genera archivos SVG con rectángulos, círculos, líneas, polilíneas y texto
    Basada en la clase Svg del ejercicio 02030-SVG.py.
    Los atributos usan los nombres válidos de SVG (stroke-width, font-family,
    font-size...), que no se pueden pasar como argumentos con nombre en Python
    porque contienen guiones; por eso se pasan mediante un diccionario.
    """

    def __init__(self, ancho, alto):
        """
        Crea el elemento raíz, el espacio de nombres, la versión y el tamaño
        """
        self.raiz = ET.Element('svg', {
            'xmlns': "http://www.w3.org/2000/svg",
            'version': "1.1",
            'width': str(ancho),
            'height': str(alto),
            'viewBox': '0 0 {} {}'.format(ancho, alto)})

    def addRect(self, x, y, width, height, fill, strokeWidth, stroke):
        """Añade un elemento rect"""
        ET.SubElement(self.raiz, 'rect', {
            'x': str(x), 'y': str(y), 'width': str(width), 'height': str(height),
            'fill': fill, 'stroke-width': str(strokeWidth), 'stroke': stroke})

    def addCircle(self, cx, cy, r, fill, stroke='black', strokeWidth='1'):
        """Añade un elemento circle"""
        ET.SubElement(self.raiz, 'circle', {
            'cx': str(cx), 'cy': str(cy), 'r': str(r), 'fill': fill,
            'stroke': stroke, 'stroke-width': str(strokeWidth)})

    def addLine(self, x1, y1, x2, y2, stroke, strokeWidth, dasharray=None):
        """Añade un elemento line"""
        atributos = {'x1': str(x1), 'y1': str(y1), 'x2': str(x2), 'y2': str(y2),
                     'stroke': stroke, 'stroke-width': str(strokeWidth)}
        if dasharray:
            atributos['stroke-dasharray'] = dasharray
        ET.SubElement(self.raiz, 'line', atributos)

    def addPolyline(self, points, stroke, strokeWidth, fill):
        """Añade un elemento polyline"""
        ET.SubElement(self.raiz, 'polyline', {
            'points': points, 'stroke': stroke, 'stroke-width': str(strokeWidth),
            'fill': fill, 'stroke-linejoin': 'round'})

    def addText(self, texto, x, y, fontFamily, fontSize, fill='black',
                anchor='start', weight='normal', rotacion=None):
        """
        Añade un elemento text. Con rotacion=-90 el texto queda vertical
        (se lee de abajo hacia arriba)
        """
        atributos = {'x': str(x), 'y': str(y), 'font-family': fontFamily,
                     'font-size': str(fontSize), 'fill': fill,
                     'text-anchor': anchor, 'font-weight': weight}
        if rotacion is not None:
            atributos['transform'] = 'rotate({} {} {})'.format(rotacion, x, y)
        ET.SubElement(self.raiz, 'text', atributos).text = texto

    def escribir(self, nombreArchivoSVG):
        """Escribe el archivo SVG con declaración XML y codificación UTF-8"""
        arbol = ET.ElementTree(self.raiz)
        ET.indent(arbol)
        arbol.write(nombreArchivoSVG, encoding='utf-8', xml_declaration=True)

    def ver(self):
        """Muestra el contenido del SVG por pantalla. Se utiliza para depurar"""
        print("\nElemento raiz = ", self.raiz.tag)
        print("Atributos = ", self.raiz.attrib)
        for hijo in self.raiz.findall('.//'):  # Expresión XPath
            print("Elemento = ", hijo.tag, hijo.attrib)


class EtapaXml(object):
    """
    Lee etapaEsquema.xml, construye el árbol DOM en memoria y extrae con
    expresiones XPath las distancias y altitudes de la etapa.
    El prefijo 'u' representa el espacio de nombres http://www.uniovi.es
    """

    ESPACIO = {'u': 'http://www.uniovi.es'}

    def __init__(self, archivoXML):
        """Lee el archivo XML y genera en memoria el árbol DOM"""
        try:
            self.arbol = ET.parse(archivoXML)
        except IOError:
            print('No se encuentra el archivo ', archivoXML)
            sys.exit(1)
        except ET.ParseError:
            print('Error procesando en el archivo XML = ', archivoXML)
            sys.exit(1)
        self.raiz = self.arbol.getroot()

    def _texto(self, nodo, expresionXPath):
        """Devuelve el texto del primer nodo que cumple la expresión XPath"""
        return nodo.find(expresionXPath, EtapaXml.ESPACIO).text.strip()

    def numeroEtapa(self):
        return self._texto(self.raiz, './u:numeroEtapa')

    def longitud(self):
        """XPath: /etapa/longitud"""
        return float(self._texto(self.raiz, './u:longitud'))

    def desnivel(self):
        """XPath: /etapa/desnivel"""
        return self._texto(self.raiz, './u:desnivel')

    def _nombreCorto(self, texto):
        """Nombre de un lugar sin la provincia ni la segunda parte tras la coma"""
        return texto.split('(')[0].split(',')[0].strip()

    def _punto(self, nodo, nombre, tipo, km):
        return {'nombre': nombre, 'tipo': tipo, 'km': km,
                'alt': float(self._texto(nodo, './/u:altitud'))}

    def perfil(self):
        """
        Devuelve la lista de puntos (km, altitud) de la etapa ordenada por
        distancia: salida, hitos (sprints, puertos), puntos anónimos y meta
        """
        puntos = []
        salida = self.raiz.find('./u:coordenadasSalida', EtapaXml.ESPACIO)
        puntos.append(self._punto(salida,
                                  self._nombreCorto(self._texto(self.raiz, './u:lugarSalida')),
                                  'salida', 0.0))
        for expresion, tipo in (('.//u:puertoMontana', 'puerto'),
                                ('.//u:sprint', 'sprint'),
                                ('.//u:puntoAnonimo', 'anonimo')):
            for nodo in self.raiz.findall(expresion, EtapaXml.ESPACIO):
                nombre = nodo.get('nombre')
                if nombre is None:
                    nombre = self._texto(nodo, './u:lugar') if tipo != 'anonimo' else 'Punto'
                km = float(self._texto(nodo, './/u:distanciaSalida'))
                puntos.append(self._punto(nodo, nombre, tipo, km))
        meta = self.raiz.find('./u:coordenadasMeta', EtapaXml.ESPACIO)
        puntos.append(self._punto(meta,
                                  self._nombreCorto(self._texto(self.raiz, './u:lugarMeta')),
                                  'meta', self.longitud()))
        return sorted(puntos, key=lambda p: p['km'])


class Xml2Altimetria(object):
    """
    Genera altimetria.svg a partir de etapaEsquema.xml
    """

    ANCHO = 1400
    ALTO = 640
    MARGEN_IZQ = 90
    MARGEN_DER = 40
    ARRIBA = 250           # espacio para título y textos verticales
    ALTO_GRAFICA = 300     # altura de la zona del perfil
    FUENTE = 'Arial, Helvetica, sans-serif'

    COLORES = {'salida': '#e30613', 'meta': '#e30613', 'sprint': '#1f6fd1',
               'puerto': '#2e9e44', 'anonimo': '#f2c200'}

    def __init__(self, archivoXML, archivoSVG):
        self.archivoXML = archivoXML
        self.archivoSVG = archivoSVG
        self.etapa = EtapaXml(archivoXML)
        self.kmTotal = self.etapa.longitud()
        self.perfil = self.etapa.perfil()
        # Altitud máxima de la escala: múltiplo de 200 m por encima del punto más alto
        maxAlt = max(p['alt'] for p in self.perfil)
        self.altMax = (int(maxAlt // 200) + 1) * 200
        self.base = Xml2Altimetria.ARRIBA + Xml2Altimetria.ALTO_GRAFICA
        self.anchoGrafica = (Xml2Altimetria.ANCHO - Xml2Altimetria.MARGEN_IZQ
                             - Xml2Altimetria.MARGEN_DER)

    def _x(self, km):
        """Convierte kilómetros en coordenada X del SVG"""
        return Xml2Altimetria.MARGEN_IZQ + km / self.kmTotal * self.anchoGrafica

    def _y(self, altitud):
        """Convierte altitud en coordenada Y del SVG (el eje Y crece hacia abajo)"""
        return self.base - altitud / self.altMax * Xml2Altimetria.ALTO_GRAFICA

    def _escala(self, svg):
        """Dibuja la escala vertical (cada 200 m) y la horizontal (cada 20 km)"""
        f = Xml2Altimetria.FUENTE
        for alt in range(0, self.altMax + 1, 200):
            y = self._y(alt)
            svg.addLine(Xml2Altimetria.MARGEN_IZQ, y,
                        Xml2Altimetria.ANCHO - Xml2Altimetria.MARGEN_DER, y,
                        '#cccccc', 1, '4 4')
            svg.addText('{} m'.format(alt), Xml2Altimetria.MARGEN_IZQ - 10, y + 4,
                        f, 12, '#444444', 'end')
        km = 0
        while km <= self.kmTotal:
            x = self._x(km)
            svg.addLine(x, self.base, x, self.base + 6, '#444444', 1)
            svg.addText('{}'.format(km), x, self.base + 22, f, 12, '#444444', 'middle')
            km += 20
        svg.addText('km', Xml2Altimetria.ANCHO - Xml2Altimetria.MARGEN_DER,
                    self.base + 40, f, 12, '#444444', 'end')

    def _perfil(self, svg):
        """
        Dibuja el perfil como polilínea cerrada contra el suelo y rellena.
        Los vértices son los puntos de la etapa (km, altitud).
        """
        vertices = ['{:.1f},{:.1f}'.format(self._x(p['km']), self._y(p['alt']))
                    for p in self.perfil]
        cierre = ['{:.1f},{:.1f}'.format(self._x(self.perfil[-1]['km']), self.base),
                  '{:.1f},{:.1f}'.format(self._x(self.perfil[0]['km']), self.base)]
        svg.addPolyline(' '.join(vertices + cierre), '#8a1a12', 2, '#e8372c')

    def _hitos(self, svg):
        """Líneas verticales, textos verticales y marcadores de cada punto"""
        f = Xml2Altimetria.FUENTE
        yTexto = Xml2Altimetria.ARRIBA - 10
        for p in self.perfil:
            x = self._x(p['km'])
            color = Xml2Altimetria.COLORES[p['tipo']]
            svg.addLine(x, yTexto + 6, x, self._y(p['alt']), '#666666', 1)
            etiqueta = '{} / {:.0f} m'.format(p['nombre'], p['alt'])
            svg.addText(etiqueta, x + 4, yTexto, f, 13, '#222222', 'start', 'normal', -90)
            svg.addCircle(x, self._y(p['alt']), 5, color, '#222222', 1)

    def _leyenda(self, svg):
        """Leyenda de colores de los marcadores"""
        f = Xml2Altimetria.FUENTE
        x = Xml2Altimetria.MARGEN_IZQ
        y = Xml2Altimetria.ALTO - 20
        for tipo, texto in (('salida', 'Salida / Meta'), ('sprint', 'Sprint intermedio'),
                            ('puerto', 'Puerto de montaña'), ('anonimo', 'Punto anónimo')):
            svg.addCircle(x, y - 4, 6, Xml2Altimetria.COLORES[tipo], '#222222', 1)
            svg.addText(texto, x + 12, y, f, 13, '#222222')
            x += 190

    def generar(self):
        """
        Escribe el archivo SVG: encabezamiento, datos de distancia y altitud
        de los puntos de la etapa y cierre
        """
        svg = Svg(Xml2Altimetria.ANCHO, Xml2Altimetria.ALTO)
        f = Xml2Altimetria.FUENTE
        svg.addRect(0, 0, Xml2Altimetria.ANCHO, Xml2Altimetria.ALTO, 'white', 0, 'white')
        svg.addText('ALTIMETRÍA ETAPA {}'.format(self.etapa.numeroEtapa()),
                    Xml2Altimetria.MARGEN_IZQ, 40, f, 26, '#111111', 'start', 'bold')
        svg.addText('{} km'.format(self.etapa.longitud()),
                    Xml2Altimetria.ANCHO - Xml2Altimetria.MARGEN_DER, 40, f, 20,
                    '#111111', 'end', 'bold')
        self._escala(svg)
        self._perfil(svg)
        self._hitos(svg)
        svg.addText('Desnivel positivo: {} m'.format(self.etapa.desnivel()),
                    Xml2Altimetria.ANCHO - Xml2Altimetria.MARGEN_DER,
                    self.base + 70, f, 16, '#111111', 'end', 'bold')
        self._leyenda(svg)
        svg.escribir(self.archivoSVG)
        print('Puntos del perfil:', len(self.perfil))
        print('Creado el archivo:', self.archivoSVG)

    @staticmethod
    def main():
        """Programa principal. Se puede indicar el XML de entrada y el SVG de salida"""
        carpeta = os.path.dirname(os.path.abspath(__file__))
        entrada = sys.argv[1] if len(sys.argv) > 1 else os.path.join(carpeta, 'etapaEsquema.xml')
        salida = sys.argv[2] if len(sys.argv) > 2 else os.path.join(carpeta, 'altimetria.svg')
        Xml2Altimetria(entrada, salida).generar()


if __name__ == "__main__":
    Xml2Altimetria.main()
