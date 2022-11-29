import streamlit as st
import requests
import base64
import json
from time import sleep
from PIL import Image
import io
import math

def cogniflow_request_image(image_base64, image_format, attempt=3):

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'x-api-key': st.secrets["api_key"]
    }

    data = {
        "format": image_format,
        "base64_image": image_base64
    }

    data_json = json.dumps(data)
    while attempt > 0:
        try:
            response = requests.post(st.secrets["model_url"], headers=headers, data=data_json)
            result = response.json()
        except Exception as ex:
            attempt = attempt - 1
            if attempt > 0:
                print(f'Error trying to get cogniflow prediction endpoint. Retrying again in 3 seconds. '
                      f'Error: {str(ex)}')
                sleep(3)
            else:
                raise ex
        else:
            return result

st.image("https://uploads-ssl.webflow.com/60510407e7726b268293da1c/638674660af8372329ee1a3e_back_eye.jpeg", width=200)

st.title('Retinopatia Diabetica')

st.markdown("Powered by [Cogniflow](https://www.cogniflow.ai)")

threshold = st.slider("Threshold", 0.0, 1.0, 0.4)

rd_confidence_threshold = threshold

file = st.file_uploader("Upload a picture", type=['jpg', 'png', 'jpeg'])

if file is not None:
    
    image_format = file.type.replace("image/", "")
    bytes_data = file.getvalue()
    
    img = Image.open(io.BytesIO(bytes_data))
    w, h = img.size
    ratio = h/w

    if w > 1024:
        img = img.resize((1024,math.ceil(ratio*1024)))
        img_bytes = io.BytesIO()
        img.save(img_bytes, format=image_format)
        bytes_data = img_bytes.getvalue()

    image_b64 = base64.b64encode(bytes_data).decode()

    with st.spinner("Procesando imagen..."):
        result = cogniflow_request_image(image_b64, image_format)

    rd_category = result["result"]
    rd_confidence = result["confidence_score"]
    
    is_positive_recognition = (rd_category == '1 - YES Diabetic Retinopathy') or (rd_confidence < (1 - rd_confidence_threshold))
    if is_positive_recognition:
        rd_confidence = rd_confidence if rd_category == '1 - YES Diabetic Retinopathy' else round(1 - rd_confidence, 3)
        rd_category = 'YES - Diabetic Retinopathy'
    else:
        rd_category = 'NO - Diabetic Retinopathy'

    st.json({ "Resultado":rd_category, "Score de confianza":rd_confidence})
    st.image(file)
