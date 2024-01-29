# Use an official Python runtime as a parent image
FROM python:3.8

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
#RUN chmod 777 -R postgres_data/
RUN apt-get update && apt-get install -y cron || pacman -Sy --noconfirm cronie

# Set the working directory in the container
WORKDIR /app
COPY . /app/
# Copy the dependencies file to the working directory
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY data_replication.py .
COPY cronjob.txt /etc/cron.d/cronjob

RUN chmod 0644 /etc/cron.d/cronjob
RUN crontab /etc/cron.d/cronjob

CMD ["cron", "-f"]