// Bağlama kontrolü: doğrulayıcı türü decltype ile (DEĞERLENDİRİLMEDEN) alınır; hiçbir işlev ÇAĞRILMAZ.
#include <jwt-cpp/jwt.h>
#include <iostream>
#include <typeinfo>
int main() {
  using dogrulayici_t = decltype(jwt::verify());
  std::cout << "jwt-cpp baglandi; tip " << typeid(dogrulayici_t).name() << "\n";
  std::cout << "tip " << typeid(jwt::algorithm::es256).name() << "\n";
  return 0;
}
