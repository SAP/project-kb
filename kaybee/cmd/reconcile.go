/*
Copyright © 2020 SAP
*/

package cmd

import (
	"github.com/sap/project-kb/kaybee/internal/tasks"
	"github.com/spf13/cobra"
)

// var vulnerabilityID string

// reconcileCmd represents the reconcile command
var reconcileCmd = &cobra.Command{
	Use:   "reconcile",
	Short: "Manually reconcile conflicting statements",
	Long:  ``,
	Run:   doReconcile,
}

func init() {
	rootCmd.AddCommand(reconcileCmd)
	// reconcileCmd.Flags().StringVarP(&vulnerabilityID, "reconcile", "r", "", "Vulnerability to reconcile")
}

func doReconcile(cmd *cobra.Command, args []string) {
	var vulnerabilityID string = args[0]

	t := tasks.ReconcileTask{
		Sources:         configuration.Sources(),
		VulnerabilityID: vulnerabilityID,
	}

	t.Verbose(verbose)
	t.Execute()
}
