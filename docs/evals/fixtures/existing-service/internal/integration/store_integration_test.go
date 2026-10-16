package integration

import (
	"context"
	"database/sql"
	"os"
	"testing"

	"github.com/acme/orders/internal/store"
)

// Integration tests in this project are selected by TEST_DATABASE_URL, not by a
// build tag: the whole package is excluded from the unit job by CI configuration,
// and each test skips itself when the variable is missing so a local
// `go test ./...` still passes without a database.
func openTestDatabase(t *testing.T) *sql.DB {
	t.Helper()

	dsn := os.Getenv("TEST_DATABASE_URL")
	if dsn == "" {
		t.Skip("TEST_DATABASE_URL is not set")
	}

	db, err := sql.Open("postgres", dsn)
	if err != nil {
		t.Fatalf("open database: %v", err)
	}
	t.Cleanup(func() { _ = db.Close() })
	return db
}

func TestOrderStoreCreateAndGet(t *testing.T) {
	db := openTestDatabase(t)
	orders := store.NewOrderStore(db)
	ctx := context.Background()

	if _, err := db.ExecContext(ctx, `DELETE FROM orders WHERE id = $1`, "test-order"); err != nil {
		t.Fatalf("clean fixture row: %v", err)
	}

	if err := orders.Create(ctx, store.Order{ID: "test-order", UserID: "user-1", Status: "pending"}); err != nil {
		t.Fatalf("create: %v", err)
	}

	got, err := orders.GetByID(ctx, "test-order")
	if err != nil {
		t.Fatalf("get: %v", err)
	}
	if got.UserID != "user-1" {
		t.Fatalf("user id = %q, want user-1", got.UserID)
	}
}
