// Linking check: the API types are referenced; no verification function is CALLED.
fn main() {
    println!("krate ssi_sd_jwt baglandi");
    println!("tip {}", std::any::type_name::<ssi_sd_jwt::SdAlg>());
    println!("tip {}", std::any::type_name::<ssi_sd_jwt::SdJwtBuf>());
}
