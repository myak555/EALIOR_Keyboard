import struct

def printEncoded( f, s):
    f.write( s.encode(encoding="utf-8"))
    return


def printKey( f, x, y, color):
    if color:
        printEncoded( f, "shape ( {:d}, {:d}, 35, 35,rectangle,3,000000,50505F)\n".format(40+x, 120+y))
    else:
        printEncoded( f, "shape ( {:d}, {:d}, 35, 35,rectangle,3,000000,FFFFFF)\n".format(40+x, 120+y))
    return


class ArduinoKeyConverter():
    def __init__(self):
        self.conversion = [
            ("_NUL_",           0x00),
            ("_MODE0_",         0x01),
            ("_MODE1_",         0x02),
            ("_MODE2_",         0x03),
            ("_MODE3_",         0x04),
            ("_MODE4_",         0x05),
            ("_MODE5_",         0x06),
            ("_MODE6_",         0x07),
            ("_MODE7_",         0x08),
            ("_MODE8_",         0x09),
            ("_MODE9_",         0x10),
            ("_RUSLAT_",        0x11),
            ("_LEFT_CTRL_",     0x80),
            ("_LEFT_SHIFT_",    0x81),
            ("_LEFT_ALT_", 	    0x82),
            ("_LEFT_GUI_", 	    0x83),
            ("_RIGHT_CTRL_", 	0x84),
            ("_RIGHT_SHIFT_", 	0x85),
            ("_RIGHT_ALT_", 	0x86),
            ("_RIGHT_GUI_", 	0x87),
            ("_UP_ARROW_", 	    0xDA),
            ("_DOWN_ARROW_", 	0xD9),
            ("_LEFT_ARROW_", 	0xD8),
            ("_RIGHT_ARROW_", 	0xD7),
            ("_BACKSPACE_", 	0xB2),
            ("_TAB_", 	        0xB3),
            ("_RETURN_", 	    0xB0),
            ("_ESC_", 	        0xB1),
            ("_INSERT_", 	    0xD1),
            ("_DELETE_", 	    0xD4),
            ("_PAGE_UP_", 	    0xD3),
            ("_PAGE_DOWN_", 	0xD6),
            ("_HOME_", 	        0xD2),
            ("_END_", 	        0xD5),
            ("_CAPS_LOCK_", 	0xC1),
            ("_F1_", 	        0xC2),
            ("_F2_", 	        0xC3),
            ("_F3_", 	        0xC4),
            ("_F4_", 	        0xC5),
            ("_F5_", 	        0xC7),
            ("_F7_", 	        0xC8),
            ("_F8_", 	        0xC9),
            ("_F9_", 	        0xCA),
            ("_F10_", 	        0xCB),
            ("_F11_", 	        0xCC),
            ("_F12_", 	        0xCD)]
        return
    def StartsWithMeta( self, s):
        self.meta = None
        for i, t in enumerate(self.conversion):
            if not s.startswith( t[0]): continue
            self.meta = t
            return True
        return False
    def ConvertString( self, s):
        tmp = []
        while(len(s)):
            if self.StartsWithMeta(s):
                tmp += [self.meta[1]]
                s = s[len(self.meta[0]):]
                continue
            tmp += [(bytearray( s[:1], encoding="UTF-8"))[0]]
            s = s[1:]
        tmp += [0]
        return tmp
    def __str__(self):
        s = ""
        for t in self.conversion:
            s += "#define {:s}\t\t\t0x{:02x}\n".format(t[0], t[1])
        return s

