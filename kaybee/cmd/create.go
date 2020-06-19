/*
Copyright © 2019 - 2020, SAP
*/

package cmd

import (
	"github.com/sap/project-kb/kaybee/internal/tasks"
	"github.com/spf13/cobra"
)

var useGUI bool

// TODO make constructor method, as in ExportCmd, for testability

/*
createCommand represents the command to make a new statement
*/
var createCommand = &cobra.Command{
	Use:   "create",
	Short: "Create a new statement",
	Long:  ``,
	Run:   doCreate,
}

func init() {
	rootCmd.AddCommand(createCommand)
	createCommand.Flags().BoolVarP(&useGUI, "gui", "g", false, "Use the browser-based graphical user interface")
}

func doCreate(cmd *cobra.Command, args []string) {
	t := tasks.NewCreateTask().
		WithGUI(useGUI)

	t.Verbose(verbose)
	t.Execute()
}
