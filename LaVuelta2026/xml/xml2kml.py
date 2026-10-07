# xml2kml.py
# -*- coding: utf-8 -*-
"""
Genera el archivo etapa.kml (planimetría de la etapa) a partir de etapaEsquema.xml

- Lee etapaEsquema.xml (con espacio de nombres http://www.uniovi.es)
- Extrae los datos con expresiones XPath
- Escribe etapa.kml con:
    rojo     -> salida y meta
    verde    -> puertos de montaña
    azul     -> sprints
    amarillo -> puntos anónimos
    línea    -> recorrido de la etapa

Uso:  python xml2kml.py [etapaEsquema.xml] [etapa.kml]

@version 1.0
Basado en los ejercicios 02010-XPath.py y 02020-KML.py de la asignatura
"""
import os
import sys
import xml.etree.ElementTree as ET


class Kml(object):
    """
    Genera un archivo KML con puntos (Placemark/Point) y líneas (LineString)
    Basada en la clase Kml del ejercicio 02020-KML.py
    """

    # Colores KML en formato aabbggrr (alfa, azul, verde, rojo)
    ROJO = 'ff0000ff'
    VERDE = 'ff00ff00'
    AZUL = 'ffff0000'
    AMARILLO = 'ff00ffff'
    NARANJA = 'ff0080ff'

    ICONO = 'http://maps.google.com/mapfiles/kml/pushpin/wht-pushpin.png'

    def __init__(self, nombre):
        """
        Crea el elemento raíz, el espacio de nombres KML y el elemento Document
        """
        self.raiz = ET.Element('kml', xmlns="http://www.opengis.net/kml/2.2")
        self.doc = ET.SubElement(self.raiz, 'Document')
        ET.SubElement(self.doc, 'name').text = nombre

    def addEstiloPunto(self, identificador, color, escala='1.2'):
        """
        Añade un <Style> con un icono de chincheta tintado con el color indicado
        """
        estilo = ET.SubElement(self.doc, 'Style', id=identificador)
        icono = ET.SubElement(estilo, 'IconStyle')
        ET.SubElement(icono, 'color').text = color
        ET.SubElement(icono, 'scale').text = escala
        ET.SubElement(ET.SubElement(icono, 'Icon'), 'href').text = Kml.ICONO

    def addEstiloLinea(self, identificador, color, ancho):
        """
        Añade un <Style> para líneas
        """
        estilo = ET.SubElement(self.doc, 'Style', id=identificador)
        linea = ET.SubElement(estilo, 'LineStyle')
        ET.SubElement(linea, 'color').text = color
        ET.SubElement(linea, 'width').text = ancho

    def addPlacemark(self, nombre, descripcion, long, lat, alt, modoAltitud, estilo):
        """
        Añade un elemento <Placemark> con un punto <Point>
        """
        pm = ET.SubElement(self.doc, 'Placemark')
        ET.SubElement(pm, 'name').text = nombre
        ET.SubElement(pm, 'description').text = descripcion
        ET.SubElement(pm, 'styleUrl').text = '#' + estilo
        punto = ET.SubElement(pm, 'Point')
        ET.SubElement(punto, 'altitudeMode').text = modoAltitud
        ET.SubElement(punto, 'coordinates').text = '{},{},{}'.format(long, lat, alt)

    def addLineString(self, nombre, extrude, tesela, listaCoordenadas, modoAltitud, estilo):
        """
        Añade un elemento <Placemark> con una línea <LineString>
        """
        pm = ET.SubElement(self.doc, 'Placemark')
        ET.SubElement(pm, 'name').text = nombre
        ET.SubElement(pm, 'styleUrl').text = '#' + estilo
        ls = ET.SubElement(pm, 'LineString')
        ET.SubElement(ls, 'extrude').text = extrude
        ET.SubElement(ls, 'tessellate').text = tesela
        ET.SubElement(ls, 'altitudeMode').text = modoAltitud
        ET.SubElement(ls, 'coordinates').text = listaCoordenadas

    def escribir(self, nombreArchivoKML):
        """
        Escribe el archivo KML con declaración XML y codificación UTF-8
        """
        arbol = ET.ElementTree(self.raiz)
        ET.indent(arbol)
        arbol.write(nombreArchivoKML, encoding='utf-8', xml_declaration=True)

    def ver(self):
        """
        Muestra el contenido del KML por pantalla. Se utiliza para depurar
        """
        print("\nElemento raiz = ", self.raiz.tag)
        print("Atributos = ", self.raiz.attrib)
        for hijo in self.raiz.findall('.//Placemark'):  # Expresión XPath
            print("Placemark = ", hijo.find('name').text)


