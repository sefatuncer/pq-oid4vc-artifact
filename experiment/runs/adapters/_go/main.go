// C3 adapter (Go): JOSE-033 golang-jwt/jwt v5, JOSE-034 jose2go, COSE-034 veraison/go-cose.
// Contract: experiment/oracle/oracle-A/adapter-contract.md (1.0) + RUNNER.md. Does NOT see the oracle; only dogrulama_girdileri from the MANIFEST.
// Usage: /a/adaptor <hedef_id> <jobs-v1.3.jsonl> <cikti.jsonl> <kosu>
package main

import (
	"bufio"
	"crypto"
	"crypto/ecdsa"
	"crypto/ed25519"
	"crypto/elliptic"
	"crypto/sha256"
	"encoding/base64"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"math/big"
	"os"
	"runtime/debug"
	"strings"
	"time"

	jose "github.com/dvsekhvalnov/jose2go"
	gjwt "github.com/golang-jwt/jwt/v5"
	cose "github.com/veraison/go-cose"
)

const A = "ES256"
const LEGACY = "https://legacy-issuer.example"

var xOf = map[string]string{"kontrol-EdDSA": "EdDSA", "kontrol-Ed25519": "Ed25519", "kontrol-ES384": "ES384", "tedavi-ML-DSA-65": "ML-DSA-65", "tedavi-composite": "ML-DSA-65-ES256"}

type JWK map[string]any

var KID = map[string]JWK{}
var ALG2KID = map[string]string{}

func b64d(s string) []byte { b, _ := base64.RawURLEncoding.DecodeString(strings.TrimRight(s, "=")); return b }

func loadKeys() {
	for _, f := range []string{"v1/acik-jwks.json", "v1.3/acik-jwks.json"} {
		var j struct{ Keys []JWK `json:"keys"` }
		b, _ := os.ReadFile("/anahtarlar/" + f)
		json.Unmarshal(b, &j)
		for _, k := range j.Keys {
			KID[k["kid"].(string)] = k
		}
	}
	for _, f := range []string{"v1/roller.json", "v1.3/roller.json"} {
		var j struct{ Roller map[string]map[string]any `json:"roller"` }
		b, _ := os.ReadFile("/anahtarlar/" + f)
		json.Unmarshal(b, &j)
		for r, d := range j.Roller {
			if strings.HasPrefix(r, "issuer/") {
				t := d["tur"].(string)
				if _, ok := ALG2KID[t]; !ok {
					ALG2KID[t] = d["kid"].(string)
				}
			}
		}
	}
}

// Only Go's built-in types (EC P-256/384, Ed25519); AKP (ML-DSA) is not supported in these libraries.
func pubOf(j JWK) (crypto.PublicKey, error) {
	if j == nil {
		return nil, errors.New("no key for kid/alg")
	}
	switch j["kty"] {
	case "EC":
		c := elliptic.P256()
		if j["crv"] == "P-384" {
			c = elliptic.P384()
		}
		return &ecdsa.PublicKey{Curve: c, X: new(big.Int).SetBytes(b64d(j["x"].(string))), Y: new(big.Int).SetBytes(b64d(j["y"].(string)))}, nil
	case "OKP":
		if j["crv"] == "Ed25519" {
			return ed25519.PublicKey(b64d(j["x"].(string))), nil
		}
	}
	return nil, fmt.Errorf("unsupported key type %v %v", j["kty"], j["alg"])
}

func hdrOf(c string) map[string]any {
	var m map[string]any
	json.Unmarshal(b64d(strings.Split(c, ".")[0]), &m)
	return m
}
func issOf(c string) string {
	p := strings.Split(c, ".")
	if len(p) < 2 {
		return ""
	}
	var m map[string]any
	json.Unmarshal(b64d(p[1]), &m)
	s, _ := m["iss"].(string)
	return s
}
func jwkFor(h map[string]any) JWK {
	if k, ok := h["kid"].(string); ok {
		if j, ok := KID[k]; ok {
			return j
		}
	}
	a, _ := h["alg"].(string)
	if k, ok := ALG2KID[a]; ok {
		return KID[k]
	}
	if a == "EdDSA" {
		return KID[ALG2KID["Ed25519"]]
	}
	return nil
}

