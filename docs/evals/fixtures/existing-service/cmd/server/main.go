package main

import (
	"database/sql"
	"log/slog"
	"net/http"
	"os"

	"github.com/acme/orders/internal/httpapi"
	"github.com/acme/orders/internal/store"
)

func main() {
	dsn := os.Getenv("DATABASE_URL")
	if dsn == "" {
		slog.Error("DATABASE_URL is required")
		os.Exit(1)
	}

	db, err := sql.Open("postgres", dsn)
	if err != nil {
		slog.Error("open database", "err", err)
		os.Exit(1)
	}
	defer db.Close()

	orders := store.NewOrderStore(db)

	mux := http.NewServeMux()
	httpapi.RegisterOrderRoutes(mux, orders)

	slog.Info("listening", "addr", ":8080")
	if err := http.ListenAndServe(":8080", mux); err != nil {
		slog.Error("serve", "err", err)
		os.Exit(1)
	}
}
