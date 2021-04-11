package reconcile

import (
	"fmt"

	"github.com/gookit/color"

	"github.com/manifoldco/promptui"
	"github.com/sap/project-kb/kaybee/internal/model"
)

/*
InteractivePolicy reconciles statements by asking the user to produce
a statement that represents the reconciliation of the input statements.
The solution to the reconciliation is saved, so that if the exact conflicting
statements are seen again, they are automatically reconciled in the same way.
A flag is provided for the user to override this behaviour and reconcile again.

In practice, the execution will stop and ask the user to solve the conflict
by picking pieces of the conflicting statements and putting them together,
possibly with further tweaking, to produce the resulting statement.

For each section of the statement structure, the user can:
- chose it from one (or more) of the input statements
(if more than one is chosen, the union of the contents is taken)
- edit it manually

This is then validated and if it is valid, the merge operation will be stored
in the mergelog.
*/
type InteractivePolicy struct{}

// NewInteractivePolicy constructs a new InteractivePolicy instance
func NewInteractivePolicy() Policy {
	return Policy{
		reconciler: InteractivePolicy{},
	}
}

// Reconcile returns a single statement out of a list of statements
func (s InteractivePolicy) Reconcile(statements []model.Statement) Result {
	var (
		mergedStatement model.Statement
		err             error
		vulnID          = statements[0].VulnerabilityID
	)

	aliases := []string{"Vim", "Emacs", "Sublime", "VSCode", "Atom"}
	index := -1
	var result string

	for index < 0 {
		prompt := promptui.SelectWithAdd{
			Label:    "What's your text editor",
			Items:    aliases,
			AddLabel: "Other",
		}

		index, result, err = prompt.Run()

		if index == -1 {
			aliases = append(aliases, result)
		}
	}

	if err != nil {
		fmt.Printf("Prompt failed %v\n", err)
		return Result{}
	}

	fmt.Printf("You choose %s\n", result)

	mergedStatement.VulnerabilityID = vulnID
	fmt.Printf("\n")
	color.Info.Prompt("Reconciling fixes for %s", vulnID)
	color.Info.Prompt("Using sources:")
	for _, s := range statements {
		color.Info.Prompt(" * %s [%s] (rank: %d)", s.Metadata.Origin, s.Metadata.Branch, s.Metadata.OriginRank)
	}

	// ask the user what aliases to keep

	// ask the user what fixes to keep

	// ask the user what affected artifacts to keep

	// ask user what notes to keep

	// ask user what links to keep

	// offer the possibility to edit the resulting statements

	// ask a log message for the mergelog

	return Result{
		reconciledStatement: mergedStatement,
		candidateStatements: statements,
		comment:             fmt.Sprintf("Reconciled %d statements about vuln. '%s'", len(statements), vulnID),
		success:             true,
	}
}

// Reduce only keeps independent statements and discards statements that are non-independent
func (s InteractivePolicy) Reduce(stmts map[string][]model.Statement) (map[string][]model.Statement, MergeLog, error) {
	var mergeLog = NewMergeLog("exec_123456789")
	var logEntry MergeLogEntry

	var statementsToReconcile []model.Statement

	for st := range stmts {
		conflictingStatementsCount := len(stmts[st])
		statementsToReconcile = stmts[st]

		if conflictingStatementsCount > 1 {
			result := s.Reconcile(statementsToReconcile)
			stmts[st] = []model.Statement{result.reconciledStatement}
			logEntry = MergeLogEntry{
				policy:             "INTERACTIVE",
				logMessage:         result.comment,
				sourceStatements:   result.candidateStatements,
				resultingStatement: result.reconciledStatement,
				success:            true,
			}

		} else {
			logEntry = MergeLogEntry{
				policy:             "INTERACTIVE",
				logMessage:         fmt.Sprintf("Found a single statement about vuln. '%s'", st),
				sourceStatements:   statementsToReconcile,
				resultingStatement: statementsToReconcile[0],
				success:            true,
			}

		}

		mergeLog.Log(logEntry)
	}

	return stmts, mergeLog, nil
}
