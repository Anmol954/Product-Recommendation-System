FROM browserless/chrome:latest

# Install Python and pip
RUN apt-get update && apt-get install -y python3 python3-pip

# Set work directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy your entire app folder
COPY . .

# Expose Streamlit port
EXPOSE 8080

# Command to run your Streamlit app
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8080", "--server.enableCORS=false"]
