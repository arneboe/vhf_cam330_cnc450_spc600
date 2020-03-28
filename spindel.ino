
#define emergencyPin A5 //Connector Pin 5 //OK
#define NUM_SPEED_PINS 10
#define PWM_IN_PIN A0

//from LSB to MSB
int speedPins[NUM_SPEED_PINS] = {4, //PORT 1 BIT 0, Connector Pin 21 //OK
                                 8, //PORT 1 BIT 1, Connector Pin 8 //OK
                                 5, //PORT 1 BIT 2, Connector Pin 20 //OK
                                 7, //PORT 1 BIT 3, Connector Pin 7 //OK
                                 12, //PORT 1 BIT 4, Connector Pin 19 //OK
                                 6, //PORT 1 BIT 5, Connector Pin 6 //OK
                                 11, //PORT 1 BIT 6, Connector Pin 18 //OK
                                 10, //PORT 1 BIT 7, Connector Pin 17 //OK
                                 9, //PORT 2 BIT 0, Connector Pin 11 //OK
                                 3}; //PORT 2 BIT 1, Connector Pin 23 //OK


#define NUM_READINGS 20
int readings[NUM_READINGS] = {0};
int total = 0;
int readIndex = 0;


void setSpeed(int value)
{
  if(value > 1023)
  {
    value = 1023;
  }
  if(value < 0)
  {
    value = 0;
  }

  for(int i = 0; i < NUM_SPEED_PINS; ++i)
  {
    if(value & 1)
    {
      digitalWrite(speedPins[i], HIGH);
    }
    else
    {
      digitalWrite(speedPins[i], LOW);
    }
    value = value >> 1;
  }
}

int getSpeed()
{

  
  return pulseIn(PWM_IN_PIN, HIGH, 100000);
  
}


void setup() {

  Serial.begin(115200);
  pinMode(emergencyPin, OUTPUT);
  digitalWrite(emergencyPin, LOW);

  for (int i = 0; i < NUM_SPEED_PINS; ++i)
  {
    pinMode(speedPins[i], OUTPUT);
    digitalWrite(speedPins[i], LOW);
  }

  pinMode(PWM_IN_PIN, INPUT);
}




int convertPWM(int pwmValue)
{
  /*
1000 rpm = [2 ... 70] value: 53
2000 rpm = [71 ... 120] value: 101
3000 rpm = [121 ...160] value: 153
*/

if(pwmValue <= 2)
{
  return 0; //turn off
}
else if(pwmValue > 2 && pwmValue < 45)
{
  return 53; //1000 rpm
}
else if(pwmValue >= 45 && pwmValue < 95)
{
  return 101; //2000 rpm
}
else if(pwmValue >= 95 && pwmValue < 150)
{
  return 153; //3000 rpm
}
else if(pwmValue >= 150 && pwmValue < 200)
{
  return 207; //4000 rpm
}
else if(pwmValue >= 200 && pwmValue < 248)
{
  return 259; //5000 rpm
}
else if(pwmValue >= 248 && pwmValue < 288)
{
  return 308; //6000 rpm
}
else if(pwmValue >= 288 && pwmValue < 333)
{
  return 361; //7000 rpm
}
else if(pwmValue >= 333 && pwmValue < 370)
{
  return 411; //8000 rpm
}
else if(pwmValue >= 370 && pwmValue < 428)
{
  return 464; //9000 rpm
}
else if(pwmValue >= 428 && pwmValue < 480)
{
  return 513; //10000 rpm
}
else if(pwmValue >= 480 && pwmValue < 540)
{
  return 563; //11000 rpm
}
else if(pwmValue >= 540 && pwmValue < 590)
{
  return 616; //12000 rpm
}
else if(pwmValue >= 590 && pwmValue < 630)
{
  return 666; //13000 rpm
}
else if(pwmValue >= 630 && pwmValue < 685)
{
  return 710; //14000 rpm
}
else if(pwmValue >= 685 && pwmValue < 730)
{
  return 768; //15000 rpm
}
else if(pwmValue >= 730 && pwmValue < 770)
{
  return 818; //16000 rpm
}
else if(pwmValue >= 770 && pwmValue < 825)
{
  return 871; //17000 rpm
}
else if(pwmValue >= 825 && pwmValue < 870)
{
  return 918; //18000 rpm
}
else if(pwmValue >= 870 && pwmValue < 911)
{
  return 972; //19000 rpm
}
else if(pwmValue >= 911)
{
  return 1023; //20000 rpm
}
else
{
  return 0;
}

}


void loop() {
  total = total - readings[readIndex];
  readings[readIndex] = getSpeed();
  // add the reading to the total:
  total = total + readings[readIndex];
  // advance to the next position in the array:
  readIndex = readIndex + 1;
  if (readIndex >= NUM_READINGS) {
    // ...wrap around to the beginning:
    readIndex = 0;
  }

  const int avgPwm = total / NUM_READINGS;
  
  if(avgPwm < 2)
  {
    setSpeed(0);
    Serial.println("0");
  }
  else
  {
    int mappedValue = map(avgPwm, 3, 925, 1, 1023);
    if(mappedValue < 1)
      mappedValue = 1;
    if(mappedValue > 1023)
      mappedValue = 1023;

      
      
    //setSpeed(mappedValue);
    setSpeed(convertPWM(avgPwm));
    
    Serial.print("pwm: "); Serial.print(avgPwm);
    Serial.print(" map: ");
    Serial.println(mappedValue);
  }
}
