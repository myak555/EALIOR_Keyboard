/////////////////////////////////////////////////////////
//
//  EALIOR - 8-key chorded keyboard for tablets
//  Copyright (c) 2020 Mike Yakimov.  All rights reserved.
//  See main file for the license
//
//////////////////////////////////////////////////////////

#include <Arduino.h>
#include "EALIOR_Decoder.hpp"

// Presumes standard keyboard driver for classic ЙЦУКЕН keyboard
#include "keymapRusStandard.h"

// Uncomment for serial debugging
//#define _DEBUG

void EALIOR_Decoder::init( EALIOR_Hardware *host){
  _host = host;
}

void EALIOR_Decoder::processKey(){
  uint16_t key = _host->getFullCode();
  #ifdef _DEBUG
  if( key>0){
    Serial.print( "Key = ");
    Serial.println( key);
  }
  #endif
  if( key >= _ADDR_TAB_LENGTH) return;
  key = key << 1;
  uint16_t addr = pgm_read_byte(&_EALIOR_Addresses[key++]) << 8;
  addr += pgm_read_byte(&_EALIOR_Addresses[key]);
  //key = _addrTable[key];
  #ifdef _DEBUG
  if( key>0){
    Serial.print( "Address = ");
    Serial.println( key);
  }
  #endif
  byte code = pgm_read_byte(&_EALIOR_Mantras[addr++]);
  while( code){
    switch( code){
      case _MODE0_:
      case _MODE1_:
      case _MODE2_:
      case _MODE3_:
      case _MODE4_:
      case _MODE5_:
      case _MODE6_:
      case _MODE7_:
      case _MODE8_:
      case _MODE9_:
        _host->setMode( code-1);
        break;
      case _RUSLAT_:
        //_host->kbdPress( _LEFT_SHIFT_); // Shifts are not needed with the AnySoftKeyboard
        _host->kbdPress( _LEFT_ALT_);
        _host->kbdHold();
        _host->kbdWrite( ' ');
        _host->kbdRelease( _LEFT_ALT_);
        //_host->kbdRelease( _LEFT_SHIFT_);
        _host->kbdHold();
        break;
      case _DISABLE_:
        _host->kbdDisable( true);
        break;
      case _ENABLE_:
        _host->kbdEnable();
        break;
      case _RELEASE_:
        _host->kbdHold();
        _host->kbdReleaseAll();
        _host->kbdHold();
        break;
      case _DELAY_:
        _host->kbdHold();
        break;
      case _LEFT_CTRL_ :
      case _LEFT_SHIFT_ :
      case _LEFT_ALT_ :
      case _LEFT_GUI_ :
        _host->kbdPress( code);
        _host->kbdHold();
        break;
      case _RIGHT_CTRL_ :  
      case _RIGHT_SHIFT_ : 
      case _RIGHT_ALT_ : 
      case _RIGHT_GUI_ : 
        _host->kbdHold();
        _host->kbdRelease( code-4);
        _host->kbdHold();
        break;
      default:
        #ifdef _DEBUG
        Serial.print( "Code = ");
        Serial.println( code);
        #endif
        _host->kbdWrite(code);
        break;
    }//switch
    code = pgm_read_byte(&_EALIOR_Mantras[addr++]);
  }//while
}
