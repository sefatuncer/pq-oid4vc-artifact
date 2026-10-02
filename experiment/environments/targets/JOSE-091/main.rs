// Linking check: the API types are referenced; no verification function is CALLED.
fn main() {
    println!("krate frank_jwt baglandi");
    println!("tip {}", std::any::type_name::<frank_jwt::Algorithm>());
    println!("tip {}", std::any::type_name::<frank_jwt::ValidationOptions>());
}
