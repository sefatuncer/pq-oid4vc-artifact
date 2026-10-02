// Evidence-rule second attempt, COSE-034 (go-cose v1.3.0).
// Own keys and objects only. A = ES256, X = EdDSA.
package main

import (
	"crypto/ecdsa"
	"crypto/ed25519"
	"crypto/elliptic"
	"crypto/rand"
	_ "crypto/sha256" // required by go-cose for ES256 (README L165)
	"fmt"


	"github.com/veraison/go-cose"
)

var ok, n int

func report(label string, err error, expect string) {
	res := "accept"
	detail := ""
	if err != nil {
		res = "reject"
		detail = err.Error()
		if len(detail) > 80 {
			detail = detail[:80]
		}
	}
	mark := "-"
	if expect != "" {
		n++
		if res == expect {
			ok++
			mark = "OK"
		} else {
			mark = "MISMATCH"
		}
	} else {
		expect = "-"
	}
	fmt.Printf("%-56s %-7s expect=%-7s %-9s %s\n", label, res, expect, mark, detail)
}

func must(err error) {
	if err != nil {
		panic(err)
	}
}

func signature(alg cose.Algorithm, kid string) *cose.Signature {
	s := cose.NewSignature()
	s.Headers.Protected.SetAlgorithm(alg)
	s.Headers.Unprotected[cose.HeaderLabelKeyID] = []byte(kid)
	return s
}

func decode(b []byte) *cose.SignMessage {
	var m cose.SignMessage
	must(m.UnmarshalCBOR(b))
	return &m
}

func sign1(signer cose.Signer, alg cose.Algorithm, kid, iss string) *cose.Sign1Message {
	m := cose.NewSign1Message()
	m.Headers.Protected.SetAlgorithm(alg)
	m.Headers.Unprotected[cose.HeaderLabelKeyID] = []byte(kid)
	m.Payload = []byte(`{"iss":"` + iss + `","sub":"user-1"}`)
	must(m.Sign(rand.Reader, nil, signer))
	return m
}

