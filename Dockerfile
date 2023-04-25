FROM python:alpine

COPY ./app /app

WORKDIR /app

RUN pip install -r requirements.txt

COPY ./crontab /etc/cron.d/crontab
RUN chmod 0644 /etc/cron.d/crontab
RUN crontab /etc/cron.d/crontab

# Create new user and change permissions
# RUN adduser --disabled-password --no-create-home app

# # Change ownership to app
# RUN chown -R app:app /app
# RUN chmod -R 700 /app

# USER app

# Copy entrypoint and make executable
COPY ./scripts /scripts
RUN chmod -R +x /scripts

# CMD ["crond", "-f"]
CMD ["/scripts/entrypoint.sh"]