// JOSE-102 jwt-kit 5.3.0 adaptörü — C3 sözleşmesi 1.0 / KOSUCU §1–§3.
// Belgeli genel API (README): JWTKeyCollection().add(ecdsa:|eddsa:|mldsa:kid:) + verify(token, as: Payload.self).
// ML-DSA README "MLDSA" bölümü: `@_spi(PostQuantum) import JWTKit` (SPI; README'de belgeli). jwt-kit'te izin listesi
// seçeneği yok; politika, koleksiyona kaydedilen anahtar nesnesinin (algoritması anahtar türüne bağlı) seçimiyle kurulur.
// Doğrulama döngüsü YOK; manifestten yalnız dogrulama_girdileri okunur; ağ yok. Eşleme: MAPPING.md.
import Foundation
@_spi(PostQuantum) import JWTKit

let xKol = ["kontrol-EdDSA": "EdDSA", "kontrol-Ed25519": "Ed25519", "kontrol-ES384": "ES384", "tedavi-ML-DSA-65": "ML-DSA-65", "tedavi-composite": "ML-DSA-65-ES256"]
// Bataryadaki algoritmalardan yerel destek (ECDSA ES256/384/512, EdDSA, MLDSA65/87 [SPI], RSA, HMAC; composite yok)
let kutuphane: Set<String> = ["ES256", "ES384", "EdDSA", "ML-DSA-65", "ML-DSA-87"]
let api = "JWTKeyCollection().add(ecdsa:|eddsa:|mldsa: <anahtar>, kid:) [alg(anahtar_turu) ∈ W]; verify(jwt, as: Yuk.self) (exp: simdi)"

struct Yuk: JWTPayload {
    var exp: ExpirationClaim?
    func verify(using algorithm: some JWTAlgorithm) async throws {
        // sözleşme §2.1: saat = simdi (çevre değişkeni üzerinden)
        let simdi = Double(ProcessInfo.processInfo.environment["A10_SIMDI"] ?? "") ?? Date().timeIntervalSince1970
        try exp?.verifyNotExpired(currentDate: Date(timeIntervalSince1970: simdi))
    }
}

func b64d(_ s: String) -> Data? {
    var t = s.replacingOccurrences(of: "-", with: "+").replacingOccurrences(of: "_", with: "/")
    while t.count % 4 != 0 { t += "=" }
    return Data(base64Encoded: t)
}
func jsonObj(_ d: Data) -> [String: Any]? {
    do {
        let o = try JSONSerialization.jsonObject(with: d, options: [.fragmentsAllowed])
        if let m = o as? [String: Any] { return m }
        if let m = o as? NSDictionary { return m as? [String: Any] }
        FileHandle.standardError.write("json: beklenmeyen tur \(type(of: o))\n".data(using: .utf8)!)
    } catch {
        FileHandle.standardError.write("json: \(error)\n".data(using: .utf8)!)
    }
    return nil
}

var manifest: [String: [String: Any]] = [:]
func girdi(_ id: String) throws -> [String: Any] {
    if manifest.isEmpty {
        let y = FileManager.default.fileExists(atPath: "/v/MANIFEST.json") ? "/v/MANIFEST.json" : "/v/v1.3/MANIFEST.json"
        let m = jsonObj(try Data(contentsOf: URL(fileURLWithPath: y)))!
        for e in m["vektorler"] as! [[String: Any]] { manifest[e["id"] as! String] = (e["dogrulama_girdileri"] as? [String: Any]) ?? [:] }
    }
    guard let g = manifest[id] else { throw NSError(domain: "manifestte yok: \(id)", code: 1) }
    return g
}
func vektorYolu(_ d: String) -> String {
    for y in ["/v/" + d, "/v/" + (d.hasPrefix("v1.3/") ? String(d.dropFirst(5)) : d)] where FileManager.default.fileExists(atPath: y) { return y }
    return "/v/" + d
}

// Politika → (taban, W|nil, R). YONTEM.md §2; VARSAYILAN = sözleşme §5.2 L5.
func politika(_ isx: [String: Any]) throws -> (String, [String]?, [String]) {
    let taban = (isx["politika"] as! String).components(separatedBy: "|")[0].components(separatedBy: "@")[0] // ekler yalnız oracle'ı böler
    let x = xKol[isx["kol"] as! String]
    switch taban {
    case "GEC", "P0", "P1", "P2", "VARSAYILAN": return (taban, nil, [])
    case "IZIN-A": return (taban, ["ES256"], [])
    case "IZIN-AX": guard let x else { throw NSError(domain: "X tanimsiz", code: 2) }; return (taban, ["ES256", x], [])
    case "L4", "L4-S", "L4-Y", "L4-YOL": guard let x else { throw NSError(domain: "X tanimsiz", code: 2) }; return (taban, ["ES256", x], [x])
    default: throw NSError(domain: "bilinmeyen politika", code: 3)
    }
}

