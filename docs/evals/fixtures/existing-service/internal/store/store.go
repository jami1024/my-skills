package store

import (
	"context"
	"database/sql"
	"errors"
	"fmt"
)

// ErrNotFound is returned when a row does not exist.
var ErrNotFound = errors.New("order not found")

// Order is an order row.
type Order struct {
	ID     string `json:"id"`
	UserID string `json:"user_id"`
	Status string `json:"status"`
}

// OrderStore reads and writes orders. It is the only type that touches the database.
type OrderStore struct {
	db *sql.DB
}

// NewOrderStore wires the store to an open database handle.
func NewOrderStore(db *sql.DB) *OrderStore {
	return &OrderStore{db: db}
}

// GetByID returns one order or ErrNotFound.
func (s *OrderStore) GetByID(ctx context.Context, id string) (Order, error) {
	var order Order
	err := s.db.QueryRowContext(ctx,
		`SELECT id, user_id, status FROM orders WHERE id = $1`, id,
	).Scan(&order.ID, &order.UserID, &order.Status)
	if errors.Is(err, sql.ErrNoRows) {
		return Order{}, ErrNotFound
	}
	if err != nil {
		return Order{}, fmt.Errorf("get order %s: %w", id, err)
	}
	return order, nil
}

// Create inserts an order.
func (s *OrderStore) Create(ctx context.Context, order Order) error {
	_, err := s.db.ExecContext(ctx,
		`INSERT INTO orders (id, user_id, status) VALUES ($1, $2, $3)`,
		order.ID, order.UserID, order.Status,
	)
	if err != nil {
		return fmt.Errorf("create order %s: %w", order.ID, err)
	}
	return nil
}
