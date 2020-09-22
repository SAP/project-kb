package model

import (
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strings"
)

// MergeLog is a collection of merge records, documenting how a merge operation was performed
type MergeLog struct {
	executionID string
	timestamp   int64
	entries     []MergeLogEntry
}

// NewMergeLog creates a new instance of a MergeLog
func NewMergeLog(executionID string) MergeLog {
	return MergeLog{
		executionID: executionID,
	}
}

// Log appends a MergeLogEntry to the MergeLog
func (ml *MergeLog) Log(logEntry MergeLogEntry) {
	logEntry.executionID = ml.executionID
	ml.entries = append(ml.entries, logEntry)
}

// Entries returns all entries in the MergeLog
func (ml *MergeLog) Entries() []MergeLogEntry {
	return ml.entries
}

func (mle MergeLogEntry) String() (output string) {
	var stmtsAsString string

	for _, s := range mle.sourceStatements {
		stmtsAsString += Indent(s.PrettyPrint(), "  ") + "\n"
	}

	output = fmt.Sprintf(
		"-----\nLog Message:  %s\n"+
			"Merge Policy: %s\n"+
			"Sources:\n%s",
		mle.logMessage,
		mle.policy,
		stmtsAsString,
	)

	return output
}

// Dump saves the MergeLog to a file
func (ml *MergeLog) Dump(path string) {
	// filesystem.CreateFile(filepath)
	// fmt.Println("==========================================")
	f, err := os.OpenFile(filepath.Join(path, "merge.log"),
		os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0600)
	if err != nil {
		log.Println(err)
	}
	defer f.Close()
	for _, l := range ml.Entries() {
		// fmt.Println(l)
		_, err := f.WriteString(l.String())
		if err != nil {
			fmt.Println(err)
			f.Close()
			return
		}
	}

	// fmt.Println(n, "bytes written successfully")
	err = f.Close()
	if err != nil {
		fmt.Println(err)
		return
	}
}

// A MergeLogEntry represents the results of a merge operation
// Must identify which element from each statments are dropped or kept
type MergeLogEntry struct {
	executionID        string
	timestamp          int64
	sourceStatements   []Statement
	resultingStatement Statement
	policy             string
	logMessage         string
	success            bool
}

// NewMergeLogEntry constructs a new MergeLogEntry instance
// func NewMergeLogEntry() MergeLogEntry {
// 	return MergeLogEntry{
// 		timestamp: time.Now().Unix(),
// 	}
// }

// Indent adds consistent indentation to a block of text
func Indent(objToPrint interface{}, indent string) string {

	text := fmt.Sprintf("%s", objToPrint)
	if text[len(text)-1:] == "\n" {
		result := ""
		for _, j := range strings.Split(text[:len(text)-1], "\n") {
			result += indent + j + "\n"
		}
		return result
	}
	result := ""
	for _, j := range strings.Split(strings.TrimRight(text, "\n"), "\n") {
		result += indent + j + "\n"
	}
	return result[:len(result)-1]
}
