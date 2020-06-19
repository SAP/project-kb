package strings

import "testing"

func TestIndent(t *testing.T) {
	type args struct {
		objToPrint interface{}
		indent     string
	}
	tests := []struct {
		name string
		args args
		want string
	}{
		{
			"basic",
			args{"x", "    "},
			"    x",
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := Indent(tt.args.objToPrint, tt.args.indent); got != tt.want {
				t.Errorf("Indent() = '%v', want '%v'", got, tt.want)
			}
		})
	}
}
