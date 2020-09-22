package model

import (
	"fmt"
	"testing"
)

var (
	s1 Statement = Statement{
		VulnerabilityID: "cve_id1",
		Aliases: []Alias{
			"bug-01",
			"bug-02",
		},
		Notes: []Note{
			{Links: []string{"ref_1"}, Text: "Text_1"},
			{Links: []string{"ref_2"}, Text: "Text_2"},
		},
		Fixes: []Fix{
			{
				ID: "DEFAULT_BRANCH",
				Commits: []Commit{
					{
						ID:            "abcd1234",
						RepositoryURL: "https://github.com/abc/def",
					},
				},
			},
		},
		Metadata: Metadata{
			Origin:     "contrib_1",
			OriginRank: 3,
		},
	}

	s2 Statement = Statement{
		VulnerabilityID: "cve_id2",
		Notes: []Note{
			{Links: []string{"ref_1"}, Text: "Text_1"},
			{Links: []string{"ref_2"}, Text: "Text_2"},
		},
		Fixes: []Fix{
			{
				ID: "DEFAULT_BRANCH",
				Commits: []Commit{
					{
						ID:            "abcd1234",
						RepositoryURL: "https://github.com/abc/def",
					},
				},
			},
		},
	}

	s3 Statement = Statement{
		VulnerabilityID: "cve_id3",
		Aliases: []Alias{
			"bug-A",
		},
		Notes: []Note{
			{Links: []string{"ref_1"}, Text: "Text_3"},
			{Links: []string{"ref_2"}, Text: "Text_5"},
		},
		Fixes: []Fix{
			{
				ID: "DEFAULT_BRANCH",
				Commits: []Commit{
					{
						ID:            "abcd1234",
						RepositoryURL: "https://github.com/abc/def",
					},
				},
			},
		},
	}

	s4 Statement = Statement{
		VulnerabilityID: "cve_id1",
		Aliases: []Alias{
			"bug-A",
			"bug-B",
		},
		Notes: []Note{
			{Links: []string{"ref_8"}, Text: "Text_8"},
			{Links: []string{"ref_6"}, Text: "Text_6"},
		},
		Fixes: []Fix{
			{
				ID: "2.x",
				Commits: []Commit{
					{
						ID:            "abcd1234",
						RepositoryURL: "https://github.com/abc/def",
					},
					{
						ID:            "abcd12341",
						RepositoryURL: "https://github.com/abc/def",
					},
					{
						ID:            "abcd12342",
						RepositoryURL: "https://github.com/abc/xyz",
					},
				},
			},
		},
		Metadata: Metadata{
			Origin:     "repo_1",
			OriginRank: 3,
			Branch:     "master",
		},
	}

	s5 Statement = Statement{
		VulnerabilityID: "cve_id5",
		Notes: []Note{
			{Links: []string{"ref_1"}, Text: "Text_1"},
			{Links: []string{"ref_2"}, Text: "Text_2"},
			{Links: []string{"ref_3"}, Text: "Text_3"},
			{Links: []string{"ref_4"}, Text: "Text_4"},
		},
		Fixes: []Fix{
			{
				ID: "DEFAULT_BRANCH",
				Commits: []Commit{
					{
						ID:            "abcd1234",
						RepositoryURL: "https://github.com/abc/def",
					},
				},
			},
		},
		Metadata: Metadata{
			Origin:     "repo_2",
			OriginRank: 4,
			Branch:     "master",
		},
	}

	s6 Statement = Statement{
		VulnerabilityID: "cve_id6",
		Notes: []Note{
			{Links: []string{"ref_1"}, Text: "Text_1000"},
			{Links: []string{"ref_2"}, Text: "Text_2000"},
			{Links: []string{"ref_3"}, Text: "Text_3"},
			{Links: []string{"ref_4"}, Text: "Text_4"},
			{Links: []string{"ref_5"}, Text: "Text_5"},
		},
		Fixes: []Fix{
			{
				ID: "DEFAULT_BRANCH",
				Commits: []Commit{
					{
						ID:            "abcd1234",
						RepositoryURL: "https://github.com/abc/def",
					},
				},
			},
		},
		Metadata: Metadata{
			Origin:     "repo_3",
			OriginRank: 6,
			LocalPath:  "repo_3",
			Branch:     "master",
		},
	}
)

