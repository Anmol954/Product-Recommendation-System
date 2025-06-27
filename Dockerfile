FROM mcr.microsoft.com/playwright:focal

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your app files
COPY . .

# Expose port for Streamlit
EXPOSE 8080

# Run your Streamlit app
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8080", "--server.enableCORS=false"]
