#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <DHT.h>
#include <ESP8266WiFi.h>
#include <BlynkSimpleEsp8266.h>

// Blynk credentials
#define BLYNK_TEMPLATE_ID "TMPL3BwYOgYXD"
#define BLYNK_TEMPLATE_NAME "SmartFarm"
#define BLYNK_AUTH_TOKEN "8VDegcvSkywp6--o9uGILoEMy1MXmGbx"

// WiFi credentials
char ssid[] = "";
char pass[] = "";

// Pin definitions
#define DHTPIN D4           // GPIO2
#define DHTTYPE DHT11
#define SOIL_MOISTURE_PIN A0
#define RELAY_PIN D3        // GPIO0
#define BUTTON_PIN D7       // GPIO13

DHT dht(DHTPIN, DHTTYPE);
LiquidCrystal_I2C lcd(0x27, 16, 2);

bool pumpState = false;
bool lastButtonState = HIGH;
BlynkTimer timer;

unsigned long previousMillis = 0;
const long interval = 2000;  // Sensor refresh interval

void setup() {
  Serial.begin(115200);
  
  dht.begin();
  lcd.init();
  lcd.backlight();

  pinMode(RELAY_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  digitalWrite(RELAY_PIN, LOW);  // Pump initially OFF

  Blynk.begin(BLYNK_AUTH_TOKEN, ssid, pass);
  timer.setInterval(200L, checkButton);

  lcd.setCursor(0, 0);
  lcd.print("Initializing...");
}

void loop() {
  Blynk.run();
  timer.run();

  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    float humidity = dht.readHumidity();
    float temperature = dht.readTemperature();
    int soilMoistureRaw = analogRead(SOIL_MOISTURE_PIN);
    int soilMoisturePercent = map(soilMoistureRaw, 1023, 300, 0, 100);
    soilMoisturePercent = constrain(soilMoisturePercent, 0, 100);

    if (isnan(humidity) || isnan(temperature)) {
      Serial.println("DHT sensor error!");
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("DHT sensor error");
      return;
    }

    // Debug output
    Serial.print("Temp: "); Serial.print(temperature);
    Serial.print(" C | Humidity: "); Serial.print(humidity);
    Serial.print(" % | Soil: "); Serial.print(soilMoisturePercent); Serial.println(" %");

    // Update LCD
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("T:");
    lcd.print(temperature, 1);
    lcd.print((char)223);  // degree symbol
    lcd.print("C H:");
    lcd.print(humidity, 0);
    lcd.print("%");

    lcd.setCursor(0, 1);
    lcd.print("Soil:");
    lcd.print(soilMoisturePercent);
    lcd.print("% Pump:");
    lcd.print(pumpState ? "ON" : "OFF");

    // Send to Blynk
    Blynk.virtualWrite(V0, temperature);
    Blynk.virtualWrite(V1, humidity);
    Blynk.virtualWrite(V2, soilMoisturePercent);
    Blynk.virtualWrite(V12, pumpState);  // Reflect pump state
  }
}

void checkButton() {
  bool currentButtonState = digitalRead(BUTTON_PIN);

  if (lastButtonState == HIGH && currentButtonState == LOW) {
    pumpState = !pumpState;
    digitalWrite(RELAY_PIN, pumpState ? HIGH : LOW);
    Blynk.virtualWrite(V12, pumpState);
    Serial.println(pumpState ? "Pump ON (button)" : "Pump OFF (button)");
  }

  lastButtonState = currentButtonState;
}

BLYNK_WRITE(V12) {
  pumpState = param.asInt();
  digitalWrite(RELAY_PIN, pumpState ? HIGH : LOW);
  Serial.println(pumpState ? "Pump ON (Blynk)" : "Pump OFF (Blynk)");
}