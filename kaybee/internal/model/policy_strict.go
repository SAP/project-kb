package model

import (
	"fmt"

	"github.com/rs/zerolog/log"
)

// StrictPolicy refuses to solve conflicts and does not perform any reconcile action;
// In other words, non-independent statements are not reconciled, but reported to the user
// who might then want to merge them manually
type StrictPolicy struct {
}

// NewStrictPolicy creates and initializes a new StrictPolicy instance
func NewStrictPolicy() Policy {
	s := Policy{
		reconciler: StrictPolicy{},
	}
	return s
}

// Reconcile does nothing (returns always a void Statement); if the two statements in input
// are not independent a suitable error signals it
// This is implemented just to satisfy the StatementReconciler interface, but this method
// is not supposed to be called ever.
func (p StrictPolicy) Reconcile(statements []Statement) ReconcileResult {
	log.Fatal().Msg("Method Reconcile() should not be invoked on a StrictPolicy!")
	return ReconcileResult{
		reconciledStatement: Statement{},
		candidateStatements: statements,
		comment:             "Method Reconcile() should not be invoked on a StrictPolicy!",
		success:             false,
	}
}

// Reduce only keeps independent statemens and discards statements that are non-independent
func (p StrictPolicy) Reduce(stmts map[string][]Statement) (map[string][]Statement, MergeLog, error) {
	var mergeLog = NewMergeLog("exec_123456789")
	var logEntry MergeLogEntry

	var statementsToReconcile []Statement

	for s := range stmts {
		conflictingStatementsCount := len(stmts[s])
		statementsToReconcile = stmts[s]

		if conflictingStatementsCount > 1 {
			log.Warn().Int("n_conflicting_statements", len(stmts[s])).Str("affected_vulnerability", s).Msg("Found conflicting statements (will not be reconciled with 'strict' policy)")
			log.Warn().Msg("You may want to try again using another policy, which you can specify with the '-p' flag.\nExample: kaybee merge -p soft")
			delete(stmts, s)
			logEntry = MergeLogEntry{
				policy:             "STRICT",
				logMessage:         fmt.Sprintf("Found %d conflicting statements about vuln. %s; won't reconcile!", conflictingStatementsCount, s),
				sourceStatements:   statementsToReconcile,
				resultingStatement: Statement{},
				success:            false,
			}
		} else {
			logEntry = MergeLogEntry{
				policy:             "STRICT",
				logMessage:         fmt.Sprintf("Found a single statement about vuln. '%s'", s),
				sourceStatements:   statementsToReconcile,
				resultingStatement: statementsToReconcile[0],
				success:            true,
			}
		}
		mergeLog.Log(logEntry)

	}

	return stmts, mergeLog, nil
}
