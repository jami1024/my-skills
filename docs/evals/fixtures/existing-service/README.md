# orders

Order service. One module, one executable.

## Layout

```text
cmd/server/main.go          entry point: read config, build the store, start the server
internal/httpapi/           HTTP handlers, one file per resource
internal/store/             PostgreSQL access; the only place that talks to the database
internal/integration/       tests that need a real database
migrations/0001_init.sql    orders table
```

This is a sample checkout used by the repository's evals. It deliberately has no module
dependencies — the real service blank-imports the PostgreSQL driver in `internal/store` — so
the sample stays readable and buildable without network access.

Wiring is explicit: `main` constructs the store with `*sql.DB` and passes it to the handler.
There is no service or repository layer — queries live in `internal/store` and handlers call it.

## Tests

Unit tests need nothing but Go:

```bash
go test ./...
```

Integration tests are selected by an environment variable and skip themselves when it is unset:

```bash
TEST_DATABASE_URL='postgres://localhost:5432/orders?sslmode=disable' go test ./internal/integration/...
```

CI sets `TEST_DATABASE_URL` in the integration job and runs `go test ./...` in the unit job.
