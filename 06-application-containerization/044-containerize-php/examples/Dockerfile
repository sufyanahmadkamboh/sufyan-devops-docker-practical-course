FROM php:8.5-fpm-alpine
WORKDIR /var/www/html
# the application code; PHP-FPM (port 9000) runs it, Nginx sits in front of it
COPY public ./public
# production PHP settings shipped with the official image
RUN cp "$PHP_INI_DIR/php.ini-production" "$PHP_INI_DIR/php.ini"
# the FPM master runs as root and starts its workers as www-data (see the lab)
EXPOSE 9000
