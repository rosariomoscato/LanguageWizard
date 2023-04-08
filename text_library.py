import streamlit as st

# Reading Files
import docx2txt
import pdfplumber


# DOCUMENT Fetching
def get_docx(docx_file):
	return docx2txt.process(docx_file)

def get_pdf(pdf_file):
	pdf_file = pdfplumber.open(pdf_file)
	p0 = pdf_file.pages[0]
	return p0.extract_text()

def get_txt(text_file):
	return str(text_file.read(),"utf-8")
