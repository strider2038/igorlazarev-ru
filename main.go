package main

import (
	"errors"
	"log"
	"net/http"
)

func main() {
	http.Handle("/", http.FileServer(http.Dir("./public")))
	log.Println("running on http://localhost:8080")
	err := http.ListenAndServe(":8080", nil)
	if err != nil && !errors.Is(err, http.ErrServerClosed) {
		log.Fatal(err)
	}
}
