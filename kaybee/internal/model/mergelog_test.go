package model

import (
	"testing"
)

var (
	st3 = Statement{
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
		Metadata: Metadata{
			LocalPath:  "/tmp/statement-03",
			Origin:     "https://github.com/copernico/vulnerability_data",
			Branch:     "master",
			OriginRank: 20,
		},
	}

	st4 = Statement{
		VulnerabilityID: "cve-1234-5678",
		Aliases: []Alias{
			"alias-03",
			"alias-04",
		},
		Notes: []Note{
			{
				Text: "Some additional note about cve-1234-5678",
			},
		},
		Metadata: Metadata{
			LocalPath:  "/tmp/statement-04",
			Origin:     "https://github.com/someoneelse/oss_vulnerabilities",
			Branch:     "master",
			OriginRank: 10,
		},
	}
)

func TestMergeLog(t *testing.T) {
	ml := NewMergeLog("ex_1234")
	logEntry := MergeLogEntry{
		logMessage: "Sample log message",
		sourceStatements: []Statement{
			st3,
			st4,
		},
		success: true,
		policy:  "soft",
	}
	ml.Log(logEntry)
	ml.Dump(".")
}
