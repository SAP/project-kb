// Copyright © 2019 - 2020, SAP. All rights reserved.

package cmd

import (
	"fmt"
	"log"

	"github.com/sap/project-kb/kaybee/internal/tasks"
	"github.com/spf13/cobra"
)

// TODO make constructor method, as in ExportCmd, for testability

// mergeCmd represents the merge command
var setupCmd = &cobra.Command{
	Use:   "setup",
	Short: "Creates a configuration, unless it exists already",
	Long: `(CAUTION! OBSOLETE DESCRIPTION) Displays from a list of different source repositories a table of
cves which are possibly conflicting, attempts a soft merge and displays
each as mergeable or not along with the conflicting slices.

	kbsync setup [-i]
`,
	Run: doSetup,
}

var (
	interactive bool
	force       bool
)

func init() {
	rootCmd.AddCommand(setupCmd)
	setupCmd.Flags().BoolVarP(&interactive, "interactive", "i", false, "Interactive configuration")
	setupCmd.Flags().BoolVarP(&force, "force", "f", false, "Force overwrite existing configuration file")
}

func doSetup(cmd *cobra.Command, args []string) {
	fmt.Println("Running setup...")

	if interactive {
		fmt.Println("Interactive mode (not implemented yet)")
		log.Fatal("Aborting.")
	} else {
		fmt.Println("Non-interactive mode")
	}

	t := tasks.NewSetupTask().
		WithInteractiveMode(interactive).
		WithForce(force)

	t.Verbose(verbose)
	t.Execute()

	fmt.Println("Setup completed")

}
