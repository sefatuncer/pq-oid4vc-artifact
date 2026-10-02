// Linking check: the API types are referenced; no verification function is CALLED.
fn main() {
    println!("krate sd_jwt_payload baglandi");
    println!("tip {}", std::any::type_name::<sd_jwt_payload::SdJwt>());
    println!("tip {}", std::any::type_name::<sd_jwt_payload::Disclosure>());
}
