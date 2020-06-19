package browser

import (
	"fmt"
	"log"
	"os/exec"
	"runtime"
)

// OpenURL opens the default browser to the url specified
func OpenURL(url string) {
	var err error

	switch runtime.GOOS {
	case "linux":
		err = exec.Command("xdg-open", url).Start()
	case "windows":
		err = exec.Command("rundll32", "url.dll,FileProtocolHandler", url).Start()
	case "darwin":
		err = exec.Command("open", url).Start()
	default:
		err = fmt.Errorf("unsupported platform: " + runtime.GOOS)
	}
	if err != nil {
		log.Fatal(err)
	}
}
