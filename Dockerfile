# Use an official Python runtime as the base image
FROM python:3.12.1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/

# Specify the command to run your bot.py script
#RUN streamlit run streamlit_app.py
#CMD ["gunicorn", "flask.py", "run:app"]
CMD ["python", "flask.py"]
