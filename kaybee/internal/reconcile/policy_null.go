package reconcile

import "github.com/sap/project-kb/kaybee/internal/model"

// NullPolicy implements a policy that does nothing
type NullPolicy struct{}

// NewNullPolicy constructs a new NullPolicy instance
func NewNullPolicy() Policy {
	return Policy{reconciler: NullPolicy{}}
}

// Reconcile just returns the first of the two statements as is
func (st NullPolicy) Reconcile(statements []model.Statement) ReconcileResult {
	return ReconcileResult{
		reconciledStatement: model.Statement{},
		candidateStatements: statements,
		comment:             "Method Reconcile() does nothing in the NullPolicy!",
		success:             false,
	}
}

// Reduce just returns the same statements as passed in input
func (st NullPolicy) Reduce(stmts map[string][]model.Statement) (map[string][]model.Statement, MergeLog, error) {
	return stmts, MergeLog{}, nil
}
