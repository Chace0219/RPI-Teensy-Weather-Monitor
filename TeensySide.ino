// Screen Pins
#define sclk 13
#define mosi 11
#define dc   9
#define cs   10
#define rst  8

// Color definitions
#define	BLACK           0x0000
#define	BLUE            0x001F
#define	RED             0xF800
#define	GREEN           0x07E0
#define CYAN            0x07FF
#define MAGENTA         0xF81F
#define YELLOW          0xFFE0  
#define WHITE           0xFFFF

//#include <Lighting.h>
#include <avr/io.h>
#include <avr/interrupt.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1351.h>
#include <Adafruit_PWMServoDriver.h>
#include <SPI.h>
#include <Wire.h>
#include <Stepper.h>
#include <Lightning.h>
#include <RainMaker.h>
#include <WeatherCloud.h>


//Screen library for Teensy screen
Adafruit_SSD1351 tft = Adafruit_SSD1351(cs, dc, mosi, sclk, rst);  

//Start STEPPER CLOUD
void CloudComplete();
WeatherCloud weatherCloud(3, 4, 5, 6, &CloudComplete);

void CloudComplete() {
  Serial.println("Cloud DONE");
}

//Interrupt for cloud stepper motor top bounds
void pin_ISR() {
  weatherCloud.HandleInterrupt();
  Serial.println("Interrupt complete");
} 

void setup() {
  Serial.begin(9600);

  Serial.println("Start cloud setup");
  
  attachInterrupt(digitalPinToInterrupt(2), pin_ISR, CHANGE);
  
  weatherCloud.setSpeed(1600);
  weatherCloud.Initialise();
  Serial.println("End cloud initialise home");
  weatherCloud.stepperStatus = FORWARD;

  Serial.println(weatherCloud.stepperStatus);
  Serial.println("End cloud setup");
  
  Serial.print("hello!");
  tft.begin();
}

void loop() {
  Serial.println("Updating Cloud");
  weatherCloud.Update();
  
//    // Drive each servo one at a time
//  Serial.println(servonum);
//  for (uint16_t pulselen = SERVOMIN; pulselen < SERVOMAX; pulselen++) {
//    pwm.setPWM(servonum, 0, pulselen);
//  }
//
//  //delay(500);
//  for (uint16_t pulselen = SERVOMAX; pulselen > SERVOMIN; pulselen--) {
//    pwm.setPWM(servonum, 0, pulselen);
//  }
//
//  //delay(500);
//
//  servonum ++;
//  if (servonum > 7) servonum = 0;
}

//// you can use this function if you'd like to set the pulse length in seconds
//// e.g. setServoPulse(0, 0.001) is a ~1 millisecond pulse width. its not precise!
//void setServoPulse(uint8_t n, double pulse) {
//  double pulselength;
//  
//  pulselength = 1000000;   // 1,000,000 us per second
//  pulselength /= 60;   // 60 Hz
//  Serial.print(pulselength); Serial.println(" us per period"); 
//  pulselength /= 4096;  // 12 bits of resolution
//  Serial.print(pulselength); Serial.println(" us per bit"); 
//  pulse *= 1000;
//  pulse /= pulselength;
//  Serial.println(pulse);
//  pwm.setPWM(n, 0, pulse);
//}

void testdrawtext(char *text, uint16_t color) {
  tft.setCursor(0,0);
  tft.setTextColor(color);
  tft.print(text);
}
