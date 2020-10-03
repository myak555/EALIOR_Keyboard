/////////////////////////////////////////////////////////
//
//  EALIOR - 8-key chorded keyboard for tablets
//  Copyright (c) 2020 Mike Yakimov.  All rights reserved.
//  See main file for the license
//
//////////////////////////////////////////////////////////

#ifndef _EALIOR_DECODER_HPP
#define _EALIOR_DECODER_HPP

#include "characters.h"
#include "EALIOR_Hardware.hpp"

#define _ADDR_TAB_LENGTH       640

class EALIOR_Decoder{
  public:
    void init( EALIOR_Hardware *host);
    void processKey();
  private:
    EALIOR_Hardware *_host;
};

#endif // _EALIOR_DECODER_HPP
