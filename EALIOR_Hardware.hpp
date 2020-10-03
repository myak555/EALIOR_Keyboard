/////////////////////////////////////////////////////////
//
//  EALIOR - 8-key chorded keyboard for tablets
//  Copyright (c) 2020 Mike Yakimov.  All rights reserved.
//  See main file for the license
//
//////////////////////////////////////////////////////////

#ifndef _EALIOR_HARDWARE_HPP
#define _EALIOR_HARDWARE_HPP

// if the user forgets to switch off the keyboard, go to sleep to prevent the battery drain
// 180 seconds is the default
#define SLEEP_DELAY (180000L)

// upon the keyboard connection, the system must recognize it
// tested on PC 1000 ms Ok
#define KBD_WAKEUP_TIMEOUT 1000

//
// Pin assignment
//
#define _EALIOR_KEY_0_      4
#define _EALIOR_KEY_1_      5
#define _EALIOR_KEY_2_      6
#define _EALIOR_KEY_3_      7
#define _EALIOR_KEY_4_      8
#define _EALIOR_KEY_5_      9
#define _THUMB_KEY_LEFT_   16
#define _THUMB_KEY_RIGHT_  10
#define _LED_LEFT_         15
#define _LED_RIGHT_        14

class EALIOR_Hardware{
  public:
    void init();
    bool readButtons();
    void setMode( uint8_t mode);
    inline uint16_t getFullCode(){
        return 10*_gChord + shiftMode;};

    void kbdPress(char key);
    void kbdWrite(char key);
    void kbdPrint(String s);
    void kbdRelease(char key);
    
    void checkSleepRequired();

  private:
    int8_t _EALIORPins[8] = {_EALIOR_KEY_0_, _EALIOR_KEY_1_, _EALIOR_KEY_2_,
                             _EALIOR_KEY_3_, _EALIOR_KEY_4_, _EALIOR_KEY_5_,
                             _THUMB_KEY_LEFT_, _THUMB_KEY_RIGHT_};
    long _lastCommandReceived = 0L;   // Controls keyboard sleep
    bool _leftPressed = false;        // previous value of the left (front) mode button
    bool _rightPressed = false;       // previous value of the right (front) mode button
    long _time = 0;                   // button press time
    long _previousTime = 0;
    long _autoRepeat = 0;             // Repeat the character if chord pressed long enough (0 or 1)
    int  _presentChord = 0;           // The chord of the keypad at present
    int  _previousChord = 0;          // To compare chord change
    int  _autoCounter = 0;            // Typematic delay counter (n x 10 ms)
    //int   EALIOR_firstChord = 0;    // First chord of a Chordon, if any
    //int   EALIOR_firstCounter = 0;  // Count to detect a separate first chord in a Chordon
    bool  _gNew = false;              // a new character is expected soon because new keys were pressed
    bool _kbdActive = false;                       // prevents keyboard going bananas
    bool _kbdSleeping = false;                     // prevents keyboard going bananas
    uint16_t  _gChord = 0;                         // EALIOR final chord value (0...63) for the character
    uint8_t  shiftMode = _SHIFTMODE_LAT_NORMAL;    // keyboard mode

    void _readModeButtons();
    void _readModeRight( bool);
    void _readModeLeft( bool);
    void _blinkLEDs();
    void _setLEDs();
    inline void _writeLEDs( bool left, bool right){
        digitalWrite(_LED_LEFT_, left);
        digitalWrite(_LED_RIGHT_, right);};
    inline int8_t _readPin( int i){
        return (digitalRead( _EALIORPins[i]) == LOW)? 1: 0;};
    inline int8_t _readPinBool( int i){
        return digitalRead( _EALIORPins[i]) == LOW;};
    void _keyboardDisable();
    void _keyboardEnable();
};

#endif // _EALIOR_HARDWARE_HPP