func allowed(pol, X, iss string, supported []string) []string {
	// Configuration name: the suffixes `|sdjwtvc=…` and `@-19` only split the oracle expectation (oracle-B METHOD §2).
	pol = strings.SplitN(strings.SplitN(pol, "|", 2)[0], "@", 2)[0]
	switch pol {
	case "GEC", "GEC@-19", "P0", "P1":
		return supported
	case "IZIN-A":
		return []string{A}
	case "IZIN-AX":
		return []string{A, X}
	case "L4", "L4-S", "L4-Y", "L4@-19", "L4-YOL":
		if iss == LEGACY {
			return []string{A, X}
		}
		return []string{X}
	}
	return supported
}
func in(s string, l []string) bool {
	for _, x := range l {
		if x == s {
			return true
		}
	}
	return false
}

func klass(e error) string {
	m := strings.ToLower(e.Error())
	for _, p := range [][2]string{{"not allowed", "alg-izin-disi"}, {"signing method", "alg-izin-disi"}, {"unknown algorithm", "alg-desteklenmiyor"},
		{"unavailable", "alg-desteklenmiyor"}, {"unsupported", "alg-desteklenmiyor"}, {"algorithm mismatch", "alg-anahtar-uyusmazligi"},
		{"key is of invalid type", "alg-anahtar-uyusmazligi"}, {"expects key", "alg-anahtar-uyusmazligi"}, {"verification", "imza-gecersiz"},
		{"signature", "imza-gecersiz"}, {"no key", "anahtar-bulunamadi"}, {"expired", "zaman"}, {"cbor", "ayristirma"}, {"malformed", "ayristirma"}} {
		if strings.Contains(m, p[0]) {
			return p[1]
		}
	}
	return "istisna-diger"
}

type Job struct {
	VektorID, Politika, Kol, Dosya, Serilestirme, Artefakt, Algler string
}

type Res struct {
	sonuc string
	algs  []map[string]any
}

type Target interface {
	ver() string
	api() string
	formats() map[string]bool
	verify(j Job, data []byte, X string) (Res, error)
}

// ---------------- golang-jwt v5 ----------------
type GJWT struct{}

var gjwtSupported = []string{"ES256", "ES384", "ES512", "EdDSA", "RS256", "PS256"}

func (GJWT) api() string              { return "jwt.Parse(token, keyFunc, jwt.WithValidMethods(W))" }
func (GJWT) formats() map[string]bool { return map[string]bool{"compact": true} }
func (GJWT) ver() string              { return depVer("github.com/golang-jwt/jwt/v5") }
func (GJWT) verify(j Job, data []byte, X string) (Res, error) {
	tok := strings.TrimSpace(string(data))
	W := allowed(j.Politika, X, issOf(tok), gjwtSupported)
	t, err := gjwt.Parse(tok, func(t *gjwt.Token) (any, error) { return pubOf(jwkFor(t.Header)) },
		gjwt.WithValidMethods(W), gjwt.WithTimeFunc(func() time.Time { return time.Unix(1790003700, 0) }))
	if err != nil {
		return Res{}, err
	}
	return Res{"kabul", []map[string]any{{"sira": 0, "alg": t.Method.Alg(), "sonuc": "gecerli"}}}, nil
}

// ---------------- jose2go ----------------
// The policy is expressed only with the global algorithm registry (RegisterJws/DeregisterJws; documented public API): L1.
type JOSE2GO struct{}

var j2gSupported = []string{"ES256", "ES384", "ES512", "RS256", "PS256"}

