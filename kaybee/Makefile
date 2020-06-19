$(eval VERSION = $(shell head VERSION))
$(eval GIT_COMMIT = $(shell git rev-parse HEAD))
$(eval NOW = $(shell date))

# Go parameters
GOCMD=go
GOBUILD=$(GOCMD) build
GOCLEAN=$(GOCMD) clean
GOTEST=$(GOCMD) test
GOGET=$(GOCMD) get
BINARY_NAME=kaybee
BINARY_UNIX=$(BINARY_NAME)-$(VERSION)_linux-amd64
BINARY_WINDOWS=$(BINARY_NAME)-$(VERSION)_win-amd64
BINARY_MACOS=$(BINARY_NAME)-$(VERSION)_darwin-amd64

all: lint vet test build ui

build: fmt
	$(GOBUILD) -ldflags='-X "github.com/sap/project-kb/kaybee/cmd.buildDate=$(NOW)" -X "github.com/sap/project-kb/kaybee/cmd.buildCommitID=$(GIT_COMMIT)" -X "github.com/sap/project-kb/kaybee/cmd.version=$(VERSION)"' -o $(BINARY_NAME) -v

ui:
	$(MAKE) --directory=ui

check: lint vet test

test: 
	$(GOTEST) -coverprofile=coverage.out ./...

coverage: test
	go tool cover -html=coverage.out

clean:
	$(GOCLEAN)
	-@rm -f $(BINARY_NAME) 2>/dev/null || true
	-@rm -f $(BINARY_UNIX) 2>/dev/null || true
	-@rm -f $(BINARY_MACOS) 2>/dev/null || true
	-@rm -fr dist 2>/dev/null || true
	-@rm coverage.out 2>/dev/null || true

run:
	$(GOBUILD) -o $(BINARY_NAME) -v ./...
	./$(BINARY_NAME)

vet: fmt
	$(GOCMD) vet ./...

doc:
	$(GOCMD) doc ./...

fmt:
	$(GOCMD) fmt ./...

lint: vet
	golint ./...

# Cross compilation
build-linux:
	CGO_ENABLED=0 GOOS=linux GOARCH=amd64 $(GOBUILD) -o dist/$(BINARY_UNIX) -v

build-win:
	CGO_ENABLED=0 GOOS=windows GOARCH=amd64 $(GOBUILD) -o dist/$(BINARY_WINDOWS) -v

build-macos:
	CGO_ENABLED=0 GOOS=darwin GOARCH=amd64 $(GOBUILD) -o dist/$(BINARY_MACOS) -v