class EALIOR_Key():
    def __init__( self, code, mode, nominal, keysequence):
        self.Code = code # 0-59
        self.Mode = mode # 0-9
        self.Index = code*10 + mode
        self.Nominal = nominal
        self.Border = 0
        self.Address = 0
        self.Keysequence = keysequence
        return
    def __str__(self):
        s = ""
        for b in self.Keysequence:
            s += "0x{:02x},".format(b)
        return s[:-1]
    def makeDefinitionFile(self, f, mode):
        if mode != self.Mode: return
        n = self.Code
        nx = self.Code % 8
        ny = self.Code // 8
        printKey( f, nx*140, ny*200, n % 2)
        printKey( f, nx*140, ny*200+40, (n//2) % 2)
        printKey( f, nx*140, ny*200+80, (n//4) % 2)
        printKey( f, nx*140+40, ny*200, (n//8) % 2)
        printKey( f, nx*140+40, ny*200+40, (n//16) % 2)
        printKey( f, nx*140+40, ny*200+80, (n//32) % 2)
        if len( self.Nominal) < 1:
            printEncoded( f, "\n")
            return
        if len( self.Nominal) < 4:
            printEncoded( f, "label ( {:d},{:d},{:d},35,nana,20,000000,FFFFFF)\n".format(nx*140+40, ny*200+240, len(self.Nominal)*18+20))
        else:
            printEncoded( f, "label ( {:d},{:d},{:d},30,nana,14,000000,FFFFFF)\n".format(nx*140+40, ny*200+240+2, len(self.Nominal)*14+20))
        print( self.Mode, self.Code)
        printEncoded( f, "\tlSize = {:d}\n".format(self.Border))
        printEncoded( f, "\ttext ={:s}\n".format(self.Nominal))
        printEncoded( f, "\n")
        return

class EALIOR_Keyboard():
    def __init__( self):
        self.Converter = ArduinoKeyConverter()
        self.Keys = []
        self.ByteSequence = []
        self.AddressSequence = bytearray( 1280)
        return

    def __str__(self):
        lc = 0
        s = "const byte _EALIOR_Mantras[] PROGMEM = {\n\t"
        for i, b in enumerate(self.ByteSequence):
            s += "0x{:02x},".format(b)
            lc += 1
            if lc >= 20:
                s += "\n\t"
                lc = 0
        if lc == 0: s = s[:-2]
        s = s[:-1] + "};\n\n"
        lc = 0
        s += "const byte _EALIOR_Addresses[] PROGMEM = {\n\t"
        for i, b in enumerate(self.AddressSequence):
            s += "0x{:02x},".format(b)
            lc += 1
            if lc >= 20:
                s += "\n\t"
                lc = 0
        if lc == 0: s = s[:-2]
        s = s[:-1] + "};\n"
        return s

    def appendKey( self, code, mode, nominal, keysequence, border=0):
        k = EALIOR_Key( code, mode, nominal,
            self.Converter.ConvertString(keysequence))
        k.Border = border
        index = bytes(self.ByteSequence).find(bytes(k.Keysequence))
        if index >= 0:
            k.Address = index
        else:
            k.Address = len( self.ByteSequence)
            self.ByteSequence += k.Keysequence
        self.Keys += [k]
        struct.pack_into(">H", self.AddressSequence, k.Index*2, k.Address)
        return

    def makeDefinitionFile(self, f, name, mode):
        printEncoded( f, "################################################\n")
        printEncoded( f, "#                                              #\n")
        printEncoded( f, "#  Chorded keyboard layout: {:15s}    #\n".format(name))
        printEncoded( f, "#                                              #\n")
        printEncoded( f, "################################################\n")
        printEncoded( f, "#\n")
        printEncoded( f, "slide ({:s},1240,1753,png+pdf,FFFFFFFF,21.01,29.69,150)\n".format(name.strip().replace(" ", "_")))
        printEncoded( f, "label (170,40,900,80,none,24)\n")
        printEncoded( f, "\tText={:s}\n".format(name))
        printEncoded( f, "\tfStyle=bold\n")
        printEncoded( f, "\tlSize=0\n")
        printEncoded( f, "\ttPosition=center\n")
        printEncoded( f, "\n")
        for k in self.Keys:
            k.makeDefinitionFile( f, mode)
        return

ek = EALIOR_Keyboard()

# Mode 0 - Latin Normal
mode = 0
ek.appendKey(  0, mode, "none", "", 2)
ek.appendKey(  1, mode, "e", "e")
ek.appendKey(  2, mode, "a", "a")
ek.appendKey(  3, mode, "t", "t")
ek.appendKey(  4, mode, "l", "l")
ek.appendKey(  5, mode, "p", "p")
ek.appendKey(  6, mode, "s", "s")
ek.appendKey(  7, mode, "backspace", "_BACKSPACE_", 2)

ek.appendKey(  8, mode, "i", "i")
ek.appendKey(  9, mode, "  ↑ ", "_UP_ARROW_", 2)
ek.appendKey( 10, mode, "j", "j")
ek.appendKey( 11, mode, "v", "v")
ek.appendKey( 12, mode, "u", "u")
ek.appendKey( 13, mode, "sh", "sh")
ek.appendKey( 14, mode, "b", "b")
ek.appendKey( 15, mode, "  → ", "_RIGHT_ARROW_", 2)

ek.appendKey( 16, mode, "o", "o")
ek.appendKey( 17, mode, "m", "m")
ek.appendKey( 18, mode, "return", "_RETURN_", 2)
ek.appendKey( 19, mode, "w", "w")
ek.appendKey( 20, mode, ",", ", ")
ek.appendKey( 21, mode, "ch", "ch")
ek.appendKey( 22, mode, "c", "c")
ek.appendKey( 23, mode, "sel→", "_LEFT_SHIFT__RIGHT_ARROW__RIGHT_SHIFT_", 2)

ek.appendKey( 24, mode, "n", "n")
ek.appendKey( 25, mode, "g", "g")
ek.appendKey( 26, mode, "q", "q")
ek.appendKey( 27, mode, "pgup", "_PAGE_UP_", 2)
ek.appendKey( 28, mode, "and", "and")
ek.appendKey( 29, mode, "or", "or")
ek.appendKey( 30, mode, "?", "_MODE1_? ")
ek.appendKey( 31, mode, "word→", "_LEFT_CTRL__RIGHT_ARROW__RIGHT_CTRL_", 2)

ek.appendKey( 32, mode, "r", "r")
ek.appendKey( 33, mode, "d", "d")
ek.appendKey( 34, mode, ".", "_MODE1_. ")
ek.appendKey( 35, mode, "z", "z")
ek.appendKey( 36, mode, "  ↓ ", "_DOWN_ARROW_", 2)
ek.appendKey( 37, mode, "-", "-")
ek.appendKey( 38, mode, "k", "k")
ek.appendKey( 39, mode, "end ", "_END_", 2)

ek.appendKey( 40, mode, "y", "y")
ek.appendKey( 41, mode, "you", "you")
ek.appendKey( 42, mode, "th", "th")
ek.appendKey( 43, mode, "sel↑", "_LEFT_SHIFT__UP_ARROW__RIGHT_SHIFT_", 2)
ek.appendKey( 44, mode, "the", "the")
ek.appendKey( 45, mode, " del", "_DELETE_", 2)
ek.appendKey( 46, mode, "sel↓", "_LEFT_SHIFT__DOWN_ARROW__RIGHT_SHIFT_", 2)
ek.appendKey( 47, mode, "copy", "_LEFT_CTRL_c_RIGHT_CTRL_", 2)

ek.appendKey( 48, mode, "h", "h")
ek.appendKey( 49, mode, "f", "f")
ek.appendKey( 50, mode, "x", "x")
ek.appendKey( 51, mode, "!", "_MODE1_! ")
ek.appendKey( 52, mode, '""', '""_LEFT_ARROW_')
ek.appendKey( 53, mode, "#", "#")
ek.appendKey( 54, mode, "pgdn", "_PAGE_DOWN_", 2)
ek.appendKey( 55, mode, "selw→", "_LEFT_CTRL__LEFT_SHIFT__RIGHT_ARROW__RIGHT_SHIFT__RIGHT_CTRL_", 2)

ek.appendKey( 56, mode, "space", " ", 2)
ek.appendKey( 57, mode, " ←  ", "_LEFT_ARROW_", 2)
ek.appendKey( 58, mode, "sel.←", "_LEFT_SHIFT__LEFT_ARROW__RIGHT_SHIFT_", 2)
ek.appendKey( 59, mode, "word←", "_LEFT_CTRL__LEFT_ARROW__RIGHT_CTRL_", 2)
ek.appendKey( 60, mode, "home", "_HOME_", 2)
ek.appendKey( 61, mode, "paste", "_LEFT_CTRL_v_RIGHT_CTRL_", 2)
ek.appendKey( 62, mode, "selw←", "_LEFT_CTRL__LEFT_SHIFT__LEFT_ARROW__RIGHT_SHIFT__RIGHT_CTRL_", 2)
ek.appendKey( 63, mode, "→RUS", "_RUSLAT__MODE5_", 2)

# Mode 1 - Latin Shifted
mode = 1
ek.appendKey(  0, mode, "none", "", 2)
ek.appendKey(  1, mode, "E", "_MODE0_E")
ek.appendKey(  2, mode, "A", "_MODE0_A")
ek.appendKey(  3, mode, "T", "_MODE0_T")
ek.appendKey(  4, mode, "L", "_MODE0_L")
ek.appendKey(  5, mode, "P", "_MODE0_P")
ek.appendKey(  6, mode, "S", "_MODE0_S")
ek.appendKey(  7, mode, "backspace", "_BACKSPACE_", 2)

ek.appendKey(  8, mode, "I", "_MODE0_I")
ek.appendKey(  9, mode, "  ↑ ", "_UP_ARROW_", 2)
ek.appendKey( 10, mode, "J", "_MODE0_J")
ek.appendKey( 11, mode, "V", "_MODE0_V")
ek.appendKey( 12, mode, "U", "_MODE0_U")
ek.appendKey( 13, mode, "Sh", "_MODE0_Sh")
ek.appendKey( 14, mode, "B", "_MODE0_B")
ek.appendKey( 15, mode, "  → ", "_RIGHT_ARROW_", 2)

ek.appendKey( 16, mode, "O", "_MODE0_O")
ek.appendKey( 17, mode, "M", "_MODE0_M")
ek.appendKey( 18, mode, "return", "_RETURN_", 2)
ek.appendKey( 19, mode, "W", "_MODE0_W")
ek.appendKey( 20, mode, ";", "_MODE0_; ")
ek.appendKey( 21, mode, "Ch", "_MODE0_Ch")
ek.appendKey( 22, mode, "C", "_MODE0_C")
ek.appendKey( 23, mode, "sel→", "_LEFT_SHIFT__RIGHT_ARROW__RIGHT_SHIFT_", 2)

ek.appendKey( 24, mode, "N", "_MODE0_N")
ek.appendKey( 25, mode, "G", "_MODE0_G")
ek.appendKey( 26, mode, "Q", "_MODE0_Q")
ek.appendKey( 27, mode, "pgup", "_PAGE_UP_", 2)
ek.appendKey( 28, mode, "And", "_MODE0_And")
ek.appendKey( 29, mode, "Or", "_MODE0_Or")
ek.appendKey( 30, mode, "?", "? ")
ek.appendKey( 31, mode, "word→", "_LEFT_CTRL__RIGHT_ARROW__RIGHT_CTRL_", 2)

ek.appendKey( 32, mode, "R", "_MODE0_R")
ek.appendKey( 33, mode, "D", "_MODE0_D")
ek.appendKey( 34, mode, ":", ": ")
ek.appendKey( 35, mode, "Z", "_MODE0_Z")
ek.appendKey( 36, mode, "  ↓ ", "_DOWN_ARROW_", 2)
ek.appendKey( 37, mode, "_", "_")
ek.appendKey( 38, mode, "K", "_MODE0_K")
ek.appendKey( 39, mode, "end ", "_END_", 2)

ek.appendKey( 40, mode, "Y", "_MODE0_Y")
ek.appendKey( 41, mode, "You", "_MODE0_You")
ek.appendKey( 42, mode, "Th", "_MODE0_Th")
ek.appendKey( 43, mode, "sel↑", "_LEFT_SHIFT__UP_ARROW__RIGHT_SHIFT_", 2)
ek.appendKey( 44, mode, "The", "_MODE0_The")
ek.appendKey( 45, mode, " del", "_DELETE_", 2)
ek.appendKey( 46, mode, "sel↓", "_LEFT_SHIFT__DOWN_ARROW__RIGHT_SHIFT_", 2)
ek.appendKey( 47, mode, "copy", "_LEFT_CTRL_c_RIGHT_CTRL_", 2)

ek.appendKey( 48, mode, "H", "_MODE0_H")
ek.appendKey( 49, mode, "F", "_MODE0_F")
ek.appendKey( 50, mode, "X", "_MODE0_X")
ek.appendKey( 51, mode, "!", "! ")
ek.appendKey( 52, mode, "'", "_MODE0_'")
ek.appendKey( 53, mode, "#", "#")
ek.appendKey( 54, mode, "pgdn", "_PAGE_DOWN_", 2)
ek.appendKey( 55, mode, "selw→", "_LEFT_CTRL__LEFT_SHIFT__RIGHT_ARROW__RIGHT_SHIFT__RIGHT_CTRL_", 2)

ek.appendKey( 56, mode, "space", " ", 2)
ek.appendKey( 57, mode, " ←  ", "_LEFT_ARROW_", 2)
ek.appendKey( 58, mode, "sel.←", "_LEFT_SHIFT__LEFT_ARROW__RIGHT_SHIFT_", 2)
ek.appendKey( 59, mode, "word←", "_LEFT_CTRL__LEFT_ARROW__RIGHT_CTRL_", 2)
ek.appendKey( 60, mode, "home", "_HOME_", 2)
ek.appendKey( 61, mode, "paste", "_LEFT_CTRL_v_RIGHT_CTRL_", 2)
ek.appendKey( 62, mode, "selw←", "_LEFT_CTRL__LEFT_SHIFT__LEFT_ARROW__RIGHT_SHIFT__RIGHT_CTRL_", 2)
ek.appendKey( 63, mode, "→RUS", "_RUSLAT__MODE6_", 2)

# Mode 2 - Latin CAPS
mode = 2
ek.appendKey(  0, mode, "none", "", 2)
ek.appendKey(  1, mode, "E", "E")
ek.appendKey(  2, mode, "A", "A")
ek.appendKey(  3, mode, "T", "T")
ek.appendKey(  4, mode, "L", "L")
ek.appendKey(  5, mode, "P", "P")
ek.appendKey(  6, mode, "S", "S")
ek.appendKey(  7, mode, "backspace", "_BACKSPACE_", 2)

ek.appendKey(  8, mode, "I", "I")
ek.appendKey(  9, mode, "  ↑ ", "_UP_ARROW_", 2)
ek.appendKey( 10, mode, "J", "J")
ek.appendKey( 11, mode, "V", "V")
ek.appendKey( 12, mode, "U", "U")
ek.appendKey( 13, mode, "SH", "SH")
ek.appendKey( 14, mode, "B", "B")
ek.appendKey( 15, mode, "  → ", "_RIGHT_ARROW_", 2)

ek.appendKey( 16, mode, "O", "O")
ek.appendKey( 17, mode, "M", "M")
ek.appendKey( 18, mode, "return", "_RETURN_", 2)
ek.appendKey( 19, mode, "W", "W")
ek.appendKey( 20, mode, ",", ", ")
ek.appendKey( 21, mode, "CH", "CH")
ek.appendKey( 22, mode, "C", "C")
ek.appendKey( 23, mode, "sel→", "_LEFT_SHIFT__RIGHT_ARROW__RIGHT_SHIFT_", 2)

ek.appendKey( 24, mode, "N", "N")
ek.appendKey( 25, mode, "G", "G")
ek.appendKey( 26, mode, "Q", "Q")
ek.appendKey( 27, mode, "pgup", "_PAGE_UP_", 2)
ek.appendKey( 28, mode, "AND", "AND")
ek.appendKey( 29, mode, "OR", "OR")
ek.appendKey( 30, mode, "?", "? ")
ek.appendKey( 31, mode, "word→", "_LEFT_CTRL__RIGHT_ARROW__RIGHT_CTRL_", 2)

ek.appendKey( 32, mode, "R", "R")
ek.appendKey( 33, mode, "D", "D")
ek.appendKey( 34, mode, ".", ". ")
ek.appendKey( 35, mode, "Z", "Z")
ek.appendKey( 36, mode, "  ↓ ", "_DOWN_ARROW_", 2)
ek.appendKey( 37, mode, "-", "-")
ek.appendKey( 38, mode, "K", "K")
ek.appendKey( 39, mode, "end ", "_END_", 2)

ek.appendKey( 40, mode, "Y", "Y")
ek.appendKey( 41, mode, "YOU", "YOU")
ek.appendKey( 42, mode, "TH", "TH")
ek.appendKey( 43, mode, "sel↑", "_LEFT_SHIFT__UP_ARROW__RIGHT_SHIFT_", 2)
ek.appendKey( 44, mode, "THE", "THE")
ek.appendKey( 45, mode, " del", "_DELETE_", 2)
ek.appendKey( 46, mode, "sel↓", "_LEFT_SHIFT__DOWN_ARROW__RIGHT_SHIFT_", 2)
ek.appendKey( 47, mode, "copy", "_LEFT_CTRL_c_RIGHT_CTRL_", 2)

ek.appendKey( 48, mode, "H", "H")
ek.appendKey( 49, mode, "F", "F")
ek.appendKey( 50, mode, "X", "X")
ek.appendKey( 51, mode, "!", "! ")
ek.appendKey( 52, mode, '""', '""_LEFT_ARROW_')
ek.appendKey( 53, mode, "#", "#")
ek.appendKey( 54, mode, "pgdn", "_PAGE_DOWN_", 2)
ek.appendKey( 55, mode, "selw→", "_LEFT_CTRL__LEFT_SHIFT__RIGHT_ARROW__RIGHT_SHIFT__RIGHT_CTRL_", 2)

ek.appendKey( 56, mode, "space", " ", 2)
ek.appendKey( 57, mode, " ←  ", "_LEFT_ARROW_", 2)
ek.appendKey( 58, mode, "sel.←", "_LEFT_SHIFT__LEFT_ARROW__RIGHT_SHIFT_", 2)
ek.appendKey( 59, mode, "word←", "_LEFT_CTRL__LEFT_ARROW__RIGHT_CTRL_", 2)
ek.appendKey( 60, mode, "home", "_HOME_", 2)
ek.appendKey( 61, mode, "paste", "_LEFT_CTRL_v_RIGHT_CTRL_", 2)
ek.appendKey( 62, mode, "selw←", "_LEFT_CTRL__LEFT_SHIFT__LEFT_ARROW__RIGHT_SHIFT__RIGHT_CTRL_", 2)
ek.appendKey( 63, mode, "→RUS", "_RUSLAT__MODE7_", 2)

# Mode 3 - Latin Numbers
mode = 3
ek.appendKey(  0, mode, "none", "", 2)
ek.appendKey(  1, mode, "1", "_MODE0_1")
ek.appendKey(  2, mode, "2", "_MODE0_2")
ek.appendKey(  3, mode, "+", "_MODE0_+")
ek.appendKey(  4, mode, "3", "_MODE0_3")
ek.appendKey(  5, mode, "()", "_MODE0_()_LEFT_ARROW_")
ek.appendKey(  6, mode, "=", "_MODE0_=")
ek.appendKey(  7, mode, "backspace", "_BACKSPACE_", 2)

ek.appendKey(  8, mode, "4", "_MODE0_4")
ek.appendKey(  9, mode, "  ↑ ", "_UP_ARROW_", 2)
ek.appendKey( 10, mode, "|", "_MODE0_|")
ek.appendKey( 11, mode, "-", "-")
ek.appendKey( 12, mode, "%", "_MODE0_%")
ek.appendKey( 13, mode, "[]", "_MODE0_[]_LEFT_ARROW_")
ek.appendKey( 14, mode, "<", "_MODE0_<")
ek.appendKey( 15, mode, "  → ", "_RIGHT_ARROW_", 2)

ek.appendKey( 16, mode, "5", "_MODE0_5")
ek.appendKey( 17, mode, "&", "_MODE0_&")
ek.appendKey( 18, mode, "return", "_RETURN_", 2)
ek.appendKey( 19, mode, "/", "_MODE0_/")
ek.appendKey( 20, mode, ",", "_MODE0_,")
ek.appendKey( 21, mode, "{}", "_MODE0_{}_LEFT_ARROW_")
ek.appendKey( 22, mode, ">", "_MODE0_>")
ek.appendKey( 23, mode, "sel→", "_LEFT_SHIFT__RIGHT_ARROW__RIGHT_SHIFT_", 2)

ek.appendKey( 24, mode, "0", "_MODE0_0")
ek.appendKey( 25, mode, "7", "_MODE0_7")
ek.appendKey( 26, mode, "8", "_MODE0_8")
ek.appendKey( 27, mode, "pgup", "_PAGE_UP_", 2)
ek.appendKey( 28, mode,  "9", "_MODE0_9")
ek.appendKey( 29, mode, "</>", "_MODE0_</>_LEFT_ARROW__LEFT_ARROW_")
ek.appendKey( 30, mode, "$", "_MODE0_$")
ek.appendKey( 31, mode, "word→", "_LEFT_CTRL__RIGHT_ARROW__RIGHT_CTRL_", 2)

ek.appendKey( 32, mode, "6", "_MODE0_6")
ek.appendKey( 33, mode, "^", "_MODE0_^")
ek.appendKey( 34, mode, ".", "_MODE0_.")
ek.appendKey( 35, mode, "*", "_MODE0_*")
ek.appendKey( 36, mode, "  ↓ ", "_DOWN_ARROW_", 2)
ek.appendKey( 37, mode, "-", "_MODE0_-")
ek.appendKey( 38, mode, "%", "_MODE0_%")
ek.appendKey( 39, mode, "end ", "_END_", 2)

ek.appendKey( 40, mode, "undef", ")", 2)
ek.appendKey( 41, mode, "undef", "_MODE0_]", 2)
ek.appendKey( 42, mode, "`", "_MODE0_`")
ek.appendKey( 43, mode, "sel↑", "_LEFT_SHIFT__UP_ARROW__RIGHT_SHIFT_", 2)
ek.appendKey( 44, mode, "~", "_MODE0_~")
ek.appendKey( 45, mode, " ins", "_MODE0__INSERT_", 2)
ek.appendKey( 46, mode, "sel↓", "_LEFT_SHIFT__DOWN_ARROW__RIGHT_SHIFT_", 2)
ek.appendKey( 47, mode, " cut", "_MODE0__LEFT_CTRL_x_RIGHT_CTRL_", 2)

ek.appendKey( 48, mode, "e", "e")
ek.appendKey( 49, mode, ">", ">")
ek.appendKey( 50, mode, "~", "_MODE0_~")
ek.appendKey( 51, mode, "|", "_MODE0_|")
ek.appendKey( 52, mode, "`", "_MODE0_`")
ek.appendKey( 53, mode, "#", "_MODE0_#")
ek.appendKey( 54, mode, "pgdn", "_PAGE_DOWN_", 2)
ek.appendKey( 55, mode, "selw→", "_LEFT_CTRL__LEFT_SHIFT__RIGHT_ARROW__RIGHT_SHIFT__RIGHT_CTRL_", 2)

ek.appendKey( 56, mode, "tab ", "_TAB_", 2)
ek.appendKey( 57, mode, " ←  ", "_LEFT_ARROW_", 2)
ek.appendKey( 58, mode, "sel.←", "_LEFT_SHIFT__LEFT_ARROW__RIGHT_SHIFT_", 2)
ek.appendKey( 59, mode, "word←", "_LEFT_CTRL__LEFT_ARROW__RIGHT_CTRL_", 2)
ek.appendKey( 60, mode, "top", "_MODE0__LEFT_CTRL__HOME__RIGHT_CTRL_", 2)
ek.appendKey( 61, mode, "undo", "_MODE0__LEFT_CTRL_z_RIGHT_CTRL_", 2)
ek.appendKey( 62, mode, "selw←", "_LEFT_CTRL__LEFT_SHIFT__LEFT_ARROW__RIGHT_SHIFT__RIGHT_CTRL_", 2)
ek.appendKey( 63, mode, "RUS synch.", "_RUSLAT__MODE0_", 2)


# Mode 4 - Latin NUMLOCK
mode = 4
ek.appendKey(  0, mode, "none", "", 2)
ek.appendKey(  1, mode, "1", "1")
ek.appendKey(  2, mode, "2", "2")
ek.appendKey(  3, mode, "+", "+")
ek.appendKey(  4, mode, "3", "3")
ek.appendKey(  5, mode, "()", "()_LEFT_ARROW_")
ek.appendKey(  6, mode, "=", "=")
ek.appendKey(  7, mode, "backspace", "_BACKSPACE_", 2)

ek.appendKey(  8, mode, "4", "4")
ek.appendKey(  9, mode, "  ↑ ", "_UP_ARROW_", 2)
ek.appendKey( 10, mode, "|", "|")
ek.appendKey( 11, mode, "-", "-")
ek.appendKey( 12, mode, "%", "%")
ek.appendKey( 13, mode, "[]", "[]_LEFT_ARROW_")
ek.appendKey( 14, mode, "<", "<")
ek.appendKey( 15, mode, "  → ", "_RIGHT_ARROW_", 2)

ek.appendKey( 16, mode, "5", "5")
ek.appendKey( 17, mode, "&", "&")
ek.appendKey( 18, mode, "return", "_RETURN_", 2)
ek.appendKey( 19, mode, "/", "/")
ek.appendKey( 20, mode, ",", ",")
ek.appendKey( 21, mode, "{}", "{}_LEFT_ARROW_")
ek.appendKey( 22, mode, ">", ">")
ek.appendKey( 23, mode, "sel→", "_LEFT_SHIFT__RIGHT_ARROW__RIGHT_SHIFT_", 2)

ek.appendKey( 24, mode, "0", "0")
ek.appendKey( 25, mode, "7", "7")
ek.appendKey( 26, mode, "8", "8")
ek.appendKey( 27, mode, "pgup", "_PAGE_UP_", 2)
ek.appendKey( 28, mode,  "9", "9")
ek.appendKey( 29, mode, "</>", "</>_LEFT_ARROW__LEFT_ARROW_")
ek.appendKey( 30, mode, "$", "$")
ek.appendKey( 31, mode, "word→", "_LEFT_CTRL__RIGHT_ARROW__RIGHT_CTRL_", 2)

ek.appendKey( 32, mode, "6", "6")
ek.appendKey( 33, mode, "^", "^")
ek.appendKey( 34, mode, ".", ".")
ek.appendKey( 35, mode, "*", "*")
ek.appendKey( 36, mode, "  ↓ ", "_DOWN_ARROW_", 2)
ek.appendKey( 37, mode, "-", "-")
ek.appendKey( 38, mode, "%", "%")
ek.appendKey( 39, mode, "end ", "_END_", 2)

ek.appendKey( 40, mode, "undef", ")", 2)
ek.appendKey( 41, mode, "undef", "]", 2)
ek.appendKey( 42, mode, "`", "`")
ek.appendKey( 43, mode, "sel↑", "_LEFT_SHIFT__UP_ARROW__RIGHT_SHIFT_", 2)
ek.appendKey( 44, mode, "~", "~")
ek.appendKey( 45, mode, " del", "_DELETE_", 2)
ek.appendKey( 46, mode, "sel↓", "_LEFT_SHIFT__DOWN_ARROW__RIGHT_SHIFT_", 2)
ek.appendKey( 47, mode, "copy", "_MODE0__LEFT_CTRL_c_RIGHT_CTRL_", 2)

ek.appendKey( 48, mode, "e", "e")
ek.appendKey( 49, mode, ">", ">")
ek.appendKey( 50, mode, "~", "~")
ek.appendKey( 51, mode, "|", "|")
ek.appendKey( 52, mode, "`", "`")
ek.appendKey( 53, mode, "#", "#")
ek.appendKey( 54, mode, "pgdn", "_PAGE_DOWN_", 2)
ek.appendKey( 55, mode, "selw→", "_LEFT_CTRL__LEFT_SHIFT__RIGHT_ARROW__RIGHT_SHIFT__RIGHT_CTRL_", 2)

ek.appendKey( 56, mode, "tab ", "_TAB_", 2)
ek.appendKey( 57, mode, " ←  ", "_LEFT_ARROW_", 2)
ek.appendKey( 58, mode, "sel.←", "_LEFT_SHIFT__LEFT_ARROW__RIGHT_SHIFT_", 2)
ek.appendKey( 59, mode, "word←", "_LEFT_CTRL__LEFT_ARROW__RIGHT_CTRL_", 2)
ek.appendKey( 60, mode, "home", "_HOME_", 2)
ek.appendKey( 61, mode, "undo", "_LEFT_CTRL_z_RIGHT_CTRL_", 2)
ek.appendKey( 62, mode, "selw←", "_LEFT_CTRL__LEFT_SHIFT__LEFT_ARROW__RIGHT_SHIFT__RIGHT_CTRL_", 2)
ek.appendKey( 63, mode, "→RUS", "_RUSLAT__MODE9_", 2)

# Mode 5 - Russian Normal
mode = 5
ek.appendKey(  0, mode, "пустой", "", 2)
ek.appendKey(  1, mode, "е", "t")
ek.appendKey(  2, mode, "а", "f")
ek.appendKey(  3, mode, "т", "n")
ek.appendKey(  4, mode, "л", "k_LEFT_ARROW__RIGHT_ARROW_") # double k (л) is a ж (;:)
ek.appendKey(  5, mode, "п", "g")
ek.appendKey(  6, mode, "с", "c")
ek.appendKey(  7, mode, "забой", "_BACKSPACE_", 2)

ek.appendKey(  8, mode, "и", "b")
ek.appendKey(  9, mode, "  ↑ ", "_UP_ARROW_", 2)
ek.appendKey( 10, mode, "й", "q")
ek.appendKey( 11, mode, "в", "d")
ek.appendKey( 12, mode, "у", "e")
ek.appendKey( 13, mode, "ш", "i")
ek.appendKey( 14, mode, "б", ",_LEFT_ARROW__RIGHT_ARROW_")
ek.appendKey( 15, mode, "  → ", "_RIGHT_ARROW_", 2)

ek.appendKey( 16, mode, "о", "j")
ek.appendKey( 17, mode, "м", "v")
ek.appendKey( 18, mode, "ввод", "_RETURN_", 2)
ek.appendKey( 19, mode, "ж", ";")
ek.appendKey( 20, mode, ",", "_RUSLAT_, _RUSLAT_")
ek.appendKey( 21, mode, "щ", "o_LEFT_ARROW__RIGHT_ARROW_")
ek.appendKey( 22, mode, "ц", "w")
ek.appendKey( 23, mode, "выд.→", "_LEFT_SHIFT__RIGHT_ARROW__RIGHT_SHIFT_", 2)

ek.appendKey( 24, mode, "н", "y")
ek.appendKey( 25, mode, "г", "u")
ek.appendKey( 26, mode, "я", "z")
ek.appendKey( 27, mode, "стр↑", "_PAGE_UP_", 2)
ek.appendKey( 28, mode, "ь", "m")
ek.appendKey( 29, mode, "ъ", "]")
ek.appendKey( 30, mode, "?", "_MODE6_& ")
ek.appendKey( 31, mode, "слово→", "_LEFT_CTRL__RIGHT_ARROW__RIGHT_CTRL_", 2)

ek.appendKey( 32, mode, "р", "h")
ek.appendKey( 33, mode, "д", "l_LEFT_ARROW__RIGHT_ARROW_")  # double д is э
ek.appendKey( 34, mode, ".", "_MODE6_/ ")
ek.appendKey( 35, mode, "з", "p_LEFT_ARROW__RIGHT_ARROW_") # double з is ъ
ek.appendKey( 36, mode, "  ↓ ", "_DOWN_ARROW_", 2)
ek.appendKey( 37, mode, "-", "-")
ek.appendKey( 38, mode, "к", "r")
ek.appendKey( 39, mode, "конец", "_END_", 2)

ek.appendKey( 40, mode, "ы", "s")
ek.appendKey( 41, mode, "ю", ".")
ek.appendKey( 42, mode, "э", "'")
ek.appendKey( 43, mode, "выд.↑", "_LEFT_SHIFT__UP_ARROW__RIGHT_SHIFT_", 2)
ek.appendKey( 44, mode, "ё", "`")
ek.appendKey( 45, mode, "удал.", "_DELETE_", 2)
ek.appendKey( 46, mode, "выд.↓", "_LEFT_SHIFT__DOWN_ARROW__RIGHT_SHIFT_", 2)
ek.appendKey( 47, mode, "копир.", "_RUSLAT__LEFT_CTRL_c_RIGHT_CTRL__RUSLAT_", 2)

ek.appendKey( 48, mode, "ч", "x")
ek.appendKey( 49, mode, "ф", "a")
ek.appendKey( 50, mode, "х", "[")
ek.appendKey( 51, mode, "!", "_MODE6_! ")
ek.appendKey( 52, mode, '""', '@@_LEFT_ARROW_')
ek.appendKey( 53, mode, "№", "#")
ek.appendKey( 54, mode, "стр↓", "_PAGE_DOWN_", 2)
ek.appendKey( 55, mode, "в.сл.→", "_LEFT_CTRL__LEFT_SHIFT__RIGHT_ARROW__RIGHT_SHIFT__RIGHT_CTRL_", 2)

ek.appendKey( 56, mode, "пробел", " ", 2)
ek.appendKey( 57, mode, " ←  ", "_LEFT_ARROW_", 2)
ek.appendKey( 58, mode, "выд.←", "_LEFT_SHIFT__LEFT_ARROW__RIGHT_SHIFT_", 2)
ek.appendKey( 59, mode, "слово←", "_LEFT_CTRL__LEFT_ARROW__RIGHT_CTRL_", 2)
ek.appendKey( 60, mode, "начало", "_RUSLAT__HOME__RUSLAT_", 2)
ek.appendKey( 61, mode, "встав.", "_RUSLAT__LEFT_CTRL_v_RIGHT_CTRL__RUSLAT_", 2)
ek.appendKey( 62, mode, "выд.с.←", "_LEFT_CTRL__LEFT_SHIFT__LEFT_ARROW__RIGHT_SHIFT__RIGHT_CTRL_", 2)
ek.appendKey( 63, mode, "→LAT", "_RUSLAT__MODE0_", 2)

# Mode 6 - Russian Shifted
mode = 6
ek.appendKey(  0, mode, "пустой", "", 2)
ek.appendKey(  1, mode, "Е", "_MODE5_T")
ek.appendKey(  2, mode, "А", "_MODE5_F")
ek.appendKey(  3, mode, "Т", "_MODE5_N")
ek.appendKey(  4, mode, "Л", "_MODE5_K_LEFT_ARROW__RIGHT_ARROW_") # double k (л) is a ж (;:)
ek.appendKey(  5, mode, "П", "_MODE5_G")
ek.appendKey(  6, mode, "С", "_MODE5_C")
ek.appendKey(  7, mode, "забой", "_BACKSPACE_", 2)

ek.appendKey(  8, mode, "И", "_MODE5_B")
ek.appendKey(  9, mode, "  ↑ ", "_UP_ARROW_", 2)
ek.appendKey( 10, mode, "Й", "_MODE5_Q")
ek.appendKey( 11, mode, "В", "_MODE5_D")
ek.appendKey( 12, mode, "У", "_MODE5_E")
ek.appendKey( 13, mode, "Ш", "_MODE5_I")
ek.appendKey( 14, mode, "Б", "_MODE5_<_LEFT_ARROW__RIGHT_ARROW_")
ek.appendKey( 15, mode, "  → ", "_RIGHT_ARROW_", 2)

ek.appendKey( 16, mode, "О", "_MODE5_J")
ek.appendKey( 17, mode, "М", "_MODE5_V")
ek.appendKey( 18, mode, "ввод", "_RETURN_", 2)
ek.appendKey( 19, mode, "Ж", "_MODE5_:")
ek.appendKey( 20, mode, ";", "_MODE5_$ ")
ek.appendKey( 21, mode, "Щ", "_MODE5_O_LEFT_ARROW__RIGHT_ARROW_")
ek.appendKey( 22, mode, "Ц", "_MODE5_W")
ek.appendKey( 23, mode, "выд.→", "_LEFT_SHIFT__RIGHT_ARROW__RIGHT_SHIFT_", 2)

ek.appendKey( 24, mode, "Н", "_MODE5_Y")
ek.appendKey( 25, mode, "Г", "_MODE5_U")
ek.appendKey( 26, mode, "Я", "_MODE5_Z")
ek.appendKey( 27, mode, "стр↑", "_PAGE_UP_", 2)
ek.appendKey( 28, mode, "Ь", "_MODE5_M")
ek.appendKey( 29, mode, "Ъ", "_MODE5_}")
ek.appendKey( 30, mode, "?", "& ")
ek.appendKey( 31, mode, "слово→", "_LEFT_CTRL__RIGHT_ARROW__RIGHT_CTRL_", 2)

ek.appendKey( 32, mode, "Р", "_MODE5_H")
ek.appendKey( 33, mode, "Д", "_MODE5_L_LEFT_ARROW__RIGHT_ARROW_")  # double д is э
ek.appendKey( 34, mode, ":", "_MODE5__RUSLAT_: _RUSLAT_")
ek.appendKey( 35, mode, "З", "P_LEFT_ARROW__RIGHT_ARROW_") # double з is ъ
ek.appendKey( 36, mode, "  ↓ ", "_DOWN_ARROW_", 2)
ek.appendKey( 37, mode, "-", "-")
ek.appendKey( 38, mode, "К", "_MODE5_R")
ek.appendKey( 39, mode, "конец", "_END_", 2)

ek.appendKey( 40, mode, "Ы", "_MODE5_S")
ek.appendKey( 41, mode, "Ю", "_MODE5_>")
ek.appendKey( 42, mode, "Э", '"')
ek.appendKey( 43, mode, "выд.↑", "_LEFT_SHIFT__UP_ARROW__RIGHT_SHIFT_", 2)
ek.appendKey( 44, mode, "Ё", "_MODE5_~")
ek.appendKey( 45, mode, "удал.", "_DELETE_", 2)
ek.appendKey( 46, mode, "выд.↓", "_LEFT_SHIFT__DOWN_ARROW__RIGHT_SHIFT_", 2)
ek.appendKey( 47, mode, "вырез.", "_MODE5__RUSLAT__LEFT_CTRL_x_RIGHT_CTRL__RUSLAT_", 2)

ek.appendKey( 48, mode, "Ч", "_MODE5_X")
ek.appendKey( 49, mode, "Ф", "_MODE5_A")
ek.appendKey( 50, mode, "Х", "_MODE5_{")
ek.appendKey( 51, mode, "!", "! ")
ek.appendKey( 52, mode, "'", "_MODE5__RUSLAT_'_RUSLAT_")
ek.appendKey( 53, mode, "№", "#")
ek.appendKey( 54, mode, "стр↓", "_PAGE_DOWN_", 2)
ek.appendKey( 55, mode, "в.сл.→", "_LEFT_CTRL__LEFT_SHIFT__RIGHT_ARROW__RIGHT_SHIFT__RIGHT_CTRL_", 2)

ek.appendKey( 56, mode, "пробел", " ", 2)
ek.appendKey( 57, mode, " ←  ", "_LEFT_ARROW_", 2)
ek.appendKey( 58, mode, "выд.←", "_LEFT_SHIFT__LEFT_ARROW__RIGHT_SHIFT_", 2)
ek.appendKey( 59, mode, "слово←", "_LEFT_CTRL__LEFT_ARROW__RIGHT_CTRL_", 2)
ek.appendKey( 60, mode, "начало", "_RUSLAT__HOME__RUSLAT_", 2)
ek.appendKey( 61, mode, "встав.", "_RUSLAT__LEFT_CTRL_v_RIGHT_CTRL__RUSLAT_", 2)
ek.appendKey( 62, mode, "выд.с.←", "_LEFT_CTRL__LEFT_SHIFT__LEFT_ARROW__RIGHT_SHIFT__RIGHT_CTRL_", 2)
ek.appendKey( 63, mode, "→LAT", "_RUSLAT__MODE1_", 2)

# Mode 7 - Russian CAPS
mode = 7
ek.appendKey(  0, mode, "пустой", "", 2)
ek.appendKey(  1, mode, "Е", "T")
ek.appendKey(  2, mode, "А", "F")
ek.appendKey(  3, mode, "Т", "N")
ek.appendKey(  4, mode, "Л", "K_LEFT_ARROW__RIGHT_ARROW_") # double k (л) is a ж (;:)
ek.appendKey(  5, mode, "П", "G")
ek.appendKey(  6, mode, "С", "C")
ek.appendKey(  7, mode, "забой", "_BACKSPACE_", 2)

ek.appendKey(  8, mode, "И", "B")
ek.appendKey(  9, mode, "  ↑ ", "_UP_ARROW_", 2)
ek.appendKey( 10, mode, "Й", "Q")
ek.appendKey( 11, mode, "В", "D")
ek.appendKey( 12, mode, "У", "E")
ek.appendKey( 13, mode, "Ш", "I")
ek.appendKey( 14, mode, "Б", "<_LEFT_ARROW__RIGHT_ARROW_")
ek.appendKey( 15, mode, "  → ", "_RIGHT_ARROW_", 2)

ek.appendKey( 16, mode, "О", "J")
ek.appendKey( 17, mode, "М", "V")
ek.appendKey( 18, mode, "ввод", "_RETURN_", 2)
ek.appendKey( 19, mode, "Ж", ":")
ek.appendKey( 20, mode, ",", "_RUSLAT_, _RUSLAT_")
ek.appendKey( 21, mode, "Щ", "O_LEFT_ARROW__RIGHT_ARROW_")
ek.appendKey( 22, mode, "Ц", "W")
ek.appendKey( 23, mode, "выд.→", "_LEFT_SHIFT__RIGHT_ARROW__RIGHT_SHIFT_", 2)

ek.appendKey( 24, mode, "Н", "Y")
ek.appendKey( 25, mode, "Г", "U")
ek.appendKey( 26, mode, "Я", "Z")
ek.appendKey( 27, mode, "стр↑", "_PAGE_UP_", 2)
ek.appendKey( 28, mode, "Ь", "M")
ek.appendKey( 29, mode, "Ъ", "}")
ek.appendKey( 30, mode, "?", "& ")
ek.appendKey( 31, mode, "слово→", "_LEFT_CTRL__RIGHT_ARROW__RIGHT_CTRL_", 2)

ek.appendKey( 32, mode, "Р", "H")
ek.appendKey( 33, mode, "Д", "L_LEFT_ARROW__RIGHT_ARROW_")  # double д is э
ek.appendKey( 34, mode, ".", "/ ")
ek.appendKey( 35, mode, "З", "P_LEFT_ARROW__RIGHT_ARROW_") # double з is ъ
ek.appendKey( 36, mode, "  ↓ ", "_DOWN_ARROW_", 2)
ek.appendKey( 37, mode, "-", "-")
ek.appendKey( 38, mode, "К", "R")
ek.appendKey( 39, mode, "конец", "_END_", 2)

ek.appendKey( 40, mode, "Ы", "S")
ek.appendKey( 41, mode, "Ю", ">")
ek.appendKey( 42, mode, "Э", '"')
ek.appendKey( 43, mode, "выд.↑", "_LEFT_SHIFT__UP_ARROW__RIGHT_SHIFT_", 2)
ek.appendKey( 44, mode, "Ё", "~")
ek.appendKey( 45, mode, "удал.", "_DELETE_", 2)
ek.appendKey( 46, mode, "выд.↓", "_LEFT_SHIFT__DOWN_ARROW__RIGHT_SHIFT_", 2)
ek.appendKey( 47, mode, "копир.", "_RUSLAT__LEFT_CTRL_c_RIGHT_CTRL__RUSLAT_", 2)

ek.appendKey( 48, mode, "Ч", "X")
ek.appendKey( 49, mode, "Ф", "A")
ek.appendKey( 50, mode, "Х", "{")
ek.appendKey( 51, mode, "!", "! ")
ek.appendKey( 52, mode, '""', '@@_LEFT_ARROW_')
ek.appendKey( 53, mode, "№", "#")
ek.appendKey( 54, mode, "стр↓", "_PAGE_DOWN_", 2)
ek.appendKey( 55, mode, "в.сл.→", "_LEFT_CTRL__LEFT_SHIFT__RIGHT_ARROW__RIGHT_SHIFT__RIGHT_CTRL_", 2)

ek.appendKey( 56, mode, "пробел", " ", 2)
ek.appendKey( 57, mode, " ←  ", "_LEFT_ARROW_", 2)
ek.appendKey( 58, mode, "выд.←", "_LEFT_SHIFT__LEFT_ARROW__RIGHT_SHIFT_", 2)
ek.appendKey( 59, mode, "слово←", "_LEFT_CTRL__LEFT_ARROW__RIGHT_CTRL_", 2)
ek.appendKey( 60, mode, "начало", "_RUSLAT__HOME__RUSLAT_", 2)
ek.appendKey( 61, mode, "встав.", "_RUSLAT__LEFT_CTRL_v_RIGHT_CTRL__RUSLAT_", 2)
ek.appendKey( 62, mode, "выд.с.←", "_LEFT_CTRL__LEFT_SHIFT__LEFT_ARROW__RIGHT_SHIFT__RIGHT_CTRL_", 2)
ek.appendKey( 63, mode, "→LAT", "_RUSLAT__MODE2_", 2)

# Mode 8 - Russian Numbers
mode = 8
ek.appendKey(  0, mode, "пустой", "", 2)
ek.appendKey(  1, mode, "1", "_MODE5_1")
ek.appendKey(  2, mode, "2", "_MODE5_2")
ek.appendKey(  3, mode, "+", "_MODE5_+")
ek.appendKey(  4, mode, "3", "_MODE5_3")
ek.appendKey(  5, mode, "()", "_MODE5_()_LEFT_ARROW_")
ek.appendKey(  6, mode, "=", "_MODE5_=")
ek.appendKey(  7, mode, "забой", "_BACKSPACE_", 2)

ek.appendKey(  8, mode, "4", "_MODE5_4")
ek.appendKey(  9, mode, "  ↑ ", "_UP_ARROW_", 2)
ek.appendKey( 10, mode, "|", "_MODE5_|")
ek.appendKey( 11, mode, "-", "-")
ek.appendKey( 12, mode, "%", "_MODE5_%")
ek.appendKey( 13, mode, "[]", "_MODE5__RUSLAT_[]_LEFT_ARROW__RUSLAT_")
ek.appendKey( 14, mode, "<", "_MODE5__RUSLAT_<_RUSLAT_")
ek.appendKey( 15, mode, "  → ", "_RIGHT_ARROW_", 2)

ek.appendKey( 16, mode, "5", "_MODE5_5")
ek.appendKey( 17, mode, "&", "_MODE5_&")
ek.appendKey( 18, mode, "ввод", "_RETURN_", 2)
ek.appendKey( 19, mode, "/", "_MODE5_|")
ek.appendKey( 20, mode, ",", "_MODE5__RUSLAT_,_RUSLAT_")
ek.appendKey( 21, mode, "{}", "_MODE5__RUSLAT_{}_LEFT_ARROW__RUSLAT_")
ek.appendKey( 22, mode, ">", "_MODE5__RUSLAT_>_RUSLAT_")
ek.appendKey( 23, mode, "выд.→", "_LEFT_SHIFT__RIGHT_ARROW__RIGHT_SHIFT_", 2)

ek.appendKey( 24, mode, "0", "_MODE5_0")
ek.appendKey( 25, mode, "7", "_MODE5_7")
ek.appendKey( 26, mode, "8", "_MODE5_8")
ek.appendKey( 27, mode, "pgup", "_PAGE_UP_", 2)
ek.appendKey( 28, mode,  "9", "_MODE5_9")
ek.appendKey( 29, mode, "</>", "_MODE5__RUSLAT_</>_RUSLAT__LEFT_ARROW__LEFT_ARROW_")
ek.appendKey( 30, mode, "$", "_MODE5_$")
ek.appendKey( 31, mode, "word→", "_LEFT_CTRL__RIGHT_ARROW__RIGHT_CTRL_", 2)

ek.appendKey( 32, mode, "6", "_MODE5_6")
ek.appendKey( 33, mode, "^", "_MODE5_^")
ek.appendKey( 34, mode, ".", "_MODE5_/")
ek.appendKey( 35, mode, "*", "_MODE5_*")
ek.appendKey( 36, mode, "  ↓ ", "_DOWN_ARROW_", 2)
ek.appendKey( 37, mode, "-", "_MODE5_-")
ek.appendKey( 38, mode, "%", "_MODE5_%")
ek.appendKey( 39, mode, "конец", "_END_", 2)

ek.appendKey( 40, mode, "неопр.", ")")
ek.appendKey( 41, mode, "неопр.", "]")
ek.appendKey( 42, mode, "неопр.", "}")
ek.appendKey( 43, mode, "выд.↑", "_LEFT_SHIFT__UP_ARROW__RIGHT_SHIFT_", 2)
ek.appendKey( 44, mode, "~", "_MODE5__RUSLAT_~_RUSLAT_")
ek.appendKey( 45, mode, "удал.", "_MODE5__INSERT_", 2)
ek.appendKey( 46, mode, "выд.↓", "_LEFT_SHIFT__DOWN_ARROW__RIGHT_SHIFT_", 2)
ek.appendKey( 47, mode, "вырез.", "_MODE5__RUSLAT__LEFT_CTRL_x_RIGHT_CTRL__RUSLAT_", 2)

ek.appendKey( 48, mode, "e", "_MODE5__RUSLAT_e_RUSLAT_")
ek.appendKey( 49, mode, ">", "_MODE5__RUSLAT_>_RUSLAT_")
ek.appendKey( 50, mode, "~", "_MODE5__RUSLAT_~_RUSLAT_")
ek.appendKey( 51, mode, "|", "_MODE5__RUSLAT_|_RUSLAT_")
ek.appendKey( 52, mode, "`", "_MODE5__RUSLAT_`_RUSLAT_")
ek.appendKey( 53, mode, "#", "_MODE5__RUSLAT_#_RUSLAT_")
ek.appendKey( 54, mode, "pgdn", "_PAGE_DOWN_", 2)
ek.appendKey( 55, mode, "selw→", "_LEFT_CTRL__LEFT_SHIFT__RIGHT_ARROW__RIGHT_SHIFT__RIGHT_CTRL_")

ek.appendKey( 56, mode, "таб ", "_MODE5__TAB_", 2)
ek.appendKey( 57, mode, " ←  ", "_LEFT_ARROW_", 2)
ek.appendKey( 58, mode, "выд.←", "_LEFT_SHIFT__LEFT_ARROW__RIGHT_SHIFT_", 2)
ek.appendKey( 59, mode, "слово←", "_LEFT_CTRL__LEFT_ARROW__RIGHT_CTRL_", 2)
ek.appendKey( 60, mode, "нач.текс.", "_MODE5__RUSLAT__LEFT_CTRL__HOME__RIGHT_CTRL__RUSLAT_", 2)
ek.appendKey( 61, mode, "отмена", "_MODE5__RUSLAT__LEFT_CTRL_z_RIGHT_CTRL__RUSLAT_", 2)
ek.appendKey( 62, mode, "в.сл.←", "_LEFT_CTRL__LEFT_SHIFT__LEFT_ARROW__RIGHT_SHIFT__RIGHT_CTRL_", 2)
ek.appendKey( 63, mode, "LAT синх.", "_RUSLAT__MODE5_", 2)

# Mode 9 - Russian NUMLOCK
mode = 9
ek.appendKey(  0, mode, "пустой", "", 2)
ek.appendKey(  1, mode, "1", "1")
ek.appendKey(  2, mode, "2", "2")
ek.appendKey(  3, mode, "+", "+")
ek.appendKey(  4, mode, "3", "3")
ek.appendKey(  5, mode, "()", "()_LEFT_ARROW_")
ek.appendKey(  6, mode, "=", "=")
ek.appendKey(  7, mode, "забой", "_BACKSPACE_", 2)

ek.appendKey(  8, mode, "4", "4")
ek.appendKey(  9, mode, "  ↑ ", "_UP_ARROW_", 2)
ek.appendKey( 10, mode, "|", "|")
ek.appendKey( 11, mode, "-", "-")
ek.appendKey( 12, mode, "%", "%")
ek.appendKey( 13, mode, "[]", "_RUSLAT_[]_LEFT_ARROW__RUSLAT_")
ek.appendKey( 14, mode, "<", "_RUSLAT_<_RUSLAT_")
ek.appendKey( 15, mode, "  → ", "_RIGHT_ARROW_", 2)

ek.appendKey( 16, mode, "5", "5")
ek.appendKey( 17, mode, "&", "&")
ek.appendKey( 18, mode, "ввод", "_RETURN_", 2)
ek.appendKey( 19, mode, "/", "|")
ek.appendKey( 20, mode, ",", "_RUSLAT_,_RUSLAT_")
ek.appendKey( 21, mode, "{}", "_RUSLAT_{}_LEFT_ARROW__RUSLAT_")
ek.appendKey( 22, mode, ">", "_RUSLAT_>_RUSLAT_")
ek.appendKey( 23, mode, "выд.→", "_LEFT_SHIFT__RIGHT_ARROW__RIGHT_SHIFT_", 2)

ek.appendKey( 24, mode, "0", "0")
ek.appendKey( 25, mode, "7", "7")
ek.appendKey( 26, mode, "8", "8")
ek.appendKey( 27, mode, "pgup", "_PAGE_UP_", 2)
ek.appendKey( 28, mode,  "9", "9")
ek.appendKey( 29, mode, "</>", "_RUSLAT_</>_RUSLAT__LEFT_ARROW__LEFT_ARROW_")
ek.appendKey( 30, mode, "$", "$")
ek.appendKey( 31, mode, "word→", "_LEFT_CTRL__RIGHT_ARROW__RIGHT_CTRL_", 2)

ek.appendKey( 32, mode, "6", "6")
ek.appendKey( 33, mode, "^", "^")
ek.appendKey( 34, mode, ".", "/")
ek.appendKey( 35, mode, "*", "*")
ek.appendKey( 36, mode, "  ↓ ", "_DOWN_ARROW_", 2)
ek.appendKey( 37, mode, "-", "-")
ek.appendKey( 38, mode, "%", "%")
ek.appendKey( 39, mode, "конец", "_END_", 2)

ek.appendKey( 40, mode, "неопр.", ")")
ek.appendKey( 41, mode, "неопр.", "]")
ek.appendKey( 42, mode, "неопр.", "}")
ek.appendKey( 43, mode, "выд.↑", "_LEFT_SHIFT__UP_ARROW__RIGHT_SHIFT_", 2)
ek.appendKey( 44, mode, "~", "_RUSLAT_~_RUSLAT_")
ek.appendKey( 45, mode, "удал.", "_DELETE_", 2)
ek.appendKey( 46, mode, "выд.↓", "_LEFT_SHIFT__DOWN_ARROW__RIGHT_SHIFT_", 2)
ek.appendKey( 47, mode, "копир.", "_RUSLAT__LEFT_CTRL_c_RIGHT_CTRL__RUSLAT_", 2)

ek.appendKey( 48, mode, "e", "_RUSLAT_e_RUSLAT_")
ek.appendKey( 49, mode, ">", "_RUSLAT_>_RUSLAT_")
ek.appendKey( 50, mode, "~", "_RUSLAT_~_RUSLAT_")
ek.appendKey( 51, mode, "|", "_RUSLAT_|_RUSLAT_")
ek.appendKey( 52, mode, "`", "_RUSLAT_`_RUSLAT_")
ek.appendKey( 53, mode, "#", "_RUSLAT_#_RUSLAT_")
ek.appendKey( 54, mode, "стр↓", "_PAGE_DOWN_", 2)
ek.appendKey( 55, mode, "в.сл.→", "_LEFT_CTRL__LEFT_SHIFT__RIGHT_ARROW__RIGHT_SHIFT__RIGHT_CTRL_")

ek.appendKey( 56, mode, "таб ", "_TAB_", 2)
ek.appendKey( 57, mode, " ←  ", "_LEFT_ARROW_", 2)
ek.appendKey( 58, mode, "выд.←", "_LEFT_SHIFT__LEFT_ARROW__RIGHT_SHIFT_", 2)
ek.appendKey( 59, mode, "слово←", "_LEFT_CTRL__LEFT_ARROW__RIGHT_CTRL_", 2)
ek.appendKey( 60, mode, "начало", "_RUSLAT__HOME__RUSLAT_", 2)
ek.appendKey( 61, mode, "отмена", "_RUSLAT__LEFT_CTRL_z_RIGHT_CTRL__RUSLAT_", 2)
ek.appendKey( 62, mode, "в.сл.←", "_LEFT_CTRL__LEFT_SHIFT__LEFT_ARROW__RIGHT_SHIFT__RIGHT_CTRL_", 2)
ek.appendKey( 63, mode, "→LAT", "_RUSLAT__MODE4_", 2)

f = open( "keymapRusStandard2.h", "wt", encoding="UTF-8")
s = "{:s}".format(str(ek))
print(s)
f.write(s)
f.close()

f = open( "./reference/StandardRussian.def", "wb")
if True:
    ek.makeDefinitionFile( f,  "ENGLISH NORMAL ", 0)
    ek.makeDefinitionFile( f, "ENGLISH SHIFTED", 1)
    ek.makeDefinitionFile( f,    "ENGLISH CAPS   ", 2)
    ek.makeDefinitionFile( f, "ENGLISH NUMBERS", 3)
    ek.makeDefinitionFile( f, "ENGLISH NUMLOCK", 4)
    ek.makeDefinitionFile( f,  "RUSSIAN NORMAL ", 5)
    ek.makeDefinitionFile( f, "RUSSIAN SHIFTED", 6)
    ek.makeDefinitionFile( f,    "RUSSIAN CAPS   ", 7)
    ek.makeDefinitionFile( f, "RUSSIAN NUMBERS", 8)
    ek.makeDefinitionFile( f, "RUSSIAN NUMLOCK", 9)
    #print( ArduinoKeyConverter())
f.close()