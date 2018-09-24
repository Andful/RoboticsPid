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
const int INTERVAL = 0; 


unsigned long previousTime = 0;

int motorSpeed = 0; // speed of the motor, values between 0 and 255

int target = 512; // position (as read by potentiometer) to move the motor to, default value 512

// ******** <TODO> **********************
// ******** define the different gains **********************
float kp = 0.0; // proportional gain
float ki = 0.0; // integral gain
float kd = 0.0; // derivative gain

String commandString, valueString; // strings to read commands from the serial port

int pos = 0; // current position for plotting

// setup code, setting pin modes and initialising the serial connection
void setup() 
{
    Serial.begin(115200);

    pinMode(ENA, OUTPUT);
    pinMode(IN1, OUTPUT);
    pinMode(IN2, OUTPUT);
    
    pinMode(SENSOR_PIN, INPUT);   
}

void loop() 
{
        //  ******** <TODO> **********************
        //  ******** implement your code  here **********************
        //  ******** HINT: you have to use the function readInput() somewhere
        //     if you wish to update PID parameters from with python script **********************

        // sending the current position to the serial connection so that it can be plotted
        Serial.println(pos);
        updatePosition();
        setMovement(500);
}

int sign(int value)
{
  if (value == 0) return 0;
  return value > 0 ? 1 : -1;
}

void updatePosition()
{
  pos = analogRead(0);
}

// method to set direction and speed of the motor
void setMovement(int speed1) 
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
  analogWrite(ENA,abs(speed1));
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
            
            //  ******** <TODO> **********************
            //  ******** reset the integral **********************
            
        } else if (commandString.startsWith("kp")) {
            // change the value of the proportional gain parameter
            valueString = commandString.substring(3, commandString.length());
            kp = valueString.toFloat();
        } else if (commandString.startsWith("ki")) {
            // change the value of the integral gain parameter
            valueString = commandString.substring(3, commandString.length());
            ki = valueString.toFloat();
        } else if (commandString.startsWith("kd")) {
            // change the value of the derivative gain parameter
            valueString = commandString.substring(3, commandString.length());
            kd = valueString.toFloat();
        }
    }
}
