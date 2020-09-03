package task

import (
	"encoding/json"
	"io/ioutil"
	"net/http"
	"regexp"
	"sync"
	"time"

	"github.com/rs/zerolog/log"
	"github.com/sap/project-kb/kaybee/internal/model"
	"github.com/schollz/progressbar/v2"
)

const (
	maxConcurrent              int    = 16
	limitImport                int    = 1000
	importClientTimeoutSeconds int    = 5
	defaultOutputFolder        string = ".kaybee/imported"
)

// Import is the task that performs exporting of vulnerability information from
// a Steady backend or database, and produces a text-based (YAML) representation,
// useful for further processing (e.g., manual inspection, uploading to a repository, analysis, etc.)
type Import struct {
	Backend      string
	Concurrency  int
	Limit        int
	OutputFolder string
}

func (t *Import) mustValidate() {
	if t.Concurrency == 0 {
		t.Concurrency = 1
	}
	if t.Backend == "" {
		log.Fatal().Msg("No backend specified, aborting.")
	}
	if t.Backend[len(t.Backend)-1] != '/' {
		t.Backend += "/"
	}
	if t.OutputFolder == "" {
		log.Fatal().Msg("Invalid output folder. Aborting.")
	}
}

// Execute performs the actual task and returns true on success
func (t *Import) Execute() (success bool) {
	log.Info().Int("n_workers", t.Concurrency).Str("backend", t.Backend).Msg("Importing vulnerability data")
	importers, err := NewImporterPool(t.Backend, t.Concurrency, t.Limit, nil)
	if err != nil {
		log.Fatal().Msg("Could not create importers pool")
	}

	vulns := importers.Run()
	for _, v := range vulns {
		v.ToFile(t.OutputFolder)
	}
	log.Info().Int("n_statements", len(vulns)).Str("dest", t.OutputFolder).Msg("Statements saved to fs")
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
	Backend     string `yaml:"backend"`
	Bugs        []*model.Bug
	Statements  map[string]model.Statement
	Client      *http.Client
	Filter      map[string][]*regexp.Regexp
	ProgressBar *progressbar.ProgressBar
}

// NewImporterPool instantiates a pool of Exporters, each taking care of fetching vulnerability
// data for a subset of the overall set of vulnerabilities stored in the Steady backend.
func NewImporterPool(backend string, concurrent int, limit int, filter map[string][]*regexp.Regexp) (*ImporterPool, error) {

	pool := &ImporterPool{}
	bugs, err := fetchVulnerabilityIDs(backend)
	if err != nil {
		log.Fatal().Err(err)
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
		resp2, err := f.Client.Get(f.Backend + BugsEndpoint + "/" + b.VulnerabilityID + "/affectedLibIds?onlyWellKnown=true")
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
		s := b.ToStatement()
		for _, al := range affectedLibs {
			// if al.Source == "MANUAL" || al.Source == "AST_EQUALITY" {
			if al.Source == "MANUAL" {
				s.AffectedArtifacts = append(s.AffectedArtifacts, al.toAffectedArtifact())
			}
		}
		// fmt.Printf("%+v", affectedLibs)
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
