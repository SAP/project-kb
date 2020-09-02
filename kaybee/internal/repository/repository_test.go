package repository

// func TestFetch(t *testing.T) {
// 	repository := NewRepository("https://github.com/ichbinfrog/test_2", "master", true, 1, "file:///../../.kaybee/repositories")

// 	// defer os.RemoveAll(repository.Path)

// 	// Remove old repository
// 	os.RemoveAll(repository.Path)

// 	// Test repository fetching from empty repo
// 	repository.Fetch(false)

// 	// Test repository fetching from preexisting repo
// 	repository.Fetch(false)

// 	// Test metadata fill
// 	statements, err := repository.Statements()
// 	if err != nil {
// 		t.Error(err)
// 	}
// 	for _, s := range statements {
// 		log.Printf("%+v\n", s)
// 	}
// }

/* func TestListFetch(t *testing.T) {
	repository := &List{}
	repository.New([]string{
		"https://github.com/ichbinfrog/test",
		"https://github.com/ichbinfrog/test_2",
	}, "master", ".")

	repository.Fetch()
} */
