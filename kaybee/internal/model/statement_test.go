package model

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"testing"

	"github.com/package-url/packageurl-go"
	"github.com/stretchr/testify/assert"
)

var st1 = Statement{
	VulnerabilityID: "cve-1234-5678",
	Aliases: []Alias{
		"alias-01",
		"alias-02",
	},
	Notes: []Note{
		{
			Links: []string{
				"some_link",
				"another_link",
			},
			Text: "Some note about cve-1234-5678",
		},
	},
	Fixes: []Fix{
		{
			ID: "1.x",
			Commits: []Commit{
				{
					ID:            "abcd1234",
					RepositoryURL: "https://github.com/fsdafa/fasdfa",
				},
				{
					ID:            "abcd1234",
					RepositoryURL: "https://github.com/fsdafa/fasdfa",
				},
				{
					ID:            "abcd1234",
					RepositoryURL: "https://github.com/fsdafa/fasdfa",
				},
			},
		},
		{
			ID: "2.x",
			Commits: []Commit{
				{
					ID:            "abcd1234",
					RepositoryURL: "https://github.com/fsdafa/fasdfa",
				},
				{
					ID:            "abcd1234",
					RepositoryURL: "https://github.com/fsdafa/fasdfa",
				},
			},
		},
	},
}

func TestStatementDeclaration(t *testing.T) {

	fmt.Printf("%v", st1)
}

func TestConvertBugToStatement(t *testing.T) {

	// jsonData, err := ioutil.ReadFile("test/bug_sample.json")
	jsonData, err := ioutil.ReadFile("../../testdata/steady/cve-2018-11040.json")

	assert.Nil(t, err)

	var b Bug
	err = json.Unmarshal(jsonData, &b)
	if err != nil {
		log.Println(err)
	}
	stmt := b.ToStatement()
	// log.Printf("%+v", stmt)

	assert.Equal(t, 2, len(stmt.Fixes))
	assert.Equal(t, 1, len(stmt.Fixes[0].Commits))
	assert.Equal(t, 1, len(stmt.Fixes[1].Commits))
	// fmt.Printf("%+v", stmt)
}

func TestStatementFromFile(t *testing.T) {
	var s Statement
	s = NewStatementFromFile("../../testdata/statements/statement_commits.yaml")
	assert.Equal(t, "CVE-2019-0191", s.VulnerabilityID)

	s = NewStatementFromFile("../../testdata/statements/statement_affected_artifacts.yaml")
	assert.Equal(t, 3, len(s.AffectedArtifacts))

	parsedPURL, err := packageurl.FromString(s.AffectedArtifacts[0].ID)
	if err != nil {
		panic(err)
	}
	assert.Equal(t, "maven", parsedPURL.Type)
	assert.Equal(t, "[1.9.0,1.9.2)-RELEASE", parsedPURL.Version)
	fmt.Printf("%+v\n", parsedPURL)

}

func TestCommitSet(t *testing.T) {

	cc1 := Commit{ID: "c1", RepositoryURL: "repo_url_A"}
	cc2 := Commit{ID: "c2", RepositoryURL: "repo_url_B"}
	cc3 := Commit{ID: "c3", RepositoryURL: "repo_url_C"}
	cc4 := Commit{ID: "c4", RepositoryURL: "repo_url_D"}

	ccs := NewCommitSet()
	assert.True(t, ccs.Empty())
	assert.Equal(t, 0, ccs.Size())

	ccs.Add(cc1)
	assert.False(t, ccs.Empty())
	assert.Equal(t, 1, ccs.Size())
	ccs.Add(cc2, cc3)
	assert.Equal(t, 3, ccs.Size())

	assert.True(t, ccs.Contains(cc1), "cc1 is in the set!")
	assert.True(t, ccs.Contains(cc3), "cc3 is in the set!")
	assert.False(t, ccs.Contains(cc4), "cc4 is not in the set!")

	ccs.Remove(cc1, cc2)
	assert.False(t, ccs.Contains(cc1), "cc1 was removed from the set!")
	assert.False(t, ccs.Contains(cc2), "cc2 was removed from the set!")
	assert.True(t, ccs.Contains(cc3), "cc3 is in the set!")

}

func TestStatementHashComparison(t *testing.T) {
	var s1, s2 Statement
	s1 = NewStatementFromFile("../../testdata/statements/statement_commits.yaml")
	s2 = NewStatementFromFile("../../testdata/statements/statement_commits.yaml")
	assert.Equal(t, s1.Hash(), s2.Hash(), "Hashes differ (for two identical statements)")

	s2.Fixes = nil
	s2.hash = [16]byte{}

	assert.NotEqual(t, s1.Hash(), s2.Hash(), "Hashes are the same (for different statements)")

}
