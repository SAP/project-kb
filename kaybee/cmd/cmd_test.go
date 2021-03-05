package cmd

import (
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"net/http/httptest"
	"os"
	"testing"

	"github.com/sap/project-kb/kaybee/internal/tasks"
)

// TestExport checks if the export cmd works
func TestExport(t *testing.T) {
	exportCmd.SetArgs([]string{"-t", "steady"})
	exportCmd.Execute()
}

func TestImport(t *testing.T) {

	f, err := os.Open("../testdata/steady/all_bugs.json")
	if err != nil {
		log.Fatal(err)
	}
	defer f.Close()

	payload, err := ioutil.ReadAll(f)
	if err != nil {
		log.Fatal(err)
	}

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(200)
		w.Write([]byte(payload))
	}))
	defer srv.Close()

	fmt.Println(srv.URL)

	task := tasks.NewImportTask().
		WithBackend(srv.URL).
		WithOutputPath("/tmp/kaybee-test/").
		WithConcurrency(4).
		WithLimit(5)

	task.Execute()
}
