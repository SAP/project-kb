package model

import (
	"log"
	"strings"
)

// A Bug represents vulnerabilities (as represented in the output obtained from the Steady backend)
type Bug struct {
	VulnerabilityID  string            `json:"bugId"`
	Description      string            `json:"description,omitempty"`
	Links            []string          `json:"reference,omitempty"`
	ConstructChanges []ConstructChange `json:"constructChanges"`
}

// ConstructChange represents a commit fix in the vuln database
type ConstructChange struct {
	Repo     string `yaml:"repo"`
	Commit   string `yaml:"commit"`
	RepoPath string `yaml:"repoPath"`
}

// ToStatement converts a bug as represented by the backend/bugs/VULN-ID endpoint of Steady
// to a statement object
func (b *Bug) ToStatement() *Statement {
	s := &Statement{
		VulnerabilityID: b.VulnerabilityID,
	}

	// == GOLANG TECHNICALITIES ==
	//
	// NOTE: this must be a map of POINTERS to CommitSet instances;
	// plain CommitSet instances would not be useful because
	// map members are not addressable (see Go spec: https://golang.org/ref/spec#Address_operators).
	// For example, the following statement would be illegal:
	//
	//   commitGroups[fixID].Add(Commit{ID: cc.Commit, RepositoryURL: cc.Repo})
	//
	// See also: https://groups.google.com/forum/?fromgroups=#!topic/golang-nuts/4_pabWnsMp0
	commitGroups := make(map[string]*CommitSet)
	// var commitID string
	// uniqueCommits.AddSlice(b.ConstructChanges)
	// fmt.Println("Unique changes: ", uniqueConstructChanges.Size())

	for _, cc := range b.ConstructChanges {
		// Get an ID for the Fix (group of commits) based on the prefix of
		// the RepoPath field
		parsedRepoPath := strings.Split(cc.RepoPath, ":")

		// sanity check: commits should be either of the form "sha1"
		// or "branchID:sha1", therefore there should be 0 or 1 occurrences
		// of the separator ':'
		parsedRepoLen := len(parsedRepoPath)
		if parsedRepoLen < 0 || parsedRepoLen > 2 {
			log.Fatal("Unable to parse RepoPath: ", cc.RepoPath)
		}

		fixID := "DEFAULT_BRANCH"
		// if the parsedRepoPath has two segments, then overwrite
		if parsedRepoLen == 2 {
			fixID = parsedRepoPath[0]
		}
		// Construct a commit and add to the commit group corresponding
		// to the fix at hand (identified by fixID)
		commit := Commit{
			ID:            cc.Commit,
			RepositoryURL: cc.Repo,
		}
		if _, ok := commitGroups[fixID]; !ok {
			cs := NewCommitSet()
			cs.Add(commit)
			commitGroups[fixID] = &cs
		} else {
			commitGroups[fixID].Add(commit)
		}
	}

	for key, commitGroup := range commitGroups {
		fix := Fix{ID: key,
			Commits: commitGroup.Elements(),
			// Metadata: Metadata{},
		}
		s.Fixes = append(s.Fixes, fix)
	}

	note := Note{Text: b.Description}
	note.Links = make([]string, len(b.Links))
	copy(note.Links, b.Links)
	s.Notes = append(s.Notes, note)
	// s.Metadata.Origin = "internal"
	// s.Metadata.Timestamp = 123456789
	return s
}