func main() {
	fmt.Println("== go-cose v1.3.0 (module pinned in go.mod/go.sum)")
	migES, _ := ecdsa.GenerateKey(elliptic.P256(), rand.Reader)
	migXpub, migXpriv, _ := ed25519.GenerateKey(rand.Reader)
	legES, _ := ecdsa.GenerateKey(elliptic.P256(), rand.Reader)

	sMigES, _ := cose.NewSigner(cose.AlgorithmES256, migES)
	sMigX, _ := cose.NewSigner(cose.AlgorithmEdDSA, migXpriv)
	sLegES, _ := cose.NewSigner(cose.AlgorithmES256, legES)
	vMigES, _ := cose.NewVerifier(cose.AlgorithmES256, &migES.PublicKey)
	vMigX, _ := cose.NewVerifier(cose.AlgorithmEdDSA, migXpub)
	vLegES, _ := cose.NewVerifier(cose.AlgorithmES256, &legES.PublicKey)

	// ------------------------------------------------------------ objects
	t1 := cose.NewSignMessage()
	t1.Payload = []byte(`{"iss":"https://issuer.example","sub":"user-1"}`)
	t1.Signatures = []*cose.Signature{signature(cose.AlgorithmES256, "mig-es256"), signature(cose.AlgorithmEdDSA, "mig-eddsa")}
	must(t1.Sign(rand.Reader, nil, sMigES, sMigX))
	T1b, _ := t1.MarshalCBOR()

	t2 := decode(T1b)
	t2.Signatures[1].Signature[3] ^= 0x01 // corrupt the X signature
	T2b, _ := t2.MarshalCBOR()

	t3 := decode(T1b)
	t3.Signatures = t3.Signatures[:1] // stripped to ES256
	T3b, _ := t3.MarshalCBOR()

	t5 := decode(T1b)
	t5.Signatures = t5.Signatures[1:] // only X
	T5b, _ := t5.MarshalCBOR()

	t1p := decode(T1b) // permutation of T1 (X first)
	t1p.Signatures = []*cose.Signature{t1p.Signatures[1], t1p.Signatures[0]}
	T1pb, _ := t1p.MarshalCBOR()

	fmt.Println("\n== 1. Validity check")
	report("V+ T1 both valid, Verify(nil, vES256, vX)", decode(T1b).Verify(nil, vMigES, vMigX), "accept")
	report("V- T2 X corrupted, Verify(nil, vES256, vX)", decode(T2b).Verify(nil, vMigES, vMigX), "reject")
	s1MigES := sign1(sMigES, cose.AlgorithmES256, "mig-es256", "https://issuer.example")
	s1MigX := sign1(sMigX, cose.AlgorithmEdDSA, "mig-eddsa", "https://issuer.example")
	s1LegES := sign1(sLegES, cose.AlgorithmES256, "leg-es256", "https://legacy-issuer.example")
	report("V+ Sign1 migrated ES256", s1MigES.Verify(nil, vMigES), "accept")
	report("V+ Sign1 migrated EdDSA", s1MigX.Verify(nil, vMigX), "accept")
	report("V+ Sign1 legacy ES256", s1LegES.Verify(nil, vLegES), "accept")

	fmt.Println("\n== 2. L4m (primary form), R = {EdDSA}, W = {ES256, EdDSA}: static configurations of SignMessage.Verify")
	type cfg struct {
		name string
		vs   []cose.Verifier
	}
	for _, c := range []cfg{{"verifiers = W in order [vES256, vX]", []cose.Verifier{vMigES, vMigX}},
		{"verifiers = R [vX]", []cose.Verifier{vMigX}},
		{"verifiers = [vX, vES256]", []cose.Verifier{vMigX, vMigES}}} {
		fmt.Println("configuration:", c.name)
		report("  T1 both valid", decode(T1b).Verify(nil, c.vs...), "accept")
		report("  T2 X corrupted", decode(T2b).Verify(nil, c.vs...), "reject")
		report("  T3 stripped to ES256", decode(T3b).Verify(nil, c.vs...), "reject")
		report("  T5 only X", decode(T5b).Verify(nil, c.vs...), "accept")
		report("  T1 permuted (X first)", decode(T1pb).Verify(nil, c.vs...), "accept")
	}
	fmt.Println("-> no static verifier list gives T1/T5 accept and T3 reject: Verify needs exactly one verifier per signature, in order.")

	fmt.Println("\n== 3. L4m with own code (B4 record only): loop over signatures with Signature.Verify")
	l4m := func(b []byte) error { // BEGIN custom
		m := decode(b)
		prot, err := m.Headers.MarshalProtected()
		if err != nil {
			return err
		}
		required := map[cose.Algorithm]cose.Verifier{cose.AlgorithmEdDSA: vMigX}
		seen := map[cose.Algorithm]bool{}
		for _, s := range m.Signatures {
			alg, err := s.Headers.Protected.Algorithm()
			if err != nil {
				return err
			}
			if v, isReq := required[alg]; isReq {
				if err := s.Verify(v, prot, m.Payload, nil); err != nil {
					return err
				}
				seen[alg] = true
			}
		}
		for alg := range required {
			if !seen[alg] {
				return fmt.Errorf("required algorithm %v missing", alg)
			}
		}
		return nil
	} // END custom
	report("  T1 both valid", l4m(T1b), "")
	report("  T2 X corrupted", l4m(T2b), "")
	report("  T3 stripped to ES256", l4m(T3b), "")
	report("  T5 only X", l4m(T5b), "")
	report("  T1 permuted", l4m(T1pb), "")

	fmt.Println("\n== 4. L4c (supplement): COSE_Sign1, per-issuer records = verifier objects (alg bound to key)")
	fmt.Println("records: migrated = {vX}, legacy = {vLegES256}")
	report("  migrated ES256 with migrated record", s1MigES.Verify(nil, vMigX), "reject")
	report("  migrated EdDSA with migrated record", s1MigX.Verify(nil, vMigX), "accept")
	report("  legacy ES256 with legacy record", s1LegES.Verify(nil, vLegES), "accept")
	fmt.Println("records: migrated record also holds its ES256 key = {vES256, vX}")
	report("  migrated ES256 with vES256 of migrated record", s1MigES.Verify(nil, vMigES), "")
	fmt.Println("-> Sign1Message.Verify takes one verifier; the record can only refuse ES256 if the ES256 key is left out.")

	fmt.Printf("\n== SUMMARY: checked rows OK = %d of %d\n", ok, n)
}