// Anahtar seçimi (sözleşme §8 m.1): başlık kid → vektörün JWKS'i; yoksa alg_kid[alg]; yoksa tek kid.
func jwkSec(_ baslik: [String: Any], _ dg: [String: Any]) throws -> [String: Any]? {
    guard let jwksYol = dg["jwks"] as? String else { return nil }
    var kid = baslik["kid"] as? String
    if kid == nil {
        var ak: Any? = dg["alg_kid"]
        if let s = ak as? String { ak = jsonObj(Data(s.utf8)) }
        if let m = ak as? [String: Any], let a = baslik["alg"] as? String { kid = m[a] as? String }
        if kid == nil, let ks = dg["kid"] as? [String], ks.count == 1 { kid = ks[0] }
    }
    let yol = "/anahtarlar/" + (jwksYol.hasPrefix("anahtarlar/") ? String(jwksYol.dropFirst(11)) : jwksYol)
    let keys = jsonObj(try Data(contentsOf: URL(fileURLWithPath: yol)))!["keys"] as! [[String: Any]]
    return keys.first { ($0["kid"] as? String) == kid }
}

func dogalAlg(_ j: [String: Any]) -> String? {
    switch (j["kty"] as? String, j["crv"] as? String) {
    case ("EC", "P-256"): return "ES256"
    case ("EC", "P-384"): return "ES384"
    case ("OKP", "Ed25519"): return "EdDSA"
    case ("AKP", _): return j["alg"] as? String
    default: return nil
    }
}

func sonuc(_ ham: String, _ sinif: String?, _ ozet: String?, yol: String? = "dogrudan", dog: [[String: Any]] = []) -> [String: Any] {
    ["sonuc_ham": ham, "hata_sinifi": sinif ?? NSNull(), "hata_ozeti": ozet ?? NSNull(), "api_yolu": api, "anahtar_yolu": yol ?? NSNull(), "dogrulanan": dog]
}

func dogrula(_ isx: [String: Any]) async throws -> [String: Any] {
    guard (isx["serilestirme"] as? String) == "compact" else {
        return sonuc("uygulanamaz", "bicim-desteklenmiyor", "B6: MAPPING.md (API incelemesi)", yol: nil)
    }
    let dg = try girdi(isx["vektor_id"] as! String)
    let jwt = try String(contentsOfFile: vektorYolu(isx["dosya"] as! String), encoding: .utf8).trimmingCharacters(in: .whitespacesAndNewlines)
    let baslik = b64d(String(jwt.split(separator: ".").first ?? "")).flatMap(jsonObj) ?? [:]
    let alg = baslik["alg"] as? String
    let (_, w, r) = try politika(isx)
    if (try politika(isx)).0 == "L4-YOL" { return sonuc("ifade-edilemedi", nil, "x5c/x5chain yol sinifi politikasi (L4-YOL, B2) icin belgeli API yok", yol: nil) }
    let izin = w == nil ? nil : (r.isEmpty ? w! : r)
    var jwk: [String: Any]? = nil
    var yol = "dogrudan"
    if (dg["anahtar"] as? String) == "jwk basligindan" { jwk = baslik["jwk"] as? [String: Any]; yol = "jwk-basligi" } else { jwk = try jwkSec(baslik, dg) }
    guard let jwk else { return sonuc("red", "anahtar-bulunamadi", "anahtar secilemedi (kid/alg_kid)", yol: yol) }
    let keys = JWTKeyCollection()
    let kid = (jwk["kid"] as? String).map { JWKIdentifier(string: $0) }
    let dogal = dogalAlg(jwk)
    var notu = "anahtar kaydedilmedi (dogal=\(dogal ?? "?"), W=\(izin?.description ?? "varsayilan"))"
    if let d = dogal, izin == nil || izin!.contains(d) {
        do {
            switch d {
            case "ES256": await keys.add(ecdsa: try ES256PublicKey(parameters: (x: jwk["x"] as! String, y: jwk["y"] as! String)), kid: kid)
            case "ES384": await keys.add(ecdsa: try ES384PublicKey(parameters: (x: jwk["x"] as! String, y: jwk["y"] as! String)), kid: kid)
            case "EdDSA": await keys.add(eddsa: try EdDSA.PublicKey(x: jwk["x"] as! String, curve: .ed25519), kid: kid)
            case "ML-DSA-65": await keys.add(mldsa: try MLDSA65PublicKey(rawRepresentation: b64d(jwk["pub"] as! String)!), kid: kid)
            case "ML-DSA-87": await keys.add(mldsa: try MLDSA87PublicKey(rawRepresentation: b64d(jwk["pub"] as! String)!), kid: kid)
            default: return sonuc("red", "alg-desteklenmiyor", "anahtar turu (\(d)) kutuphanede yok", yol: yol)
            }
            notu = "anahtar kaydedildi (\(d))"
        } catch {
            return sonuc("red", "alg-desteklenmiyor", "anahtar nesnesi kurulamadi (\(d)): \(error)", yol: yol)
        }
    }
    do {
        _ = try await keys.verify(jwt, as: Yuk.self)
        // jwt-kit imzayı kayıtlı anahtar nesnesinin algoritmasıyla doğrular (JWTSigner.verify; başlık alg'ı karşılaştırılmaz)
        return sonuc("kabul", nil, nil, yol: yol, dog: [["sira": 0, "alg": dogal ?? "?", "sonuc": "gecerli"]])
    } catch let e as JWTError {
        let s: String
        switch e.errorType {
        case .signatureVerificationFailed: s = "imza-gecersiz"
        case .claimVerificationFailure: s = "zaman"
        case .malformedToken, .invalidHeaderField: s = "ayristirma"
        case .noKeyProvided, .unknownKID:
            s = (alg == nil || !kutuphane.contains(alg!)) ? "alg-desteklenmiyor" : ((izin != nil && !izin!.contains(alg!)) ? "alg-izin-disi" : "anahtar-bulunamadi")
        default: s = "istisna-diger"
        }
        return sonuc("red", s, "JWTError.\(e.errorType): \(e.reason ?? "") | \(notu)", yol: yol)
    } catch {
        return sonuc("istisna", "istisna-diger", "\(error) | \(notu)", yol: yol)
    }
}

