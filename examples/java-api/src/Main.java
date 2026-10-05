// A small HTTP API with only the JDK: GET / and GET /health
import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;

public class Main {
    public static void main(String[] args) throws IOException {
        int port = Integer.parseInt(System.getenv().getOrDefault("PORT", "8080"));
        String host = InetAddress.getLocalHost().getHostName();
        HttpServer server = HttpServer.create(new InetSocketAddress("0.0.0.0", port), 0);
        server.createContext("/health", ex -> reply(ex, "{\"status\":\"ok\"}"));
        server.createContext("/", ex -> reply(ex, "{\"message\":\"Hello from Java\",\"hostname\":\"" + host + "\"}"));
        server.start();
        System.out.println("java-api listening on port " + port);
    }

    static void reply(com.sun.net.httpserver.HttpExchange ex, String body) throws IOException {
        byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
        ex.getResponseHeaders().set("Content-Type", "application/json");
        ex.sendResponseHeaders(200, bytes.length);
        ex.getResponseBody().write(bytes);
        ex.close();
    }
}
