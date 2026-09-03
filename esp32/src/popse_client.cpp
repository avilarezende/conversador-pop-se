#include "popse_client.h"

#include <HTTPClient.h>
#include <WiFiClient.h>
#include <ArduinoJson.h>

#include "config.h"
#include "wifi_manager.h"

#if __has_include("secrets.h")
#include "secrets.h"
#else
#include "secrets.h.example"
#endif

namespace popse {
namespace {

PopseHealth g_last_health;

String trim_slash(String url) {
    while (url.endsWith("/")) {
        url.remove(url.length() - 1);
    }
    return url;
}

bool http_get(const String& url, String& body, int& code, String& error) {
    body = "";
    code = 0;
    error = "";

    if (!wifi_mgr::is_connected()) {
        error = "wifi_down";
        return false;
    }

    HTTPClient http;
    http.setTimeout(POPSE_HTTP_TIMEOUT_MS);
    http.setConnectTimeout(POPSE_HTTP_TIMEOUT_MS);
    if (!http.begin(url)) {
        error = "begin_failed";
        return false;
    }

    code = http.GET();
    if (code > 0) {
        body = http.getString();
    } else {
        error = http.errorToString(code);
    }
    http.end();
    return code > 0;
}

bool http_post_json(const String& url, const String& payload, String& body, int& code,
                    String& error) {
    body = "";
    code = 0;
    error = "";

    if (!wifi_mgr::is_connected()) {
        error = "wifi_down";
        return false;
    }

    HTTPClient http;
    http.setTimeout(POPSE_HTTP_TIMEOUT_MS);
    http.setConnectTimeout(POPSE_HTTP_TIMEOUT_MS);
    if (!http.begin(url)) {
        error = "begin_failed";
        return false;
    }
    http.addHeader("Content-Type", "application/json");

    code = http.POST(payload);
    if (code > 0) {
        body = http.getString();
    } else {
        error = http.errorToString(code);
    }
    http.end();
    return code > 0;
}

}  // namespace

bool begin() {
    Serial.printf("[popse] Engine: %s\n", POPSE_ENGINE_URL);
    return true;
}

PopseHealth fetch_health() {
    PopseHealth h;
#if !POPSE_ENABLED
    h.error = "disabled";
    g_last_health = h;
    return h;
#endif

    String body;
    String url = trim_slash(String(POPSE_ENGINE_URL)) + "/health";
    if (!http_get(url, body, h.http_code, h.error)) {
        g_last_health = h;
        return h;
    }

    if (h.http_code != 200) {
        h.error = "http_" + String(h.http_code);
        g_last_health = h;
        return h;
    }

    JsonDocument doc;
    const DeserializationError err = deserializeJson(doc, body);
    if (err) {
        h.error = String("json:") + err.c_str();
        g_last_health = h;
        return h;
    }

    h.status = doc["status"] | "";
    h.service = doc["service"] | "";
    h.llm_provider = doc["llm_provider"] | "";
    h.ok = h.status.equalsIgnoreCase("ok");
    g_last_health = h;

    Serial.printf("[popse] health ok=%d status=%s llm=%s\n",
                  h.ok ? 1 : 0, h.status.c_str(), h.llm_provider.c_str());
    return h;
}

PopseChatReply ask(const String& message) {
    PopseChatReply r;
#if !POPSE_ENABLED
    r.error = "disabled";
    return r;
#endif

    JsonDocument req;
    req["message"] = message;
    req["user_id"] = POPSE_USER_ID;
    req["channel"] = POPSE_CHANNEL;

    String payload;
    serializeJson(req, payload);

    String body;
    String url = trim_slash(String(POPSE_ENGINE_URL)) + "/api/v1/chat";
    if (!http_post_json(url, payload, body, r.http_code, r.error)) {
        return r;
    }

    if (r.http_code != 200) {
        r.error = "http_" + String(r.http_code);
        return r;
    }

    JsonDocument doc;
    const DeserializationError err = deserializeJson(doc, body);
    if (err) {
        r.error = String("json:") + err.c_str();
        return r;
    }

    r.reply = doc["reply"] | "";
    r.ok = r.reply.length() > 0;
    Serial.printf("[popse] chat ok=%d len=%u\n", r.ok ? 1 : 0,
                  static_cast<unsigned>(r.reply.length()));
    return r;
}

const PopseHealth& last_health() {
    return g_last_health;
}

}  // namespace popse
