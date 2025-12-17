/*
 * WinAudioControl - Arduino Firmware
 * Provides example on how to control 4 rotary encoders to send 
 * volume and button events to Windows via Serial.
 */

// Pin Configuration
const int CLK_PINS[] = {2, 4, 6, 8};     // Clock Pins
const int DT_PINS[]  = {3, 5, 7, 9};     // Data Pins
const int SW_PINS[]  = {A0, A1, A2, A3}; // Button/Switch Pins
const int NUM_ENCODERS = 4;

// State Variables
int lastClk[NUM_ENCODERS];
int lastButtonState[NUM_ENCODERS];

void setup() {
  // Initialize Serial Communication (must match Python baud rate)
  Serial.begin(9600);

  // Initialize all pins
  for (int i = 0; i < NUM_ENCODERS; i++) {
    pinMode(CLK_PINS[i], INPUT);
    pinMode(DT_PINS[i], INPUT);
    pinMode(SW_PINS[i], INPUT_PULLUP); // Uses internal pull-up resistor for buttons
    
    // Read initial states
    lastClk[i] = digitalRead(CLK_PINS[i]);
    lastButtonState[i] = digitalRead(SW_PINS[i]);
  }
}

void loop() {
  for (int i = 0; i < NUM_ENCODERS; i++) {
    // 1. CHECK ROTATION
    int currentClk = digitalRead(CLK_PINS[i]);
    
    // Check for falling edge on CLK pin
    if (currentClk != lastClk[i] && currentClk == LOW) {
      // Rotation logic: 
      // Checking if DT matches current CLK to determine direction
      if (digitalRead(DT_PINS[i]) == currentClk) {
        Serial.print("VOL_UP_");
      } else {
        Serial.print("VOL_DOWN_");
      }
      Serial.println(i + 1); // Send ID (1, 2, 3, or 4)
    }
    lastClk[i] = currentClk;

    // 2. CHECK BUTTON (Mute/Toggle function)
    int currentButton = digitalRead(SW_PINS[i]);
    
    // Detect button press (Transition from HIGH to LOW)
    if (lastButtonState[i] == HIGH && currentButton == LOW) {
      Serial.print("BUTTON_");
      Serial.println(i + 1);
      delay(50); // Software debounce to prevent double triggers
    }
    lastButtonState[i] = currentButton;
  }
}