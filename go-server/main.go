package main

import (
	"bytes"
	"fmt"
	"io"
	"log/slog"
	"net/http"
	"os"
)

func testHandlerFunc() http.HandlerFunc {
	const responseBodyString = "hello world"

	responseBodyBytes := []byte(responseBodyString)

	return func(w http.ResponseWriter, r *http.Request) {

		io.Copy(w, bytes.NewReader(responseBodyBytes))
	}
}

func runHTTPServer() {
	const addr = ":8080"

	mux := http.NewServeMux()

	mux.Handle("GET /test", testHandlerFunc())

	slog.Info("starting server",
		"addr", addr,
	)

	httpServer := http.Server{
		Addr:    addr,
		Handler: mux,
	}

	err := httpServer.ListenAndServe()

	slog.Error("httpServer.ListenAndServe error",
		"error", err,
	)
}

func main() {
	setupSlog()

	runHTTPServer()
}

func setupSlog() {
	level := slog.LevelInfo

	if levelString, ok := os.LookupEnv("LOG_LEVEL"); ok {
		err := level.UnmarshalText([]byte(levelString))
		if err != nil {
			panic(fmt.Errorf("level.UnmarshalText error %w", err))
		}
	}

	slog.SetDefault(
		slog.New(
			slog.NewJSONHandler(
				os.Stdout,
				&slog.HandlerOptions{
					Level: level,
				},
			),
		),
	)

	slog.Info("setupSlog",
		"configuredLevel", level,
	)
}
