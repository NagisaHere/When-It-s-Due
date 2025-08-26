FROM python:3.8-slim
WORKDIR /app

# RUN pip install -r requirements.txt
# COPY ./src /app

RUN chmod +x /app/gunicorn.sh

CMD ["bash", "gunicorn.sh"]