func (JOSE2GO) api() string { return "jose.DeregisterJws(alg) [genel kayıt] + jose.Decode(token, key)" }
func (JOSE2GO) formats() map[string]bool { return map[string]bool{"compact": true} }
func (JOSE2GO) ver() string { return depVer("github.com/dvsekhvalnov/jose2go") }
func (JOSE2GO) verify(j Job, data []byte, X string) (Res, error) {
	tok := strings.TrimSpace(string(data))
	h := hdrOf(tok)
	W := allowed(j.Politika, X, issOf(tok), j2gSupported)
	removed := []jose.JwsAlgorithm{}
	for _, a := range []string{"ES256", "ES384", "ES512", "RS256", "RS384", "RS512", "PS256", "PS384", "PS512", "HS256", "HS384", "HS512", "none"} {
		if !in(a, W) {
			if r := jose.DeregisterJws(a); r != nil {
				removed = append(removed, r)
			}
		}
	}
	defer func() {
		for _, r := range removed {
			jose.RegisterJws(r)
		}
	}()
	key, err := pubOf(jwkFor(h))
	if err != nil {
		return Res{}, err
	}
	if _, _, err := jose.Decode(tok, key); err != nil {
		return Res{}, err
	}
	return Res{"kabul", []map[string]any{{"sira": 0, "alg": h["alg"], "sonuc": "gecerli"}}}, nil
}

// ---------------- go-cose ----------------
type GOCOSE struct{}

var coseAlg = map[cose.Algorithm]string{cose.AlgorithmES256: "ES256", cose.AlgorithmES384: "ES384", cose.AlgorithmEdDSA: "EdDSA", cose.AlgorithmPS256: "PS256"}
var coseSupported = []string{"ES256", "ES384", "EdDSA", "PS256"}

func (GOCOSE) api() string { return "cose.Sign1Message/SignMessage .UnmarshalCBOR + .Verify(nil, cose.NewVerifier(alg, key)...)" }
func (GOCOSE) formats() map[string]bool { return map[string]bool{"COSE_Sign1": true, "COSE_Sign": true} }
func (GOCOSE) ver() string { return depVer("github.com/veraison/go-cose") }
func kidKey(kid []byte) JWK {
	return KID[base64.RawURLEncoding.EncodeToString(kid)]
}
func verifierFor(alg cose.Algorithm, kid []byte, W []string) (cose.Verifier, error) {
	name, ok := coseAlg[alg]
	if !ok {
		return nil, fmt.Errorf("unsupported algorithm %d", alg)
	}
	if !in(name, W) {
		return nil, fmt.Errorf("algorithm %s not allowed", name)
	}
	pk, err := pubOf(kidKey(kid))
	if err != nil {
		return nil, err
	}
	return cose.NewVerifier(alg, pk)
}
func (GOCOSE) verify(j Job, data []byte, X string) (Res, error) {
	iss := ""
	if strings.Contains(j.VektorID, "eski") {
		iss = LEGACY
	}
	W := allowed(j.Politika, X, iss, coseSupported)
	if j.Serilestirme == "COSE_Sign1" {
		var m cose.Sign1Message
		if err := m.UnmarshalCBOR(data); err != nil {
			return Res{}, err
		}
		alg, err := m.Headers.Protected.Algorithm()
		if err != nil {
			return Res{}, err
		}
		kid, _ := m.Headers.Unprotected[cose.HeaderLabelKeyID].([]byte)
		v, err := verifierFor(alg, kid, W)
		if err != nil {
			return Res{}, err
		}
		if err := m.Verify(nil, v); err != nil {
			return Res{}, err
		}
		return Res{"kabul", []map[string]any{{"sira": 0, "alg": coseAlg[alg], "sonuc": "gecerli"}}}, nil
	}
	// COSE_Sign: SignMessage.Verify verifies every signature with the positional verifier (all-present-valid).
	// "R={X} mandatory, A optional" (L4/L4-Y) and "X must be present" (L4-S) are not in the public API → ifade-edilemedi.
	if strings.HasPrefix(j.Politika, "L4") { // the forms with suffixes (L4|sdjwtvc=…, L4@-19) also belong to the L4 family
		return Res{"ifade-edilemedi", nil}, nil
	}
	var m cose.SignMessage
	if err := m.UnmarshalCBOR(data); err != nil {
		return Res{}, err
	}
	vs := []cose.Verifier{}
	algs := []map[string]any{}
	for i, s := range m.Signatures {
		alg, err := s.Headers.Protected.Algorithm()
		if err != nil {
			return Res{}, err
		}
		kid, _ := s.Headers.Unprotected[cose.HeaderLabelKeyID].([]byte)
		v, err := verifierFor(alg, kid, W)
		if err != nil {
			return Res{}, err
		}
		vs = append(vs, v)
		algs = append(algs, map[string]any{"sira": i, "alg": coseAlg[alg], "sonuc": "gecerli"})
	}
	if err := m.Verify(nil, vs...); err != nil {
		return Res{}, err
	}
	return Res{"kabul", algs}, nil
}

