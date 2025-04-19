import os
import base64
import fitz  # PyMuPDF
import requests
from dotenv import load_dotenv
import gradio as gr

import pandas as pd
from io import BytesIO

load_dotenv()

# --- Upload Invoice ---
def upload_invoice(uploaded):
    if uploaded is None:
        return {"error": "No file uploaded yet"}
    
    url = os.getenv("N8N_WEBHOOK_INVOICE_LOCAL")
    if not url:
        return {"error": "N8N_WEBHOOK_INVOICE_LOCAL not configured"}

    file_path = uploaded.name
    filename = os.path.basename(file_path)

    if file_path.lower().endswith(".pdf"):
        pages = []
        try:
            doc = fitz.open(file_path)
        except Exception as e:
            return {"error": f"Failed to open PDF: {e}"}

        for i in range(len(doc)):
            pix = doc.load_page(i).get_pixmap(alpha=False)
            img_b = pix.tobytes("png")
            pages.append({
                "page": i + 1,
                "data": base64.b64encode(img_b).decode()
            })
        payload = {
            "fileType": "pdf",
            "filename": filename,
            "pages": pages
        }
    else:
        try:
            with open(file_path, "rb") as f:
                img_b = f.read()
        except Exception as e:
            return {"error": f"Failed to read image: {e}"}

        payload = {
            "fileType": "image",
            "filename": filename,
            "data": base64.b64encode(img_b).decode()
        }

    # Send to n8n
    try:
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        return {"error": str(e)}
    try:
        return resp.json()
    except ValueError:
        return {"error": "Invalid JSON response", "raw": resp.text}


# --- Upload Product List ---
def upload_products(uploaded):
    if uploaded is None:
        return {"error": "No file uploaded yet"}
    
    url = os.getenv("N8N_WEBHOOK_PRODUCTS_LOCAL")
    if not url:
        return {"error": "N8N_WEBHOOK_PRODUCTS_LOCAL not configured"}
    
    file_path = uploaded.name
    
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        return {"error": f"Failed to read Excel file: {e}"}
    
    # Convert DataFrame to JSON
    records = []
    for _, row in df.iterrows():
        records.append({
            "id":            row.get("品號"),
            "product_name":  row.get("品名"),
            "unit":          row.get("單位"),
            "currency":      row.get("幣別"),
            "unit_price":    float(row.get("單價") or 0)
        })

    try:
        resp = requests.post(url, json=records, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        return {"error": str(e)}
    try:
        return resp.json()
    except ValueError:
        return {"error": "Invalid JSON response", "raw": resp.text}

def main():
    with gr.Blocks() as demo:
        gr.Markdown("## Invoice Agent")

        with gr.Tabs():
            # 分頁 1：OCR 上傳
            with gr.TabItem("Invoice上傳"):
                upload_img = gr.File(label="請上傳圖片或 PDF")
                ocr_out    = gr.JSON(label="OCR & 結構化結果")
                upload_img.change(fn=upload_invoice, inputs=upload_img, outputs=ocr_out)

            # 分頁 2：產品清單上傳
            with gr.TabItem("產品清單上傳"):
                upload_xlsx = gr.File(label="請上傳產品清單 (.xlsx)")
                prod_out    = gr.JSON(label="產品清單處理結果")
                upload_xlsx.change(fn=upload_products, inputs=upload_xlsx, outputs=prod_out)

        demo.launch()

if __name__ == "__main__":
    main()