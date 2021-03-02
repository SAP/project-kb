package tasks

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"regexp"
	"sync"
	"time"

	"github.com/schollz/progressbar/v2"

	"github.com/sap/project-kb/kaybee/internal/model"
)

const (
	maxConcurrent              int    = 16
	limitImport                int    = 1000
	importClientTimeoutSeconds int    = 5
	defaultOutputFolder        string = ".kaybee/imported"
)

// ImportTask is the task that performs exporting of vulnerability information from
// a Steady backend or database, and produces a text-based (YAML) representation,
// useful for further processing (e.g., manual inspection, uploading to a repository, analysis, etc.)
type ImportTask struct {
	BaseTask
	backend      string
	concurrency  int
	limit        int
	outputFolder string
}

// NewImportTask constructs a new ImportTask
func NewImportTask() *ImportTask {
	return &ImportTask{
		concurrency:  maxConcurrent,
		limit:        limitImport,
		outputFolder: defaultOutputFolder,
	}
}

// WithBackend sets the URL of the backend  from which data will be imported
func (t *ImportTask) WithBackend(backend string) *ImportTask {
	if backend == "" {
		log.Fatal("No backend specified, aborting.")
	}
	if backend[len(backend)-1] != '/' {
		backend += "/"
	}
	t.backend = backend
	return t
}

// WithConcurrency sets the number of concurrent importers
func (t *ImportTask) WithConcurrency(c int) *ImportTask {
	if c == 0 {
		t.concurrency = 1
	} else {
		t.concurrency = c
	}
	return t
}

// WithLimit sets the maximum number of statements that will be imported
func (t *ImportTask) WithLimit(l int) *ImportTask {
	t.limit = l
	return t
}

// WithOutputPath sets the path to which the imported data will be saved
func (t *ImportTask) WithOutputPath(p string) *ImportTask {
	t.outputFolder = p
	return t
}

func (t *ImportTask) validate() (ok bool) {
	if t.backend == "" {
		log.Fatalln("Invalid backend for import. Aborting.")
		return false
	}
	if t.outputFolder == "" {
		log.Fatalln("Invalid output folder. Aborting.")
		return false
	}

	return true
}

// Execute performs the actual task and returns true on success
func (t *ImportTask) Execute() (success bool) {

	fmt.Printf("Importing vulnerability data from %s (using %d workers)\n", t.backend, t.concurrency)

	importers, err := NewImporterPool(t.backend, t.concurrency, t.limit, nil, t.verbose)
	if err != nil {
		log.Fatalln("Could not create importers pool")
	}

	vulns := importers.Run()
	for _, v := range vulns {
		v.ToFile(t.outputFolder)
	}
	fmt.Printf("\nSaved %d vulnerability statements in directory '%s'\n", len(vulns), t.outputFolder)
	return true
}

const (
	// BugsEndpoint is the endpoint for the rest-backend API to fetch bugs
	BugsEndpoint = "/bugs"
)

// ImporterPool is a pool of importers
type ImporterPool []Importer

// Importer is used to download and convert bugs to statements. Each exporter instance
// gets a slice of bugs to fetch. Multiple importers can be used ad once, as part of
// a pool of importers (ImporterPool).
type Importer struct {
	Backend           string `yaml:"backend"`
	Bugs              []*model.Bug
	Statements        map[string]model.Statement
	SkippedStatements []model.Statement
	Client            *http.Client
	Filter            map[string][]*regexp.Regexp
	ProgressBar       *progressbar.ProgressBar
	Verbose           bool
}

// NewImporterPool instantiates a pool of Exporters, each taking care of fetching vulnerability
// data for a subset of the overall set of vulnerabilities stored in the Steady backend.
func NewImporterPool(backend string, concurrent int, limit int, filter map[string][]*regexp.Regexp, verbose bool) (*ImporterPool, error) {

	pool := &ImporterPool{}
	bugs, err := fetchVulnerabilityIDs(backend)
	if err != nil {
		log.Fatal(err)
		return nil, err
	}

	// fetch them all, unless a limit is supplied
	n := len(bugs)
	if limit != 0 {
		if limit < n {
			n = limit
		}
	}

	bar := progressbar.NewOptions(
		n,
		progressbar.OptionSetWidth(50),
		progressbar.OptionSetRenderBlankState(true),
		progressbar.OptionSetPredictTime(false),
	)
	// bar.Describe(fmt.Sprintf("    Importing vulnerability data from %s (%d workers)\n", backend, concurrent))

	itemsPerWorker := (n / concurrent) + 1
	for i := 0; i < n; i += itemsPerWorker {
		end := i + itemsPerWorker

		if end > n {
			end = n
		}

		*pool = append(*pool, Importer{
			Backend: backend,
			Bugs:    bugs[i:end],
			Client: &http.Client{
				Timeout: time.Duration(importClientTimeoutSeconds) * time.Second,
			},
			Filter:      filter,
			Statements:  make(map[string]model.Statement),
			ProgressBar: bar,
			Verbose:     verbose,
		})
	}

	return pool, nil
}

