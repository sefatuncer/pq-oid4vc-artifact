# C3 adaptörü (Go): üç hedef tek ikilide (sürümler go.mod/go.sum'da sabit)
FROM pq-a09-env-go:1.0 AS b
WORKDIR /a
COPY go.mod go.sum main.go /a/
RUN go mod download && go build -o /a/adaptor . && go version -m /a/adaptor > /a/surumler.txt
FROM pq-a09-env-go:1.0
COPY --from=b /a/adaptor /a/surumler.txt /a/main.go /a/
ENTRYPOINT ["/a/adaptor"]
