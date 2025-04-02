import xml.etree.ElementTree as ET
import re
import tkinter as tk
from tkinter import filedialog, messagebox
import os

def corrigir_kml(kml_path):
    with open(kml_path, "r", encoding="utf-8", errors="ignore") as f:
        kml_data = f.read()
    kml_data = re.sub(r"^\s*", "", kml_data)

    kml_data = kml_data.replace("&", "&amp;") 
    kml_data = kml_data.replace("\x00", "") 

    try:
        ET.fromstring(kml_data)
    except ET.ParseError as e:
        print(f"Erro de sintaxe detectado: {e}")

    return kml_data

def salvar_kml(kml_data, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(kml_data)
    print(f"KML corrigido salvo em: {output_path}")

def processar_kml(kml_data):
    tree = ET.ElementTree(ET.fromstring(kml_data))
    root = tree.getroot()

    coordenadas = []
    for placemark in root.iter('{http://www.opengis.net/kml/2.2}Placemark'):
        for point in placemark.findall(".//{http://www.opengis.net/kml/2.2}Point"):
            for coordinates in point.findall(".//{http://www.opengis.net/kml/2.2}coordinates"):
                coords = coordinates.text.strip()
                coordenadas.append(coords)

    if not coordenadas:
        print("Nenhum ponto encontrado para gerar a linha!")
        return None

    new_kml = ET.Element('{http://www.opengis.net/kml/2.2}kml', xmlns="http://www.opengis.net/kml/2.2")
    document = ET.SubElement(new_kml, '{http://www.opengis.net/kml/2.2}Document')

    style = ET.SubElement(document, '{http://www.opengis.net/kml/2.2}Style', id="style1")
    line_style = ET.SubElement(style, '{http://www.opengis.net/kml/2.2}LineStyle')
    ET.SubElement(line_style, '{http://www.opengis.net/kml/2.2}color').text = 'ff0000ff'
    ET.SubElement(line_style, '{http://www.opengis.net/kml/2.2}width').text = '6'

    placemark = ET.SubElement(document, '{http://www.opengis.net/kml/2.2}Placemark')
    ET.SubElement(placemark, '{http://www.opengis.net/kml/2.2}styleUrl').text = '#style1'

    line_string = ET.SubElement(placemark, '{http://www.opengis.net/kml/2.2}LineString')
    coordinates = ET.SubElement(line_string, '{http://www.opengis.net/kml/2.2}coordinates')
    coordinates.text = " ".join(coordenadas)

    return ET.tostring(new_kml, encoding="utf-8").decode('utf-8')

def selecionar_arquivo():
    arquivo_origem = filedialog.askopenfilename(filetypes=[("KML Files", "*.kml")])
    if not arquivo_origem:
        return
    
    diretorio, nome_arquivo = os.path.split(arquivo_origem)
    nome_base, extensao = os.path.splitext(nome_arquivo)
    arquivo_saida = os.path.join(diretorio, f"{nome_base}_corrigido{extensao}")
    
    kml_corrigido = corrigir_kml(arquivo_origem)
    kml_processado = processar_kml(kml_corrigido)
    
    if kml_processado:
        salvar_kml(kml_processado, arquivo_saida)
        messagebox.showinfo("Sucesso", f"Arquivo corrigido salvo em:\n{arquivo_saida}")
    else:
        messagebox.showerror("Erro", "Falha ao processar o KML!")

root = tk.Tk()
root.title("Corretor de KML (Filipe Gabriel)")
root.geometry("350x100")

tk.Button(root, text="Selecionar KML", command=selecionar_arquivo, bg="red", fg="white").pack(pady=20)

root.mainloop()