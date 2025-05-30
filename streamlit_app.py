import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
import tempfile
import os
import zipfile
import io

def get_file_size_mb(filepath):
    return os.path.getsize(filepath) / (1024 * 1024)

def clean_filename(filename):
    return os.path.splitext(os.path.basename(filename))[0]

def split_pdf_by_size(input_path, max_mb, base_name):
    reader = PdfReader(input_path)
    total_pages = len(reader.pages)

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
        size_mb = get_file_size_mb(temp_file)

        if size_mb > max_mb:
            writer = PdfWriter()
            for page in page_batch[:-1]:
                writer.add_page(page)
            end_page = start_page + len(page_batch) - 2
            output_filename = os.path.join(
                tempfile.gettempdir(), f"{base_name}-{start_page}-{end_page}.pdf"
            )
            with open(output_filename, "wb") as f_out:
                writer.write(f_out)
            output_files.append(output_filename)

            start_page = end_page + 1
            writer = PdfWriter()
            writer.add_page(page_batch[-1])
            page_batch = [page_batch[-1]]

    if page_batch:
        end_page = start_page + len(page_batch) - 1
        output_filename = os.path.join(
            tempfile.gettempdir(), f"{base_name}-{start_page}-{end_page}.pdf"
        )
        with open(output_filename, "wb") as f_out:
            writer.write(f_out)
        output_files.append(output_filename)

    return output_files

# Streamlit UI
st.title("📄 Split PDF by Max File Size (MB)")

uploaded_file = st.file_uploader("Upload PDF", type="pdf")
max_mb = st.number_input("Max Size per Part (MB)", min_value=0.5, value=1.0, step=0.1)

if uploaded_file and max_mb:
    base_name = clean_filename(uploaded_file.name)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(uploaded_file.read())
        temp_pdf_path = temp_pdf.name

    output_files = split_pdf_by_size(temp_pdf_path, max_mb, base_name)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for file_path in output_files:
            zipf.write(file_path, arcname=os.path.basename(file_path))
    zip_buffer.seek(0)

    st.success(f"✅ Split into {len(output_files)} parts.")
    st.download_button(
        label="📦 Download All as ZIP",
        data=zip_buffer,
        file_name=f"{base_name}_split.zip",
        mime="application/zip"
    )
