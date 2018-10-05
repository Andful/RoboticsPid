// *********************************************************************************************************************** //
// Variables                                                                                                               //
// *********************************************************************************************************************** //

//pin definition
#define ENA 9
#define IN1 20
#define IN2 21
#define SENSOR_PIN A0


// ******** <TODO> **********************
// ******** define interval between recomputing error and adjusting feedback (in milliseconds) ********************** 
const int INTERVAL = 10; 
const float MAX_SPEED = 255.0;
const float MIN_SPEED = -255.0;

unsigned long previousTime = 0;

//int motorSpeed = 0; // speed of the motor, values between 0 and 255

int target = 512; // position (as read by potentiometer) to move the motor to, default value 512

// ******** <TODO> **********************
// ******** define the different gains **********************
float kp = 0.0; // proportional gain
float ki = 0.0; // integral gain
float kd = 0.0; // derivative gain

String commandString, valueString; // strings to read commands from the serial port

int pos = 0; // current position for plotting

float prev_err=0;
float integral=0;

// setup code, setting pin modes and initialising the serial connection
void setup() 
{
    Serial.begin(115200);

    pinMode(ENA, OUTPUT);
    pinMode(IN1, OUTPUT);
    pinMode(IN2, OUTPUT);
    
    pinMode(SENSOR_PIN, INPUT);   
    updatePosition();
}

unsigned long previousMillis = 0;
void loop() 
{
        //  ******** <TODO> **********************
        //  ******** implement your code  here **********************
        //  ******** HINT: you have to use the function readInput() somewhere
        //     if you wish to update PID parameters from with python script **********************

        // sending the current position to the serial connection so that it can be plotted

        unsigned long currentMillis = millis();
        
        if(currentMillis - previousMillis >= INTERVAL){
          //setMovement(-38); //38 minimum
          Serial.println(pos);
          if(abs(pos - target) > (1024 / 360 * 3)){            
            update();
          }
          readInput();
          previousMillis = currentMillis;
        }
}

void update(){
  float oldPos = pos;
  updatePosition();
  float error = target-pos;
  prev_err = error;
  
  float temp = oldPos - pos;
  
  float prop = error * kp;
  prop = abs(prop) < 38 ? 40 * sign(prop) : prop;
  integral = ki == 0 ? 0 : integral + error * ki * INTERVAL - kp * temp;
  integral = integral > MAX_SPEED ? MAX_SPEED : integral;
  integral = integral < MIN_SPEED ? MIN_SPEED : integral;
  
  float derivative = temp * kd / INTERVAL;
  
  float output = prop + integral - derivative;
  output = output > MAX_SPEED ? MAX_SPEED : output;
  output = output < MIN_SPEED ? MIN_SPEED : output;
  setMovement(output);
}

int sign(int value)
{
  if (value == 0) return 0;
  return value > 0 ? 1 : -1;
}

void updatePosition()
{
  pos = analogRead(SENSOR_PIN);
}

// method to set direction and speed of the motor
void setMovement(float speed1) 
{
  int dir = sign(speed1);
  
  if(dir == 1)
  {
    digitalWrite(IN2,LOW);
    digitalWrite(IN1,HIGH);
  } 
  else if(dir == -1)
  {
    digitalWrite(IN1,LOW);
    digitalWrite(IN2,HIGH);
  }
  else 
  {
    digitalWrite(IN1,LOW);
    digitalWrite(IN2,LOW);
  }
  speed1 = speed1 < 0 ? -speed1 : speed1;
  analogWrite(ENA,speed1);
}

// method for receiving commands over the serial port
void readInput() 
{
    if (Serial.available()) {
        commandString = Serial.readStringUntil('\n');
        if (commandString.startsWith("target")) {
            // change the target value that the motor should rotate to
            valueString = commandString.substring(7, commandString.length());
            target = (int) valueString.toInt();
            if(target>1024){
              target = 1024;
            } else if(target<0){
              target = 0;
            }
            integral = 0;
            prev_err = 0;
            //  ******** <TODO> **********************
            //  ******** reset the integral **********************
            
        } else if (commandString.startsWith("kp")) {
            // change the value of the proportional gain parameter
            valueString = commandString.substring(3, commandString.length());
            kp = valueString.toFloat();
            kp = kp < 0 ? 0 : kp;
        } else if (commandString.startsWith("ki")) {
            // change the value of the integral gain parameter
            valueString = commandString.substring(3, commandString.length());
            ki = valueString.toFloat();
            ki = ki < 0 ? 0 : ki;
        } else if (commandString.startsWith("kd")) {
            // change the value of the derivative gain parameter
            valueString = commandString.substring(3, commandString.length());
            kd = valueString.toFloat();
            kd = kd < 0 ? 0 : kd;
        }
    }
}
