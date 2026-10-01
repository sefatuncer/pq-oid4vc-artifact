#include <stdio.h>
#include <wolfcose/wolfcose.h>
int main(void) {
  puts("wolfcose baglandi (islevler CAGRILMAZ; yalniz adres)");
  printf("sembol wc_CoseSign1_Verify %s\n", (void*)&wc_CoseSign1_Verify ? "var" : "yok");
  printf("sembol wc_CoseSign_Verify %s\n", (void*)&wc_CoseSign_Verify ? "var" : "yok");
  return 0; }
