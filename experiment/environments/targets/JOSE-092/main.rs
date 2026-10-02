// Linking check: the API types are referenced; no verification function is CALLED.
fn main() {
    println!("krate jsonwebtoken baglandi");
    println!("tip {}", std::any::type_name::<jsonwebtoken::Validation>());
    println!("tip {}", std::any::type_name::<jsonwebtoken::DecodingKey>());
    println!("tip {}", std::any::type_name::<jsonwebtoken::Algorithm>());
}
