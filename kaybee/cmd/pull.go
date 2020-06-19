/*
Copyright © 2020 SAP
*/

package cmd

import (
	"github.com/sap/project-kb/kaybee/internal/tasks"
	"github.com/spf13/cobra"
)

// TODO make constructor method, as in ExportCmd, for testability

// pullCmd represents the pull command
var pullCmd = &cobra.Command{
	Use:   "pull",
	Short: "Pull vulnerability data from remote repositories into local clones",
	Long: `A longer description that spans multiple lines and likely contains examples
and usage of using your command. For example:

Cobra is a CLI library for Go that empowers applications.
This application is a tool to generate the needed files
to quickly create a Cobra application.`,
	Run: doPull,
}

func init() {
	rootCmd.AddCommand(pullCmd)
}

func doPull(cmd *cobra.Command, args []string) {
	t := tasks.NewPullTask().
		WithSources(configuration.Sources())

	t.Verbose(verbose)
	t.Execute()
}
