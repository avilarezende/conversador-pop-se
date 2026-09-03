#pragma once

#include <Arduino.h>

struct PopseHealth {
    bool ok = false;
    String status;
    String service;
    String llm_provider;
    int http_code = 0;
    String error;
};

struct PopseChatReply {
    bool ok = false;
    String reply;
    int http_code = 0;
    String error;
};

namespace popse {

bool begin();
PopseHealth fetch_health();
PopseChatReply ask(const String& message);
const PopseHealth& last_health();

}  // namespace popse
