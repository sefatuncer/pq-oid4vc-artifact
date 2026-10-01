// C3 adaptörü (JVM/Java): JOSE-052 auth0 java-jwt, JOSE-055 jjwt, SDJWT-004 authlete sd-jwt (+ belgeli doğrulama
// yolu Nimbus JOSE+JWT; ÖK §2H m.15: imzayı kendisi doğrulamayan kütüphane önerdiği JOSE katmanıyla ölçülür).
// Sözleşme: adaptor-sozlesme.md (1.0) + KOSUCU.md. Oracle'ı GÖRMEZ; MANIFEST'ten yalnız dogrulama_girdileri.
// Kullanım: java -jar adaptor.jar <hedef_id> <isler.jsonl> <cikti.jsonl> <kosu>
package c3;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.math.BigInteger;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.*;
import java.security.interfaces.ECPublicKey;
import java.security.spec.*;
import java.util.*;

public class Main {
  static final ObjectMapper M = new ObjectMapper();
  static final String A = "ES256", LEGACY = "https://legacy-issuer.example";
  static final Map<String, String> X_OF = Map.of("kontrol-EdDSA", "EdDSA", "kontrol-Ed25519", "Ed25519", "kontrol-ES384", "ES384",
      "tedavi-ML-DSA-65", "ML-DSA-65", "tedavi-composite", "ML-DSA-65-ES256");
  static final Map<String, JsonNode> KID = new HashMap<>();
  static final Map<String, String> ALG2KID = new HashMap<>();

  static byte[] b64d(String s) { return Base64.getUrlDecoder().decode(s.replace("=", "")); }

  static void loadKeys() throws Exception {
    for (String f : List.of("v1/acik-jwks.json", "v1.3/acik-jwks.json"))
      for (JsonNode k : M.readTree(Path.of("/anahtarlar/" + f).toFile()).get("keys")) KID.put(k.get("kid").asText(), k);
    for (String f : List.of("v1/roller.json", "v1.3/roller.json")) {
      var it = M.readTree(Path.of("/anahtarlar/" + f).toFile()).get("roller").fields();
      while (it.hasNext()) { var e = it.next(); if (e.getKey().startsWith("issuer/")) ALG2KID.putIfAbsent(e.getValue().get("tur").asText(), e.getValue().get("kid").asText()); }
    }
  }

  static JsonNode hdr(String c) throws Exception { return M.readTree(b64d(c.split("\\.")[0])); }
  static String iss(String c) { try { var p = M.readTree(b64d(c.split("\\.")[1])); return p.has("iss") ? p.get("iss").asText() : ""; } catch (Exception e) { return ""; } }
  static JsonNode jwkFor(JsonNode h) {
    if (h.has("kid") && KID.containsKey(h.get("kid").asText())) return KID.get(h.get("kid").asText());
    String a = h.has("alg") ? h.get("alg").asText() : "";
    String k = ALG2KID.getOrDefault(a, "EdDSA".equals(a) ? ALG2KID.get("Ed25519") : null);
    return k == null ? null : KID.get(k);
  }
  static PublicKey pub(JsonNode j) throws Exception {
    if (j == null) throw new GeneralSecurityException("no key for kid/alg");
    String kty = j.get("kty").asText();
    if ("EC".equals(kty)) {
      AlgorithmParameters p = AlgorithmParameters.getInstance("EC");
      p.init(new ECGenParameterSpec("P-384".equals(j.get("crv").asText()) ? "secp384r1" : "secp256r1"));
      ECParameterSpec spec = p.getParameterSpec(ECParameterSpec.class);
      return KeyFactory.getInstance("EC").generatePublic(new ECPublicKeySpec(new ECPoint(new BigInteger(1, b64d(j.get("x").asText())), new BigInteger(1, b64d(j.get("y").asText()))), spec));
    }
    if ("OKP".equals(kty) && "Ed25519".equals(j.get("crv").asText())) {
      byte[] x = b64d(j.get("x").asText()), pre = HexFormat.of().parseHex("302a300506032b6570032100");
      byte[] spki = new byte[pre.length + x.length]; System.arraycopy(pre, 0, spki, 0, pre.length); System.arraycopy(x, 0, spki, pre.length, x.length);
      return KeyFactory.getInstance("Ed25519").generatePublic(new X509EncodedKeySpec(spki));
    }
    throw new GeneralSecurityException("unsupported key type " + kty + " " + j.path("alg").asText());
  }
  static List<String> allowed(String pol, String X, String iss, List<String> sup) {
    // Yapılandırma adı: `|sdjwtvc=…` ve `@-19` ekleri yalnız oracle beklentisini böler (oracle-B YONTEM §2).
    pol = pol.split("[|]")[0].split("@")[0];
    switch (pol) {
      case "GEC", "GEC@-19", "P0", "P1": return sup;
      case "IZIN-A": return List.of(A);
      case "IZIN-AX": return List.of(A, X);
      case "L4", "L4-S", "L4-Y", "L4@-19", "L4-YOL": return LEGACY.equals(iss) ? List.of(A, X) : List.of(X);
      default: return sup;
    }
  }
  static String klass(Throwable e) {
    String m = (e.getClass().getSimpleName() + " " + e.getMessage()).toLowerCase();
    String[][] t = {{"signature does not match", "imza-gecersiz"}, {"signature resulted invalid", "imza-gecersiz"}, {"invalid signature", "imza-gecersiz"},
        {"another algorithm expected", "alg-izin-disi"}, {"algorithmmismatch", "alg-izin-disi"}, {"not allowed", "alg-izin-disi"}, {"unsupported", "alg-desteklenmiyor"}, {"unsupportedjwt", "alg-desteklenmiyor"},
        {"not supported", "alg-desteklenmiyor"}, {"unknown", "alg-desteklenmiyor"}, {"invalidkey", "alg-anahtar-uyusmazligi"}, {"does not match", "alg-anahtar-uyusmazligi"},
        {"signature", "imza-gecersiz"}, {"no key", "anahtar-bulunamadi"}, {"expired", "zaman"}, {"malformed", "ayristirma"}, {"parse", "ayristirma"}};
    for (String[] p : t) if (m.contains(p[0])) return p[1];
    return "istisna-diger";
  }

