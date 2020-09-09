// Copyright © 2019 - 2020, SAP

package model

import (
	"encoding/hex"
	"encoding/json"

	"fmt"
	"io/ioutil"
	"log"
	"os"
	"path/filepath"
	"reflect"
	"regexp"

	"github.com/google/uuid"
	"gopkg.in/yaml.v2"
	// "strings"
)

// Statement represents a vulnerability statement
type Statement struct {
	ID                uuid.UUID  `yaml:"-" json:"-"`
	VulnerabilityID   string     `yaml:"vulnerability_id" json:"vulnerability_id"`
	Aliases           []Alias    `yaml:"aliases" json:"aliases"`
	Fixes             []Fix      `yaml:"fixes" json:"-"`
	AffectedArtifacts []Artifact `yaml:"artifacts" json:"affected_artifacts"`
	Notes             []Note     `yaml:"notes" json:"notes"`
	Metadata          Metadata   `yaml:"-" json:"-"`
}

func (s Statement) String() (output string) {

	output = fmt.Sprintf("%s", s.VulnerabilityID)

	return output
}

// PrettyPrint formats a Statement nicely for output on screen/file
func (s Statement) PrettyPrint() (output string) {
	output = fmt.Sprintf("%s (branch: %s)\n  local path: %s\n  rank:       %d", s.Metadata.Origin, s.Metadata.Branch, s.Metadata.LocalPath, s.Metadata.OriginRank)
	return output
}

// Alias represents other alternative identifiers of the vulnerability
type Alias string

// func (a Alias) String() string {
// 	return a.Value
// }

// Fix represents a group of commits that implement the fix for
// a given vulnerability
type Fix struct {
	ID      string
	Commits []Commit
	// Metadata Metadata `yaml:"metadata,omitempty"`
}

// Commit identifies a single commit in a repository
type Commit struct {
	ID            string `yaml:"id"`
	RepositoryURL string `yaml:"repository"`
}

// Artifact represents a binary artifact (e.g., a .jar, a POM)
type Artifact struct {
	// ID is a PURL
	ID string `yaml:"id" json:"id"`
	// VersionRange string `yaml:"versions"`
	Reason   string `yaml:"reason" json:"reason"`
	Affected bool   `yaml:"affected" json:"affected"`
}

// A Note represents a description that accompanies a statement; it can have a
// set of links and a free-text comment. Neither are mandatory.
type Note struct {
	Links []string `json:"links"`
	Text  string   `json:"text"`
	hash  string
}

// Hash computes a unique identifiers for a Note value
func (n Note) Hash() string {
	if n.hash == "" {
		var x string

		x += n.Text
		for _, l := range n.Links {
			x += l
		}

		n.hash = hex.EncodeToString([]byte(x))
	}
	return n.hash

}

func (n Note) String() string {
	output := fmt.Sprintf("\n%s", n.Text)
	for _, l := range n.Links {
		output += "\n - " + l
	}
	return output + "\n"
}

// ContainsSlice tells whether a contains x.
func ContainsSlice(a []string, x string) bool {
	for _, n := range a {
		if x == n {
			return true
		}
	}
	return false
}

// Equals determines whether two Notes are the same
func (n Note) Equals(anotherNote Note) bool {
	if n.Text != anotherNote.Text {
		return false
	}

	if len(n.Links) != len(anotherNote.Links) {
		return false
	}

	for _, l := range anotherNote.Links {
		if ContainsSlice(anotherNote.Links, l) {
			return false
		}
	}

	return true
}

// Metadata represents the commit relating to the statement.yaml itself
type Metadata struct {
	Origin     string
	Branch     string
	OriginRank int
	LocalPath  string
	// Timestamp  int64  `yaml:"timestamp"`
	// Signature  string `yaml:"signature,omitempty"`
}

// IsIndependent checks if two statement contain contradicting information
// that cannot be merged without conflict resolution
// func (s1 *Statement) IsIndependent(s2 Statement) bool {
// 	// TODO This function is not really necessary, to be removed
// 	if s1.VulnerabilityID != s2.VulnerabilityID {
// 		return true
// 	}

