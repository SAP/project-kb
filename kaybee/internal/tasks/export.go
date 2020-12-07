package tasks

import (
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"path"

	"path/filepath"
	"strings"
	"text/template"

	"github.com/sap/project-kb/kaybee/internal/conf"
	"github.com/sap/project-kb/kaybee/internal/filesystem"
	"github.com/sap/project-kb/kaybee/internal/model"
)

// ExportTask is the task that generates a script to import statements into 3rd-party systems
type ExportTask struct {
	BaseTask
	policy     []model.Policy
	source     string
	target     string
	outputFile string
	scripts    []conf.ExportScript
	denylist   []string
}

// NewExportTask constructs a new ExportTask
func NewExportTask() *ExportTask {

	mt := ExportTask{}
	return &mt
}

// WithSource sets the source to export from
func (t *ExportTask) WithSource(s string) *ExportTask {
	if s == "" {
		log.Fatal("Invalid export source specified. Aborting.")
	}
	t.source = s
	return t
}

// WithTarget sets the target type
func (t *ExportTask) WithTarget(target string) *ExportTask {
	if target == "" {
		log.Fatal("Invalid export target specified. Aborting.")
	}
	t.target = target
	return t
}

// WithDenylist sets the identifiers of vulnerabilities to exclude from the export
func (t *ExportTask) WithDenylist(bl []string) *ExportTask {
	t.denylist = bl
	return t
}

// WithOutputFile sets the name of the file that the export will produce
func (t *ExportTask) WithOutputFile(filename string) *ExportTask {
	t.outputFile = filename
	return t
}

// WithExportScripts passes the export script templates to the task
func (t *ExportTask) WithExportScripts(scripts []conf.ExportScript) *ExportTask {
	t.scripts = scripts
	return t
}

func (t *ExportTask) validate() (ok bool) {
	if t.source == "" {
		log.Fatalln("Invalid source for export. Aborting.")
		return false
	}
	if t.target == "" {
		log.Fatalln("Invalid export target. Aborting.")
		return false
	}
	// if t.outputFile == "" {
	// 	log.Fatalln("Invalid filename for export script. Aborting.")
	// 	return false
	// }
	if len(t.scripts) < 1 {
		log.Fatalln("No export scripts specified. Aborting.")
		return false
	}
	return true
}

// Execute performs the actual merge task and returns true on success
// The task supports both exporting sets of statements and individual statements.
// To export sets of statements, the source must be a directory containing
// either statements or subdirectories that contain, each, a statement.
// A source can also be an individual statement file.
// If no source is specified, the task aborts. If a default directory must be
// considered, it must be set in the calling command.
func (t *ExportTask) Execute() (success bool) {

	t.validate()

	var statements []model.Statement

	var dirs []os.FileInfo
	var err error
	var statementFile string

	if filesystem.IsDir(t.source) {
		// FIXME this works only if the source directory contains directories that ocntain statements
		// if the source contains directly a statament, this does not work
		dirs, err = ioutil.ReadDir(t.source)
		if err != nil {
			log.Fatal(err)
		}

		for _, d := range dirs {
			statementFile = filepath.Join(t.source, d.Name(), "statement.yaml")

			if !filesystem.IsFile(statementFile) {
				continue
			}
			statements = append(statements, model.NewStatementFromFile(statementFile))
		}
	} else {
		statements = append(statements, model.NewStatementFromFile(t.source))
	}

	// c := ctx.Get("configuration").(conf.Configuration)
	// exportTarget := ctx.Get("exportTarget")

	// if exportTarget == "" {
	// 	log.Fatal("No export target specified. Aborting.")
	// }

	// TODO set a default target in configuration file so that the CLI is cleaner
	// TODO set a default output filename in configuration file so that the CLI is cleaner
	// TODO remove the --from flag, make the source folder an optional argument of export
	// (if not specified, a default merge folder is to be used)
	var tEach, tPre, tPost template.Template
	// var outputFilename string

	for _, s := range t.scripts {
		if s.Target != t.target {
			continue
		}

		// outputFilename = ctx.Get("outputFile").(string)
		// if outputFilename == "" {
		// 	outputFilename = s.Filename
		// }

		funcMap := template.FuncMap{
			"LinksAsCSV": LinksAsCSV,
			"JoinNotes":  JoinNotes,
			"MatchPath":  path.Match,
			"JoinPath":   path.Join,
		}

		tEach = *template.Must(template.New("each").Funcs(funcMap).Parse(s.Each))
		tPre = *template.Must(template.New("pre").Parse(s.Pre))
		tPost = *template.Must(template.New("post").Parse(s.Post))

		if t.outputFile == "" {
			t.outputFile = s.Filename
		}
	}

	if tEach.Name() == "" {
		log.Fatal("Make sure you have a valid export section in your configuration.")
	}

	// var err error

	f, err := os.Create(t.outputFile)
	if err != nil {
		log.Println("create file: ", err)
		return
	}

	err = tPre.Execute(f, nil)
	if err != nil {
		log.Println("Error executing template:", err)
	}

	exportCount := 0
	for _, r := range statements {
		if IsVulnerabilityExportExcluded(t.denylist, r.VulnerabilityID) {
			log.Println("Skipping excluded vulnerability: ", r.VulnerabilityID)
			continue
		}
		err = tEach.Execute(f, r)
		if err != nil {
			log.Println("Error executing template:", err)
		}
		exportCount++
	}

	err = tPost.Execute(f, nil)
	if err != nil {
		log.Println("Error executing template:", err)
	}

	fmt.Printf("Exported %d statements to %s\n", exportCount, t.outputFile)

	return true
}

// IsVulnerabilityExportExcluded checks if a vulnerability id
// should be excluded from the export
func IsVulnerabilityExportExcluded(excluded []string, vulnID string) bool {
	for _, item := range excluded {
		if item == vulnID {
			return true
		}
	}
	return false
}

// LinksAsCSV prints all links as csv
func LinksAsCSV(s model.Statement) string {
	var links []string
	for _, n := range s.Notes {
		for _, l := range n.Links {
			links = append(links, l)
		}
	}
	return strings.Join(links, ",")
}

// JoinNotes collects the text from all notes and concatenates it
func JoinNotes(s model.Statement) string {
	var out []string
	for _, n := range s.Notes {

		out = append(out, n.Text)

	}
	return escapeForBash(strings.Join(out, "\\\n"))
}

func escapeForBash(in string) string {
	// '"'"'
	return strings.ReplaceAll(in, "'", "'\"'\"'")
}

/*
Notes on exporting to kb-importer

- when exporting statements:
  - for top-level metadata.json file, produce by removing fixes and converting yaml to json
  - consequence: kb-importer will have to parse xPURLs (x= with version intervals, see below)
- interpretation of version intervals
  - use the Mvn convention, see: https://docs.oracle.com/middleware/1212/core/MAVEN/maven_version.htm#MAVEN8903
  - EXCEPT: we do not support comma-separated intervals, e.g., (,1.0.0),(2.0.0,3.0.0), one will need
	two distict triples in the statement for that
- If a PURL of type MAVEN has only one segment, that is the name (no namespace); in that case, we consider it to be a SHA-1
*/
