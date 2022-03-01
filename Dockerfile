FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
WORKDIR /
COPY . /
RUN pip install -r requirements.txt
RUN pip install pydantic[email]
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]