func sabit(_ ad: String) -> String {
    ((try? String(contentsOfFile: "/opt/a/" + ad, encoding: .utf8)) ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
}

@main
struct Adaptor {
    static func main() async {
        let a = CommandLine.arguments
        guard a.count >= 3 else { FileHandle.standardError.write("kullanim: adaptor <jobs-v1.3.jsonl> <cikti.jsonl>\n".data(using: .utf8)!); exit(2) }
        let ad = URL(fileURLWithPath: a[2]).deletingPathExtension().lastPathComponent.components(separatedBy: ".")
        let env = ProcessInfo.processInfo.environment
        let kosu = (env["KOSU"].flatMap { $0.isEmpty ? nil : $0 }) ?? (ad.count >= 2 ? ad.last! : "oncesi")
        guard FileManager.default.createFile(atPath: a[2], contents: Data()),
              let out = FileHandle(forWritingAtPath: a[2]) else {
            FileHandle.standardError.write("cikti dosyasi olusturulamadi: \(a[2])\n".data(using: .utf8)!)
            exit(3)
        }
        // CRLF güvenli: Swift'te "\r\n" tek bir Character'dır; iş dosyaları CRLF satır sonu taşıyabilir.
        let satirlar = ((try? String(contentsOfFile: a[1], encoding: .utf8)) ?? "").components(separatedBy: .newlines)
        for l in satirlar where !l.trimmingCharacters(in: .whitespaces).isEmpty {
            let isx = jsonObj(Data(l.utf8))!
            if let dg = try? girdi(isx["vektor_id"] as! String), let s = dg["simdi"] { setenv("A10_SIMDI", "\(s)", 1) }
            let t0 = Date()
            var s: [String: Any]
            do { s = try await dogrula(isx) } catch { s = ["sonuc_ham": "istisna", "hata_sinifi": "adaptor-hatasi", "hata_ozeti": "\(error)", "api_yolu": NSNull(), "dogrulanan": []] }
            var oz: Any = s["hata_ozeti"] ?? NSNull()
            if let o = oz as? String, o.count > 200 { oz = String(o.prefix(200)) }
            let satir: [String: Any] = ["sozlesme": "adaptor-sozlesme/1.0", "hedef_id": env["HEDEF_ID"] ?? "bilinmiyor", "hedef_surum": sabit("HEDEF_SURUM"),
                "adaptor_sha256": sabit("ADAPTOR_SHA256"), "kosu": kosu, "vektor_id": isx["vektor_id"]!, "politika": isx["politika"]!, "kol": isx["kol"]!,
                "sonuc_ham": s["sonuc_ham"]!, "hata_sinifi": s["hata_sinifi"] ?? NSNull(), "hata_ozeti": oz, "dogrulanan_algoritmalar": s["dogrulanan"] ?? [],
                "api_yolu": s["api_yolu"] ?? NSNull(), "anahtar_yolu": s["anahtar_yolu"] ?? NSNull(), "sure_ms": Int(Date().timeIntervalSince(t0) * 1000)]
            let d = try! JSONSerialization.data(withJSONObject: satir, options: [.sortedKeys, .withoutEscapingSlashes])
            out.write(d); out.write("\n".data(using: .utf8)!)
        }
        try? out.close()
    }
}
