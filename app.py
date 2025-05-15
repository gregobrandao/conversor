import sys, os
print("Executável:", sys.executable)
print("sys.path:")
for p in sys.path:
    print(" ", p)

import os
import tempfile
from flask import Flask, request, render_template, send_file, abort
import camelot
import pandas as pd

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def upload_and_convert():
    if request.method == "GET":
        return render_template("upload.html")

    pdf = request.files.get("pdf_file")
    if not pdf or not pdf.filename.lower().endswith(".pdf"):
        abort(400, "Envie um arquivo PDF válido.")

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
        pdf.save(tmp_pdf.name)

    try:
        tables = camelot.read_pdf(tmp_pdf.name, pages="all", flavor="stream")
        if not tables:
            abort(422, "Nenhuma tabela encontrada no PDF.")

        df = pd.concat([t.df for t in tables], ignore_index=True)
        tmp_xlsx = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        df.to_excel(tmp_xlsx.name, index=False)
        tmp_xlsx.close()

        return send_file(
            tmp_xlsx.name,
            as_attachment=True,
            download_name="saida.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    finally:
        os.unlink(tmp_pdf.name)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
