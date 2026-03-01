#include <unistd.h>
#include <sys/io.h>
#include <stdint.h>

#define PIT_CONTROL   0x43
#define PIT_CHANNEL2  0x42
#define SPEAKER_CTRL  0x61
#define PIT_FREQ      1193182  // 1.193182 MHz

void beep(int frequency, int duration_ms) {
    if (frequency <= 0 || duration_ms <= 0) return;
    
    if (iopl(3) != 0) {
        return; // Failed to gain I/O privileges
    }
    
    uint16_t divisor = PIT_FREQ / frequency;
    
    outb(0xB6, PIT_CONTROL);
    outb(divisor & 0xFF, PIT_CHANNEL2);
    outb((divisor >> 8) & 0xFF, PIT_CHANNEL2);
    
    uint8_t tmp = inb(SPEAKER_CTRL);
    outb(tmp | 0x03, SPEAKER_CTRL);
    
    usleep(duration_ms * 1000);
    
    tmp = inb(SPEAKER_CTRL) & 0xFC;
    outb(tmp, SPEAKER_CTRL);
    
    iopl(0);
}
