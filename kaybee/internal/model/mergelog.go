package model

import (
	"os"
	"path/filepath"

	"github.com/rs/zerolog/log"
	"gopkg.in/yaml.v2"
)

// MergeLog is a collection of merge records, documenting how a merge operation was performed
type MergeLog struct {
	ExecutionID string          `yaml:"execution_id"`
	Timestamp   int64           `yaml:"timestamp"`
	Entries     []MergeLogEntry `yaml:"entries"`
}

// NewMergeLog creates a new instance of a MergeLog
func NewMergeLog(executionID string) MergeLog {
	return MergeLog{
		ExecutionID: executionID,
	}
}

// Log appends a MergeLogEntry to the MergeLog
func (ml *MergeLog) Log(logEntry MergeLogEntry) {
	logEntry.executionID = ml.ExecutionID
	ml.Entries = append(ml.Entries, logEntry)
}

// Dump saves the MergeLog to a file
func (ml *MergeLog) Dump(file string) {
	f, err := os.OpenFile(filepath.Join(file, "merge.log"),
		os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0600)
	defer f.Close()
	if err != nil {
		log.Fatal().Err(err)
	}
	data, err := yaml.Marshal(ml)
	if err != nil {
		log.Fatal().Err(err).Msg("Failed to marshal mergelog entries")
	}
	if _, err := f.Write(data); err != nil {
		// if err := ioutil.WriteFile(file, data, 0644); err != nil {
		log.Fatal().Err(err).Msg("Failed to write mergelog entries")
	}
}

// A MergeLogEntry represents the results of a merge operation
// Must identify which element from each statments are dropped or kept
type MergeLogEntry struct {
	executionID        string
	timestamp          int64
	sourceStatements   []Statement `yaml:"sources"`
	resultingStatement Statement
	policy             string `yaml:"policy"`
	logMessage         string `yaml:"message"`
	success            bool
}

// NewMergeLogEntry constructs a new MergeLogEntry instance
// func NewMergeLogEntry() MergeLogEntry {
// 	return MergeLogEntry{
// 		timestamp: time.Now().Unix(),
// 	}
//
