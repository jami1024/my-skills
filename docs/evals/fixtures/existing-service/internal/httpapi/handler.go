package httpapi

import (
	"context"
	"encoding/json"
	"errors"
	"net/http"

	"github.com/acme/orders/internal/store"
)

// orderReader is the only dependency the handlers need.
type orderReader interface {
	GetByID(ctx context.Context, id string) (store.Order, error)
}

// RegisterOrderRoutes wires order routes onto the mux.
func RegisterOrderRoutes(mux *http.ServeMux, orders orderReader) {
	mux.HandleFunc("GET /orders/{id}", func(w http.ResponseWriter, r *http.Request) {
		order, err := orders.GetByID(r.Context(), r.PathValue("id"))
		if errors.Is(err, store.ErrNotFound) {
			http.Error(w, `{"error":"not found"}`, http.StatusNotFound)
			return
		}
		if err != nil {
			http.Error(w, `{"error":"internal"}`, http.StatusInternalServerError)
			return
		}
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(order)
	})
}
