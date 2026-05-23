# million-hello-challenge

Benchmarking 1 million HTTP “Hello World” requests across nginx, Rust, Go, Kotlin, Node.js, and Python servers in GitHub Actions.

Consider this an upper bound on the performance of each language/framework, adding more code will make things slower.

# Latest results:
* [Formatted](https://aaronriekenberg.github.io/million-hello-challenge/)
* [Raw](https://github.com/aaronriekenberg/million-hello-challenge/blob/main/results/raw.md)

# Servers in this repo:
* [rust-server](https://github.com/aaronriekenberg/million-hello-challenge/tree/main/rust-server) using [axum](https://github.com/tokio-rs/axum)
* [go-server](https://github.com/aaronriekenberg/million-hello-challenge/tree/main/go-server) using builtin `net/http`
* [kotlin-server](https://github.com/aaronriekenberg/million-hello-challenge/tree/main/kotlin-server) using [http4k](https://www.http4k.org) with [Helidon](https://helidon.io) server using virtual threads, Java 25.
* [node-server](https://github.com/aaronriekenberg/million-hello-challenge/tree/main/node-server) using builtin `node:http` server.
* [python-server](https://github.com/aaronriekenberg/million-hello-challenge/tree/main/python-server) using [tornado](https://www.tornadoweb.org/en/stable/) server, using [pre-forking](https://www.tornadoweb.org/en/stable/process.html#tornado.process.fork_processes) to use all available CPUs.
* [nginx-server](https://github.com/aaronriekenberg/million-hello-challenge/tree/main/nginx-server) using [nginx](https://nginx.org).

# Test Setup:
* Use [oha](https://crates.io/crates/oha) test tool to make 1 million HTTP requests
* Using HTTP 1.1 with varying number of connections.
* At oha client measure:
  * Success rate
  * Test duration
  * Requsts per Second (RPS)
  * Response time (P50, P99, P99.9 milliseconds)
* At server measure:
  * Total resident (RSS) memory usage
  * Total CPU time
  * Total threads created
  * Total processes created
