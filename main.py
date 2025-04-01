import xml.etree.ElementTree as ET
import re

def corrigir_kml(kml_path):
    """ Tenta corrigir um KML quebrado removendo erros comuns. """
    with open(kml_path, "r", encoding="utf-8", errors="ignore") as f:
        kml_data = f.read()

    # Remove espaços em branco antes da declaração XML
    kml_data = re.sub(r"^\s*", "", kml_data)

    # Correções comuns
    kml_data = kml_data.replace("&", "&amp;")  # Corrige caracteres especiais
    kml_data = kml_data.replace("\x00", "")  # Remove caracteres nulos

    try:
        ET.fromstring(kml_data)  # Valida o XML
    except ET.ParseError as e:
        print(f"Erro de sintaxe detectado: {e}")

    return kml_data

def salvar_kml(kml_data, output_path):
    """ Salva o KML corrigido em um novo arquivo. """
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(kml_data)
    print(f"KML corrigido salvo em: {output_path}")

def processar_kml(kml_data):
    """ Processa o KML para gerar uma linha contínua a partir dos pontos. """
    tree = ET.ElementTree(ET.fromstring(kml_data))
    root = tree.getroot()

    # Namespace para lidar com possíveis namespaces no KML
    namespaces = {'kml': 'http://www.opengis.net/kml/2.2'}

    # Lista para armazenar as coordenadas de todos os pontos
    coordenadas = []

    # Iterar sobre todos os elementos <Placemark> que possuem <Point>
    for placemark in root.iter('{http://www.opengis.net/kml/2.2}Placemark'):
        for point in placemark.findall(".//{http://www.opengis.net/kml/2.2}Point"):
            for coordinates in point.findall(".//{http://www.opengis.net/kml/2.2}coordinates"):
                # Coletar as coordenadas do ponto
                coords = coordinates.text.strip()
                coordenadas.append(coords)  # Adiciona a coordenada do ponto à lista

    # Verifica se há coordenadas para gerar a linha
    if not coordenadas:
        print("Nenhum ponto encontrado para gerar a linha!")
        return None

    # Criar um novo KML com as coordenadas unidas como um único caminho (LineString)
    new_kml = ET.Element('{http://www.opengis.net/kml/2.2}kml', xmlns="http://www.opengis.net/kml/2.2")
    document = ET.SubElement(new_kml, '{http://www.opengis.net/kml/2.2}Document')

    # Definir o estilo para a linha (cor azul, largura 6)
    style = ET.SubElement(document, '{http://www.opengis.net/kml/2.2}Style', id="style1")
    line_style = ET.SubElement(style, '{http://www.opengis.net/kml/2.2}LineStyle')
    ET.SubElement(line_style, '{http://www.opengis.net/kml/2.2}color').text = 'ff0000ff'  # Azul
    ET.SubElement(line_style, '{http://www.opengis.net/kml/2.2}width').text = '6'  # Largura 6

    # Aplicar o estilo ao Placemark
    placemark = ET.SubElement(document, '{http://www.opengis.net/kml/2.2}Placemark')
    ET.SubElement(placemark, '{http://www.opengis.net/kml/2.2}styleUrl').text = '#style1'  # Referencia o estilo

    line_string = ET.SubElement(placemark, '{http://www.opengis.net/kml/2.2}LineString')
    coordinates = ET.SubElement(line_string, '{http://www.opengis.net/kml/2.2}coordinates')

    # Colocar as coordenadas como um caminho contínuo
    coordinates.text = " ".join(coordenadas)

    # Gerar o KML final
    return ET.tostring(new_kml, encoding="utf-8").decode('utf-8')

def ler_kml_quebrado(kml_path, output_path):
    """ Tenta ler um KML quebrado após corrigir erros e gerar um caminho contínuo. """
    kml_corrigido = corrigir_kml(kml_path)
    
    try:
        kml_processado = processar_kml(kml_corrigido)  # Processa o KML para gerar o caminho contínuo
        if kml_processado:
            salvar_kml(kml_processado, output_path)  # Salva o KML com o caminho contínuo
            print("KML com caminho contínuo carregado com sucesso!")
        else:
            print("Erro: Nenhum ponto encontrado para processar.")
        return kml_processado
    except ET.ParseError as e:
        print(f"Erro ao carregar KML: {e}")
        return None

# Teste com um arquivo quebrado
ler_kml_quebrado("kmlquebrado.kml", "kmlcorrigido_caminho_continuo_com_estilo.kml")
