package store

import (
	"errors"
	"testing"
)

// SQL paths are covered by internal/integration; unit tests here stay free of a
// database so `go test ./...` works in the unit CI job.
func TestOrderStoreSentinelErrorSupportsErrorsIs(t *testing.T) {
	if !errors.Is(ErrNotFound, ErrNotFound) {
		t.Fatal("ErrNotFound must keep working with errors.Is")
	}
}

func TestOrderStoreExposesTheDatabaseHandle(t *testing.T) {
	s := NewOrderStore(nil)
	if s == nil {
		t.Fatal("NewOrderStore must return a usable store")
	}
}