// 	return false
// }

// NewStatementFromFile creates a statement
func NewStatementFromFile(path string) Statement {
	data, err := ioutil.ReadFile(path)
	if err != nil {
		log.Println(err)
		return nil
	}
	s := &Statement{}
	err := yaml.Unmarshal(data, &s)
	if err != nil {
		log.Println(err)
	}

	return s
}

// ToFile writes a statement to a file in the directory path specified as argument.
// If the specified directory does not exist, is is created (including all necessary
// ancestors)
func (s *Statement) ToFile(path string) error {
	targetDir := filepath.Join(path, s.VulnerabilityID)
	if _, err := os.Stat(targetDir); os.IsNotExist(err) {
		// log.Println("Creating folder: " + targetDir)
		os.MkdirAll(targetDir, 0750)
	}

	dest := filepath.Join(targetDir, "statement.yaml")
	// fmt.Print("\nSaving statement to file", dest)
	data, _ := yaml.Marshal(s)
	err := ioutil.WriteFile(dest, data, 0600)
	if err != nil {
		log.Fatalln("Could not save statement to file: ", dest)
		log.Fatal(err)
	}
	return nil
}

// ToJSON returns the JSON representation of a statement (as a string)
func (s Statement) ToJSON() string {
	data, err := json.MarshalIndent(s, "", "  ")
	if err != nil {
		log.Fatalln("Could not represent statement in JSON format")
		log.Fatal(err)
	}
	return string(data)
}

// Matches applies a list of map of param -> regexes to a statement structure
func Matches(Iface interface{}, regexes map[string][]*regexp.Regexp) bool {
	sReflect := reflect.ValueOf(Iface)
	// Check if the passed interface is a pointer
	if sReflect.Type().Kind() != reflect.Ptr {
		// Create a new type of Iface's Type, so we have a pointer to work with
		sReflect = reflect.New(reflect.TypeOf(Iface))
	}

	for param, regex := range regexes {
		field := sReflect.Elem().FieldByName(param)
		if field.IsValid() {
			for _, r := range regex {
				if r.MatchString(field.String()) {
					return true
				}
			}
		}
	}
	return false
}

// MergeStatements merges a variable number of statements
func MergeStatements(ms ...map[string]Statement) map[string]Statement {
	res := map[string]Statement{}
	for _, m := range ms {
		for k, v := range m {
			res[k] = v
		}
	}
	return res
}

// CommitSet implements a set of (unique) Commits
type CommitSet struct {
	data map[Commit]struct{}
}

// NewCommitSet creates a new empty CommitSet
func NewCommitSet() CommitSet {
	set := CommitSet{}
	set.data = make(map[Commit]struct{})
	return set
}

// Empty returns true if the set contains no elements
func (set *CommitSet) Empty() bool {
	return len(set.data) == 0
}

// Size returns the number of elements in the set
func (set *CommitSet) Size() int {
	return len(set.data)
}

// Elements returns the number of elements in the set
func (set *CommitSet) Elements() []Commit {
	keys := make([]Commit, 0, len(set.data))
	for k := range set.data {
		keys = append(keys, k)
	}
	return keys
}

// Contains checks if *Commit cc exists in the set
func (set *CommitSet) Contains(cc Commit) bool {
	if _, ok := set.data[cc]; ok {
		return true
	}
	return false
}

// Add adds a Commit cc to the set
func (set *CommitSet) Add(cc ...Commit) {
	for _, elem := range cc {
		set.data[elem] = struct{}{}
	}
}

// AddSlice adds all *Commit elements in slice s to the set
func (set *CommitSet) AddSlice(s []Commit) {
	for _, elem := range s {
		set.Add(elem)
	}
}

// Remove deletes a *Commit cc from the set
func (set *CommitSet) Remove(cc ...Commit) {
	for _, elem := range cc {
		delete(set.data, elem)
	}
}
