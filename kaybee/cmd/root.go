// Copyright © 2019 - 2020, SAP

package cmd

import (
	"fmt"
	"log"
	"os"

	// homedir "github.com/mitchellh/go-homedir"

	"github.com/sap/project-kb/kaybee/internal/conf"
	"github.com/sap/project-kb/kaybee/internal/filesystem"
	"github.com/spf13/cobra"
	// "gopkg.in/src-d/go-git.v4/storage/filesystem"
)

var (
	verbose       bool
	configuration conf.Configuration
	cfgFile       string = "kaybeeconf.yaml"
)

// TODO make constructor method, as in ExportCmd, for testability

// rootCmd represents the base command when called without any subcommands
var rootCmd = &cobra.Command{
	Use:              "kaybee",
	TraverseChildren: true,
	Short:            "KayBee is a tool to maintain a collaborative, distributed knowledge base of vulnerabilities affecting open-source software.",
	Long:             `KayBee is a tool to maintain a collaborative, distributed knowledge base of vulnerabilities affecting open-source software.`,
	Run: func(cmd *cobra.Command, args []string) {

	},
}

// Execute adds all child commands to the root command and sets flags appropriately.
// This is called by main.main(). It only needs to happen once to the rootCmd.
func Execute() {

	if len(os.Args) == 1 {
		rootCmd.Help()
		os.Exit(0)

	}
	if err := rootCmd.Execute(); err != nil {
		log.Println(err)
		os.Exit(1)
	}
}

func init() {
	// OnInitialize sets the passed functions to be run when each command's Execute method is called.
	cobra.OnInitialize(initConfig)
	rootCmd.PersistentFlags().StringVarP(&cfgFile, "config", "c", cfgFile, "config file")
	rootCmd.PersistentFlags().BoolVarP(&verbose, "verbose", "v", false, "Verbose mode")
}

func initConfig() {
	// fmt.Println("CONFIG: " + cfgFile)

	if !filesystem.IsFile(cfgFile) {
		configuration = conf.Configuration{}
		return
	}

	p, err := conf.NewParser(cfgFile)
	if err != nil {
		log.Fatal("Error parsing configuration")
	}

	c, _ := p.Parse()
	if verbose {
		fmt.Println("Using config file:", p.Viper.ConfigFileUsed())
	}

	_, err = c.Validate()
	if err != nil {
		log.Fatalln("Invalid config.")
	}
	configuration = c
}
