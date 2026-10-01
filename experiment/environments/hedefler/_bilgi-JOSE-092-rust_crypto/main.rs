// Bağlama kontrolü: API tiplerine başvurulur; hiçbir doğrulama işlevi ÇAĞRILMAZ.
fn main() {
    println!("krate jsonwebtoken baglandi");
    println!("tip {}", std::any::type_name::<jsonwebtoken::Validation>());
    println!("tip {}", std::any::type_name::<jsonwebtoken::DecodingKey>());
    println!("tip {}", std::any::type_name::<jsonwebtoken::Algorithm>());
}
