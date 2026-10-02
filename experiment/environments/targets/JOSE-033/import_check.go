// Link check: the verification API symbols are linked into the binary; NO function is called.
package main

import (
	"fmt"

	jwt "github.com/golang-jwt/jwt/v5"
)

func main() {
	fmt.Println("paket github.com/golang-jwt/jwt/v5 baglandi")
	fmt.Printf("sembol ParseWithClaims %T\n", jwt.ParseWithClaims)
	fmt.Printf("sembol RegisterSigningMethod %T\n", jwt.RegisterSigningMethod)
}
