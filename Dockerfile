FROM python:3.11-alpine

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# Expose the port according to the port you list under listen in config.json
EXPOSE 80
EXPOSE 443
# Debug port
EXPOSE 3030

# Logging to stdout
ENV PYTHONUNBUFFERED=1

CMD ["python3", "src/main.py"]