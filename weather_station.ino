#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h>
#include <DHT.h>

// ---------------- CONFIG ----------------
#define DHT_PIN 2
#define DHT_TYPE DHT22
#define RAIN_ANALOG A0
#define RAIN_DIGITAL 4

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define OLED_ADDR 0x3C

DHT dht(DHT_PIN, DHT_TYPE);
Adafruit_BMP280 bmp;
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

bool bmpOK = false;

float temperature, humidity, pressure, altitude;
int rainValue, rainDigital;

unsigned long lastRead = 0;
const unsigned long INTERVAL = 5000;

// Forward declare
void printJSON();

// --------------- SETUP -------------------
void setup() {
  Serial.begin(115200);
  delay(300);

  dht.begin();

  // BMP detect
  bmpOK = bmp.begin(0x76) || bmp.begin(0x77);

  // OLED detect
  if (!display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR)) {
    while (1); // freeze
  }

  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(10, 20);
  display.println("Weather");
  display.setCursor(10, 40);
  display.println("Station");
  display.display();
  delay(1500);
}

// --------------- LOOP ---------------------
void loop() {
  if (millis() - lastRead >= INTERVAL) {
    lastRead = millis();
    readSensors();
    updateDisplay();
    printJSON();
  }
}

// --------------- READ SENSORS -------------
void readSensors() {
  humidity = dht.readHumidity();
  temperature = dht.readTemperature();

  if (bmpOK) {
    pressure = bmp.readPressure() / 100.0;
    altitude = bmp.readAltitude(1013.25);
  } else {
    pressure = 0;
    altitude = 0;
  }

  rainValue = analogRead(RAIN_ANALOG);
  rainDigital = digitalRead(RAIN_DIGITAL);
}

// --------------- OLED DISPLAY -------------
void updateDisplay() {
  display.clearDisplay();

  // ----- TITLE -----
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(20, 0);
  display.println("Weather Station");

  // ----- BIG TEMPERATURE -----
  display.setTextSize(2);

  // Make temperature text
  char tempBuff[10];
  dtostrf(temperature, 4, 1, tempBuff);  // Safe for AVR

  // Measure text BEFORE drawing
  int16_t x1, y1;
  uint16_t w, h;
  display.getTextBounds(tempBuff, 0, 0, &x1, &y1, &w, &h);

  // Leave space for degree symbol + C
  int tempX = (SCREEN_WIDTH - (w + 14)) / 2;  // +14px = bitmap (6px) + spacing + C

  // Draw temperature text
  display.setCursor(tempX, 14);
  display.print(tempBuff);

  // Draw degree bitmap
  drawDegreeSymbol(tempX + w + 2, 16);  // align vertically nicely

  // Draw 'C'
  display.setCursor(tempX + w + 10, 14);
  display.print("C");

  // ----- ROW 1 -----
  display.setTextSize(1);

  display.setCursor(0, 42);
  display.print("H:");
  display.print(humidity, 0);
  display.print("%");

  display.setCursor(70, 42);
  display.print("P:");
  display.print(pressure, 0);

  // ----- ROW 2 -----
  display.setCursor(0, 54);
  display.print("Rain:");
  display.print(rainDigital ? "Dry" : "Wet");

  display.setCursor(70, 54);
  display.print("A:");
  display.print(rainValue);

  display.display();
}

// Draw custom degree symbol (6x6)
void drawDegreeSymbol(int x, int y) {
  static const unsigned char degreeBitmap[] PROGMEM = {
    0b00111000,
    0b01101100,
    0b01000100,
    0b01000100,
    0b01101100,
    0b00111000
  };
  display.drawBitmap(x, y, degreeBitmap, 6, 6, SSD1306_WHITE);
}

// --------------- JSON OUTPUT --------------
void printJSON() {
  Serial.print("{");

  Serial.print("\"timestamp\":"); Serial.print(millis()/1000);
  Serial.print(",\"temperature\":"); Serial.print(temperature);
  Serial.print(",\"humidity\":"); Serial.print(humidity);
  Serial.print(",\"pressure\":"); Serial.print(pressure);
  Serial.print(",\"altitude\":"); Serial.print(altitude);
  Serial.print(",\"rain_value\":"); Serial.print(rainValue);
  Serial.print(",\"rain_digital\":"); Serial.print(rainDigital);

  Serial.println("}");
}
