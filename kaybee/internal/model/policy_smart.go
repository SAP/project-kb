package model

import (
	"fmt"
)

/*
SmartPolicy reconciles statements trying hard to merge different sources.
*/
type SmartPolicy struct{}

// NewSmartPolicy constructs a new SoftPolicy instance
func NewSmartPolicy() Policy {
	return Policy{
		reconciler: SmartPolicy{},
	}
}

// Reduce only keeps independent statements and discards statements that are non-independent
func (s SmartPolicy) Reduce(stmts map[string][]Statement) (map[string][]Statement, MergeLog, error) {
	var mergeLog = NewMergeLog("exec_123456789")
	var logEntry MergeLogEntry

	// var statementsToReconcile []Statement

	for st := range stmts {
		// conflictingStatementsCount := len(stmts[st])
		// statementsToReconcile = stmts[st]

		result := s.Reconcile(stmts[st])
		stmts[st] = []Statement{result.reconciledStatement}
		logEntry = MergeLogEntry{
			policy:             "SMART",
			logMessage:         result.comment,
			sourceStatements:   result.candidateStatements,
			resultingStatement: result.reconciledStatement,
			success:            true,
		}

		mergeLog.Log(logEntry)
	}

	return stmts, mergeLog, nil
}

// Reconcile returns a single statement out of a list of statements
func (s SmartPolicy) Reconcile(statements []Statement) ReconcileResult {
	var (
		reconcileResult ReconcileResult
		mergedStatement Statement
		vulnID          = statements[0].VulnerabilityID
	)

	mergedStatement.VulnerabilityID = vulnID

	rankedCandidates := rankStatements(statements)

	for _, sameRankCandidates := range rankedCandidates {
		if len(sameRankCandidates) > 1 {
			reconcileResult = ReconcileResult{
				reconciledStatement: Statement{},
				candidateStatements: statements,
				comment:             fmt.Sprintf("Reconcile aborted, there are multiple statements from same-rank sources for %s", vulnID),
				success:             false,
			}
			return reconcileResult
		}
		for _, c := range sameRankCandidates {
			fmt.Printf("Examining candidate at rank %d\n", c.Metadata.OriginRank)
			// if mergedStatement.Fixes
		}
	}

	reconcileResult = ReconcileResult{
		reconciledStatement: mergedStatement,
		candidateStatements: statements,
		comment:             fmt.Sprintf("Reconciled %d statements about vuln. '%s'", len(statements), vulnID),
		success:             true,
	}

	return reconcileResult

}

// return a list of lists of statements, grouped by rank
func rankStatements(statements []Statement) (results [][]Statement) {
	results = append(results, statements)
	return results
}

// // ReconcileAliases implements the policy to reconcile the Aliases
// // section of a Statement
// // Result: union
// func (s *SmartPolicy) ReconcileAliases(statements []Statement, result *Statement) error {
// 	aliasSet := make(map[Alias]struct{})

// 	for _, item := range statements {
// 		for _, a := range item.Aliases {
// 			aliasSet[a] = struct{}{}
// 		}
// 	}

// 	for k := range aliasSet {
// 		result.Aliases = append(result.Aliases, k)
// 	}

// 	return nil
// }

// // ReconcileFixesAndNotes implements the policy to reconcile the Fixes
// // section of a Statement as well as the Notes
// // Result: take all the fixes from the highest ranked source. If same rank, fail.
// //
// // As for Notes: take them from the Statement from which the Fixes are taken.
// // If there are other Statements that do not bring Fixes, append their Notes.
// // IGNORE THIS: Description-only statemetns should only be considered if they are reconciled with
// // another non-independent statement that does have fixes
// /*

// cases:
// - multiple top-rank sources
// 	- FAIL
// - one top-rank source has fixes, additional lower-rank sources have notes
// 	- take fixes from top-rank, append notes from all the other lower-rank sources that do now bring fixes
// - one top-rank source has only notes
// 	- take those notes, plus take fixes (and notes if any) from second-best ranked, if unique, else FAIL

// */
// func (s *SmartPolicy) ReconcileFixesAndNotes(statements []Statement, result *Statement) error {
// 	var topRank int = 1000
// 	var countTopRank = 0
// 	var selectedOrigin string
// 	var selectedOriginBranch string

// 	var additionalNotes []Note

// 	for _, s := range statements {
// 		if len(s.Fixes) > 0 {
// 			if s.Metadata.OriginRank > topRank {
// 				continue
// 			}

// 			if s.Metadata.OriginRank == topRank {
// 				countTopRank++
// 				continue
// 			}

// 			countTopRank = 1
// 			topRank = s.Metadata.OriginRank
// 			result.Notes = s.Notes
// 			result.Fixes = s.Fixes
// 			selectedOrigin = s.Metadata.Origin
// 			selectedOriginBranch = s.Metadata.Branch

// 		} else {
// 			additionalNotes = append(additionalNotes, s.Notes...)
// 		}

// 	}

// 	result.Notes = append(result.Notes, additionalNotes...)

// 	if countTopRank > 1 {
// 		return errors.ErrConflictingStatements
// 	}

// 	fmt.Printf("Reconciled by taking the fixes from top-rank source %s (%s), rank %d\n", selectedOrigin, selectedOriginBranch, topRank)

// 	return nil
// }

// // ReconcileAffectedArtifacts implements the policy to reconcile the AffectedArtifact
// // section of a Statement
// //
// // Result: union
// // func (s *SoftPolicy) ReconcileAffectedArtifacts(a, b Statement) Statement {
// // 	affectedArtifactSet := make(map[string]struct{})

// // 	// take all elements in a...
// // 	for _, item := range a {
// // 		affectedArtifactSet[item.Identifier] = struct{}{}
// // 	}

// // 	// ...and add all elements in b that are not in a
// // 	for _, item := range b {
// // 		if _, ok := affectedArtifactSet[item.Identifier]; !ok {
// // 			a = append(a, item)
// // 		}
// // 	}
// // 	return a
// // }
