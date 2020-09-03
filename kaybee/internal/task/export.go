package task

import (
	"io/ioutil"
	"os"
	"path/filepath"
	"strings"
	"text/template"

	"github.com/rs/zerolog/log"
	"github.com/sap/project-kb/kaybee/internal/conf"
	"github.com/sap/project-kb/kaybee/internal/filesystem"
	"github.com/sap/project-kb/kaybee/internal/model"
)

// Export is the task that generates a script to import statements into 3rd-party systems
type Export struct {
	policy     []model.Policy
	Source     string
	Target     string
	OutputFile string
	Scripts    []conf.ExportScript
	Denylist   []string
}

func (t *Export) mustValidate() {
	if t.Source == "" {
		log.Fatal().Msg("Invalid source for export. Aborting.")
	}
	if t.Target == "" {
		log.Fatal().Msg("Invalid export target. Aborting.")
	}
	// if t.outputFile == "" {
	// 	log.Fatalln("Invalid filename for export script. Aborting.")
	// 	return false
	// }
	if len(t.Scripts) < 1 {
		log.Fatal().Msg("No export scripts specified. Aborting.")
	}
}

// Execute performs the actual merge task and returns true on success
// The task supports both exporting sets of statements and individual statements.
// To export sets of statements, the source must be a directory containing
// either statements or subdirectories that contain, each, a statement.
// A source can also be an individual statement file.
// If no source is specified, the task aborts. If a default directory must be
// considered, it must be set in the calling command.
func (t *Export) Execute() (success bool) {
	t.mustValidate()

	var statements []model.Statement

	var dirs []os.FileInfo
	var err error
	var statementFile string

	if filesystem.IsDir(t.Source) {
		// TODO this works only if the source directory contains directories that ocntain statements
		// if the source contains directly a statament, this does not work
		dirs, err = ioutil.ReadDir(t.Source)
		if err != nil {
			log.Fatal().Err(err)
		}

		for _, d := range dirs {
			statementFile = filepath.Join(t.Source, d.Name(), "statement.yaml")

			if !filesystem.IsFile(statementFile) {
				continue
			}
			statements = append(statements, model.NewStatementFromFile(statementFile))
		}
	} else {
		statements = append(statements, model.NewStatementFromFile(t.Source))
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

	for _, s := range t.Scripts {
		if s.Target != t.Target {
			continue
		}

		// outputFilename = ctx.Get("outputFile").(string)
		// if outputFilename == "" {
		// 	outputFilename = s.Filename
		// }

		funcMap := template.FuncMap{
			"LinksAsCSV": LinksAsCSV,
			"JoinNotes":  JoinNotes,
		}

		tEach = *template.Must(template.New("each").Funcs(funcMap).Parse(s.Each))
		tPre = *template.Must(template.New("pre").Parse(s.Pre))
		tPost = *template.Must(template.New("post").Parse(s.Post))

		if t.OutputFile == "" {
			t.OutputFile = s.Filename
		}
	}

	if tEach.Name() == "" {
		log.Fatal().Msg("Make sure you have a valid export section in your configuration.")
	}

	// var err error

	f, err := os.Create(t.OutputFile)
	if err != nil {
		log.Error().Err(err).Msg("Failed to create file")
		return
	}

	err = tPre.Execute(f, nil)
	if err != nil {
		log.Error().Err(err).Msg("Failed to execute template")
	}

	exportCount := 0
	for _, r := range statements {
		if IsVulnerabilityExportExcluded(t.Denylist, r.VulnerabilityID) {
			log.Trace().Str("vulnID", r.VulnerabilityID).Msg("Skipping excluded vulnerability")
			continue
		}
		if err := tEach.Execute(f, r); err != nil {
			log.Error().Err(err).Msg("Error executing template")
		}
		exportCount++
	}

	err = tPost.Execute(f, nil)
	if err != nil {
		log.Error().Err(err).Msg("Error executing template")
	}

	log.Trace().Int("n_exported", exportCount).Str("dest", t.OutputFile).Msg("Exported statement")
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
