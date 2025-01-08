Create a new project/sketch with the example code named `StandardFirmata`.


If you're using a Waveshare display,
go to [https://github.com/waveshareteam/e-Paper/tree/master/Arduino](https://github.com/waveshareteam/e-Paper/tree/master/Arduino).
Here you will see all the different versions that there are.

Go look for the folders matching your resolution. There possibly are multiple folders for it.
So scroll down to the README and check which subfolder is recommended to use for your display.
I have an 2.9 inch 3 color display (black-white, red-white). So mine would be `epd2in9b`.
The README says to use `epd2in9bc`, so I will go into that folder.

Now copy the `epdif.cpp` and `epdif.h` and also the files that start with `epd` followed by your resolution and then ending on the `.cpp` and `.h`.

In my case it would be the `epdif.cpp`, `epdif.h`, `epd2in9b.h`, `epd2in9b.cpp` files that I need to copy.
*(P.s. yes, the names aren't always the same as the folder name, but it's fine)*

Now go back to your project and add the files to it.

Afterwards, open up the `StandardFirmata.ino` file and make the following changes:



1. At the top, look for the `#include <Firmata.h>`, add the following code below it:
```cpp
#include "epd2in9b.h"
```
   Please note that you do need to edit it to the name of the `.h` file you copied over! (not the `epdif.h`, but the other one!)

2. Search for `boolean isResetting = false;` and add the following code ABOVE this line:
```cpp
Epd epd;
boolean isReceivingData = false;

```

3. Search for `void sysexCallback(byte command, byte argc, byte *argv)` and add the following above the comment (the lines with the `/*====`)
```cpp
/*==============================================================================
 * ePaper-BASED SERIAL_MESSAGE commands
 *============================================================================*/

void epaperHandleMessage(byte command, byte argc, byte *argv)
{
  if (argc > 0) {
    switch (argv[0]) {
      case 1: // Reset: Init will first run Reset and then init the screen, else it won't be usable
        Firmata.sendString(STRING_DATA, "[epaperHandleMessage] Reset");
        epd.Init();
        Firmata.sendString(STRING_DATA, "[epaperHandleMessage] Done");
        break;
      case 2: // Clear
        Firmata.sendString(STRING_DATA, "[epaperHandleMessage] Clear");
        // When the epaper has an buffer, you need to do these:
        epd.ClearFrame();
        epd.DisplayFrame();
        // Else comment the above two lines out and uncomment this one:
        // epd.Clear();
        Firmata.sendString(STRING_DATA, "[epaperHandleMessage] Done");
        break;
      case 3: // Sleep
        Firmata.sendString(STRING_DATA, "[epaperHandleMessage] Sleep");
        epd.Sleep();
        Firmata.sendString(STRING_DATA, "[epaperHandleMessage] Done");
        break;
      case 4: // Start black DATA
        if (!isReceivingData) {
          Firmata.sendString(STRING_DATA, "[epaperHandleMessage] Start black data");
          epd.SendCommand(0x10); // DATA_START_TRANSMISSION_1;
          isReceivingData = true;
        }
        break;
      case 5: // Start red DATA
        if (!isReceivingData) {
      	  Firmata.sendString(STRING_DATA, "[epaperHandleMessage] Start red data");
      	  epd.SendCommand(0x13); // DATA_START_TRANSMISSION_2
      	  isReceivingData = true;
        }
        break;
      case 6: // DATA
        if (isReceivingData) {
          for (int i = 1; i < argc; i += 2) {
            unsigned char data = argv[i] + (argv[i + 1] << 7);
            epd.SendData(data);
          }
        }
        break;
      case 7: // End DATA
        if (isReceivingData) {
          Firmata.sendString(STRING_DATA, "[epaperHandleMessage] End data");
          epd.SendCommand(0x92); // DATA_STOP
          isReceivingData = false;
        }
        break;
      case 8: // End message DATA
        Firmata.sendString(STRING_DATA, "[epaperHandleMessage] End message");
        epd.SendCommand(0x12); // DISPLAY_REFRESH
        epd.WaitUntilIdle();
        Firmata.sendString(STRING_DATA, "[epaperHandleMessage] Done");
        break;
    }
  }
}

```

4. In the `void sysexCallback(byte command, byte argc, byte *argv)` function,
   you need to find the part with `case SERIAL_MESSAGE:` (nearly at the end of the function)
   and add the following code just before the line with `break;`:
```cpp
      epaperHandleMessage(command, argc, argv);
```

5. In the `void systemResetCallback()` function, add the following above the line saying `isResetting = false;`:
```cpp

  if (epd.Init() != 0) { return; }
  epd.Sleep(); // Will always sleep, run epd.Init() if you want to wake it up. (pyfirmata2_epd will do it when you run Reset command)

```


After having done that, you're basically done!
Just build the code and upload it to your arduino!