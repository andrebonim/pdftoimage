import os
import PyPDF2
import fitz
import codecs
import requests
import base64
import random
import string
import tempfile
import pytesseract
import io
from flask import Flask
from io import BytesIO
from PIL import Image

app = Flask(__name__)
#http://127.0.0.1:5000/aHR0cHMgLy9sb2NhbGhvc3QvcHVibGljL2luY2lsLnBkZg==
#http://127.0.0.1:5000/aHR0cDovL2xvY2FsaG9zdC9wdWJsaWMvaW5jaWwucGRm
#https://f2w-pdf2image.azurewebsites.net/aHR0cDovL2xvY2FsaG9zdC9wdWJsaWMvaW5jaWwucGRm
#https://f2w-pdf2image.azurewebsites.net/aHR0cHM6Ly93d3cubGV4cGl0LmNvbS9zdG9yYWdlL2RkSDZXYUpZaXUucGRm
#http://127.0.0.1:5000/aHR0cHM6Ly93d3cubGV4cGl0LmNvbS9zdG9yYWdlL2RkSDZXYUpZaXUucGRm
# Caminho para o arquivo PDF

# Diretório de saída para as imagens
output_dir = ''

@app.route('/pdf/<string:name>')
def hello(name):        
    response = requests.get(base64.b64decode(name))
    images_base64 = []
    # Verifique se a solicitação foi bem-sucedida
    if response.status_code == 200:
        # Defina o nome do arquivo para salvar
        filename = generate_random_string(10,'pdf')
        
        # Salve o conteúdo do PDF em um arquivo local
        with open(filename, 'wb') as file:
            file.write(response.content)

        images_base64 = extrair_texto_imagem_pdf(filename)
        #images_base64 = pdf_to_images(filename, output_dir)

    os.remove(filename)
    return images_base64

@app.route('/ocr/<string:name>')
def ocr(name):            
    response = requests.get(base64.b64decode(name))    
    texto_imagem = []
    # Verifique se a solicitação foi bem-sucedida
    if response.status_code == 200:
        
        # Defina o nome do arquivo para salvar
        filename = generate_random_string(10,'pdf')
        
        # Salve o conteúdo do PDF em um arquivo local
        with open(filename, 'wb') as file:
            file.write(response.content)

        # Abre o arquivo PDF        
        doc = fitz.open(filename)
        
        # Itera sobre as páginas do PDF
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            pix = page.get_pixmap()

            textPage = page.get_text("text").strip()

            if textPage:
                texto_imagem.append(('texto', textPage))

            # Extrai imagens da página
            images = page.get_images()

            # Itera sobre as imagens
            for i, img_info in enumerate(images):
                xref = img_info[0]
                base_image = doc.extract_image(xref)
                image = Image.open(io.BytesIO(base_image["image"]))

                # Aplica OCR na imagem                
                texto_imagem.append(('ocr', extract_text_from_image(image)))

        # Fecha o arquivo PDF        
        doc.close()
        os.remove(filename)
    
    return texto_imagem

if __name__ == '__main__':
    app.run()

# Função para extrair texto de uma imagem usando o pytesseract
def extract_text_from_image(image):
    text = pytesseract.image_to_string(image)
    return text    

def generate_random_string(length,extension):
    letters = string.digits
    random_string = ''.join(random.choices(letters, k=length))
    return random_string + '.' + extension

def extrair_texto_imagem_pdf(pdf_path):
    texto_imagem = []

    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)

        for page_number in range(len(reader.pages)):
            page = reader.pages[page_number]
            text = page.extract_text().strip()

            if text:
                texto_imagem.append(('texto', text))
            else:
                doc = fitz.open(pdf_path)
                page_doc = doc.load_page(page_number)
                pix = page_doc.get_pixmap()

                if pix is not None:
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    img = redimensionar_imagem(img, 512, 512)
                    img = img.convert("RGB")
                    
                    tempFielName = generate_random_string(10,'jpg')
                    
                    img.save(tempFielName, format="JPEG", quality=50)
                    with open(tempFielName, 'rb') as image_file:
                        img_bytes = image_file.read()

                    os.remove(tempFielName)
                    #img_bytes = pix.tobytes()
                    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                    img_html = f'data:image/jpeg;base64,{img_base64}'
                    texto_imagem.append(('imagem', img_html))

    return texto_imagem    

def redimensionar_imagem(imagem, max_largura, max_altura):
    largura, altura = imagem.size

    # Verifica se a imagem precisa ser redimensionada
    if largura > max_largura or altura > max_altura:
        proporcao = min(max_largura / largura, max_altura / altura)
        nova_largura = int(largura * proporcao)
        nova_altura = int(altura * proporcao)
        imagem = imagem.resize((nova_largura, nova_altura), Image.LANCZOS)

    return imagem    

def pdf_to_images(pdf_path, output_dir):
    images_base64 = []
    # Crie o diretório de saída se não existir
    #os.makedirs(output_dir, exist_ok=True)

    # Abra o arquivo PDF
    with fitz.open(pdf_path) as doc:
        # Itere sobre cada página do PDF
        for page_number in range(len(doc)):
            # Renderize a página como uma imagem
            page = doc[page_number]
            pix = page.get_pixmap()

            # Salve a imagem no diretório de saída
            image_path = os.path.join(output_dir, f'{pdf_path}_page_{page_number+1}.png')
            pix.save(image_path)

            # Converta a imagem em base64
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')
                images_base64.append(image_base64)

            # Exclua o arquivo de imagem
            os.remove(image_path)
    
    os.remove(pdf_path)
    return images_base64



# Chame a função para converter o PDF em imagens
#pdf_to_images(pdf_path, output_dir)