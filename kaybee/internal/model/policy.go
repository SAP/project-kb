package model

// See https://github.com/tmrts/go-patterns/blob/master/behavioral/policy.md
// for an explanation of the pattern adopted here

// The StatementReconciler interface defines the types that have the capability to reconcile statements
// that are not independent and how to reduce sets of statements by applying such reconcile operation
// to non-independent statements
type StatementReconciler interface {
	Reconcile([]Statement) ReconcileResult
	Reduce(stmts map[string][]Statement) (map[string][]Statement, MergeLog, error)
}

// ReconcileResult encodes the result of a reconcile operation
type ReconcileResult struct {
	reconciledStatement Statement
	candidateStatements []Statement
	comment             string
	success             bool
}

// Policy represents a way to reconcile non-independent statements and how
// to reduce sets of statements merging those that can be reconciled
type Policy struct {
	reconciler StatementReconciler
}

// Reconcile merges two statements into one as specified in the Merger object
func (s *Policy) Reconcile(statements []Statement) ReconcileResult {
	// the actual Merge() that is invoked is the one defined
	// in a type that implements the StatementReconciler interface and
	// an instance of which is assigned to the reconciler field of a Policy instance
	return s.reconciler.Reconcile(statements)
}

// Reduce scans a list of Statements and merges those that can be reconciled
func (s *Policy) Reduce(stmts map[string][]Statement) (map[string][]Statement, MergeLog, error) {
	// the actual Merge() that is invoked is the one defined
	// in a type that implements the StatementReconciler interface and
	// an instance of which is assigned to the reconciler field of a Policy instance
	return s.reconciler.Reduce(stmts)
}
