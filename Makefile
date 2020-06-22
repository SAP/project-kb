# $(eval VERSION = $(shell head VERSION))
# $(eval GIT_COMMIT = $(shell git rev-parse HEAD))
# $(eval NOW = $(shell date))

# # Go parameters
# GOCMD=go
# GOBUILD=$(GOCMD) build
# GOCLEAN=$(GOCMD) clean
# GOTEST=$(GOCMD) test
# GOGET=$(GOCMD) get
# BINARY_NAME=kaybee
# BINARY_UNIX=$(BINARY_NAME)-$(VERSION)_linux-amd64
# BINARY_WINDOWS=$(BINARY_NAME)-$(VERSION)_win-amd64
# BINARY_MACOS=$(BINARY_NAME)-$(VERSION)_darwin-amd64

# all: lint vet test build #ui

# build: fmt
# 	$(GOBUILD) -ldflags='-X "github.com/sap/project-kb/kaybee/cmd.buildDate=$(NOW)" -X "github.com/sap/project-kb/kaybee/cmd.buildCommitID=$(GIT_COMMIT)" -X "github.com/sap/project-kb/kaybee/cmd.version=$(VERSION)"' -o $(BINARY_NAME) -v

# # ui:
# # 	$(MAKE) --directory=ui

.PHONY: docs

docs:
	mkdocs serve

