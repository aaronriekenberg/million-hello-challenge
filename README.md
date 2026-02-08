# million-hello-challenge

Benchmarking the performance of Rust, Go, Kotlin, Node.js, and Python HTTP APIs using one million Hello World requests in GitHub Actions.

Consider this an upper bound on the performance of each language/framework, adding more code will make things slower.

# Latest results:
* [raw.md](https://github.com/aaronriekenberg/million-hello-challenge/blob/main/results/raw.md)

# API Servers in this repo:
* [rust-api](https://github.com/aaronriekenberg/million-hello-challenge/tree/main/rust-api) using [axum](https://github.com/tokio-rs/axum)
* [go-api](https://github.com/aaronriekenberg/million-hello-challenge/tree/main/go-api) using builtin `net/http`
* [kotlin-api](https://github.com/aaronriekenberg/million-hello-challenge/tree/main/kotlin-api) using [http4k](https://www.http4k.org) with [Helidon](https://helidon.io) server using virutal threads, Java 25.
* [node-api](https://github.com/aaronriekenberg/million-hello-challenge/tree/main/node-api) using builtin `node:http` server.
* [python-api](https://github.com/aaronriekenberg/million-hello-challenge/tree/main/python-api) using [tornado](https://www.tornadoweb.org/en/stable/) server, using [pre-forking](https://www.tornadoweb.org/en/stable/process.html#tornado.process.fork_processes) to use all available CPUs.

# Test Setup:
* Use [oha](https://crates.io/crates/oha) test tool to make 1 million HTTP requests
* Using HTTP 1.1 with varying number of connections.
* At oha client measure:
  * Success rate
  * Test duration
  * Requsts per Second (RPS)
  * Response time (P50, P99, P99.9 milliseconds)
* At API server measure:
  * Total resident (RSS) memory usage
  * Total CPU time
  * Total threads created
  * Total processes created
