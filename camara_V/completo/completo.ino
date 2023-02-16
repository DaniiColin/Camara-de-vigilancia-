#include <Servo.h>
#include <DS3231.h>
#include <DHT.h>
#include <Wire.h>

#define DHTTYPE DHT11
#define DHTPIN 2

DHT dht(DHTPIN, DHTTYPE);
DS3231 Clock;
Servo servoMotor;

float Hum ;
float Temp ;
char *horas[]={
    "8:00",
    "15:19",
    "20:00"  
  };
  
long nhoras = (sizeof(horas)/sizeof(char *));
bool h12;
bool PM;

byte year, month, date, DoW, hour, minute, second;


void setup() {
  
  Serial.begin(9600);
  Wire.begin();
  dht.begin();
}


void loop() {
    delay(5000);

    
    
    Clock.getTime(year, month, date, DoW, hour, minute, second);
    if(deboGirar()==1)
      girar();

     
  Temp = dht.readTemperature();
  Hum = dht.readHumidity();

  if(isnan(Hum) || isnan(Temp)){
    Serial.println("Error en el sensor");
  }
  
  Serial.println("\n ++++**************************************************++++");
  Serial.print(" H: ");
  Serial.print(Hum);
  Serial.print(" % ");
  Serial.print(" \t\t T: ");
  Serial.print(Temp);
  Serial.print(" °C ");
  Serial.println("\n ++++**************************************************++++");
  
}


void girar(){
    servoMotor.attach(8);
    int i;
  for (i=0;i<4;i++){
    servoMotor.write(0);
    delay(500);
    servoMotor.write(90);
    delay(500);
  }
  servoMotor.detach();
}

int deboGirar(){
  String h = "";
  String m = "";
  for(int i=0;i<nhoras;i++){
    h= getValue(horas[i], ':', 0);
    m= getValue(horas[i], ':', 1);
    hour = Clock.getHour(h12, PM);
    if(int(hour)==atoi(h.c_str()) && int(minute)==atoi(m.c_str()) && int(second)==0)
      return 1;
  }
  return 0;  
}
String getValue(String data, char separator, int index)
{
    int found = 0;
    int strIndex[] = { 0, -1 };
    int maxIndex = data.length() - 1;

    for (int i = 0; i <= maxIndex && found <= index; i++) {
        if (data.charAt(i) == separator || i == maxIndex) {
            found++;
            strIndex[0] = strIndex[1] + 1;
            strIndex[1] = (i == maxIndex) ? i+1 : i;
        }
    }
    return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}
