import gradio as gr
import requests
import mimetypes
import os




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

        response = requests.post(os.getenv("N8N_WEBHOOK_TEST_URL"), files=files)
        # # Check for errors
        response.raise_for_status()
        return response.json()



def main():
    iface = gr.Interface(
        fn=process_invoice,
        inputs=gr.File(label="Upload Invoice"),
        outputs="json",
        title="Invoice Agent Demo"
        )
    iface.launch()

if __name__ == "__main__":
    main()