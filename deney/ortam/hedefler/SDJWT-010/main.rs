// Bağlama kontrolü: API tiplerine başvurulur; hiçbir doğrulama işlevi ÇAĞRILMAZ.
fn main() {
    println!("krate sd_jwt_payload baglandi");
    println!("tip {}", std::any::type_name::<sd_jwt_payload::SdJwt>());
    println!("tip {}", std::any::type_name::<sd_jwt_payload::Disclosure>());
}