// Run launches a series of go routines that each try to fetch specific
// information from the slice of bug found in the local instance of the
// postgresql database and converts it to statements
func (p ImporterPool) Run() map[string]model.Statement {
	var wg sync.WaitGroup
	res := map[string]model.Statement{}

	for i := range p {
		wg.Add(1)
		go func(f *Importer) {
			defer wg.Done()
			f.Run()
		}(&p[i])
	}
	wg.Wait()

	for _, f := range p {
		res = model.MergeStatements(res, f.Statements)
	}

	return res
}

// Run fetches specific information from a slice of bugs and converts it to statements
func (f *Importer) Run() error {
	for _, b := range f.Bugs {
		// Fetch bug data
		resp1, err := f.Client.Get(f.Backend + BugsEndpoint + "/" + b.VulnerabilityID)
		if err != nil {
			return err
		}

		defer resp1.Body.Close()
		body1, err := ioutil.ReadAll(resp1.Body)
		if err != nil {
			return err
		}
		if err := json.Unmarshal(body1, b); err != nil {
			return err
		}

		// Fetch affected artifacts data
		var affectedLibs []SteadyAffectedLib
		resp2, err := f.Client.Get(f.Backend + BugsEndpoint + "/" + b.VulnerabilityID + "/affectedLibIds?onlyWellKnown=true&resolved=true")
		// resp2, err := f.Client.Get(f.Backend + BugsEndpoint + "/" + b.VulnerabilityID + "/affectedLibIds?onlyWellKnown=true")
		if err != nil {
			return err
		}
		defer resp2.Body.Close()
		body2, err := ioutil.ReadAll(resp2.Body)
		if err != nil {
			return err
		}
		if err := json.Unmarshal(body2, &affectedLibs); err != nil {
			return err
		}
		f.ProgressBar.Add(1)
		// fmt.Println("Fetching " + b.VulnerabilityID)
		s := b.ToStatement()
		for _, al := range affectedLibs {
			if al.Source == "MANUAL" {
				aa := al.toAffectedArtifact()
				aa.Reason = "Reviewed manually"
				s.AffectedArtifacts = append(s.AffectedArtifacts, aa)
			} else if al.Source == "AST_EQUALITY" {
				aa := al.toAffectedArtifact()
				aa.Reason = "Assessed with Eclipse Steady (AST_EQUALITY)"
				s.AffectedArtifacts = append(s.AffectedArtifacts, aa)
			}
		}
		// fmt.Printf("%+v", affectedLibs)

		// Skip statements that would not contain neither commits nor affected artifacts
		if len(s.Fixes) == 0 && len(s.AffectedArtifacts) == 0 {
			if f.Verbose {
				fmt.Println("\nNo fix-commits nor (well-known) affected artifacts for " + s.VulnerabilityID + ", skipping.")
			}
			continue
		}
		if !model.Matches(s, f.Filter) {
			f.Statements[b.VulnerabilityID] = *s
		}

	}
	return nil
}

// fetchVulnerabilityIDs retrieves all vulnerability identifiers from the Steady backend
// Note: they are called "bugs" in Steady
func fetchVulnerabilityIDs(backend string) ([]*model.Bug, error) {
	resp, err := http.Get(backend + BugsEndpoint)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	var bugs []*model.Bug
	if err := json.Unmarshal(body, &bugs); err != nil {
		return nil, err
	}
	return bugs, nil
}

// func saveToFile(s *model.Statement, path string) error {
// 	targetDir := filepath.Join(path, s.VulnerabilityID)
// 	if _, err := os.Stat(targetDir); os.IsNotExist(err) {
// 		log.Println("Creating folder: " + targetDir)
// 		// os.MkdirAll(targetDir, os.ModeDir)
// 		os.MkdirAll(targetDir, 0770)
// 	}

// 	dest := filepath.Join(targetDir, "statement.yaml")
// 	fmt.Println("Saving statement to file", dest)
// 	data, _ := yaml.Marshal(s)
// 	err := ioutil.WriteFile(dest, data, 0666)
// 	if err != nil {
// 		log.Fatalln("Could not save statement to file: ", dest)
// 		log.Fatal(err)
// 	}
// 	return nil
// }

// SteadyAffectedLib represents an affected artifact as represented in the output of the Steady
// API /backend/bugs/CVE-2019-0232/affectedLibIds?onlyWellKnown=true
type SteadyAffectedLib struct {
	LibraryID   SteadyLibID `json:"libraryId"`
	Affected    bool        `json:"affected"`
	Explanation string      `json:"explanation"`
	Source      string      `json:"source"`
}

// SteadyLibID represents a GAV in the output of the Steady API
type SteadyLibID struct {
	ArtifactID string `json:"artifact"`
	GroupID    string `json:"group"`
	Version    string `json:"version"`
}

// toAffectedArtifact converts an library entry as returned by Steady API to a
// KayBee AffectedArtifact structure (that ends up being part of a Statement)
func (al SteadyAffectedLib) toAffectedArtifact() (aa model.Artifact) {
	// TODO maven is hardcoded; how to distinguish between different PURL types?
	aa.ID = "pkg:maven/" + al.LibraryID.GroupID + "/" + al.LibraryID.ArtifactID + "@" + al.LibraryID.Version
	aa.Affected = al.Affected
	// aa.Reason = al.Explanation + " (source: " + al.Source + ")"
	aa.Reason = al.Explanation
	return aa
}
