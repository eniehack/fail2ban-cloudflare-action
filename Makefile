FLAGS =
GO = go
BINARIES = ruledeploy rulegen
BINDIR = dist
SRC = $(shell find . -type f -name '*.go' -print)
.PHONY: clean pre-build

all: $(BINARIES)

pre-build:
	mkdir -p ./$(BINDIR)
	cp -r ./src/ipmglist.py ./$(BINDIR)/

$(BINARIES): pre-build $(SRC) 
	$(GO) $(FLAGS) build -o ./$(BINDIR)/$@ ./cmd/$@/main.go

clean:
	rm -rf ./$(BINDIR)