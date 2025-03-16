package main

import (
	"errors"
	"log"
	"net/http"
)

func main() {
	http.Handle("/", http.FileServer(http.Dir("./public")))
	log.Println("running on http://localhost:1313")
	err := http.ListenAndServe(":1313", nil)
	if err != nil && !errors.Is(err, http.ErrServerClosed) {
		log.Fatal(err)
	}
}
