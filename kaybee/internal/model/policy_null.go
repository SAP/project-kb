package model

// NullPolicy implements a policy that does nothing
type NullPolicy struct{}

// NewNullPolicy constructs a new NullPolicy instance
func NewNullPolicy() Policy {
	return Policy{reconciler: NullPolicy{}}
}

// Reconcile just returns the first of the two statements as is
func (st NullPolicy) Reconcile(statements []Statement) ReconcileResult {
	return ReconcileResult{
		reconciledStatement: Statement{},
		candidateStatements: statements,
		comment:             "Method Reconcile() does nothing in the NullPolicy!",
		success:             false,
	}
}

// Reduce just returns the same statements as passed in input
func (st NullPolicy) Reduce(stmts map[string][]Statement) (map[string][]Statement, MergeLog, error) {
	return stmts, MergeLog{}, nil
}
