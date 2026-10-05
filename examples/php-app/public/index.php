<?php
// A small PHP page served by PHP-FPM behind Nginx
header('Content-Type: application/json');
if ($_SERVER['REQUEST_URI'] === '/health') {
    echo json_encode(['status' => 'ok']);
    exit;
}
echo json_encode(['message' => 'Hello from PHP', 'hostname' => gethostname(), 'php' => PHP_VERSION]);
