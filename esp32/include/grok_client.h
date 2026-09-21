#pragma once

#include <Arduino.h>

struct GrokReply {
    bool ok = false;
    String reply;
    String mood;  // idle | listening | thinking | speaking | happy | concerned
    int http_code = 0;
    String error;
};

namespace grok {

bool begin();
bool configured();
GrokReply ask(const String& message);
String infer_mood(const String& reply);

}  // namespace grok
