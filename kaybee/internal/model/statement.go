// Copyright © 2019 - 2020, SAP

package model

import (
	"crypto/md5"
	"encoding/json"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"os"
	"path/filepath"
	"reflect"
	"regexp"
	"strconv"
	"strings"

	"gopkg.in/yaml.v2"
)

// const hashSize int = 80

// Checksum is a checksum :-)
type Checksum [16]byte

var zeroChecksum Checksum = [16]byte{0}

// Statement represents a vulnerability statement
type Statement struct {
	// ID                uuid.UUID  `yaml:"-" json:"-"`
	VulnerabilityID   string     `yaml:"vulnerability_id" json:"vulnerability_id"`
	Aliases           []Alias    `yaml:"-" json:"-"`
	Notes             []Note     `yaml:"notes,omitempty" json:"notes"`
	Fixes             []Fix      `yaml:"fixes,omitempty" json:"-"`
	AffectedArtifacts []Artifact `yaml:"artifacts,omitempty" json:"affected_artifacts"`
	Metadata          Metadata   `yaml:"-" json:"-"`
	hash              Checksum
}

// Hash computes a unique identifiers for a Statement instance
func (s *Statement) Hash() Checksum {
	// FIXME
	// if the values are changed after the first invocation to this method,
	// the results might be unexpected... (one would need to manually reset hash to ""
	// for this to work as expected)

	if s.hash == zeroChecksum {
		var x string

		x += s.VulnerabilityID
		for _, n := range s.Notes {
			x += n.Text
			for _, l := range n.Links {
				x += l
			}
		}

		for _, f := range s.Fixes {
			for _, c := range f.Commits {
				x += c.RepositoryURL + c.ID
			}
		}

		for _, a := range s.AffectedArtifacts {
			x += a.ID + a.Reason + strconv.FormatBool(a.Affected)
		}

		for _, al := range s.Aliases {
			x += string(al)
		}

		s.hash = md5.Sum([]byte(x))
	}
	return s.hash
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
	hash    Checksum
	// Metadata Metadata `yaml:"metadata,omitempty"`
}

// Hash returns a unique identifier for the Fix, based on its contents
func (f Fix) Hash() Checksum {
	if f.hash == zeroChecksum {
		var x string

		x += f.ID
		for _, c := range f.Commits {
			x += c.RepositoryURL + c.ID
		}

		f.hash = md5.Sum([]byte(x))
	}
	return f.hash
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
	Links []string `yaml:"links" json:"links"`
	Text  string   `json:"text"`
	hash  Checksum
}

// Hash computes a unique identifiers for a Note value
func (n Note) Hash() Checksum {
	if n.hash == zeroChecksum {
		var x string

		x += n.Text
		for _, l := range n.Links {
			x += l
		}

		n.hash = md5.Sum([]byte(x))
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

// StringSliceContains tells whether a contains x.
func StringSliceContains(a []string, x string) bool {
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
		if StringSliceContains(anotherNote.Links, l) {
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
	}
	s := &Statement{}
	if err := yaml.Unmarshal(data, &s); err != nil {
		log.Println(err)
	}

	// TODO
	// if there exist a tar.gz with sources,
	// store the path to that tarball in the statement metadata
	//
	// EDIT: no need to do this: because the path to the statement
	// is in the metadata, it is easy for the client to check
	// if the tarball is there or not
	s.Metadata.LocalPath = filepath.Dir(path)
	s.hash = zeroChecksum

	return *s
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

	// strip slashes from the end of repository URLs
	for i := range s.Fixes {
		for j := range s.Fixes[i].Commits {
			s.Fixes[i].Commits[j].RepositoryURL = strings.TrimRight(s.Fixes[i].Commits[j].RepositoryURL, "/")
		}
	}

	dest := filepath.Join(targetDir, "statement.yaml")
	// fmt.Print("\nSaving statement to file", dest)
	data, _ := yaml.Marshal(s)
	err := ioutil.WriteFile(dest, data, 0600)
	if err != nil {
		log.Fatalln("Could not save statement to file: ", dest)
		log.Fatal(err)
	}

	// if  the statement has an associated sources tarball,
	// then write it to disk, as a sibling to the statement.yaml file
	changedSourceCodeTarball := filepath.Join(filepath.Dir(s.Metadata.LocalPath), "changed-source-code.tar.gz")

	//log.Println("Looking for tarball: " + changedSourceCodeTarball)
	if _, err := os.Stat(changedSourceCodeTarball); err == nil {
		_, err := copyFile(changedSourceCodeTarball, filepath.Join(filepath.Dir(dest), "changed-source-code.tar.gz"))
		if err != nil {
			log.Fatal("Could not copy file " + changedSourceCodeTarball + " to destination: " + filepath.Dir(dest))
		} else {
			// log.Println("Tarball copied")
		}
	} else {
		// log.Println("No tarball found")
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

// FIXME: get rid of this, not really needed...

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

func copyFile(src, dst string) (int64, error) {
	sourceFileStat, err := os.Stat(src)
	if err != nil {
		return 0, err
	}

	if !sourceFileStat.Mode().IsRegular() {
		return 0, fmt.Errorf("%s is not a regular file", src)
	}

	source, err := os.Open(src)
	if err != nil {
		return 0, err
	}
	defer source.Close()

	destination, err := os.Create(dst)
	if err != nil {
		return 0, err
	}
	defer destination.Close()
	nBytes, err := io.Copy(destination, source)
	return nBytes, err
}
