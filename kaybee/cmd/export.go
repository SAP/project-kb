/*
Copyright © 2020 SAP
*/

// Package cmd contains all commands
package cmd

import (
	"github.com/sap/project-kb/kaybee/internal/tasks"
	"github.com/spf13/cobra"
)

var (
	skipMerge           bool
	exportTarget        string
	mergedStatementsDir string = "./merged"
	outputFile          string
)

var exportCmd = &cobra.Command{
	Use:   "export",
	Short: "Export a merged text-based kb into a variety of formats",
	Long: `A longer description that spans multiple lines and likely contains examples
and usage of using your command. For example:

Cobra is a CLI library for Go that empowers applications.
This application is a tool to generate the needed files
to quickly create a Cobra application.`,
	Run: runCommand,
}

func init() {
	rootCmd.AddCommand(exportCmd)

	exportCmd.Flags().StringVarP(&exportTarget, "target", "t", "", "Target of the export (e.g., xml, json, steady")
	exportCmd.Flags().StringVarP(&mergedStatementsDir, "from", "f", ".kaybee/merged", "Path to the statements to export")
	exportCmd.Flags().StringVarP(&outputFile, "to", "o", "", "Name of the output file")
}

func runCommand(cmd *cobra.Command, args []string) {
	doExport(args)
}

func doExport(args []string) {
	// fmt.Println("Exporting....")

	// if skipMerge {
	// 	fmt.Println("Skipping merge, re-using the results of the previous merge")
	// } else {
	// 	doMerge(cmd, args)
	// }

	t := tasks.NewExportTask().
		WithExportScripts(configuration.ExportScripts()).
		WithSource(mergedStatementsDir).
		WithTarget(exportTarget).
		WithOutputFile(outputFile).
		WithDenylist(configuration.ExportDenylist())

	t.Verbose(verbose)
	t.Execute()

}
