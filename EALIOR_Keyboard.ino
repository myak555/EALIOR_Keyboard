/*
  EALIOR (mark 4)
  This is a much updated version of GKOS keyboard of Seppo Tiainen, 28-Mar-2010, and
  GKOS keyboard of Pavel Travnik, 15-Sep-2019
  Copyright (c) 2020 Mike Yakimov.  All rights reserved.

  The name is derived from the first letters on the 6 chorded keys (if faced to the user):
  Left_Thumb  E  I  Right_Thumb   
              A  O
              L  R

  This is free software; you can redistribute it and/or
  modify it under the terms of the GNU Lesser General Public
  License as published by the Free Software Foundation; either
  version 3 of the License, or (at your option) any later version.

  This software is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
  Lesser General Public License for more details.

  You should have received a copy of the GNU Lesser General Public
  License along with this library; if not, write to the Free Software
  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

 Inspired by work of: 
    Seppo Tiainen (http://gkos.com/gkos/gkos-sixback.html)
    Pavel Travnik (https://hackaday.io/project/158377-mechanical-gkos-keyboard-for-phones-and-tablets)
    and the last but not least: Menny (https://github.com/AnySoftKeyboard/AnySoftKeyboard/commits?author=menny)
*/

////////////////////////////////////////////////////////
//
// This code implementation is for (Chinese clone) Sparkfun Micro Pro ATMmega32U4 5V
//
// Pin assignment:
// Keys:
// Left_Thumb  E  I  Right_Thumb   
// Left_LED    A  O  Right_LED
//             L  R
//    16       5  8       10 
//    15       6  9       14
//             7  10
//
////////////////////////////////////////////////////////


#include "EALIOR_Decoder.hpp"

// Uncomment for serial debugging
//#define _DEBUG

static EALIOR_Hardware hardware;
static EALIOR_Decoder decoder;

//
// Setup code here, to run once:
//
void setup()
{
  #ifdef _DEBUG
  Serial.begin(9600);
  #endif
  hardware.init();
  decoder.init( &hardware);
}

//
// Runs continuously
//
void loop()
{
  if (hardware.readButtons())
    decoder.processKey();
  #ifdef _DEBUG
  delay(100);
  #else
  hardware.checkSleepRequired();
  #endif
}
