#include "grok_client.h"

#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include <ArduinoJson.h>

#include "config.h"
#include "wifi_manager.h"

#if __has_include("secrets.h")
#include "secrets.h"
#else
#include "secrets.h.example"
#endif

namespace grok {
namespace {

String trim_slash(String url) {
    while (url.endsWith("/")) {
        url.remove(url.length() - 1);
    }
    return url;
}

}  // namespace

bool begin() {
    Serial.printf("[grok] model=%s base=%s\n", GROK_MODEL, GROK_BASE_URL);
    return configured();
}

bool configured() {
    return String(GROK_API_KEY).length() > 0;
}

String infer_mood(const String& reply) {
    String low = reply;
    low.toLowerCase();
    if (low.indexOf("desculpe") >= 0 || low.indexOf("problema") >= 0 ||
        low.indexOf("falha") >= 0 || low.indexOf("infelizmente") >= 0) {
        return "concerned";
    }
    if (low.indexOf("bom dia") >= 0 || low.indexOf("tudo bem") >= 0 ||
        low.indexOf("otimo") >= 0 || low.indexOf("ótimo") >= 0 ||
        low.indexOf("prazer") >= 0) {
        return "happy";
    }
    return "speaking";
}

GrokReply ask(const String& message) {
    GrokReply r;
    if (!configured()) {
        r.error = "missing_api_key";
        return r;
    }
    if (!wifi_mgr::is_connected()) {
        r.error = "wifi_down";
        return r;
    }

    JsonDocument req;
    req["model"] = GROK_MODEL;
    JsonArray messages = req["messages"].to<JsonArray>();
    JsonObject sys = messages.add<JsonObject>();
    sys["role"] = "system";
    sys["content"] = ASSISTANT_SYSTEM_PROMPT;
    JsonObject user = messages.add<JsonObject>();
    user["role"] = "user";
    user["content"] = message;

    String payload;
    serializeJson(req, payload);

    WiFiClientSecure client;
    client.setInsecure();  // CYD: sem store CA; troque por setCACert se preferir

    HTTPClient http;
    http.setTimeout(GROK_HTTP_TIMEOUT_MS);
    http.setConnectTimeout(GROK_HTTP_TIMEOUT_MS);

    const String url = trim_slash(String(GROK_BASE_URL)) + "/chat/completions";
    if (!http.begin(client, url)) {
        r.error = "begin_failed";
        return r;
    }
    http.addHeader("Content-Type", "application/json");
    http.addHeader("Authorization", String("Bearer ") + GROK_API_KEY);

    r.http_code = http.POST(payload);
    String body;
    if (r.http_code > 0) {
        body = http.getString();
    } else {
        r.error = http.errorToString(r.http_code);
        http.end();
        return r;
    }
    http.end();

    if (r.http_code != 200) {
        r.error = "http_" + String(r.http_code);
        Serial.printf("[grok] error body: %s\n", body.substring(0, 180).c_str());
        return r;
    }

    JsonDocument doc;
    const DeserializationError err = deserializeJson(doc, body);
    if (err) {
        r.error = String("json:") + err.c_str();
        return r;
    }

    r.reply = doc["choices"][0]["message"]["content"] | "";
    r.ok = r.reply.length() > 0;
    r.mood = infer_mood(r.reply);
    Serial.printf("[grok] ok=%d len=%u mood=%s\n", r.ok ? 1 : 0,
                  static_cast<unsigned>(r.reply.length()), r.mood.c_str());
    return r;
}

}  // namespace grok
