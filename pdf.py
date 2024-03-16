import os
import fitz
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello(string url):
    return "Hello, Azure! " . url

if __name__ == '__main__':
    app.run()

def pdf_to_images(pdf_path, output_dir):
    # Crie o diretório de saída se não existir
    os.makedirs(output_dir, exist_ok=True)

    # Abra o arquivo PDF
    with fitz.open(pdf_path) as doc:
        # Itere sobre cada página do PDF
        for page_number in range(len(doc)):
            # Renderize a página como uma imagem
            page = doc[page_number]
            pix = page.get_pixmap()

            # Salve a imagem no diretório de saída
            image_path = os.path.join(output_dir, f'page_{page_number+1}.png')
            pix.save(image_path)

            print(f'Página {page_number+1} salva como {image_path}')

# Caminho para o arquivo PDF
pdf_path = 'Z:\SouceCode\PdfToImage\incil.pdf'

# Diretório de saída para as imagens
output_dir = 'Z:\SouceCode\PdfToImage\saida'

# Chame a função para converter o PDF em imagens
pdf_to_images(pdf_path, output_dir)