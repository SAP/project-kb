// Copyright © 2019 - 2020, SAP. All rights reserved.

package cmd

import (
	"fmt"

	"github.com/spf13/cobra"
)

// TODO make constructor method, as in ExportCmd, for testability

// pushCmd represents the push command
var pushCmd = &cobra.Command{
	Use:   "push",
	Short: "Push a merged text-format Kb to a repository",
	Long: `A longer description that spans multiple lines and likely contains examples
and usage of using your command. For example:

Cobra is a CLI library for Go that empowers applications.
This application is a tool to generate the needed files
to quickly create a Cobra application.`,
	Run: doPush,
}

func init() {
	rootCmd.AddCommand(pushCmd)

	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	// pushCmd.PersistentFlags().String("foo", "", "A help for foo")

	// Cobra supports local flags which will only run when this command
	// is called directly, e.g.:
	// pushCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
}

func doPush(cmd *cobra.Command, args []string) {
	fmt.Println("Pushing....")
	fmt.Println("UNIMPLEMENTED")
	fmt.Println("Push completed")
}
