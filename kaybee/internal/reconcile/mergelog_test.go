package reconcile

import (
	"testing"

	"github.com/sap/project-kb/kaybee/internal/model"
)

var (
	st3 = model.Statement{
		VulnerabilityID: "cve-1234-5678",
		Aliases: []model.Alias{
			"alias-01",
			"alias-02",
		},
		Notes: []model.Note{
			{
				Links: []string{
					"some_link",
					"another_link",
				},
				Text: "Some note about cve-1234-5678",
			},
		},
		Metadata: model.Metadata{
			LocalPath:  "/tmp/statement-03",
			Origin:     "https://github.com/copernico/vulnerability_data",
			Branch:     "master",
			OriginRank: 20,
		},
	}

	st4 = model.Statement{
		VulnerabilityID: "cve-1234-5678",
		Aliases: []model.Alias{
			"alias-03",
			"alias-04",
		},
		Notes: []model.Note{
			{
				Text: "Some additional note about cve-1234-5678",
			},
		},
		Metadata: model.Metadata{
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
		sourceStatements: []model.Statement{
			st3,
			st4,
		},
		success: true,
		policy:  "soft",
	}
	ml.Log(logEntry)
	ml.Dump(".")
}
