FROM nginx:latest

# For caching static files
RUN mkdir /tmp/cache
RUN chown www-data /tmp/cache

# Replace the Nginx configuration with our configuration
RUN rm /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/

# Replacing the default configuration with custom configuration
RUN rm /etc/nginx/conf.d/default.conf
COPY idfmi.conf /etc/nginx/conf.d/
