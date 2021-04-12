package source

import (
	"log"
	"os"
	"testing"
)

func TestFetch(t *testing.T) {
	source := NewSource(
		"https://github.com/sap/project-kb",
		"vulnerability-data",
		"/statements",
		true,
		1,
		"file:///../../.kaybee/repositories")

	// defer os.RemoveAll(source.Path)

	// Remove old repository
	os.RemoveAll(source.Path)

	// Test repository fetching from empty repo
	source.Fetch(false)

	// Test repository fetching from preexisting repo
	source.Fetch(false)

	// Test metadata fill
	statements, err := source.Statements()
	if err != nil {
		t.Error(err)
	}
	for _, s := range statements {
		log.Printf("%+v\n", s)
	}
}