  interface T { String ver(); String api(); Set<String> formats(); Object verify(JsonNode job, String data, String X) throws Exception; }

  // ---------- auth0 java-jwt: bir Verifier = bir Algorithm (anahtar–alg bağlaması yapısal) ----------
  static class JavaJwt implements T {
    static final List<String> SUP = List.of("ES256", "ES384", "ES512", "RS256", "PS256");
    public String ver() { return "4.6.1"; }
    public String api() { return "JWT.require(Algorithm.ECDSA256(pub)).build().verify(token)"; }
    public Set<String> formats() { return Set.of("compact"); }
    public Object verify(JsonNode job, String data, String X) throws Exception {
      String tok = data.trim(); JsonNode h = hdr(tok); String alg = h.path("alg").asText();
      List<String> W = allowed(job.get("politika").asText(), X, iss(tok), SUP);
      // Uygulama beklenen algoritmanın Verifier'ını kurar; başlıktaki alg W dışındaysa W'nin ilk algoritmasıyla kurulan
      // Verifier kütüphanenin AlgorithmMismatchException'ını üretir.
      String use = W.contains(alg) ? alg : W.get(0);
      PublicKey pk = pub(W.contains(alg) ? jwkFor(h) : (KID.get(ALG2KID.get(use)) != null ? KID.get(ALG2KID.get(use)) : jwkFor(h)));
      com.auth0.jwt.algorithms.Algorithm a = switch (use) {
        case "ES256" -> com.auth0.jwt.algorithms.Algorithm.ECDSA256((ECPublicKey) pk, null);
        case "ES384" -> com.auth0.jwt.algorithms.Algorithm.ECDSA384((ECPublicKey) pk, null);
        default -> throw new GeneralSecurityException("unsupported algorithm " + use);
      };
      com.auth0.jwt.JWT.require(a).acceptLeeway(Long.MAX_VALUE / 2000).build().verify(tok);
      return List.of(Map.of("sira", 0, "alg", alg, "sonuc", "gecerli"));
    }
  }

  // ---------- jjwt: parser başına algoritma kayıt defteri (sig().remove) ----------
  static class Jjwt implements T {
    public String ver() { return "0.13.0"; }
    public String api() { return "Jwts.parser().sig().remove(alg∉W).and().keyLocator(…).build().parseSignedClaims(token)"; }
    public Set<String> formats() { return Set.of("compact"); }
    public Object verify(JsonNode job, String data, String X) throws Exception {
      String tok = data.trim(); JsonNode h = hdr(tok);
      var reg = io.jsonwebtoken.Jwts.SIG.get();
      List<String> sup = new ArrayList<>(); for (var a : reg.values()) if (!a.getId().startsWith("HS")) sup.add(a.getId());
      List<String> W = allowed(job.get("politika").asText(), X, iss(tok), sup);
      var b = io.jsonwebtoken.Jwts.parser();
      var sig = b.sig();
      for (var a : reg.values()) if (!W.contains(a.getId())) sig.remove(a);
      b = sig.and();
      b.keyLocator(new io.jsonwebtoken.LocatorAdapter<Key>() {
        @Override protected Key locate(io.jsonwebtoken.ProtectedHeader ph) {
          try { ObjectNode hh = M.createObjectNode(); if (ph.getKeyId() != null) hh.put("kid", ph.getKeyId()); hh.put("alg", ph.getAlgorithm()); return pub(jwkFor(hh)); }
          catch (Exception e) { throw new io.jsonwebtoken.security.InvalidKeyException("no key: " + e.getMessage()); }
        }
      });
      b.unsecured(); // 'none' yalnız kayıt defteri izin verirse; varsayılan kayıt 'none' içermez
      b.clockSkewSeconds(Long.MAX_VALUE / 2000);
      var p = b.build();
      p.parseSignedClaims(tok);
      return List.of(Map.of("sira", 0, "alg", h.path("alg").asText(), "sonuc", "gecerli"));
    }
  }

