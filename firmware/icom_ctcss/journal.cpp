#include "journal.h"
namespace Ctcss {
uint16_t crc16(const uint8_t *bytes, uint8_t length) {
  uint16_t crc = 0xFFFF;
  while (length--) {
    crc ^= uint16_t(*bytes++) << 8;
    for (uint8_t i=0; i<8; ++i) crc = (crc & 0x8000) ? (crc << 1) ^ 0x1021 : crc << 1;
  }
  return crc;
}
void encodeRecord(uint8_t *b, uint16_t sequence, uint16_t tone) {
  b[0]=recordMarker; b[1]=1; b[2]=uint8_t(sequence); b[3]=uint8_t(sequence>>8);
  b[4]=uint8_t(tone); b[5]=uint8_t(tone>>8); b[6]=0; b[7]=0;
  uint16_t crc=crc16(b+1,7); b[8]=uint8_t(crc); b[9]=uint8_t(crc>>8);
}
bool decodeRecord(const uint8_t *b, uint16_t &sequence, uint16_t &tone) {
  sequence=uint16_t(b[2]) | uint16_t(b[3])<<8;
  tone=uint16_t(b[4]) | uint16_t(b[5])<<8;
  return b[0]==recordMarker && b[1]==1 && b[6]==0 && b[7]==0 &&
    validTone(tone) && crc16(b+1,7)==(uint16_t(b[8]) | uint16_t(b[9])<<8);
}
int8_t newestRecord(const uint8_t *a,const uint8_t *b) {
  uint16_t sa,sb,t; bool va=decodeRecord(a,sa,t), vb=decodeRecord(b,sb,t);
  if (!va) return vb ? 1 : -1;
  if (!vb) return 0;
  uint16_t delta=sb-sa;
  return delta && delta<0x8000 ? 1 : 0;
}
}
