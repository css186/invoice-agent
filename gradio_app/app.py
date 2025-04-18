import gradio as gr
import requests
import json
import mimetypes

test_host = "https://n8n-kgyg.onrender.com/webhook-test/invoice"


def process_invoice(file):
    # Check file reading
    if hasattr(file, "read"):
        filename = getattr(file, "name", "upload.jpg")
        file_bytes = file.read()
    else:
        filename = file
        with open(file, "rb") as f:
            file_bytes = f.read()

        # Guess the MIME type
        mine_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"

        files = {
            "file": (filename, file_bytes, mine_type)
        }

        response = requests.post(test_host, files=files)
        # # Check for errors
        response.raise_for_status()
        return response.json()


iface = gr.Interface(
    fn=process_invoice,
    inputs=gr.File(label="Upload Invoice"),
    outputs="json",
    title="Ivoice Agent Demo"
)


if __name__ == "__main__":
    iface.launch(debug=True)