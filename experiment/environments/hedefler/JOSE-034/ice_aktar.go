// Link check: NO function is called.
package main

import (
	"fmt"

	jose "github.com/dvsekhvalnov/jose2go"
)

func main() {
	fmt.Println("paket github.com/dvsekhvalnov/jose2go baglandi")
	fmt.Printf("sembol Decode %T\n", jose.Decode)
	fmt.Printf("sembol RegisterJws %T\n", jose.RegisterJws)
}
