/////////////////////////////////////////////////////////
//
//  EALIOR - 8-key chorded keyboard for tablets
//  Copyright (c) 2020 Mike Yakimov.  All rights reserved.
//  See main file for the license
//
//////////////////////////////////////////////////////////

#include <Arduino.h>
#include <Keyboard.h>
#include <LowPower.h>
#include "characters.h"
#include "EALIOR_Hardware.hpp"

// Uncomment to disable features while debugging
//#define _DISABLE_KEYBOARD
//#define _DISABLE_POWERSAVE
//#define _DEBUG

void EALIOR_Hardware::init(){
  pinMode(_LED_LEFT_, OUTPUT);
  pinMode(_LED_RIGHT_, OUTPUT);
  _writeLEDs( true, true);
  _kbdActive = false;
  for ( int i = 0; i < 8; i++){
    pinMode(_EALIORPins[i], INPUT_PULLUP);
    _kbdActive = _kbdActive || _readPinBool(i);
  }
  _kbdActive = !_kbdActive; // if any key is stuck, no runover
  if ( !_kbdActive) return;
  #ifndef _DISABLE_KEYBOARD
  Keyboard.begin();
  #endif
  _blinkLEDs();
  _setLEDs();
  _lastCommandReceived = millis();
}

//
// Reads the rear 6 buttons, processes them into the press codes
//
bool EALIOR_Hardware::readButtons(){
  if( !_kbdActive) return false;
  _readModeButtons();
  uint8_t button_weight = 1;
  int pin = 0;

  // Return empty immediately if 10 ms not elapsed
  _time = millis();
  if ((_time - _previousTime) < (10 + 64 * _autoRepeat)) return false;

  // Read buttons and form a code 
  _presentChord = 0;
  for( int i=0; i<6; i++){
    pin = _readPin( i);
    _presentChord += pin * button_weight;
    button_weight += button_weight; 
  }
  if(_presentChord) _lastCommandReceived = millis();
  #ifdef _DEBUG
  if(_presentChord)
    Serial.println( _presentChord, DEC);
  #endif

  // any buttons pressed
  if (_presentChord != 0){
    // Chord pressed long enough for autorepeat
    _autoCounter++;
    if (_autoCounter >= 100){
      _autoCounter = 99;
      _autoRepeat = 1;
    }

    // Chord pressed long enough to be first chord in Chordon
    //_firstCounter++;
    //if (_firstCounter > 25){
    //  _firstCounter = 25;
    //  if (_firstChord == 0) _firstChord = _presentChord;
    //}
  }

  // New key(s) pressed, expect a new character soon
  if (_presentChord > _previousChord){
    _gNew = true;
    _autoCounter = 0;
    _autoRepeat = 0;
    //_firstCounter = 0;
  }

  // key(s) relased
  if (_presentChord < _previousChord){
    _autoCounter = 0;
    _autoRepeat = 0;
    //EALIOR_firstCounter = 0;
    _gChord = _previousChord;  // the chord before the first release of key(s) is what we are after
    _previousChord = _presentChord;  
    _previousTime = _time;
    if (!_gNew) return false;
    _gNew = false; // next key releases will no more represent chords for characters
    return true; // a real chord entered!
  }

  // no buttons pressed
  //if (_presentChord == 0)
  //{
  //  _firstChord = 0; 
  //  _firstCounter = 0;
  //}
  _previousChord = _presentChord; // to be able to compare next time
  _previousTime = _time;

  if (!_autoRepeat) return false;
  _gChord = _previousChord;
  //_firstCounter = 0;
  //_firstChord = 0;
  return true;
}

void EALIOR_Hardware::setMode( uint8_t mode){
  if( shiftMode == mode) return;
  shiftMode = mode;
  _setLEDs();
}

void EALIOR_Hardware::_setLEDs(){
  uint8_t tmp = shiftMode % 5;
  const bool leftLED[5] = {false, true, true, false, true};
  const bool rightLED[5] = {false, false, false, true, true};
  _writeLEDs( leftLED[tmp], rightLED[tmp]);
}

void EALIOR_Hardware::kbdPress(char key){
  #ifndef _DISABLE_KEYBOARD
  _keyboardEnable();
  Keyboard.press( key);
  #endif
}

void EALIOR_Hardware::kbdWrite(char key){
  #ifndef _DISABLE_KEYBOARD
  _keyboardEnable();
  Keyboard.write( key);
  #endif
}

void EALIOR_Hardware::kbdPrint(String s){
  #ifndef _DISABLE_KEYBOARD
  _keyboardEnable();
  Keyboard.print( s);
  #endif
}

