#!/bin/bash

# Instalação das dependências do Tesseract OCR
apt-get update
apt-get install -y tesseract-ocr
apt-get install -y libtesseract-dev

# Instalação dos idiomas suportados pelo Tesseract OCR
apt-get install -y tesseract-ocr-eng  # Inglês
apt-get install -y tesseract-ocr-deu  # Alemão
apt-get install -y tesseract-ocr-fra  # Francês
# Adicione mais comandos de instalação para outros idiomas conforme necessário