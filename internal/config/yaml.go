// Package config provides YAML file loader.
//
// File: internal/config/yaml.go

package config

import (
	"context"
	"fmt"
	"os"

	"gopkg.in/yaml.v3"
)

// YamlLoader loads configuration from a YAML file.
type YamlLoader struct {
	path string
}

// NewYamlLoader creates a loader for the given file path.
func NewYamlLoader(path string) *YamlLoader {
	return &YamlLoader{path: path}
}

// Load reads and parses the YAML file.
// Returns an empty map if the file does not exist (no error).
func (l *YamlLoader) Load(ctx context.Context) (map[string]interface{}, error) {
	data, err := os.ReadFile(l.path)
	if err != nil {
		if os.IsNotExist(err) {
			return make(map[string]interface{}), nil
		}
		return nil, fmt.Errorf("read yaml file: %w", err)
	}
	var result map[string]interface{}
	if err := yaml.Unmarshal(data, &result); err != nil {
		return nil, fmt.Errorf("parse yaml: %w", err)
	}
	return result, nil
}

// EOF: internal/config/yaml.go