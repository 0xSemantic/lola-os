// Example 03: Register and call a custom tool.
//
// File: sdk/examples/03_custom_tool/main.go

package main

import (
	"context"
	"fmt"
	"log"

	"github.com/0xSemantic/lola-os/sdk"
	"github.com/0xSemantic/lola-os/sdk/types"
)

// Custom tool that greets a user.
func greetTool(ctx context.Context, args map[string]interface{}) (interface{}, error) {
	name, ok := args["name"].(string)
	if !ok {
		return nil, fmt.Errorf("missing 'name' argument")
	}
	return fmt.Sprintf("Hello, %s!", name), nil
}

func main() {
	// Register the tool globally.
	sdk.RegisterTool("greet", greetTool)

	rt := sdk.Init()

	err := rt.Run(context.Background(), func(ctx context.Context, rt *sdk.Runtime) error {
		result, err := rt.Execute(ctx, "greet", map[string]interface{}{
			"name": "LOLA",
		})
		if err != nil {
			return err
		}
		fmt.Println(result)
		return nil
	})

	if err != nil {
		log.Fatal(err)
	}
}

// EOF: sdk/examples/03_custom_tool/main.go