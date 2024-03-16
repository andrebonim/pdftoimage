import os
import fitz
import requests
import base64
import random
import string
from flask import Flask

app = Flask(__name__)
#http://127.0.0.1:5000/aHR0cHMgLy9sb2NhbGhvc3QvcHVibGljL2luY2lsLnBkZg==
#http://127.0.0.1:5000/aHR0cDovL2xvY2FsaG9zdC9wdWJsaWMvaW5jaWwucGRm
#https://f2w-pdf2image.azurewebsites.net/
# Caminho para o arquivo PDF

# Diretório de saída para as imagens
output_dir = 'saida'

@app.route('/<string:name>')
def hello(name):    
    response = requests.get(base64.b64decode(name))
    images_base64 = []
    # Verifique se a solicitação foi bem-sucedida
    if response.status_code == 200:
        # Defina o nome do arquivo para salvar
        filename = generate_random_string(10)
        
        # Salve o conteúdo do PDF em um arquivo local
        with open(filename, 'wb') as file:
            file.write(response.content)

        images_base64 = pdf_to_images(filename, output_dir)

    return images_base64

if __name__ == '__main__':
    app.run()

def generate_random_string(length):
    letters = string.ascii_letters + string.digits
    random_string = ''.join(random.choices(letters, k=length))
    return random_string + '.pdf'

def pdf_to_images(pdf_path, output_dir):
    images_base64 = []
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