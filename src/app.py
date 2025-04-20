import os
import base64
import fitz  # PyMuPDF
import requests
from dotenv import load_dotenv
import gradio as gr

import pandas as pd
from utils.image_checker import is_blank_image, is_mostly_black_image, is_mostly_black_pdf_from_pages

load_dotenv()

WEBHOOKS_INVOICE = {
    "Invoice正式環境": os.getenv("N8N_WEBHOOK_INVOICE_PROD"),
    "Invoice測試環境": os.getenv("N8N_WEBHOOK_INVOICE_TEST"),
}

WEBHOOKS_PRODUCTS = {
    "Products正式環境": os.getenv("N8N_WEBHOOK_PRODUCTS_PROD"),
    "Products測試環境": os.getenv("N8N_WEBHOOK_PRODUCTS_TEST"),
}

# --- Upload Invoice ---
def upload_invoice(uploaded, env_choice="Invoice正式環境"):
    if uploaded is None:
        return {"error": "No file uploaded yet"}
    
    url = WEBHOOKS_INVOICE.get(env_choice)
    if not url:
        return {"error": f"Webhook URL not configured for {env_choice}"}

    file_path = uploaded.name
    filename = os.path.basename(file_path)

    # Check if the file is a PDF or an image
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

        if is_mostly_black_pdf_from_pages(pages):
            return {"error": "PDF 看起來是全黑的，請上傳有效的發票。"}
        
        payload = {
            "fileType": "pdf",
            "filename": filename,
            "pages": pages
        }
    # images
    else:
        try:
            with open(file_path, "rb") as f:
                img_b = f.read()
        except Exception as e:
            return {"error": f"Failed to read image: {e}"}
        
        if is_blank_image(img_b) or is_mostly_black_image(img_b):
            return {"error": "圖片看起來是空白或全黑的，請上傳有效的發票。"}

        payload = {
            "fileType": "image",
            "filename": filename,
            "data": base64.b64encode(img_b).decode()
        }

    # Send to n8n
    try:
        resp = requests.post(url, json=payload, timeout=150)
        resp.raise_for_status()
        return resp.json()
    
    except requests.RequestException as e:
        return {"error": str(e)}
    except ValueError:
        return {"error": "Invalid JSON response", "raw": resp.text}


# --- Upload Product List ---
def upload_products(uploaded, env_choice="Products正式環境"):
    if uploaded is None:
        return {"error": "No file uploaded yet"}
    
    url = WEBHOOKS_PRODUCTS.get(env_choice)
    if not url:
        return {"error": f"Webhook URL not configured for {env_choice}"}
    
    file_path = uploaded.name
    
    try:
        if file_path.lower().endswith(".csv"):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
    except Exception as e:
        return {"error": f"Failed to read file: {e}"}
    
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
        resp = requests.post(url, json=records, timeout=150)
        resp.raise_for_status()
        return resp.json()
    
    except requests.RequestException as e:
        return {"error": str(e)}



def main():
    with gr.Blocks() as demo:
        gr.Markdown("## Invoice Agent")

        with gr.Tabs():
            # 分頁 1：OCR 上傳
            with gr.TabItem("Invoice上傳"):
                env_choice = gr.Dropdown(
                    choices=list(WEBHOOKS_INVOICE.keys()),
                    value="Invoice正式環境",
                    label="Webhook環境選擇"
                )
                upload_img = gr.File(label="請上傳圖片或 PDF")
                ocr_out    = gr.JSON(label="OCR & 結構化結果")
                upload_img.change(fn=upload_invoice, inputs=[upload_img, env_choice], outputs=ocr_out)

            # 分頁 2：產品清單上傳
            with gr.TabItem("產品清單上傳"):
                env_choice = gr.Dropdown(
                    choices=list(WEBHOOKS_PRODUCTS.keys()),
                    value="Products正式環境",
                    label="Webhook環境選擇"
                )
                upload_xlsx = gr.File(label="請上傳產品清單 (.xlsx 或 .csv)")
                prod_out    = gr.JSON(label="產品清單處理結果")
                upload_xlsx.change(fn=upload_products, inputs=[upload_xlsx, env_choice], outputs=prod_out)
        demo.launch(server_name="0.0.0.0", server_port=7860)

if __name__ == "__main__":
    main()