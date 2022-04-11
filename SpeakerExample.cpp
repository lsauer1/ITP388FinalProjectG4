#include <SD.h>
#include <SPI.h>
#include <AudioZero.h>

void setup()
{


  if (!SD.begin(4)) {

    while(true);

  }

  // 44100kHz stereo => 88200 sample rate

  AudioZero.begin(2*44100);
}

void loop()
{

  int count = 0;

  File myFile = SD.open("test.wav");

  AudioZero.play(myFile);

}