/*
Copyright © 2019 - 2020, SAP
*/

package cmd

import (
	"github.com/sap/project-kb/kaybee/internal/tasks"
	"github.com/spf13/cobra"
)

// NewImportCmd is a constructor of an ImportCommand, useful for testability
func NewImportCmd() *cobra.Command {
	return &cobra.Command{
		Use:   "import",
		Short: "Imports vulnerability data from a Steady backend or database to plain-text  statements",
		Long:  `Imports vulnerability data from a Steady backend or database to plain-text  statements`,
		// Args:  cobra.MinimumNArgs(1),
		Run: doImport,
	}
}

/*
	importCmd represents the import command, which is used to extract data from an
	existing Steady backend and populate a plain-text statement repository.
*/
var importCmd = NewImportCmd()

var (
	concurrency int
	backend     string
	limit       int
	importPath  string
)

func init() {
	rootCmd.AddCommand(importCmd)
	importCmd.Flags().IntVarP(&limit, "limit", "n", 0, "limits the amount of rows displays (default 0)")
	importCmd.Flags().IntVar(&concurrency, "concurrency", 0, "limits the amount go routine per thread (default 0)")
	importCmd.Flags().StringVarP(&backend, "backend", "b", "", "URL of the Steady backend from which to import vulnerability data.")
	importCmd.Flags().StringVarP(&importPath, "path", "p", ".kaybee/imported", "Folder in which to store the imported statements")
}

func doImport(cmd *cobra.Command, args []string) {

	if backend == "" {
		backend = configuration.Backend()
	}

	t := tasks.NewImportTask().
		WithBackend(backend).
		WithConcurrency(concurrency).
		WithLimit(limit).
		WithOutputPath(importPath)

	t.Verbose(verbose)
	t.Execute()
}