class EtapaXml(object):
    """
    Lee etapaEsquema.xml, construye el árbol DOM en memoria y extrae los datos
    de la etapa mediante expresiones XPath.
    Como el archivo usa el espacio de nombres http://www.uniovi.es, las
    expresiones XPath utilizan el prefijo 'u' asociado a ese espacio de nombres.
    """

    ESPACIO = {'u': 'http://www.uniovi.es'}

    def __init__(self, archivoXML):
        """
        Lee el archivo XML y genera en memoria el árbol DOM
        """
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
        """
        Devuelve el texto del primer nodo que cumple la expresión XPath
        """
        return nodo.find(expresionXPath, EtapaXml.ESPACIO).text.strip()

    def _coordenadas(self, nodo):
        """
        Devuelve (longitud, latitud, altitud) a partir de un nodo que contiene
        los elementos longitudGeo, latitud y altitud
        """
        return (self._texto(nodo, './/u:longitudGeo'),
                self._texto(nodo, './/u:latitud'),
                self._texto(nodo, './/u:altitud'))

    def _punto(self, nodo, nombre, tipo):
        """
        Construye un diccionario con los datos de un punto de la etapa
        """
        long, lat, alt = self._coordenadas(nodo)
        distancia = self._texto(nodo, './/u:distanciaSalida')
        return {'nombre': nombre, 'tipo': tipo, 'long': long, 'lat': lat,
                'alt': alt, 'km': float(distancia)}

    def nombreEtapa(self):
        return self._texto(self.raiz, './u:nombre')

    def numeroEtapa(self):
        return self._texto(self.raiz, './u:numeroEtapa')

    def salida(self):
        """XPath: /etapa/coordenadasSalida"""
        nodo = self.raiz.find('./u:coordenadasSalida', EtapaXml.ESPACIO)
        long, lat, alt = self._coordenadas(nodo)
        nombre = self._texto(self.raiz, './u:lugarSalida')
        return {'nombre': nombre, 'tipo': 'salida', 'long': long, 'lat': lat,
                'alt': alt, 'km': 0.0}

    def meta(self):
        """XPath: /etapa/coordenadasMeta"""
        nodo = self.raiz.find('./u:coordenadasMeta', EtapaXml.ESPACIO)
        long, lat, alt = self._coordenadas(nodo)
        nombre = self._texto(self.raiz, './u:lugarMeta')
        km = float(self._texto(self.raiz, './u:longitud'))
        return {'nombre': nombre, 'tipo': 'meta', 'long': long, 'lat': lat,
                'alt': alt, 'km': km}

    def puertos(self):
        """XPath: //puertoMontana"""
        lista = []
        for nodo in self.raiz.findall('.//u:puertoMontana', EtapaXml.ESPACIO):
            lugar = self._texto(nodo, './u:lugar')
            lista.append(self._punto(nodo, lugar, 'puerto'))
        return lista

    def sprints(self):
        """XPath: //sprint"""
        lista = []
        for nodo in self.raiz.findall('.//u:sprint', EtapaXml.ESPACIO):
            lugar = self._texto(nodo, './u:lugar')
            lista.append(self._punto(nodo, lugar, 'sprint'))
        return lista

    def puntosAnonimos(self):
        """XPath: //puntoAnonimo"""
        lista = []
        for nodo in self.raiz.findall('.//u:puntoAnonimo', EtapaXml.ESPACIO):
            nombre = nodo.get('nombre', 'Punto anónimo')
            lista.append(self._punto(nodo, nombre, 'anonimo'))
        return lista


class Xml2Kml(object):
    """
    Genera etapa.kml a partir de etapaEsquema.xml
    """

    def __init__(self, archivoXML, archivoKML):
        self.archivoXML = archivoXML
        self.archivoKML = archivoKML
        self.etapa = EtapaXml(archivoXML)

    def _descripcion(self, punto):
        """Texto descriptivo de un punto: distancia desde la salida y altitud"""
        return 'Km {:.1f} - Altitud {} m'.format(punto['km'], punto['alt'])

    def generar(self):
        """
        Lee los datos con XPath y escribe el archivo KML
        (prólogo + coordenadas + epílogo)
        """
        etapa = self.etapa
        kml = Kml('Etapa {} - {}'.format(etapa.numeroEtapa(), etapa.nombreEtapa()))

        # Prólogo: estilos
        kml.addEstiloPunto('rojo', Kml.ROJO)
        kml.addEstiloPunto('verde', Kml.VERDE)
        kml.addEstiloPunto('azul', Kml.AZUL)
        kml.addEstiloPunto('amarillo', Kml.AMARILLO)
        kml.addEstiloLinea('recorrido', Kml.NARANJA, '4')

        salida = etapa.salida()
        meta = etapa.meta()
        puertos = etapa.puertos()
        sprints = etapa.sprints()
        anonimos = etapa.puntosAnonimos()

        # Recorrido: salida + puntos ordenados por distancia + meta
        intermedios = sorted(puertos + sprints + anonimos, key=lambda p: p['km'])
        trazado = [salida] + intermedios + [meta]
        coordenadas = '\n'.join('{},{},{}'.format(p['long'], p['lat'], p['alt'])
                                for p in trazado)
        kml.addLineString('Recorrido de la etapa', '0', '1', coordenadas,
                          'clampToGround', 'recorrido')

        # Puntos: rojo salida/meta, verde puertos, azul sprints, amarillo anónimos
        for punto, estilo in ([(salida, 'rojo'), (meta, 'rojo')]
                              + [(p, 'verde') for p in puertos]
                              + [(p, 'azul') for p in sprints]
                              + [(p, 'amarillo') for p in anonimos]):
            kml.addPlacemark(punto['nombre'], self._descripcion(punto),
                             punto['long'], punto['lat'], punto['alt'],
                             'clampToGround', estilo)

        # Epílogo: escritura del archivo
        kml.escribir(self.archivoKML)
        print('Puntos: salida 1, meta 1, puertos {}, sprints {}, anónimos {}'
              .format(len(puertos), len(sprints), len(anonimos)))
        print('Vértices del recorrido:', len(trazado))
        print('Creado el archivo:', self.archivoKML)

    @staticmethod
    def main():
        """Programa principal. Se puede indicar el XML de entrada y el KML de salida"""
        carpeta = os.path.dirname(os.path.abspath(__file__))
        entrada = sys.argv[1] if len(sys.argv) > 1 else os.path.join(carpeta, 'etapaEsquema.xml')
        salida = sys.argv[2] if len(sys.argv) > 2 else os.path.join(carpeta, 'etapa.kml')
        Xml2Kml(entrada, salida).generar()


if __name__ == "__main__":
    Xml2Kml.main()