  // ---------- authlete sd-jwt (ayrıştırma) + Nimbus (belgeli imza yolu) ----------
  static class Authlete implements T {
    public String ver() { return "1.9 (+nimbus-jose-jwt 10.10)"; }
    public String api() { return "com.authlete.sd.SDJWT.parse(s).getCredentialJwt() → Nimbus DefaultJWTProcessor + JWSVerificationKeySelector(W)"; }
    public Set<String> formats() { return Set.of("sd-jwt-compact", "compact-as-sdjwt"); }
    public Object verify(JsonNode job, String data, String X) throws Exception {
      String s = data.trim(); if ("compact".equals(job.get("serilestirme").asText())) s = s + "~";
      com.authlete.sd.SDJWT sd = com.authlete.sd.SDJWT.parse(s);
      String cred = sd.getCredentialJwt();
      JsonNode h = hdr(cred);
      List<String> sup = new ArrayList<>(); for (var a : com.nimbusds.jose.JWSAlgorithm.Family.SIGNATURE) sup.add(a.getName());
      sup.add("EdDSA"); sup.add("Ed25519");
      List<String> W = allowed(job.get("politika").asText(), X, iss(cred), sup);
      Set<com.nimbusds.jose.JWSAlgorithm> ws = new HashSet<>(); for (String a : W) ws.add(com.nimbusds.jose.JWSAlgorithm.parse(a));
      var jwk = jwkFor(h); if (jwk == null) throw new GeneralSecurityException("no key for kid/alg");
      var njwk = com.nimbusds.jose.jwk.JWK.parse(M.writeValueAsString(jwk));
      var src = new com.nimbusds.jose.jwk.source.ImmutableJWKSet<com.nimbusds.jose.proc.SecurityContext>(new com.nimbusds.jose.jwk.JWKSet(njwk));
      var proc = new com.nimbusds.jwt.proc.DefaultJWTProcessor<com.nimbusds.jose.proc.SecurityContext>();
      proc.setJWSTypeVerifier((t, c) -> {});
      proc.setJWSKeySelector(new com.nimbusds.jose.proc.JWSVerificationKeySelector<>(ws, src));
      proc.setJWTClaimsSetVerifier((cl, c) -> {});
      proc.process(cred, null);
      return List.of(Map.of("sira", 0, "alg", h.path("alg").asText(), "sonuc", "gecerli"));
    }
  }

  public static void main(String[] a) throws Exception {
    String hid = a[0], isler = a[1], cikti = a[2], kosu = a[3];
    loadKeys();
    T t = switch (hid) { case "JOSE-052" -> new JavaJwt(); case "JOSE-055" -> new Jjwt(); case "SDJWT-004" -> new Authlete(); default -> throw new IllegalArgumentException(hid); };
    String asha = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(Path.of("/a/Main.java"))));
    try (var out = Files.newBufferedWriter(Path.of(cikti), StandardCharsets.UTF_8)) {
      for (String line : Files.readAllLines(Path.of(isler), StandardCharsets.UTF_8)) {
        if (line.isBlank()) continue;
        JsonNode job = M.readTree(line); String X = X_OF.getOrDefault(job.get("kol").asText(), "EdDSA");
        ObjectNode r = M.createObjectNode();
        r.put("hedef_id", hid); r.put("hedef_surum", t.ver()); r.put("adaptor_sha256", asha); r.put("kosu", kosu);
        r.put("vektor_id", job.get("vektor_id").asText()); r.put("politika", job.get("politika").asText()); r.put("kol", job.get("kol").asText());
        r.putNull("sonuc_ham"); r.putNull("hata_sinifi"); r.putNull("hata_ozeti"); r.putArray("dogrulanan_algoritmalar"); r.put("api_yolu", t.api());
        String ser = job.get("serilestirme").asText();
        String eff = ("compact".equals(ser) && t.formats().contains("compact-as-sdjwt")) ? "compact-as-sdjwt" : ser;
        if (!t.formats().contains(eff)) { r.put("sonuc_ham", "uygulanamaz"); r.put("hata_sinifi", "bicim-desteklenmiyor"); out.write(r + "\n"); continue; }
        String data = Files.readString(Path.of("/v/" + job.get("dosya").asText()));
        long t0 = System.nanoTime();
        try { Object res = t.verify(job, data, X); r.put("sonuc_ham", "kabul"); r.set("dogrulanan_algoritmalar", M.valueToTree(res)); }
        catch (Throwable e) { r.put("sonuc_ham", "red"); r.put("hata_sinifi", klass(e)); String m = e.getClass().getSimpleName() + ": " + e.getMessage(); r.put("hata_ozeti", m.length() > 200 ? m.substring(0, 200) : m); }
        r.put("sure_ms", (System.nanoTime() - t0) / 1e6);
        out.write(r + "\n");
      }
    }
  }
}
