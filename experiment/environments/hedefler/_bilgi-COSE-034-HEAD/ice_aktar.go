// Link check: NO function is called.
package main

import (
	"fmt"

	cose "github.com/veraison/go-cose"
)

func main() {
	fmt.Println("paket github.com/veraison/go-cose baglandi")
	fmt.Printf("sembol NewVerifier %T\n", cose.NewVerifier)
	var s1 *cose.Sign1Message
	var sm *cose.SignMessage
	fmt.Printf("tip %T %T\n", s1, sm)
}
