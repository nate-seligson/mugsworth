#include <SPI.h>
#include <SD.h>
#include <Adafruit_VS1053.h>
#include <WiFi.h>

#define CLK            18
#define MISO           19
#define MOSI           23
#define BREAKOUT_RESET 15
#define BREAKOUT_CS    5
#define BREAKOUT_DCS   33
#define CARDCS         14
#define DREQ           35

// default network/server params – will be overridden via Serial
char ssid[32]     = "dpupsk";
char password[64] = "vincentdepaul15811660";
IPAddress hostIP(192,0,0,2);
const int port    = 8000;

const int motorPin  = 26;
const int buttonPin = 27;

volatile bool buttonPressed = false;
bool motorRunning = false;
bool speech = true;

Adafruit_VS1053_FilePlayer musicPlayer(
  BREAKOUT_RESET, BREAKOUT_CS, BREAKOUT_DCS, DREQ, CARDCS
);

String serialBuf;

void IRAM_ATTR handleButtonPress() {
  buttonPressed = digitalRead(buttonPin) == LOW;
}

void setup() {
  Serial.begin(115200);
  pinMode(motorPin, OUTPUT);
  pinMode(buttonPin, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(buttonPin), handleButtonPress, CHANGE);

  // init WiFi and VS1053/SD
  connectWiFi();
  if (!musicPlayer.begin()) {
    Serial.println(F("VS1053 not detected")); while (1);
  }
  if (!SD.begin(CARDCS)) {
    Serial.println("SD card init failed!"); while(1);
  }
  musicPlayer.setVolume(0,0);
  getData();  
}

void loop() {
  // check for serial commands
  if (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      processSerialCommand(serialBuf);
      serialBuf = "";
    } else {
      serialBuf += c;
      // guard buffer length
      if (serialBuf.length() > 200) serialBuf = "";
    }
  }

  // existing logic unchanged
  if (buttonPressed) {
    motorRunning = true;
  } else {
    motorRunning = false;
    analogWrite(motorPin, 0);
    if (speech) {
      Serial.println("playing");
      musicPlayer.playFullFile("/audio.mp3");
      speech = false;
      getData();
    }
  }

  if (motorRunning) {
    if (!speech) speech = true;
    analogWrite(motorPin, 200);
    delay(1000);
    analogWrite(motorPin, 0);
    delay(200);
  }
}

void processSerialCommand(const String &cmd) {
  // expected: SSID=...;PASS=...;IP=...;
  String s = cmd + ';';  
  int idx;
  if ((idx = s.indexOf("SSID=")) >= 0) {
    String v = s.substring(idx+5, s.indexOf(';',idx));
    v.toCharArray(ssid, sizeof(ssid));
    Serial.printf("Updated SSID: %s\n", ssid);
  }
  if ((idx = s.indexOf("PASS=")) >= 0) {
    String v = s.substring(idx+5, s.indexOf(';',idx));
    v.toCharArray(password, sizeof(password));
    Serial.printf("Updated PASS: %s\n", password);
  }
  if ((idx = s.indexOf("IP=")) >= 0) {
    String v = s.substring(idx+3, s.indexOf(';',idx));
    hostIP.fromString(v);
    Serial.printf("Updated IP: %s\n", hostIP.toString().c_str());
  }
  // reconnect Wi-Fi with new creds, then fetch once
  connectWiFi();
  getData();
}

void connectWiFi() {
  WiFi.disconnect(true);
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi ");
  Serial.println(ssid);

  unsigned long startAttemptTime = millis();
  const unsigned long timeout = 5000; // 5 seconds

  while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < timeout) {
    delay(200);
    Serial.print('.');
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nWiFi connection failed. Continuing without WiFi.");
  }
}


void getData() {
  WiFiClient client;
  Serial.print("Connecting to ");
  Serial.println(hostIP);
  client.setTimeout(100000);
  if (!client.connect(hostIP, port)) {
    Serial.println("Connection failed");
    return;
  }
  client.print(String("GET ") + "/cgi-bin/mugsworth.cgi HTTP/1.1\r\n" +
               "Host: " + hostIP.toString() + "\r\n" +
               "Accept: audio/mpeg\r\n" +
               "Connection: close\r\n\r\n");
  // skip headers
  while (client.connected()) {
    if (client.readStringUntil('\n') == "\r") break;
  }
  File mp3File = SD.open("/audio.mp3", FILE_WRITE);
  if (!mp3File) { Serial.println("File open failed"); client.stop(); return; }
  Serial.println("Saving MP3...");
  while (client.connected() || client.available()) {
    if (client.available()) {
      mp3File.write(client.read());
    }
  }
  mp3File.close();
  client.stop();
  Serial.println("Done.");
}