func TestSoftPolicy(t *testing.T) {
	statementsToMerge := map[string][]Statement{
		s1.VulnerabilityID: {s1},
		s2.VulnerabilityID: {s2},
		s3.VulnerabilityID: {s3},
		s4.VulnerabilityID: {s4},
		s5.VulnerabilityID: {s5},
		s6.VulnerabilityID: {s6},
	}
	var s Policy
	// p, err := conf.NewParser()
	// if err != nil {
	// 	return
	// }

	// p.SetConfigFile("../../testdata/conf/kaybeeconf.yaml")
	// c, _ := p.Parse()

	s = NewSoftPolicy()
	mergedStatement, mergeLog, err := s.Reduce(statementsToMerge)

	fmt.Println("Merge log:")
	for _, logEntry := range mergeLog.Entries() {
		fmt.Printf("%v\n", logEntry)
	}

	if err != nil {
		fmt.Printf("Could not merge: %v", err)
	}
	fmt.Printf("Merged:\n%v", mergedStatement)
}

func TestStrictPolicy(t *testing.T) {
	var s Policy
	s = NewStrictPolicy()
	statementsToMerge := map[string][]Statement{
		s1.VulnerabilityID: {s1},
		s2.VulnerabilityID: {s2},
		s3.VulnerabilityID: {s3},
		s4.VulnerabilityID: {s4},
		s5.VulnerabilityID: {s5},
		s6.VulnerabilityID: {s6},
	}
	mergedStatement, mergeLog, err := s.Reduce(statementsToMerge)
	if err != nil {
		fmt.Printf("Could not merge: %v", err)
	}

	fmt.Println("Merge log:")
	for _, logEntry := range mergeLog.Entries() {
		fmt.Printf("%v\n", logEntry)
	}

	fmt.Printf("Merged:\n%+v\n", mergedStatement)
}

func TestSmartPolicy(t *testing.T) {
	var s Policy
	s = NewSmartPolicy()
	statementsToMerge := map[string][]Statement{
		s1.VulnerabilityID: {s1},
		s2.VulnerabilityID: {s2},
		s3.VulnerabilityID: {s3},
		s4.VulnerabilityID: {s4},
		s5.VulnerabilityID: {s5},
		s6.VulnerabilityID: {s6},
	}
	mergedStatement, mergeLog, err := s.Reduce(statementsToMerge)
	if err != nil {
		fmt.Printf("Could not merge: %v", err)
	}

	fmt.Println("Merge log:")
	for _, logEntry := range mergeLog.Entries() {
		fmt.Printf("%v\n", logEntry)
	}

	fmt.Printf("Merged:\n%v\n", mergedStatement)
}

func TestNullPolicy(t *testing.T) {
	var s Policy
	s = NewNullPolicy()
	reconcileResults := s.Reconcile([]Statement{s1, s2})
	fmt.Printf("Merged: %v", reconcileResults.reconciledStatement)
}

// func BenchmarkRandom(b *testing.B) {
// 	G := &RandomPolicy{}
// 	G.New(time.Now().UnixNano())

// 	for i := 1; i <= b.N; i++ {
// 		_, err := G.Merge(s1, s2)
// 		if err != nil {
// 			b.Error(err)
// 		}
// 		// fmt.Println(val.BugID)
// 	}
// }

// func BenchmarkSoft(b *testing.B) {
// 	G := &SoftPolicy{}
// 	G.New()

// 	for i := 1; i <= b.N; i++ {
// 		_, err := G.Merge(s1, s5)
// 		if err != nil {
// 			b.Error(err)
// 		}
// 	}
// }
