import os 

import pytesseract
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

import pytesseract
import cv2
import matplotlib.pyplot as plt
from pytesseract import Output
import numpy as np
import sys
import re
import itertools
import pickle
from PIL import Image
import pandas as pd
import os
import json
from img2table.ocr import TesseractOCR
from img2table.document import Image as table_Image
from dotenv import load_dotenv

load_dotenv("/content/drive/MyDrive/Colab Notebooks/Week6/.env")
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

# Flask Imports
from flask import (
    Blueprint,
    render_template,
    flash,
    redirect,
    url_for,
    request,
    session,
    current_app as app
    )


user_route = Blueprint("user", __name__)

@user_route.route("/")
def index():
    return redirect(url_for("user.home"))

@user_route.route("/home")
def home():
    # Instantiation of OCR
    ocr = TesseractOCR(lang="eng", n_threads=1)

    # Instantiation of document, either an image or a PDF
    doc = table_Image(os.path.join(os.path.dirname(__file__), 'static', "StockReport_2016-07.jpeg" ))

    # Table extraction
    extracted_tables = doc.extract_tables(ocr=ocr,
                                        implicit_rows=True,
                                        implicit_columns=True,
                                        borderless_tables=True,
                                        min_confidence=50)
    for table in extracted_tables:
        table_content = table.content
        columns = []
        for cell in table_content[0]:
            columns.append(cell.value)
        df = pd.DataFrame(columns=columns)
        for i in range(1, len(table_content)):
            row = {}
            for j in range(len(columns)):
                row[columns[j]] = table_content[i][j].value
            df.loc[len(df)] = row

    html_table = df.to_html(classes="table table-striped table-bordered", index=False)

    endpoint = "https://gen-ai-training-internal-july.cognitiveservices.azure.com/"
    model_name = "gpt-4o-mini"
    deployment = "gpt-4o-mini"

    subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
    api_version = "2024-12-01-preview"

    client = AzureOpenAI(
        api_version=api_version,
        azure_endpoint=endpoint,
        api_key=subscription_key,
    )

    # Call Azure OpenAI
    resp = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant that helps to analyze tables extracted from images."},
            {"role": "user", "content": "Summarize the table in a few sentences." + df.to_string() }
        ],
        max_tokens=1200,
        temperature=0.7,
        top_p=1.0,
        model=deployment
    )
    content = resp.choices[0].message.content
    return render_template("home.html", html_table=html_table, content=content)


