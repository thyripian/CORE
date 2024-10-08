from file_handling import (read_excel_file, read_pdf_file, read_pptx_file,
                           read_word_file)


def extract_text_from_word(file_path):
    return read_word_file(file_path)


def extract_text_from_excel(file_path):
    return read_excel_file(file_path)


def extract_text_from_pdf(file_path):
    return read_pdf_file(file_path)


def extract_text_from_pptx(file_path):
    return read_pptx_file(file_path)
