// Copyright © 2019 - 2020, SAP

package cmd

import (
	"fmt"
	"os"

	"github.com/rs/zerolog"
	"github.com/rs/zerolog/log"

	"github.com/sap/project-kb/kaybee/internal/conf"
	"github.com/spf13/cobra"
)

var (
	verbose       bool
	configuration conf.Config
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
		if verbose {
			zerolog.SetGlobalLevel(zerolog.TraceLevel)
		}
		log.Fatal().Err(err)
	}
}

func init() {
	// OnInitialize sets the passed functions to be run when each command's Execute method is called.
	cobra.OnInitialize(initConfig)
	rootCmd.PersistentFlags().StringVarP(&cfgFile, "config", "c", cfgFile, "config file")
	rootCmd.PersistentFlags().BoolVarP(&verbose, "verbose", "v", false, "Verbose mode")

	// setup log levels
	log.Logger = log.Output(zerolog.ConsoleWriter{Out: os.Stderr})
	zerolog.SetGlobalLevel(zerolog.InfoLevel)
}

func initConfig() {
	configuration, err := conf.ParseConfiguration(cfgFile)
	if err != nil {
		log.Fatal().Str("path", cfgFile).Msg("Error parsing configuration")
	}
	log.Trace().Str("config", fmt.Sprintf("%+v\n", configuration)).Msg("Running with configuration")
}
