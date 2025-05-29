# streamlit_app.py
import streamlit as st
import os
from PyPDF2 import PdfReader, PdfWriter
import tempfile

def split_pdf_by_size(input_path, max_mb):
    reader = PdfReader(input_path)
    total_pages = len(reader.pages)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    writer = PdfWriter()
    output_files = []
    page_batch = []
    start_page = 1

    for i in range(total_pages):
        page_batch.append(reader.pages[i])
        writer.add_page(reader.pages[i])
        temp_file = os.path.join(tempfile.gettempdir(), "temp_output.pdf")
        with open(temp_file, "wb") as f:
            writer.write(f)
        size_mb = os.path.getsize(temp_file) / (1024 * 1024)
        if size_mb > max_mb:
            writer = PdfWriter()
            for page in page_batch[:-1]:
                writer.add_page(page)
            end_page = start_page + len(page_batch) - 2
            output_filename = os.path.join(tempfile.gettempdir(), f"{base_name}-{start_page}-{end_page}.pdf")
            with open(output_filename, "wb") as f_out:
                writer.write(f_out)
            output_files.append(output_filename)
            start_page = end_page + 1
            writer = PdfWriter()
            writer.add_page(page_batch[-1])
            page_batch = [page_batch[-1]]
    if page_batch:
        end_page = start_page + len(page_batch) - 1
        output_filename = os.path.join(tempfile.gettempdir(), f"{base_name}-{start_page}-{end_page}.pdf")
        with open(output_filename, "wb") as f_out:
            writer.write(f_out)
        output_files.append(output_filename)
    return output_files

st.title("Split PDF by Max File Size (MB)")

uploaded_file = st.file_uploader("Upload PDF", type="pdf")
max_mb = st.number_input("Max Size per Part (MB)", min_value=0.5, value=1.0, step=0.1)

if uploaded_file and max_mb:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(uploaded_file.read())
        temp_pdf_path = temp_pdf.name

    output_files = split_pdf_by_size(temp_pdf_path, max_mb)

    st.success(f"Split into {len(output_files)} files:")
    for path in output_files:
        with open(path, "rb") as f:
            st.download_button(
                label=f"Download {os.path.basename(path)}",
                data=f,
                file_name=os.path.basename(path)
            )
