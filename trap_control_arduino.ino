#define PIN_SIDEFAN 4
#define PIN_BOTTOMFAN 5
#define PIN_LIGHT 7
#define PIN_SOLENOID 6 //6

#define SERVO_START 152 // 150
#define SERVO_END 0

#define NUM_SHAKE 10

#include <Servo.h>
#include <MsTimer2.h>

Servo myservo;

bool stat_sidefan = LOW; // Initially Turn On
bool stat_bottomfan = HIGH; // Initially Turn Off
bool stat_solenoid = LOW; // Initially Turn On
bool stat_light = HIGH; // Initially Turn Off
bool stat_shutdown = false;

char msg = 0;
int pos = SERVO_START;
int time_elapsed = 0;

void shuffle_panel(char c) {
  int angle = 50;
  if(c=='l'){
    for (int i = 0; i < NUM_SHAKE; i++) {
      myservo.write(150+50);
      delay(50);
      myservo.write(150+20);
      delay(50);
    }
  } else if(c =='r'){
        for (int i = 0; i < NUM_SHAKE; i++) {
      myservo.write(150-50);
      delay(50);
      myservo.write(150-20);
      delay(50);
    }
  }

}


void shake_panel() {
  for (int i = 0; i < NUM_SHAKE; i++) {
    myservo.write(-20);
    delay(100);
    myservo.write(20);
    delay(100);
  }
}

void toggle_solenoid() {
  time_elapsed++;
}

void setup() {
  // put your setup code here, to run once:
  digitalWrite(PIN_SIDEFAN, stat_sidefan);
  digitalWrite(PIN_BOTTOMFAN, stat_bottomfan);
  digitalWrite(PIN_SOLENOID, stat_solenoid);
  digitalWrite(PIN_LIGHT, stat_light);

  myservo.attach(9);
  myservo.write(pos);

  MsTimer2::set(1000, toggle_solenoid); // 1[min] period
  MsTimer2::start();

  pinMode(PIN_SIDEFAN, OUTPUT);
  pinMode(PIN_BOTTOMFAN, OUTPUT);
  pinMode(PIN_SOLENOID, OUTPUT);
  pinMode(PIN_LIGHT, OUTPUT);

  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }
  Serial.write("Connection Estabilished!");

}


void loop() {

  msg = Serial.read();

  // put your main code here, to run repeatedly:
  if (msg == 's') {
    Serial.println("Toggle Sidefan");
    stat_sidefan = !stat_sidefan;
  }
  else if (msg == 'b') {
    Serial.println("Toggle Bottomfan");
    stat_bottomfan = !stat_bottomfan;
  }
  else if (msg == 'l') {
    Serial.println("Toggle Light");
    stat_light = !stat_light;
  }
  else if (msg == 'u') {
    shuffle_panel('l');
    myservo.write(SERVO_START);
  }
  else if (msg == 'i') {
    shuffle_panel('r');
    myservo.write(SERVO_START);
  }
  else if (msg == 'd') {
    Serial.println("Drop Mosquitoes");
    delay(400);
    shake_panel();
    myservo.write(SERVO_START);
    delay(400);
  }
  else if (msg == 'e'){
    Serial.println("Toggle Shutdown");
    stat_shutdown != stat_shutdown;
  }

  if (time_elapsed == 180) {
    time_elapsed = 0;
  }
  else if (time_elapsed >= 120 && time_elapsed < 180) {
    stat_solenoid = HIGH;
  } else {
    stat_solenoid = LOW;
  }

  if(stat_shutdown){
    digitalWrite(PIN_SIDEFAN, HIGH);
    digitalWrite(PIN_LIGHT, HIGH);
    digitalWrite(PIN_BOTTOMFAN, HIGH);
    digitalWrite(PIN_SOLENOID, HIGH);
  }else{
    digitalWrite(PIN_SIDEFAN, stat_sidefan);
    digitalWrite(PIN_LIGHT, stat_light);
    digitalWrite(PIN_BOTTOMFAN, stat_bottomfan);
    digitalWrite(PIN_SOLENOID, stat_solenoid);
  }
  
}
