// Bağlama kontrolü: API tiplerine başvurulur; hiçbir doğrulama işlevi ÇAĞRILMAZ.
fn main() {
    println!("krate frank_jwt baglandi");
    println!("tip {}", std::any::type_name::<frank_jwt::Algorithm>());
    println!("tip {}", std::any::type_name::<frank_jwt::ValidationOptions>());
}
