FROM python:3.12-slim
WORKDIR /app

LABEL "title" = "Crusadetome DataEntry Tool"
LABEL "version" = "1.0.0"
LABEL "description" = "Data Entry tool for converting Warhammer 40k unit data into JSON format."

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501
CMD ["streamlit", "run", "main.py"]