void EALIOR_Hardware::kbdRelease(char key){
  #ifndef _DISABLE_KEYBOARD
  _keyboardEnable();
  Keyboard.release( key);
  #endif
}

//
// This is to prevent battery drain if the user forgets the power
// At this moment cannot resolve the issue of keyboard quitting
// With USB on, drain 22 mA, with USB_OFF - 17 mA
// Maximum drainage (5V input):
//    Normal running - 28 mA
//    Shift ON - 30 mA
//    Both LEDs ON - 33 mA
//    Sleep forever - 3 mA (probably due to the POWER LED on-board; will cut it off)
//
void EALIOR_Hardware::checkSleepRequired(){
  // Eliminate unwanted Tx, Rx lights
  RXLED0;
  TXLED0;

  // Check activity
  long t = millis();
  if( t<_lastCommandReceived) _lastCommandReceived = t; // wrap-around for the counter
  if( t-_lastCommandReceived < SLEEP_DELAY){
    delay(15);
    return; // user actively typing...
  }
  
  // Go sleep for 500MS
  if( !_kbdSleeping){
    _blinkLEDs();
    _blinkLEDs();
  }
  _writeLEDs(false, false);
  
  #ifndef _DISABLE_POWERSAVE
  _keyboardDisable();
  LowPower.powerDown(SLEEP_500MS, ADC_OFF, BOD_OFF);
  #else
  delay(200);
  _lastCommandReceived = millis();
  #endif
}

void EALIOR_Hardware::_blinkLEDs( ){
  _writeLEDs( false, false);
  delay( 100);
  _writeLEDs( true, true);
  delay( 100);
}

//
// Reads the top mode buttons
//
void EALIOR_Hardware::_readModeButtons(){
  _readModeRight(_readPinBool( 7));
  _readModeLeft(_readPinBool( 6));
  _setLEDs();
}


void EALIOR_Hardware::_readModeRight(bool modebutton){
  uint8_t modes[] =
      {_SHIFTMODE_LAT_NUMS, _SHIFTMODE_LAT_NUMS, _SHIFTMODE_LAT_NUMS, _SHIFTMODE_LAT_NUMLOCK, _SHIFTMODE_LAT_NORMAL,
       _SHIFTMODE_RUS_NUMS, _SHIFTMODE_RUS_NUMS, _SHIFTMODE_RUS_NUMS, _SHIFTMODE_RUS_NUMLOCK, _SHIFTMODE_RUS_NORMAL};
  if(modebutton){
    _lastCommandReceived = millis();
    _keyboardEnable();
  }
  if( modebutton && !_rightPressed){
    _rightPressed = true;
    shiftMode = modes[shiftMode];
    #ifdef _DEBUG
    Serial.print( "Mode set to ");
    Serial.print( shiftMode);
    #endif
  }  
  if( !modebutton && _rightPressed) _rightPressed = false;
}

void EALIOR_Hardware::_readModeLeft( bool modebutton){
  uint8_t modes[] =
      {_SHIFTMODE_LAT_SHIFTED, _SHIFTMODE_LAT_CAPS, _SHIFTMODE_LAT_NORMAL, _SHIFTMODE_LAT_NORMAL, _SHIFTMODE_LAT_NORMAL,
       _SHIFTMODE_RUS_SHIFTED, _SHIFTMODE_RUS_CAPS, _SHIFTMODE_RUS_NORMAL, _SHIFTMODE_RUS_NORMAL, _SHIFTMODE_RUS_NORMAL};
  if(modebutton){
    _lastCommandReceived = millis();
    _keyboardEnable();
  }
  if( modebutton && !_leftPressed){
    _leftPressed = true;
    shiftMode = modes[shiftMode];
    #ifdef _DEBUG
    Serial.print( "Mode set to ");
    Serial.print( shiftMode);
    #endif
  }  
  if( !modebutton && _leftPressed) _leftPressed = false;
}

void EALIOR_Hardware::_keyboardDisable(){
  if( _kbdSleeping) return;
  _kbdSleeping = true;

  // Apparently USBDevice.detach() does nothing; need to do manually 
  // Disable USB clock by registers 
  USBCON |= _BV(FRZCLK);
  // Disable USB PLL
  PLLCSR &= ~_BV(PLLE); 
  // Disable USB
  USBCON &= ~_BV(USBE); 
}

void EALIOR_Hardware::_keyboardEnable(){
  if( !_kbdSleeping) return;
  _kbdSleeping = false;
  USBDevice.attach();
  delay(KBD_WAKEUP_TIMEOUT); // How much delay is needed?
}