func depVer(p string) string {
	if bi, ok := debug.ReadBuildInfo(); ok {
		for _, d := range bi.Deps {
			if d.Path == p {
				return d.Version
			}
		}
	}
	return "?"
}

func main() {
	hid, isler, cikti, kosu := os.Args[1], os.Args[2], os.Args[3], os.Args[4]
	loadKeys()
	var t Target
	switch hid {
	case "JOSE-033":
		t = GJWT{}
	case "JOSE-034":
		t = JOSE2GO{}
	case "COSE-034":
		t = GOCOSE{}
	}
	self, _ := os.ReadFile("/a/main.go")
	asha := fmt.Sprintf("%x", sha256.Sum256(self))
	f, _ := os.Open(isler)
	defer f.Close()
	out, _ := os.Create(cikti)
	defer out.Close()
	sc := bufio.NewScanner(f)
	sc.Buffer(make([]byte, 1<<20), 1<<20)
	for sc.Scan() {
		var j Job
		var raw map[string]string
		json.Unmarshal(sc.Bytes(), &raw)
		j = Job{raw["vektor_id"], raw["politika"], raw["kol"], raw["dosya"], raw["serilestirme"], raw["artefakt"], raw["algler"]}
		X := xOf[j.Kol]
		if X == "" {
			X = "EdDSA"
		}
		rec := map[string]any{"hedef_id": hid, "hedef_surum": t.ver(), "adaptor_sha256": asha, "kosu": kosu, "vektor_id": j.VektorID,
			"politika": j.Politika, "kol": j.Kol, "sonuc_ham": nil, "hata_sinifi": nil, "hata_ozeti": nil,
			"dogrulanan_algoritmalar": []any{}, "api_yolu": t.api(), "sure_ms": nil}
		if !t.formats()[j.Serilestirme] {
			rec["sonuc_ham"], rec["hata_sinifi"] = "uygulanamaz", "bicim-desteklenmiyor"
		} else {
			data, _ := os.ReadFile("/v/" + j.Dosya)
			t0 := time.Now()
			func() {
				defer func() {
					if r := recover(); r != nil {
						rec["sonuc_ham"], rec["hata_sinifi"], rec["hata_ozeti"] = "cokme", "cokme", fmt.Sprint(r)
					}
				}()
				r, err := t.verify(j, data, X)
				if err != nil {
					s := err.Error()
					if len(s) > 200 {
						s = s[:200]
					}
					rec["sonuc_ham"], rec["hata_sinifi"], rec["hata_ozeti"] = "red", klass(err), s
				} else if r.sonuc == "ifade-edilemedi" {
					rec["sonuc_ham"] = "ifade-edilemedi"
				} else {
					rec["sonuc_ham"], rec["dogrulanan_algoritmalar"] = "kabul", r.algs
				}
			}()
			rec["sure_ms"] = float64(time.Since(t0).Microseconds()) / 1000
		}
		b, _ := json.Marshal(rec)
		out.Write(append(b, '\n'))
	}
	_ = hex.EncodeToString
}
