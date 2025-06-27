FROM python:3.12-slim

# Switch to root explicitly
USER root

# Install dependencies for Google Chrome
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y wget unzip curl gnupg && \
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    DEBIAN_FRONTEND=noninteractive apt install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port for Streamlit
EXPOSE 8080

# Command to run app
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8080", "--server.enableCORS=false"]
