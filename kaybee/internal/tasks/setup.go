package tasks

import (
	"bytes"
	"fmt"
	"io"
	"os"

	"github.com/markbates/pkger"
	"github.com/rs/zerolog/log"
	"github.com/sap/project-kb/kaybee/internal/filesystem"
)

// SetupTask is the task that performs merging of statements, reconciling any
// conflicts using a set of pre-defined policies.
type SetupTask struct {
	force       bool
	interactive bool
}

// NewSetupTask constructs a new MergeTask
func NewSetupTask() *SetupTask {

	t := SetupTask{
		force:       false,
		interactive: false,
	}
	return &t
}

// WithForce sets the flag that controls whether the setup should be done even
// if a configuration file is already existing (in which case, it will be overwritten)
func (t *SetupTask) WithForce(f bool) *SetupTask {
	t.force = f
	return t
}

// WithInteractiveMode enables interactive mode
func (t *SetupTask) WithInteractiveMode(im bool) *SetupTask {
	t.interactive = im
	return t
}

// Execute performs the actual task and returns true on success
func (t *SetupTask) Execute() (success bool) {
	fmt.Println("[+] Running Setup task")
	const configFileName string = "./kaybeeconf.yaml"

	// cwd, err := os.Getwd()
	// if err != nil {
	// 	log.Println(err)
	// }

	// configFileFullPath := path.Join(cwd, configFileName)
	configFileFullPath := configFileName
	// check if file exists
	if filesystem.FileExists(configFileFullPath) {
		if t.force {
			fmt.Printf("Overwriting the existing configuration file at %s\n", configFileFullPath)
			if err := os.Remove(configFileFullPath); err != nil {
				log.Fatal().Msg("There was an error removing the existing file")
			}
		} else {
			log.Info().Str("path", configFileFullPath).Msg("The configuration file already exists. Re-run with the -f flag to overwrite it")
			log.Fatal().Msg("Aborting")
		}
	}

	f, err := os.Create(configFileFullPath)
	if err != nil {
		fmt.Printf("Failed to create file: %s", configFileFullPath)
	}
	f.Close()

	f, err = os.OpenFile(configFileFullPath, os.O_RDWR, 0600)
	defer f.Close()
	if err != nil {
		log.Fatal().Err(err)
	}

	configFileContent := getDefaultConfig()
	_, err = f.WriteString(configFileContent)
	if err != nil {
		log.Fatal().Err(err)
	}

	// Save file changes.
	err = f.Sync()
	if err != nil {
		log.Fatal().Err(err)
	}

	log.Info().Msg("Setup task completed")
	return true
}

func getDefaultConfig() string {
	box, err := pkger.Open("/kaybee/internal/tasks/data/default_config.yaml")
	if err != nil {
		log.Fatal().Err(err)
	}
	defer box.Close()

	s := new(bytes.Buffer)
	if _, err := io.Copy(s, box); err != nil {
		log.Fatal().Err(err)
	}
	return s.String()
}
